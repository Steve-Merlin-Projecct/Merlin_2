/**
 * Salary Formatting Utilities for Frontend
 * Provides consistent salary formatting with currency across all templates
 */

class SalaryFormatter {
    /**
     * Format salary range with proper currency display
     * @param {number|null} salaryLow - Minimum salary amount
     * @param {number|null} salaryHigh - Maximum salary amount  
     * @param {string} currency - Currency code (CAD, USD, etc.)
     * @returns {string} Formatted salary string with currency
     */
    static formatRange(salaryLow = null, salaryHigh = null, currency = 'CAD') {
        if (!salaryLow && !salaryHigh) {
            return "Salary not specified";
        }
        
        if (salaryLow && salaryHigh) {
            if (salaryLow === salaryHigh) {
                return `$${salaryLow.toLocaleString()} ${currency}`;
            } else {
                return `$${salaryLow.toLocaleString()} - $${salaryHigh.toLocaleString()} ${currency}`;
            }
        } else if (salaryLow) {
            return `$${salaryLow.toLocaleString()}+ ${currency}`;
        } else if (salaryHigh) {
            return `Up to $${salaryHigh.toLocaleString()} ${currency}`;
        }
        
        return "Salary not specified";
    }

    /**
     * Format single salary amount with currency and period
     * @param {number} amount - Salary amount
     * @param {string} currency - Currency code (CAD, USD, etc.)
     * @param {string} period - Salary period (annually, monthly, hourly)
     * @returns {string} Formatted salary string
     */
    static formatSingle(amount, currency = 'CAD', period = 'annually') {
        if (!amount) {
            return "Amount not specified";
        }
        
        let formatted = `$${amount.toLocaleString()} ${currency}`;
        
        if (period && period !== 'annually') {
            formatted += ` ${period}`;
        }
        
        return formatted;
    }

    /**
     * Determine currency based on location
     * @param {string} location - Location string
     * @param {string} country - Country name
     * @returns {string} Currency code (CAD, USD, etc.)
     */
    static getCurrencyFromLocation(location = null, country = null) {
        if (country) {
            const countryLower = country.toLowerCase();
            if (countryLower.includes('canada')) {
                return 'CAD';
            } else if (countryLower.includes('united states') || countryLower.includes('usa')) {
                return 'USD';
            }
        }
        
        if (location) {
            const locationLower = location.toLowerCase();
            // Canadian indicators
            if (locationLower.includes('canada') || 
                locationLower.includes('alberta') || 
                locationLower.includes('ontario') ||
                locationLower.includes('quebec') ||
                locationLower.includes('bc') ||
                locationLower.includes('british columbia') ||
                locationLower.includes('saskatchewan') ||
                locationLower.includes('manitoba') ||
                locationLower.includes('nova scotia') ||
                locationLower.includes('new brunswick') ||
                locationLower.includes('newfoundland') ||
                locationLower.includes('pei') ||
                locationLower.includes('yukon') ||
                locationLower.includes('northwest territories') ||
                locationLower.includes('nunavut')) {
                return 'CAD';
            }
            // US indicators  
            else if (locationLower.includes('usa') ||
                     locationLower.includes('united states') ||
                     locationLower.includes('california') ||
                     locationLower.includes('texas') ||
                     locationLower.includes('new york') ||
                     locationLower.includes('florida')) {
                return 'USD';
            }
        }
        
        // Default to CAD for Canadian job board
        return 'CAD';
    }

    /**
     * Parse salary text and extract components
     * @param {string} salaryText - Raw salary text
     * @returns {object} Object with salary_low, salary_high, currency, period
     */
    static parseSalaryText(salaryText) {
        const result = {
            salary_low: null,
            salary_high: null,
            currency: 'CAD',
            period: 'annually'
        };
        
        if (!salaryText) {
            return result;
        }
        
        const text = salaryText.toString();
        
        // Extract currency
        if (text.toUpperCase().includes('USD')) {
            result.currency = 'USD';
        } else if (text.toUpperCase().includes('CAD')) {
            result.currency = 'CAD';
        }
        
        // Extract period
        const textLower = text.toLowerCase();
        if (textLower.includes('hour') || textLower.includes('hourly') || textLower.includes('/hr') || textLower.includes('per hour')) {
            result.period = 'hourly';
        } else if (textLower.includes('month') || textLower.includes('monthly') || textLower.includes('/mo') || textLower.includes('per month')) {
            result.period = 'monthly';
        }
        
        // Extract numbers
        const numbers = text.replace(/,/g, '').match(/\d+(?:\.\d+)?/g);
        if (numbers) {
            const nums = numbers.map(n => parseInt(parseFloat(n)));
            if (nums.length === 1) {
                result.salary_low = result.salary_high = nums[0];
            } else if (nums.length >= 2) {
                result.salary_low = Math.min(...nums);
                result.salary_high = Math.max(...nums);
            }
        }
        
        return result;
    }

    /**
     * Update job display elements with proper salary formatting
     * @param {HTMLElement} container - Container element with job data
     * @param {object} jobData - Job data object
     */
    static updateJobDisplays(container, jobData) {
        const salaryElements = container.querySelectorAll('[data-salary]');
        
        salaryElements.forEach(element => {
            const currency = jobData.salary_currency || this.getCurrencyFromLocation(jobData.location, jobData.country);
            const formattedSalary = this.formatRange(jobData.salary_low, jobData.salary_high, currency);
            element.textContent = formattedSalary;
        });
    }
}

// Make available globally
window.SalaryFormatter = SalaryFormatter;

// Convenience functions for backwards compatibility
window.formatSalaryRange = SalaryFormatter.formatRange;
window.formatSingleSalary = SalaryFormatter.formatSingle;
window.getCurrencyFromLocation = SalaryFormatter.getCurrencyFromLocation;