/**
 * Generated Menu.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import { connect } from 'react-redux';
import { MenuItemLink, getResources } from 'admin-on-rest';
import ListIcon from 'material-ui/svg-icons/action/view-list';

const Menu = ({ resources, onMenuTap, logout }) => (
    <div>
        {% for name, actions in resources.items() %}
        {% if actions.has_methods %}
        <MenuItemLink to="/{{ actions.path }}" primaryText="{{ actions.path|title }}" onClick={onMenuTap} leftIcon={<ListIcon />} />
        {% endif %}
        {% endfor %}
        {logout}
    </div>
);

const mapStateToProps = state => ({
    resources: getResources(state),
})
export default connect(mapStateToProps)(Menu);
/** End of Generated Menu.js Code **/