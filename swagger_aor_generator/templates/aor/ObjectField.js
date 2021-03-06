/**
 * Generic Admin on rest Custom Fields!
 * Change/add at your own risk! 
**/
import React from 'react';
import {
    TextField
} from 'admin-on-rest';

const objectToText = ModifiedComponent => props => {
    let data = props.record[props.source];
    props.record[props.source] = data instanceof Object ? JSON.stringify(data) : data;   
    return <ModifiedComponent {...props} addLabel />;
};

const ObjectField = objectToText(TextField);

export default ObjectField;
/* End of ObjectField.js */