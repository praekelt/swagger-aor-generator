/**
 * Generated utils.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/

// Produce a title case string
export const titleCase = string => {
    return string
        .toLowerCase()
        .split(' ')
        .map(word => {
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join(' ');
};

{% if add_permissions %}
// Check if access can be granted with the given and required permissions.
export const allowAccess = (permissions, required) => {

};
{% endif %}

/** End of Generated Code **/
