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

const {{ title }}Filter = props => (
    <Filter {...props}>
        {% for filter in filters.filters %}
        <{{ filter.component }} label="{{ filter.label }}" source="{{ filter.source }}"{% if filter.props %}{% for name, value in filter.props.items() %} {{ name }}{% if value %}={{ value }}{% endif %}{% endfor %}{% endif %} />
        {% endfor %}
    </Filter>
);

export default {{ title }}Filter;
/** End of Generated Code **/