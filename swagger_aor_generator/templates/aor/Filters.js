/** 
 * Generated Filters.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import {
    {% for import in filters.imports %}
    {{ import }},
    {% endfor %}
    Filter
} from 'admin-on-rest';

export const {{ title }}Filter = props => (
    <Filter {...props}>
        {% for filter in filters.filters %}
        <{{ filter.component }} label="{{ filter.label }}" source="{{ filter.source }}" />
        {% endfor %}
    </Filter>
);
/** End of Generated Code **/