/** 
 * Generated Filters.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import {
    {% for import in filters.imports %}
    {% if "DateRange" not in import %}
    {{ import }},
    {% endif %}
    {% endfor %}
    Filter
} from 'admin-on-rest';
{% if "DateRangeInput" in filters.imports %}
import DateRangeInput from '../inputs/DateRangeInput';
{% endif %}
{% for filter in filters.filters %}
{% if filter.array %}

const parse{{ filter.title }} = value => value.replace(/[^\w]/gi, ',');
{% endif %}
{% if filter.array == "integer" %}

const validate{{ filter.title }} = value => {
    const valid = value.replace(/[^\w]/gi, ',').split(',').every(item => !isNaN(item))
    if (!valid) {
        return "{{ filter.label }} are not all numbers.";
    }
};
{% endif %}
{% endfor %}

const {{ title }}Filter = props => (
    <Filter {...props}>
        {% for filter in filters.filters %}
        <{{ filter.component }} label="{{ filter.label }}" source="{{ filter.source }}"{% if filter.array %} parse={parse{{ filter.title }}}{% if filter.array == "integer" %} validate={validate{{ filter.title }}}{% endif %}{% endif %}{% if filter.props %}{% for name, value in filter.props.items() %} {{ name }}{% if value %}={{ value }}{% endif %}{% endfor %}{% endif %} />
        {% endfor %}
    </Filter>
);

export default {{ title }}Filter;
/** End of Generated Code **/