/**
 * Generated {{ resource.title }}.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import {
    {% for import in resource.imports %}
    {{ import }},
    {% endfor %}
    {% if resource.remove %}
    DeleteButton,
    {% endif %}
    {% if resource.edit %}
    EditButton,
    {% endif %}
    ShowButton
} from 'admin-on-rest';
{% for import in resource.custom_imports %}
import {{ import.name }} from '{{ import.directory }}';
{% endfor %}
{% if resource.filters %}
import {{ resource.title }}Filter from '../filters/{{ resource.title }}Filter';
{% endif %}
{% for import in resource.custom_imports %}
{% if import.name == "DateTimeInput" %}
const timezoneOffset = new Date().getTimezoneOffset();

const dateTimeFormatter = value => {
    // Value received is a date object in the DateTimeInput.
    if (timezoneOffset !== 0 && value) {
        value = new Date(value);
        value = new Date(value.valueOf() + timezoneOffset * 60000);
    }
    return value;
};

const dateTimeParser = value => {
    // Value received is a date object in the DateTimeInput.
    if (timezoneOffset !== 0 && value) {
        value = new Date(value.valueOf() - timezoneOffset * 60000);
    }
    return value;
};
{% endif %}
{% endfor %}

{% if resource.create %}
const validationCreate{{ name }} = values => {
    const errors = {};
    {% for attribute in resource.create.fields %}
    {% if attribute.required %}
    if (!values.{{ attribute.source }}) {
        errors.{{ attribute.source }} = ["{{ attribute.source }} is required"];
    }
    {% endif %}
    {% endfor %}
    return errors;
};

{% endif %}
{% if resource.edit %}
const validationEdit{{ name }} = values => {
    const errors = {};
    {% for attribute in resource.edit.fields %}
    {% if attribute.required %}
    if (!values.{{ attribute.source }}) {
        errors.{{ attribute.source }} = ["{{ attribute.source }} is required"];
    }
    {% endif %}
    {% endfor %}
    return errors;
};

{% endif %}
{% for component, entries in resource.items() %}
{% for attribute in entries.fields %}
{% if attribute.choices %}
const choice{{ component|title }}{{ attribute.source|title }} = [
    {% if attribute.type == "integer" %}
    {% for choice in attribute.choices %}
    { id: {{ choice }}, name: {{ choice }} },
    {% endfor %}
    {% else %}
    {% for choice in attribute.choices %}
    { id: '{{ choice }}', name: '{{ choice }}' },
    {% endfor %}
    {% endif%}
];

{% endif %}
{% endfor %}
{% endfor %}
{% for component, entries in resource.items() %}
{% if component in supported_components and (entries.fields|length > 0 or entries.inlines) %}
export const {{ resource.title }}{{ component|title }} = props => (
    <{{ component|title }} {...props} title="{{ resource.title }} {{ component|title }}"{% if component == "list" and resource.filters %} filters={<{{ resource.title }}Filter />}{% endif %}>
        <{% if component == "list" %}Datagrid bodyOptions={ { showRowHover: true } }{% elif component == "show" %}SimpleShowLayout{% else %}SimpleForm validate={validation{{ component|title }}{{ name }}}{% endif %}>
            {% for attribute in entries.fields %}
            {% if attribute.related_component %}
            {% if add_permissions and "Field" in attribute.component %}
            {PermissionsStore.getResourcePermission('{{ attribute.reference }}', 'list') ? (
                <{{ attribute.component }} label="{{ attribute.label }}" source="{{ attribute.source }}" reference="{{ attribute.reference }}" {% if "Field" in attribute.component %}linkType="show" {% else %}perPage={0} {% endif %}allowEmpty>
                    <{% if attribute.read_only %}DisabledInput{% else %}{{ attribute.related_component }}{% endif %} {% if "Input" in attribute.related_component %}optionText={% else %}source={% endif %}"{{ attribute.option_text }}" />
                </{{ attribute.component }}>
            ) : (
                <EmptyField />
            )}
            {% else %}
            <{{ attribute.component }} label="{{ attribute.label }}" source="{{ attribute.source }}" reference="{{ attribute.reference }}" {% if "Field" in attribute.component %}linkType="show" {% else %}perPage={0} {% endif %}allowEmpty>
                <{% if attribute.read_only %}DisabledInput{% else %}{{ attribute.related_component }}{% endif %} {% if "Input" in attribute.related_component %}optionText={% else %}source={% endif %}"{{ attribute.option_text }}" />
            </{{ attribute.component }}>
            {% endif %}
            {% else %}
            <{% if attribute.read_only %}DisabledInput{% else %}{{ attribute.component }}{% endif %} source="{{ attribute.source }}"{% if attribute.choices %} choices={choice{{ component|title }}{{ attribute.source|title }}}{% endif %}{% if attribute.type == "object" and "Input" in attribute.component %} format={value => value instanceof Object ? JSON.stringify(value) : value} parse={value => { try { return JSON.parse(value); } catch (e) { return value; } }}{% endif %}{% if attribute.component == "DateTimeInput" %} format={dateTimeFormatter} parse={dateTimeParser}{% endif %}{% if attribute.component == "ObjectField" %} addLabel{% endif %} />
            {% endif %}
            {% endfor %}
            {% for inline in entries.inlines %}
            {% if add_permissions %}
            {PermissionsStore.getResourcePermission('{{ inline.reference }}', 'list') ? (
                <{{ inline.component }} label="{{ inline.label }}" reference="{{ inline.reference }}" target="{{ inline.target }}">
                    <Datagrid bodyOptions={ { showRowHover: true } }>
                        {% for attribute in inline.fields %}
                        {% if attribute.related_component %}
                        <{{ attribute.component }} label="{{ attribute.label }}" source="{{ attribute.source }}" reference="{{ attribute.reference }}" {% if "Field" in attribute.component %}linkType="show" {% endif %}allowEmpty>
                            <{{ attribute.related_component }} source="{{ attribute.option_text }}" />
                        </{{ attribute.component }}>
                        {% else %}
                        <{{ attribute.component }} source="{{ attribute.source }}"{% if attribute.component == "ObjectField" %} addLabel{% endif %} />
                        {% endif %}
                        {% endfor %}
                    </Datagrid>
                </{{ inline.component }}>
            ) : (
                <EmptyField />
            )}
            {% else %}
            <{{ inline.component }} label="{{ inline.label }}" reference="{{ inline.reference }}" target="{{ inline.target }}">
                <Datagrid bodyOptions={ { showRowHover: true } }>
                    {% for attribute in inline.fields %}
                    {% if attribute.related_component %}
                    <{{ attribute.component }} label="{{ attribute.label }}" source="{{ attribute.source }}" reference="{{ attribute.reference }}" {% if "Field" in attribute.component %}linkType="show" {% endif %}allowEmpty>
                        <{{ attribute.related_component }} source="{{ attribute.option_text }}" />
                    </{{ attribute.component }}>
                    {% else %}
                    <{{ attribute.component }} source="{{ attribute.source }}"{% if attribute.component == "ObjectField" %} addLabel{% endif %} />
                    {% endif %}
                    {% endfor %}
                </Datagrid>
            </{{ inline.component }}>
            {% endif %}
            {% endfor %}
            {% if component == "list" %}
            {% if resource.edit %}
            {% if add_permissions %}
            {PermissionsStore.getResourcePermission('{{ resource.path }}', 'edit') ? <EditButton /> : null}
            {% else %}
            <EditButton />
            {% endif %}
            {% endif %}
            {% if resource.show %}
            <ShowButton />
            {% endif %}
            {% if resource.remove %}
            {% if add_permissions %}
            {PermissionsStore.getResourcePermission('{{ resource.path }}', 'remove') ? <DeleteButton />: null}
            {% else %}
            <DeleteButton />
            {% endif %}
            {% endif %}
            {% endif %}
        </{% if component == "list" %}Datagrid{% elif component == "show" %}SimpleShowLayout{% else %}SimpleForm{% endif %}>
    </{{ component|title }}>
);

{% endif %}
{% endfor %}
/** End of Generated Code **/
