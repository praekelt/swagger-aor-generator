/**
 * Generated authPermissions.js code. Edit at own risk.
 * When regenerated the changes will be lost.
 **/
class PermissionsStore {
    constructor() {
        if (!PermissionsStore.instance) {
            this.requiredPermissions = {
                {% for name, actions in resources.items() %}
                {% if actions.has_methods %}
                {{ actions.path }}: {
                    {% for action, details in actions.items() %}
                    {% if action in supported_components and action != "show" %}
                    {{ action }}: {{ details.permissions }},
                    {% endif %}
                    {% endfor %}
                },
                {% endif %}
                {% endfor %}
            };
            this.permissionFlags = null;
            this.loadPermissions = this.loadPermissions.bind(this);
            this.getResourcePermission = this.getResourcePermission.bind(this);
            this.manyResourcePermissions = this.manyResourcePermissions.bind(this);
            PermissionsStore.instance = this;
        }
        return PermissionsStore.instance;
    }
    loadPermissions(userPermissions) {
        this.permissionFlags = {};
        const allowAccess = (userPermissions, requiredPermissions) => {
            if (requiredPermissions.length > 0) {
                return requiredPermissions.every(permission => {
                    return userPermissions.has(permission);
                });
            } else {
                return true;
            }
        };
        const permissionSet = new Set(userPermissions);
        Object.entries(this.requiredPermissions).map(
            ([resource, permissions]) => {
                this.permissionFlags[resource] = Object.entries(
                    permissions
                ).reduce((total, [action, required]) => {
                    total[action] = allowAccess(permissionSet, required);
                    return total;
                }, {});
                return null;
            }
        );
        localStorage.setItem(
            'permissions',
            JSON.stringify(this.permissionFlags)
        );
    }
    getResourcePermission(resource, permission) {
        if (this.permissionFlags) {
            return this.permissionFlags[resource][permission];
        } else {
            let userPermissions = localStorage.getItem('permissions');
            if (userPermissions) {
                this.permissionFlags = JSON.parse(userPermissions);
                return this.permissionFlags[resource][permission];
            }
        }
        console.log('Permissions store not loaded yet.');
        return false;
    }
    manyResourcePermissions(resourcePermissions) {
        return resourcePermissions.every(
            ([resource, permission]) => {
                return this.getResourcePermission(resource, permission);
            }
        );
    }
}

const storeInstance = new PermissionsStore();
Object.freeze(PermissionsStore);

export default storeInstance;

/** End of Generated Code **/
