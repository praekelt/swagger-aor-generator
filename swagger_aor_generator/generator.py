import click
import inflect
import jinja2
import os
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

BACKEND_CHOICES = ["aor", "ra"]

# File name mapping for versions.
FILENAME_MAPPING = {
    "aor": {
        "main": "App"
    },
    "ra": {
        "main": "ReactAdmin"
    }
}

# Component Mapping for swagger types to AOR components
COMPONENT_MAPPING = {
    "aor": {
        "Field": {
            "boolean": "BooleanField",
            "date": "DateField",
            "date-time": "DateField",
            "enum": "SelectField",
            "integer": "NumberField",
            "many": "ReferenceManyField",
            "object": "ObjectField",
            "relation": "ReferenceField",
            "string": "TextField"
        },
        "Input": {
            "array": "TextInput",
            "boolean": "BooleanInput",
            "date": "DateInput",
            "date-time": "DateTimeInput",
            "date-range": "DateRangeInput",
            "date-time-range": "DateRangeInput",
            "enum": "SelectInput",
            "integer": "NumberInput",
            "many": "ReferenceManyField",
            "object": "LongTextInput",
            "relation": "ReferenceInput",
            "string": "TextInput"
        }
    },
    "ra": {
        "Field": {
            "boolean": "BooleanField",
            "date": "DateField",
            "date-time": "DateField",
            "enum": "SelectField",
            "integer": "NumberField",
            "many": "ReferenceManyField",
            "relation": "ReferenceField",
            "string": "TextField"
        },
        "Input": {
            "array": "TextInput",
            "boolean": "BooleanInput",
            "date": "DateInput",
            "date-time": "DateInput",
            "date-range": "DateRangeInput",
            "date-time-range": "DateRangeInput",
            "enum": "SelectInput",
            "integer": "NumberInput",
            "many": "ReferenceManyField",
            "relation": "ReferenceInput",
            "string": "TextInput"
        }
    }

}

PROPS_MAPPING = {
    "Input": {
        "date-time-range": {
            "time": None
        }
    }
}

COMPONENT_SUFFIX = {
    "list": "Field",
    "show": "Field",
    "create": "Input",
    "edit": "Input"
}

OPERATION_SUFFIXES = ["list", "read", "create", "update", "delete"]

SUPPORTED_COMPONENTS = {
    "aor": ["list", "show", "create", "edit", "remove"],
    "ra": ["list", "show", "create", "edit"]
}

ADDITIONAL_FILES = {
    "aor": {
        "root": ["Theme.js", "utils.js", "catchAll.js"],
        "auth": ["authClient.js"],
        "fields": ["ObjectField.js", "EmptyField.js"],
        "inputs": ["DateRangeInput.js"]
    },
    "ra": {
        "root": ["Theme.js"],
        "auth": ["authProvider.js"]
    }
}

CUSTOM_IMPORTS = {
    "object-field": {
        "name": "ObjectField",
        "directory": "../fields/ObjectField"
    },
    "empty": {
        "name": "EmptyField",
        "directory": "../fields/EmptyField"
    },
    "date-time-input": {
        "name": "DateTimeInput",
        "directory": "aor-datetime-input"
    },
    "permissions": {
        "name": "PermissionsStore",
        "directory": "../auth/PermissionsStore"
    }
}

CUSTOM_COMPONENTS = ["ObjectField", "EmptyField", "DateTimeInput"]


def render_to_string(filename, context, backend):
    # type: (str, Dict) -> str
    """
    Render a template using the specified context
    :param filename: The template name
    :param context: The data to use when rendering the template
    :param backend: The backend templates to use.
    :return: The rendered template as a string
    """
    template_directory = "./swagger_aor_generator/templates/{}".format(backend)
    loaders = [jinja2.FileSystemLoader(template_directory)]
    try:
        import swagger_aor_generator
        loaders.append(
            jinja2.PackageLoader(
                "swagger_aor_generator", "templates/{}".format(backend))
        )
    except ImportError:
        pass

    return jinja2.Environment(
        loader=jinja2.ChoiceLoader(loaders),
        trim_blocks=True,
        lstrip_blocks=True
    ).get_template(filename).render(context)


class Generator(object):

    def __init__(self, output_dir, module_name=DEFAULT_MODULE,
                 admin_version="aor", verbose=False,
                 rest_server_url=None, permissions=False):
        self.parser = None
        self.module_name = module_name
        self.admin_version = admin_version
        self._resources = None
        self.verbose = verbose
        self.output_dir = output_dir
        self.rest_server_url = rest_server_url
        self.permissions = permissions

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
        found_reference = False
        for name, details in properties.items():
            # Check for desired fields and continue if not in there.
            if fields is not None:
                if name not in fields:
                    continue
            # Handle reference definition
            _property, title = self._get_definition_from_ref(details)
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
                self._resources[resource_name]["imports"].append(
                    "DisabledInput")

            # Based on the type/format combination get the correct
            # AOR component to use.
            related_field = False
            if attribute["type"] in COMPONENT_MAPPING[self.admin_version][suffix]:
                # Check if it is a related field or not
                if _property.get("x-related-info", None) is not None:
                    if self.permissions and not found_reference:
                        found_reference = True
                        custom_imports = [
                            custom["name"]
                            for custom in self._resources[resource_name]["custom_imports"]
                        ]
                        if "EmptyField" not in custom_imports:
                            self._resources[resource_name]["custom_imports"].append(
                                CUSTOM_IMPORTS["empty"]
                            )
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
                        # Get the option text to be used in the Select input from the
                        # label field, else guess it from the current property name.
                        guess = name.rsplit("_", 1)[1]
                        label = related_info.get("label", None) or guess
                        attribute["option_text"] = label

                elif name.endswith("_id"):
                    related_field = True
                    relation = name.replace("_id", "")
                    attribute["label"] = relation.title()
                    attribute["reference"] = words.plural(relation)
                    attribute["related_field"] = "id"

                # LongTextFields don't exist
                # Handle component after figuring out if a related field or not.
                if not related_field:
                    if _property.get("format", None) in COMPONENT_MAPPING[self.admin_version][suffix]:
                        # DateTimeField is currently not supported.
                        if suffix == "Field" and _property["format"] == "date-time":
                            _type = "date"
                        else:
                            _type = _property["format"]
                        attribute["component"] = \
                            COMPONENT_MAPPING[self.admin_version][suffix][_type]
                    else:
                        attribute["component"] = \
                            COMPONENT_MAPPING[self.admin_version][suffix][attribute["type"]]
                else:
                    attribute["component"] = \
                        COMPONENT_MAPPING[self.admin_version][suffix]["relation"]
                    if suffix != "Input":
                        attribute["related_component"] = \
                            COMPONENT_MAPPING[self.admin_version][suffix][attribute["type"]]
                    else:
                        attribute["related_component"] = "SelectInput"

            # Handle an enum possibility
            if _property.get("enum", None) is not None:
                attribute["component"] = COMPONENT_MAPPING[self.admin_version][suffix]["enum"]
                # Only add choices if an input
                if suffix == "Input":
                    attribute["choices"] = _property["enum"]

            if attribute.get("component", None) is not None:
                # Add component to resource imports if not there.
                if attribute["component"] not in \
                        self._resources[resource_name]["imports"] and \
                        attribute["component"] not in CUSTOM_COMPONENTS:
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
            # Check for custom import types here.
            _type = "{}-{}".format(attribute["type"], suffix.lower())
            _format = "{}-{}".format(_property.get("format",
                                                   ""), suffix.lower())
            if _type in CUSTOM_IMPORTS or _format in CUSTOM_IMPORTS:
                custom_imports = [
                    custom["name"]
                    for custom in self._resources[resource_name]["custom_imports"]
                ]
                _import = CUSTOM_IMPORTS.get(
                    _format) or CUSTOM_IMPORTS.get(_type)
                if _import["name"] not in custom_imports:
                    self._resources[resource_name]["custom_imports"].append(
                        _import
                    )

        return attributes

    def _get_resource_from_definition(self, resource_name, head_component,
                                      definition, permissions=None):
        self._resources[resource_name][head_component] = {
            "permissions": permissions or []
        }
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
                if self.permissions:
                    custom_imports = [
                        custom["name"]
                        for custom in self._resources[resource_name]["custom_imports"]
                    ]
                    if "EmptyField" not in custom_imports:
                        self._resources[resource_name]["custom_imports"].append(
                            CUSTOM_IMPORTS["empty"]
                        )
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
                        "component": COMPONENT_MAPPING[self.admin_version][suffix]["many"]
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

        permission_imports_loaded = False
        for path, verbs in self.parser.specification["paths"].items():
            for verb, io in verbs.items():

                # Check if this is not a valid path method then skip it.
                if verb == "parameters":
                    continue
                else:
                    operation_id = io.get("operationId", "")
                    valid_operation = any([
                        operation in operation_id
                        for operation in OPERATION_SUFFIXES
                    ])
                    if operation_id and not valid_operation:
                        continue

                # Get resource name and path and add it to the list
                # for the first occurring instance of the resource

                name = operation_id.split("_")[0]
                if name not in self._resources:
                    permission_imports_loaded = False
                    self._resources[name] = {
                        "path": path[1:].split("/")[0],
                        "imports": [],
                        "custom_imports": [],
                        "has_methods": False,
                        "filter_lengths": {}
                    }

                definition = None
                head_component = None
                permissions = io.get("x-aor-permissions",
                                     []) if self.permissions else None

                if not permission_imports_loaded and self.permissions:
                    permission_imports_loaded = True
                    self._resources[name]["custom_imports"].append(
                        CUSTOM_IMPORTS["permissions"]
                    )

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
                        self._resources[name]["imports"].append(
                            "SimpleShowLayout")
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
                    filter_imports = []
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
                                and param["type"] in COMPONENT_MAPPING[self.admin_version]["Input"]\
                                and not param.get("x-admin-on-rest-exclude", False):
                            # Get component based on the explicit declaration or just the type.
                            declared_input = param.get("x-aor-filter", None)
                            related_input = param.get("x-related-info", None)
                            _type = param["type"]
                            relation = None
                            if declared_input:
                                _range = "-range" if declared_input.get(
                                    "range", False) else ""
                                _type = "{_type}{_range}".format(
                                    _type=declared_input["format"],
                                    _range=_range
                                )
                            elif related_input:
                                _type = "relation"
                                relation = {
                                    "component": COMPONENT_MAPPING[self.admin_version]["Input"]["enum"],
                                    "resource": related_input["rest_resource_name"],
                                    "text": related_input.get("label", None)
                                }
                                if relation["component"] not in filter_imports:
                                    filter_imports.append(relation["component"])
                            component = COMPONENT_MAPPING[self.admin_version]["Input"][_type]
                            # Add props if needed.
                            props = None
                            if _type in PROPS_MAPPING["Input"]:
                                props = PROPS_MAPPING["Input"][_type]
                            # Add component to filter imports if not there.
                            if component not in filter_imports:
                                filter_imports.append(component)
                            source = param["name"]
                            label = source.replace("_", " ").title()
                            _min = param.get("minLength", None)
                            _max = param.get("maxLength", None)
                            if _min or _max:
                                self._resources[name]["filter_lengths"][source] = {
                                    "min_length": _min,
                                    "max_length": _max
                                }
                            # Handle Array filter types finally!
                            array_validation = param["items"]["type"] \
                                if _type == "array" else None
                            filters.append({
                                "source": source,
                                "label": label,
                                "title": label.replace(" ", ""),
                                "component": component,
                                "relation": relation,
                                "props": props,
                                "array": array_validation
                            })
                    if filters:
                        self._resources[name]["filters"] = {
                            "filters": filters,
                            "imports": filter_imports
                        }
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
                elif "delete" in operation_id:
                    self._resources[name]["remove"] = {
                        "permissions": permissions
                    }
                if head_component and definition:
                    # Toggle to be included in AOR if it has a single method.
                    self._resources[name]["has_methods"] = True
                    self._get_resource_from_definition(
                        resource_name=name,
                        head_component=head_component,
                        definition=definition,
                        permissions=permissions
                    )

    def generate_js_file(self, filename, context):
        """
        Generate a js file from the given specification.
        :param filename: The name of the template file.
        :param context: Context to be passed.
        :return: str
        """
        return render_to_string(filename, context, self.admin_version)

    def add_additional_file(self, filename):
        """
        Add an additional file, that does not require context,
        to the generated admin.
        :return: str
        """
        return render_to_string(filename, {}, self.admin_version)

    def create_and_generate_file(self, dir, filename, context, source=None):
        """
        Create a file of the given name and context.
        :param dir: The output directory.
        :param filename: The name of the file to be created.
        :param context: The context for jinja.
        :param source: Alternative source file for the template.
        """
        click.secho("Generating {}.js file...".format(filename), fg="green")
        with open(os.path.join(dir, "{}.js".format(
                filename)), "w") as f:
            data = self.generate_js_file(
                filename="{}.js".format(source or filename),
                context=context)
            f.write(data)
            if self.verbose:
                print(data)

    def admin_generation(self):
        click.secho("Generating main JS component file...", fg="green")
        main_file = FILENAME_MAPPING[self.admin_version]["main"]
        self.create_and_generate_file(
            dir=self.output_dir,
            filename=main_file,
            context={
                "title": self.module_name,
                "rest_server_url": self.rest_server_url,
                "resources": self._resources,
                "supported_components": SUPPORTED_COMPONENTS[self.admin_version],
                "add_permissions": self.permissions
            }
        )
        self.create_and_generate_file(
            dir=self.output_dir,
            filename="Menu",
            context={
                "resources": self._resources
            }
        )
        click.secho("Generating resource component files...", fg="blue")
        resource_dir = self.output_dir + "/resources"
        if not os.path.exists(resource_dir):
            os.makedirs(resource_dir)
        for name, resource in self._resources.items():
            title = resource.get("title", None)
            if title:
                self.create_and_generate_file(
                    dir=resource_dir,
                    filename=title,
                    context={
                        "name": title,
                        "resource": resource,
                        "supported_components": SUPPORTED_COMPONENTS[self.admin_version],
                        "add_permissions": self.permissions
                    },
                    source="Resource"
                )
        click.secho("Generating Filter files for resources...", fg="blue")
        filter_dir = self.output_dir + "/filters"
        if not os.path.exists(filter_dir):
            os.makedirs(filter_dir)
        for name, resource in self._resources.items():
            if resource.get("filters", None) is not None:
                title = resource.get("title", None)
                if title:
                    filter_file = "{}Filter.js".format(title)
                    self.create_and_generate_file(
                        dir=filter_dir,
                        filename=filter_file,
                        context={
                            "title": title,
                            "filters": resource["filters"]
                        },
                        source="Filters"
                    )
        click.secho("Adding basic rest client file...", fg="cyan")
        self.create_and_generate_file(
            dir=self.output_dir,
            filename="restClient",
            context={
                "resources": self._resources
            }
        )
        if self.permissions:
            permissions_file = FILENAME_MAPPING[self.admin_version]["permissions"]
            if permissions_file:
                path_dir = self.output_dir + "/auth"
                if not os.path.exists(path_dir):
                    os.makedirs(path_dir)
                self.create_and_generate_file(
                    dir=path_dir,
                    filename=permissions_file,
                    context={
                        "resources": self._resources,
                        "supported_components": SUPPORTED_COMPONENTS[self.admin_version]
                    }
                )
        # Generate additional Files
        for _dir, files in ADDITIONAL_FILES[self.admin_version].items():
            if _dir != "root":
                path_dir = "{}/{}".format(self.output_dir, _dir)
                if not os.path.exists(path_dir):
                    os.makedirs(path_dir)
            else:
                path_dir = self.output_dir
            for file in files:
                click.secho("Adding {} file...".format(file), fg="cyan")
                with open(os.path.join(path_dir, file), "w") as f:
                    data = self.add_additional_file(file)
                    f.write(data)
                    if self.verbose:
                        print(data)


@click.command()
@click.argument("specification_path", type=click.Path(dir_okay=False, exists=True))
@click.argument("admin_version", type=click.Choice(BACKEND_CHOICES))
@click.option("--spec-format", type=click.Choice(SPEC_CHOICES))
@click.option("--verbose/--no-verbose", default=False)
@click.option("--output-dir", type=click.Path(file_okay=False, exists=True,
                                              writable=True),
              default=DEFAULT_OUTPUT_DIR)
@click.option("--module-name", type=str, default=DEFAULT_MODULE,
              help="The name of the module where the generated code will be "
                   "used, e.g. myproject.some_application")
@click.option("--rest-server-url", type=str,
              default="http://localhost:8000/api/v1",
              help="Use a desired rest server URL rather than "
                   "'http://localhost:8000/api/v1'")
@click.option("--permissions/--no-permissions", default=False)
def main(specification_path, admin_version, spec_format, verbose,
         output_dir, module_name, rest_server_url, permissions):

    generator = Generator(
        output_dir, module_name=module_name, admin_version=admin_version,
        verbose=verbose, rest_server_url=rest_server_url, permissions=permissions
    )
    try:
        click.secho("Loading specification file...", fg="green")
        generator.load_specification(specification_path, spec_format)
        generator.admin_generation()
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
