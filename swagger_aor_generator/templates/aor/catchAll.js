/**
 * Generated catchAll.js code. Edit at own risk.
 * When regenerated the changes will be lost.
 **/
import React, { Component } from 'react';
import { Redirect } from 'react-router';
import { NotFound } from 'admin-on-rest';

class catchAll extends Component {
    render() {
        return localStorage.getItem('id_token') ? (
            <NotFound />
        ) : (
            <Redirect push to="/login" />
        );
    }
}

export default catchAll;
/** End of Generated Code **/
