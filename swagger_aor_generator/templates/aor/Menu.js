/**
 * Generated Menu.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React from 'react';
import { connect } from 'react-redux';
import { MenuItemLink, getResources } from 'admin-on-rest';

const Menu = ({ resources, onMenuTap, logout }) => (
    <div>
        {% for name, actions in resources.items() %}
        <MenuItemLink to="/{{ actions.path }}" primaryText="{{ actions.path|title }}" onClick={onMenuTap} />
        {% endfor %}
        {logout}
    </div>
);

const mapStateToProps = state => ({
    resources: getResources(state),
})
export default connect(mapStateToProps)(Menu);
/** End of Generated Menu.js Code **/