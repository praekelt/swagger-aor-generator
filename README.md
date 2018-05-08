# swagger-aor-generator
Convert Swagger specifications into a simple Admin on Rest client.

## Introduction
This utility parses a Swagger specification and generates a simple Admin on Rest client implementation to integration with a given rest server.
In particular, the following files are currently generated:
* `App.js`, The main App file containing your Admin component,
* Resource JS files, A resource file is generated for each resource found and placed in `resources`,
* Filter JS files, For each resource with any filters found a filter file will be generated and placed in `filters`,
* `swaggerRestServer.js`, a swagger rest client included with the generated files (use if needed),
* `authClient.js`, a basic Auth Client included in the generation.
* `ObjectField.js`, a common custom field type for object types, included if needed.


## Admin On Rest Client Generation
This portion of work is to generate a basic working Admin on Rest client that can be modified for custom requirements.
In order for the generation to behave as desired, the swagger specification is required to follow a certain configuration. Note, this generated code
comes along with a generic swagger rest server and authentication implementation.

## Include in your project

Include in your requirements file for pip within a Virtual Environment with Python 3.6 (to guarantee order of generation):

`-e git+https://github.com/praekelt/swagger-aor-generator.git@master#egg=swagger-aor-generator`

Pip install your requirements and the generator will be in your project Virtual Environment.

To run the generator now you can run the command:

```
./{ve}/bin/python {ve}/src/swagger-aor-generator/swagger_aor_generator/generator.py {swagger_spec} --output-dir={output_dir} --module-name="{module_name}" --rest-server-url="{rest_server_url}"
```

Replace all instances of `{}` variables with your desired setup. Here are each on of their purposes.

| Name            | Description                                             |
| ----------------| --------------------------------------------------------|
| ve              | Your virtual environment directory.                     |
| swagger_spec    | The path to your swagger specification (JSON/YAML).     |
| output_dir      | The output directory to generate into.                  |
| module_name     | What you want the title of your admin to be.            | 
| rest_server_url | The url which points to your rest server for the admin. |

### Path Configuration
Here is a configuration of paths for a single model to be implemented on the Admin on Rest interface.

```
"/pets": {
  "get": {
    "operationId": "pet_list",
    "parameters": [
      {
        "description": "An Optional Filter by pet_id.",
        "in": "query",
        "name": "pet_id",
        "required": false,
        "type": "integer"
      }
    ],
    "produces": [
      "application/json"
    ],
    "responses": {
      "200": {
        "description": "",
        "schema": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/pet"
          }
        }
      }
    },
    "tags": []
  },
  "post": {
    "consumes": [
      "application/json"
    ],
    "operationId": "pet_create",
    "parameters": [
      {
        "in": "body",
        "name": "data",
        "schema": {
          "$ref": "#/definitions/pet_create"
        }
      }
    ],
    "produces": [
      "application/json"
    ],
    "responses": {
      "201": {
        "description": "",
        "schema": {
          "$ref": "#/definitions/pet"
        }
      }
    },
    "tags": []
  }
},
"/pets/{pet_id}": {
  "parameters": [
    {
      "$ref": "#/parameters/pet_id"
    }
  ],
  "delete": {
    "operationId": "pet_delete",
    "responses": {
      "204": {
        "description": ""
      }
    },
    "tags": []
  },
  "get": {
    "operationId": "pet_read",
    "produces": [
      "application/json"
    ],
    "responses": {
      "200": {
        "description": "",
        "schema": {
          "$ref": "#/definitions/pet"
        }
      }
    },
    "tags": []
  },
  "put": {
    "consumes": [
      "application/json"
    ],
    "operationId": "pet_update",
    "parameters": [
      {
        "in": "body",
        "name": "data",
        "schema": {
          "$ref": "#/definitions/pet_update"
        }
      }
    ],
    "produces": [
      "application/json"
    ],
    "responses": {
      "200": {
        "description": "",
        "schema": {
          "$ref": "#/definitions/pet"
        }
      }
    },
    "tags": []
  }
}
```

This is a suitable layout for the endpoints of the Pet Model. The important attributes of each path/method pair are:

1. The base resource name `pets` remains the same for each path regarding pets. (VERY IMPORTANT)
2. With each operationId, the start is always the model name (`pet`) and the trailing word describes which AOR component the generator is looking at to generate.

All components for pets will be generated for the base resource path name `pets`, and each trailing word correlates to a given AOR component as listed below:
```
list - List Component
create - Create Component
read - Show Component
update - Edit Component
```

Here we can go over the endpoints and how they will be used in generation.

`/pets GET`: This path method will be used for the List component of the Pet model. The operationId must contain the suffix
             "list". Here the generator will build a List component for Pet based on the definition or schema provided in the 200 response for a SINGLE item of the array.
             In this example it will look at `"$ref": "#/definitions/pet"`

`/pets POST`: This path method will be used for the Create component of the Pet Model. The operationId must contain the suffix "create". Here the
              generator will build a Create component for Pet based on the definition or schema provided in the body parameter. In this example it will look at `"$ref": "#/definitions/pet_create"`.

`/pets/{pet_id} GET`: This path method will be used for the Show component of the Pet Model. The operationId must contain the suffix "read". Here the generator
                      will build a Show component for the Pet based on the definition or schema provided in the 200 response. In this example it will look at `"$ref": "#/definitions/pet"`.

`/pets/{pet_id} PUT`: This path method will be used for the Edit component of the Pet Model. The operationId must contain the suffix "update". Here the generator will
                      build an Edit component for the Pet based on the definition or schema provided in the body parameter. In this example it will look at `"$ref": "#/definitions/pet_create"`.

The delete method is not used as a standard delete component is used in the generated Admin on Rest client.

### Definition Configuration

A simple definition can be given as follows:

```
"pet": {
  "properties": {
    "id": {
      "type": "integer",
      "format": "int64",
      "readOnly": true
    },
    "category_id": {
      "type": "integer"
    },
    "name": {
      "type": "string",
      "example": "doggie"
    },
    "metadata": {
      "type": "object"
    },
    "date_of_birth": {
      "type": string
      "format": date
    },
    "created_at": {
      "type": string,
      "format": date-time
    },
    "updated_at": {
      "type": string,
      "format": date-time
    }
  }
}
```

Each property will be catered for in the generated Admin on Rest client. The property type will dictate the component to be generated for the property, however note that if the format is a supported component, it will overwrite the type component with the given format component. Also note the presence of `enum` in a property will change the component. The following types/formats have supported admin on rest components and are shown in the table below.

*NOTE: Date-time formats will require an additional npm package `aor-datetime-input` for DateTimeInput components, so add it to your project if necessary.*

| Type/Format     | Field Component  | Input Component  |
| ----------------| -----------------| -----------------|
| string          | TextField        | TextInput        |
| integer         | NumberField      | NumberInput      |
| boolean         | BooleanField     | BooleanInput     |
| date            | DateField        | DateInput        |
| date-time       | DateField        | DateTimeInput    |
| enum            | SelectField      | SelectInput      |
| object*         | ObjectField*     | LongTextInput*   |

* Object types use a Custom ObjectField included in the generation of the Admin on Rest Client. For their input a LongTextInput is utilized with `parse` and `format` props that handle the sending and presentation of the field data.

### Foriegn Key relationships

Foriegn key relationships can be setup in the definition quite easily. In order for a field to be picked up as a foreign key either of the following must be present.

1. The field name is suffixed by `_id`.
2. There is an additional field for related information named `x-related-info`

The latter will appear as such:

```
"category_id": {
  "type": "integer"
  "x-related-info": {
    "model": "category", # The name of the model that is the foreign key.
    "rest_resource_name": "categories" # The base resource path on the API ie `pets` in the above path specification.
    "field": "id", # The related field of the related model.
    "label": "name" # The field to be seen when viewing the related model instance on the given model.
  }
}
```

The property will then generate a simple Reference component. Each one of the fields in the `x-related-info` attribute is optional and if not present, assumptions will be made by the generator.
The behaviour of the generator with regards to the `x-related-info` is as follows:

1. If `model` is NOT present, grab the substring before the last `_` in the property key, eg. `category`.
2. If `rest_resource_name` is NOT present, take the `model` (or the substring before the last `_` in the property key) and attempt to remove all `_` and pluralize it for a guessed base resource path on the API.
3. If `field` is NOT present, grab the substring after the last `_` in the property key, eg. `id`.
4. If `label` is NOT present, use the `field` or what was found in part 3 before.

The relation Field component will be generated as follows:

```
<ReferenceField label="Category" source="category_id" reference="categories" linkType="show" allowEmpty>
  <NumberField source="name" />
</ReferenceField>
```

The relation Input component will be generated as follows:

```
<ReferenceInput label="Category" source="category_id" reference="categories" allowEmpty>
  <SelectInput source="id" optionText="name" />
</ReferenceInput>
```

*NOTE: If you have a property with `_id` on the end and you do not want it to be a relation, set the `x-related-info` `model` field to `None`*

### Inline models

Additional info can be included in the swagger specification, at a global level, to produce inline displays on any desired model with related models. The additional field `x-detail-page-definitions` must be included on the highest level in the swagger specification with all models with inlines. An example is given as follows:

```
"x-detail-page-definitions": {
  "category": {
    "inlines": [
      {
        "model": "pet",
        "rest_resource_name": "pets",
        "label": "Pets",
        "key": "category_id",
        "fields": [
          "name",
          "date_of_birth"
        ]
      }
    ]
  }
}
```

Here we have the category model with an inline of all pets with the category_id of the given category. The optional fields here are `rest_resource_name`, `label` and `fields`.
The generator with behave as follows:

1. The `model` is required.
2. `rest_resource_name` is the base resource path to point to, and behaves the same as before. If not present, the generator will attempt to guess the base resource path with the given model name minus `_` and pluralized as best as possible.'
3. The `label` is used for aesthetic purposes.
4. The `key` is the required related_field to filter the given resource by (eg `category_id`).
5. `fields` specifies the fields to be shown in the inline, if `fields` is omitted, then all fields of the related model will be shown.

This will finally generate a `<ReferenceManyField>` with a list of all the related items.

*NOTE: The inlines will only be generated on the `Show` and `Edit` components. The Edit inlines will include edit buttons on the right side of an entry.*

### List Filters

List filters are all generated in and additional file `Filters.js`. In order to generate filters, the path in charge of dictating the list component must contain optional query parameters. These will be noticed by the generator and added to the list components filter props. Taking from the `pet` specification established above we have:

```
"get": {
  "operationId": "pet_list",
  "parameters": [
    {
      "description": "An Optional Filter by pet_id.",
      "in": "query",
      "name": "pet_id",
      "required": false,
      "type": "integer"
    },
    {
      "description": "A name for a given pet.",
      "in": "query",
      "name": "name",
      "required": false,
      "type": "string",
      "minLength": 3
    },
    {
      "description": "A date range filter for pet date of birth",
      "in": "query",
      "name": "date_of_birth",
      "required": false,
      "type": "string",
      "x-aor-filter": {
        "format": "date",
        "range": true
      }
    }
  ],
  "produces": [
    "application/json"
  ],
  "responses": {
    "200": {
      "description": "",
      "schema": {
        "type": "array",
        "items": {
          "$ref": "#/definitions/pet"
        }
      }
    }
  },
  "tags": []
}
```

Here we have one parameter named `pet_id`. This parameter is given `in` the `query`. This will generate a filter component for Pet list with a single filter option, many can be added to the parameters for more filter options.
The filter `type`/`format` is important for the component to be used and maps to the table as given above in the `Definition Configuration` section. Also each query parameter can have a `minLength` attribute which will dictate in the `swaggerRestServer.js` to only query when the minimum length of input has been typed in that filter.

### Different Filter Inputs

One can specify the use of a custom input component with the extra attribute `x-aor-filter`. Here is an example of an `x-aor-filter`:

```
"x-aor-filter": {
  "format": "date",
  "range": true
}
```

The format attribute will override the type in the parameter with the type you would like to use and you can specify if you would like it to be a range based input. PLEASE NOTE only types of `date` and `date-time` have available custom range inputs, so specifying range for another type with fail.
The format attribute is REQUIRED however range defaults to false.

* This uses the same input component, however it will be given additional props to use date-time inputs for the from and to range inputs rather than the standard date inputs.

*NOTE* If you would like to not include a parameter as a filter, add the following to the parameter definition:

`x-admin-on-rest-exlude: true`


## TODOS (What would be cool as well)

* Fix up templates folder/file organization, thus resulting in some minor code changes. (Neatening up).
* Update swaggerRestServer.js and authClient.js to work out the box for a standard JSON rest server. (Currently a bit too specific for some projects I used the tool for).
* Add more range based filter types (like integer/number range).
* Template render neatening always needs work...