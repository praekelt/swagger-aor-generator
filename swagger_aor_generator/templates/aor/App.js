/**
 * Generated App.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import { Admin, Delete, Resource } from 'admin-on-rest';

import { muiTheme } from './Theme';
import authClient from './auth/authClient';
import catchAll from './catchAll';
import Menu from './Menu';
{% if add_permissions %}
import PermissionsStore from './auth/PermissionsStore';
{% endif %}
import restClient from './restClient';

{% for name, actions in resources.items() %}
{% if actions.has_methods %}
import {
    {% for action, details in actions.items() %}
    {% if action in supported_components and action != 'remove' %}
    {{ actions.title }}{{ action|title }},
    {% endif %}
    {% endfor %}
} from './resources/{{ actions.title }}';

{% endif %}
{% endfor %}

const App = () => (
    <Admin
        title="{{ title }}"
        menu={Menu}
        theme={muiTheme}
        restClient={restClient('{{ rest_server_url }}')}
        authClient={authClient}
        catchAll={catchAll}
    >
    {% if add_permissions %}
        {permissions => [
            {% for name, actions in resources.items() %}
            {% if actions.has_methods %}
            PermissionsStore.getResourcePermission('{{ actions.path }}', 'list')
                ? <Resource
                      name="{{ actions.path }}"
                      {% for action, details in actions.items() %}
                      {% if action in supported_components %}
                      {{ action }}={% if action == "list" or action == "show" %}{% if action == "remove" %}{ Delete }
                      {% else %}{ {{ actions.title }}{{ action|title }} }
                      {% endif %}
                      {% else %}{PermissionsStore.getResourcePermission('{{ actions.path }}', '{{ action }}') ? {% if action == "remove" %}Delete{% else %}{{ actions.title }}{{ action|title }}{% endif %} : null}
                      {% endif %}
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
            {{ action }}={% if action == "remove" %}{ Delete }
            {% else %}{ {{ actions.title }}{{ action|title }} }
            {% endif %}
            {% endif %}
            {% endfor %}
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