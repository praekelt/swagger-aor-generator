import copy

import click
import inflect
import jinja2
import json
import os
import sys
from swagger_parser import SwaggerParser

words = inflect.engine()

DEFAULT_OUTPUT_DIR = "./generated"
DEFAULT_MODULE = "generated"

# Defaults used when the path is "/".
ROOT_CLASS_NAME = u"Root"
ROOT_OPERATION = u"root"

# Known extensions in lowercase
YAML_EXTENSIONS = ["yaml", "yml"]
JSON_EXTENSIONS = ["json"]

# Choices provided when specifying the specification format
SPEC_JSON = "json"
SPEC_YAML = "yaml"
SPEC_CHOICES = [SPEC_JSON, SPEC_YAML]

BACKEND_CHOICES = ["aor"]

# Component Mapping for swagger types to AOR components
COMPONENT_MAPPING = {
    "Field": {
        "integer": "NumberField",
        "string": "TextField",
        "object": "ObjectField",
        "boolean": "BooleanField",
        "date-time": "DateTimeField",
        "date": "DateField",
        "enum": "SelectField",
        "relation": "ReferenceField",
        "many": "ReferenceManyField"
    },
    "Input": {
        "integer": "NumberInput",
        "string": "TextInput",
        "object": "LongTextInput",
        "boolean": "BooleanInput",
        "date-time": "DateTimeInput",
        "date": "DateInput",
        "enum": "SelectInput",
        "relation": "ReferenceInput",
        "many": "ReferenceManyField"
    }
}

COMPONENT_SUFFIX = {
    "list": "Field",
    "show": "Field",
    "create": "Input",
    "edit": "Input"
}

SUPPORTED_COMPONENTS = ["list", "show", "create", "edit"]


def render_to_string(backend, filename, context):
    # type: (str, str, Dict) -> str
    """
    Render a template using the specified context
    :param backend: The backend for which the template is rendered
    :param filename: The template name
    :param context: The data to use when rendering the template
    :return: The rendered template as a string
    """
    template_directory = "./swagger_django_generator/templates/{}".format(backend)
    loaders = [jinja2.FileSystemLoader(template_directory)]
    try:
        import swagger_django_generator
        loaders.append(jinja2.PackageLoader("swagger_django_generator", "templates/{}".format(backend)))
    except ImportError:
        pass

    return jinja2.Environment(
        loader=jinja2.ChoiceLoader(loaders),
        trim_blocks=True,
        lstrip_blocks=True
    ).get_template(filename).render(context)


class Generator(object):

    def __init__(self, output_dir, module_name=DEFAULT_MODULE, verbose=False,
                 rest_server_url=None):
        self.parser = None
        self.module_name = module_name
        self._resources = None
        self.verbose = verbose
        self.output_dir = output_dir
        self.rest_server_url = rest_server_url

    def load_specification(self, specification_path, spec_format=None):
        # If the swagger spec format is not specified explicitly, we try to
        # derive it from the specification path
        if not spec_format:
            filename = os.path.basename(specification_path)
            extension = filename.rsplit(".", 1)[-1]
            if extension in YAML_EXTENSIONS:
                spec_format = SPEC_YAML
            elif extension in JSON_EXTENSIONS:
                spec_format = SPEC_JSON
            else:
                raise RuntimeError("Could not infer specification format. Use "
                                   "--spec-format to specify it explicitly.")

        click.secho("Using spec format '{}'".format(spec_format), fg="green")
        if spec_format == SPEC_YAML:
            with open(specification_path, "r") as f:
                self.parser = SwaggerParser(swagger_yaml=f)
        else:
            self.parser = SwaggerParser(swagger_path=specification_path)

        self._make_resource_definitions()

    def _get_definition_from_ref(self, definition):
        if "$ref" in definition:
            definition_name = \
                self.parser.get_definition_name_from_ref(definition["$ref"])
            ref_def = self.parser.specification["definitions"][definition_name]
            title = definition_name.replace("_", " ").title().replace(" ", "")
            return ref_def, title
        else:
            return definition, None

    def _get_resource_attributes(self, resource_name, properties,
                                 definition, suffix, fields=None):
        attributes = []
        for name, details in properties.items():
            # Check for desired fields and continue if not in there.
            if fields is not None:
                if name not in fields:
                    continue
            # Handle reference definition
            _property, title = self._get_definition_from_ref(details)
            # Don't handle referenced objects yet.
            if _property.get("properties", None) is not None:
                continue
            attribute = {
                "source": name,
                "type": _property.get("type", None),
                "required": name in definition.get("required", []),
                "read_only": _property.get("readOnly", False)
                if suffix == "Input" else False
            }
            # Add DisabledInput to Imports if read_only is true.
            if attribute["read_only"] and "DisabledInput" \
                    not in self._resources[resource_name]["imports"]:
                self._resources[resource_name]["imports"].append("DisabledInput")

            # Based on the type/format combination get the correct
            # AOR component to use.
            related_field = False
            if attribute["type"] in COMPONENT_MAPPING[suffix]:
                # Check if it is a related field or not
                if _property.get("x-related-info", None) is not None:
                    related_info = _property["x-related-info"]
                    model = related_info.get("model", False)
                    # Check if related model is not set to None.
                    if model is not None:
                        related_field = True
                        # If model didn't even exist then attempt to guess the model
                        # from the substring before the last "_".
                        if not model:
                            model = name.rsplit("_", 1)[0]
                        attribute["label"] = model.replace("_", " ").title()
                        # If a custom base path has been given set the reference to it
                        # else attempt to get the plural of the given model.
                        if related_info.get("rest_resource_name", None) is not None:
                            reference = related_info["rest_resource_name"]
                        else:
                            reference = words.plural(model.replace("_", ""))
                        attribute["reference"] = reference
                        # Get the related model field from the specification or
                        # attempt to guess it from the substring after the last "_".
                        field = related_info.get("field", None)
                        if field is None:
                            field = name.rsplit("_", 1)[1]
                        attribute["related_field"] = field
                        attribute["option_text"] = related_info.get("label", None)

                elif name.endswith("_id"):
                    related_field = True
                    relation = name.replace("_id", "")
                    attribute["label"] = relation.title()
                    attribute["reference"] = words.plural(relation)
                    attribute["related_field"] = "id"

                # LongTextFields don't exist
                # Handle component after figuring out if a related field or not.
                if not related_field:
                    if _property.get("format", None) in COMPONENT_MAPPING[suffix]:
                        # DateTimeField is currently not supported.
                        if suffix == "Field" and _property["format"] == "date-time":
                            _type = "date"
                        else:
                            _type = _property["format"]
                        attribute["component"] = \
                            COMPONENT_MAPPING[suffix][_type]
                    else:
                        attribute["component"] = \
                            COMPONENT_MAPPING[suffix][attribute["type"]]
                else:
                    attribute["component"] = \
                        COMPONENT_MAPPING[suffix]["relation"]
                    if suffix != "Input":
                        attribute["related_component"] = \
                            COMPONENT_MAPPING[suffix][attribute["type"]]
                    else:
                        attribute["related_component"] = "SelectInput"

            # Handle an enum possibility
            if _property.get("enum", None) is not None:
                attribute["component"] = COMPONENT_MAPPING[suffix]["enum"]
                attribute["choices"] = _property["enum"]

            if attribute.get("component", None) is not None:
                # Add component to resource imports if not there.
                if attribute["component"] not in \
                        self._resources[resource_name]["imports"]:
                    self._resources[resource_name]["imports"].append(
                        attribute["component"]
                    )
                # Add related component to resource imports if not there.
                if attribute.get("related_component", None) is not None:
                    if attribute["related_component"] not in \
                            self._resources[resource_name]["imports"]:
                        self._resources[resource_name]["imports"].append(
                            attribute["related_component"]
                        )
                attributes.append(attribute)
        return attributes

    def _get_resource_from_definition(self, resource_name, head_component,
                                      definition):
        self._resources[resource_name][head_component] = {}
        suffix = COMPONENT_SUFFIX[head_component]
        properties = definition.get("properties", {})
        resource = self._get_resource_attributes(
            resource_name=resource_name,
            properties=properties,
            definition=definition,
            suffix=suffix
        )
        # Only add if there is something in resource
        if resource:
            self._resources[resource_name][head_component]["fields"] = resource

        # Check if there are inline models for the given resource.
        inlines = self.parser.specification.get(
            "x-detail-page-definitions", None
        )
        # Inlines are only shown on the Show and Edit components.
        if inlines is not None and head_component in ["show", "edit"]:
            if resource_name in inlines:
                self._resources[resource_name][head_component]["inlines"] = []
                inlines = inlines[resource_name]["inlines"]
                for inline in inlines:
                    model = inline["model"]
                    label = inline.get("label", None)
                    # If a custom base path has been given.
                    if inline.get("rest_resource_name", None) is not None:
                        reference = inline["rest_resource_name"]
                    else:
                        reference = words.plural(model.replace("_", ""))
                    fields = inline.get("fields", None)
                    many_field = {
                        "label": label or model.replace("_", " ").title(),
                        "reference": reference,
                        "target": inline["key"],
                        "component": COMPONENT_MAPPING[suffix]["many"]
                    }
                    # Add ReferenceMany component to imports
                    if many_field["component"] not in \
                            self._resources[resource_name]["imports"]:
                        self._resources[resource_name]["imports"].append(
                            many_field["component"]
                        )
                    inline_def = \
                        self.parser.specification["definitions"][inline["model"]]
                    properties = inline_def.get("properties", {})
                    many_field["fields"] = self._get_resource_attributes(
                        resource_name=resource_name,
                        properties=properties,
                        definition=inline_def,
                        suffix="Field",
                        fields=fields
                    )
                    self._resources[resource_name][head_component]["inlines"].append(
                        many_field
                    )

    def _make_resource_definitions(self):
        self._resources = {}

        for path, verbs in self.parser.specification["paths"].items():
            for verb, io in verbs.items():

                # Check if this is not a valid path method then skip it.
                if verb == "parameters":
                    continue
                elif not io.get("operationId", None):
                    continue

                # Get resource name and path and add it to the list
                # for the first occurring instance of the resource
                operation_id = io["operationId"]
                name = operation_id.split("_")[0]
                if name not in self._resources:
                    self._resources[name] = {
                        "path": path[1:].split("/")[0],
                        "imports": [],
                        "has_methods": False
                    }

                definition = None
                head_component = None

                # Get the correct definition/head_component/component suffix per
                # verb based on the operation.
                _create = "create" in operation_id
                _update = "update" in operation_id
                if "read" in operation_id:
                    definition, title = self._get_definition_from_ref(
                        definition=io["responses"]["200"]["schema"]
                    )
                    self._resources[name]["title"] = title or name
                    head_component = "show"
                    # Add show component imports
                    if "Show" not in self._resources[name]["imports"]:
                        self._resources[name]["imports"].append("Show")
                        self._resources[name]["imports"].append("SimpleShowLayout")
                elif "list" in operation_id:
                    definition, title = self._get_definition_from_ref(
                        definition=io["responses"]["200"]["schema"]["items"]
                    )
                    head_component = "list"
                    # Add list component imports
                    if "List" not in self._resources[name]["imports"]:
                        self._resources[name]["imports"].append("List")
                        self._resources[name]["imports"].append("Datagrid")
                    filters = []
                    # Get all method filters for the list component.
                    for parameter in io.get("parameters", []):
                        # If the parameter is a reference, get the actual parameter.
                        if "$ref" in parameter:
                            ref = parameter["$ref"].split("/")[2]
                            param = self.parser.specification["parameters"][ref]
                        else:
                            param = parameter
                        # Filters are only in the query string and their type needs
                        # to be a supported component.
                        if param["in"] == "query" \
                                and param["type"] in COMPONENT_MAPPING["Input"]:
                            filters.append({
                                "source": param["name"],
                                "label": param["name"].replace("_", " ").title(),
                                "component": COMPONENT_MAPPING["Input"][param["type"]]
                            })
                    self._resources[name]["filters"] = filters
                elif _create or _update:
                    for parameter in io.get("parameters", []):
                        # If the parameter is a reference, get the actual parameter.
                        if "$ref" in parameter:
                            ref = parameter["$ref"].split("/")[2]
                            param = self.parser.specification["parameters"][ref]
                        else:
                            param = parameter
                        # Grab the body parameter as the create definition
                        if param["in"] == "body":
                            definition, title = self._get_definition_from_ref(
                                definition=param["schema"]
                            )
                    head_component = "create" if _create else "edit"
                    # Add SimpleForm and the head component to the imports
                    if "SimpleForm" not in self._resources[name]["imports"]:
                        self._resources[name]["imports"].append("SimpleForm")
                    the_import = head_component.title()
                    if the_import not in self._resources[name]["imports"]:
                        self._resources[name]["imports"].append(the_import)
                if head_component and definition:
                    # Toggle to be included in AOR if it has a single method.
                    self._resources[name]["has_methods"] = True
                    self._get_resource_from_definition(
                        resource_name=name,
                        head_component=head_component,
                        definition=definition
                    )

    def generate_app_js(self):
        """
        Generate an `App.js` file from the given specification.
        :return: str
        """
        return render_to_string(self.backend, "App.js", {
            "title": self.module_name,
            "rest_server_url": self.rest_server_url,
            "resources": self._resources,
            "supported_components": SUPPORTED_COMPONENTS
        })

    def generate_resource_js(self, name, resource):
        """
        Generate a single resource component file.
        :return: str
        """
        return render_to_string(self.backend, "Resource.js", {
            "name": name,
            "resource": resource,
            "supported_components": SUPPORTED_COMPONENTS
        })

    def generate_filters_js(self):
        """
        Generate a filter components file.
        :return: str
        """
        return render_to_string(self.backend, "Filters.js", {
            "resources": self._resources
        })

    def add_additional_file(self, filename):
        """
        Add an additional file, that does not require context,
        to the generated admin.
        :return: str
        """
        return render_to_string(self.backend, filename, {})

    def aor_generation(self):
        click.secho("Generating App.js component file...", fg="green")
        with open(os.path.join(self.output_dir, "App.js"), "w") as f:
            data = self.generate_app_js()
            f.write(data)
            if self.verbose:
                print(data)
        click.secho("Generating resource component files...", fg="green")
        for name, resource in self._resources.items():
            title = resource.get("title", None)
            if title:
                click.secho("Generating {}.js file...".format(title), fg="green")
                with open(os.path.join(self.output_dir, "{}.js".format(title)), "w") as f:
                    data = self.generate_resource_js(title, resource)
                    f.write(data)
                    if self.verbose:
                        print(data)
        click.secho("Generating Filters.js file...", fg="green")
        with open(os.path.join(self.output_dir, "Filters.js"), "w") as f:
            data = self.generate_filters_js()
            f.write(data)
            if self.verbose:
                print(data)
        click.secho("Adding basic swagger rest server file...", fg="green")
        with open(os.path.join(self.output_dir, "swaggerRestServer.js"), "w") as f:
            data = self.add_additional_file("swaggerRestServer.js")
            f.write(data)
            if self.verbose:
                print(data)
        click.secho("Adding authClient.js file...", fg="green")
        with open(os.path.join(self.output_dir, "authClient.js"), "w") as f:
            data = self.add_additional_file("authClient.js")
            f.write(data)
            if self.verbose:
                print(data)
        click.secho("Adding CustomFields.js file...", fg="green")
        with open(os.path.join(self.output_dir, "CustomFields.js"), "w") as f:
            data = self.add_additional_file("CustomFields.js")
            f.write(data)
            if self.verbose:
                print(data)


@click.command()
@click.argument("specification_path", type=click.Path(dir_okay=False, exists=True))
@click.option("--spec-format", type=click.Choice(SPEC_CHOICES))
@click.option("--verbose/--no-verbose", default=False)
@click.option("--output-dir", type=click.Path(file_okay=False, exists=True,
                                              writable=True),
              default=DEFAULT_OUTPUT_DIR)
@click.option("--module-name", type=str, default=DEFAULT_MODULE,
              help="The name of the module where the generated code will be "
                   "used, e.g. myproject.some_application")
@click.option("--rest_server_url", type=str,
              default="http://localhost:8000/api/v1",
              help="Use a desired rest server URL rather than "
                   "'http://localhost:8000/api/v1'")
def main(specification_path, spec_format, verbose, output_dir, module_name,
         rest_server_url):

    generator = Generator(
        output_dir, module_name=module_name,
        verbose=verbose, rest_server_url=rest_server_url
    )
    try:
        click.secho("Loading specification file...", fg="green")
        generator.load_specification(specification_path, spec_format)
        generator.aor_generation()
        click.secho("Done.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        click.secho("""
        If you get schema validation errors from a yaml Swagger spec that passes validation on other
        validators, it may be because of single apostrophe's (') used in some descriptions. The
        parser used does not like it at all.
        """)


if __name__ == "__main__":
    main()
