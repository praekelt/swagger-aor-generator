/**
 * Generated App.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import { cyan500, cyan300 } from 'material-ui/styles/colors';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import { Admin, Delete, Resource } from 'admin-on-rest';
import swaggerRestServer from './swaggerRestServer';
import authClient from './auth/authClient';
{% if add_permissions %}
import { PERMISSIONS } from './auth/authPermissions';
import { allowAccess } from './utils';
{% endif %}
import Menu from './Menu';

{% for name, actions in resources.items() %}
{% if actions.has_methods %}
import {
    {% for action, details in actions.items() %}
    {% if action in supported_components %}
    {{ actions.title }}{{ action|title }},
    {% endif %}
    {% endfor %}
} from './resources/{{ actions.title }}';

{% endif %}
{% endfor %}

const App = () => (
    <Admin title="{{ title }}" menu={Menu} theme={getMuiTheme(muiTheme)} restClient={swaggerRestServer('{{ rest_server_url }}')} authClient={authClient}>
    {% if add_permissions %}
        {permissions => [
            {% for name, actions in resources.items() %}
            {% if actions.has_methods %}
            allowAccess(permissions, PERMISSIONS.{{ actions.path }}.list) 
                ? <Resource
                      name="{{ actions.path }}"
                      {% for action, details in actions.items() %}
                      {% if action in supported_components %}
                      {{ action }}={allowAccess(permissions, PERMISSIONS.{{ actions.path }}.{{ action }}) ? {{ actions.title }}{{ action|title }} : null}
                      {% endif %}
                      {% endfor %} 
                /> : null,
            {% endif %}
            {% endfor %}
        ]}
    {% else %}
    {% for name, actions in resources.items() %}
    {% if actions.has_methods %}
        <Resource
            name="{{ actions.path }}"
            {% for action, details in actions.items() %}
            {% if action in supported_components %}
            {{ action }}={ {{ actions.title }}{{ action|title }} }
            {% endif %}
            {% endfor %}
            remove={Delete}
        />
    {% endif %}
    {% endfor %}
    {% endif %}
    </Admin>
)

const muiTheme = getMuiTheme({
    palette: {
        primary1Color: cyan500,
        accent1Color: cyan300
    }
});

export default App;
/** End of Generated Code **/