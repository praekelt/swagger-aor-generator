
export const PERMISSIONS = {
    {% for name, actions in resources.items() %}
    {% if actions.has_methods %}
    {{ actions.path }}: {
        {% for action, details in actions.items() %}
        {% if action in supported_components %}
        {{ action }}: [
            {% for permission in details.permissions %}
            {% endfor %}
        ]
        {% endif %}
        {% endfor %}
    }
    {% endif %}
    {% endfor %}
};

