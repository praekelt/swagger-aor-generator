/**
 * Generated Menu.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import { connect } from 'react-redux';
import { MenuItemLink, getResources } from 'admin-on-rest';
import ListIcon from 'material-ui/svg-icons/action/view-list';
import { titleCase } from './utils';

const ICONS = {
    {% for name, actions in resources.items() %}
    {% if actions.has_methods %}
    {{ actions.path }}: <ListIcon />,
    {% endif %}
    {% endfor %}
}

const Menu = ({ resources, onMenuTap, logout }) => (
    <div>
        {resources
            ? resources.map(resource => (
                    <MenuItemLink
                        key={resource.name}
                        to={`/${resource.name}`}
                        primaryText={`${titleCase(resource.name)}`}
                        onClick={onMenuTap}
                        leftIcon={ICONS[resource.name]}
                    />
                ))
            : ''}
        {logout}
    </div>
);

const mapStateToProps = state => ({
    resources: getResources(state)
});
export default connect(mapStateToProps)(Menu);
/** End of Generated Menu.js Code **/
