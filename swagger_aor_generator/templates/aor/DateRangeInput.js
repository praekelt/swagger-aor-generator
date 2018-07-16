/**
 * Generated DateRangeInput.js code. Edit at own risk.
 * When regenerated the changes will be lost.
 **/
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Field } from 'redux-form';
import { DateInput } from 'admin-on-rest';
import DateTimeInput from 'aor-datetime-input';

const timezoneOffset = new Date().getTimezoneOffset();

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

    dateParser(value) {
        // Value received is a string in the DateInput.
        const regexp = /(\d{4})-(\d{2})-(\d{2})/;
        let match = regexp.exec(value);
        if (match === null) return;

        let year = match[1];
        let month = match[2];
        let day = match[3];

        if (timezoneOffset < 0) {
            // Negative offset means our picked UTC date got converted to previous day
            var date = new Date(value);
            date.setDate(date.getDate() + 1);
            match = regexp.exec(date.toISOString());
            year = match[1];
            month = match[2];
            day = match[3];
        }
        const correctDate = [year, month, day].join('-');

        return correctDate;
    }

    dateTimeFormatter(value) {
        // Value received is a date object in the DateTimeInput.
        if (timezoneOffset !== 0 && value) {
            value = new Date(value);
            value = new Date(value.valueOf() + timezoneOffset * 60000);
        }
        return value;
    }

    dateTimeParser(value) {
        // Value received is a date object in the DateTimeInput.
        if (timezoneOffset !== 0 && value) {
            value = new Date(value.valueOf() - timezoneOffset * 60000);
        }
        return value;
    }

    render() {
        const { source, time } = this.props;
        const today = new Date();
        const fromProps = {
            options: {
                maxDate: this.state.to
                    ? new Date(this.state.to)
                    : new Date(today.getFullYear() + 100, today.getMonth(), today.getDay())
            }
        };
        const toProps = {
            options: {
                minDate: this.state.from
                    ? new Date(this.state.from)
                    : new Date(today.getFullYear() - 100, today.getMonth(), today.getDay())
            }
        };
        return (
            <span>
                <Field
                    name={`${source}.from`}
                    component={this.component}
                    props={fromProps}
                    label="From"
                    parse={time ? this.dateTimeParser : this.dateParser}
                    format={time ? this.dateTimeFormatter : null}
                    onChange={this.handleFromOnChange}
                />
                <Field
                    name={`${source}.to`}
                    component={this.component}
                    props={toProps}
                    label="To"
                    parse={time ? this.dateTimeParser : this.dateParser}
                    format={time ? this.dateTimeFormatter : null}
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
