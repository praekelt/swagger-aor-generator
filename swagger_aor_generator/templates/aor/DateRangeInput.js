/** 
 * Generated DateRangeInput.js code. Edit at own risk.
 * When regenerated the changes will be lost.
**/
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Field } from 'redux-form';
import { DateInput } from 'admin-on-rest';
import DateTimeInput from 'aor-datetime-input';

const COMPONENTS = {
    date: DateInput,
    datetime: DateTimeInput
};

class DateRangeInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            from: this.props.input.value.from,
            to: this.props.input.value.to
        };
        this.component = props.time ? COMPONENTS.datetime : COMPONENTS.date;
        this.handleFromOnChange = this.handleFromOnChange.bind(this);
        this.handleToOnChange = this.handleToOnChange.bind(this);
    }

    handleFromOnChange(event, value) {
        this.setState({ from: value });
    }

    handleToOnChange(event, value) {
        this.setState({ to: value });
    }

    render() {
        const { source } = this.props;
        const today = new Date();
        const fromProps = {
            options: {
                maxDate:
                    this.state.to !== ''
                        ? new Date(this.state.to)
                        : new Date(
                              today.getFullYear() + 100,
                              today.getMonth(),
                              today.getDay()
                          )
            }
        };
        const toProps = {
            options: {
                minDate:
                    this.state.from !== ''
                        ? new Date(this.state.from)
                        : new Date(
                              today.getFullYear() - 100,
                              today.getMonth(),
                              today.getDay()
                          )
            }
        };
        return (
            <span>
                <Field
                    name={`${source}.from`}
                    component={this.component}
                    props={fromProps}
                    label="From"
                    onChange={this.handleFromOnChange}
                />
                <Field
                    name={`${source}.to`}
                    component={this.component}
                    props={toProps}
                    label="To"
                    onChange={this.handleToOnChange}
                />
            </span>
        );
    }
}
DateRangeInput.propTypes = {
    time: PropTypes.bool
};
DateRangeInput.defaultProps = {
    time: false
};
export default DateRangeInput;
/** End of Generated Code **/
