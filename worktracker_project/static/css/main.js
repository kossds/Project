/**
 * Main JavaScript file for Employee Work Tracking System
 * Handles client-side interactions, form validations, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeTooltips();
    initializeSessionTimers();
    initializeTableFilters();
    initializeModals();
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

/**
 * Form Validation Enhancement
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
            this.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Special validations
    if (form.querySelector('input[name="confirm_password"]')) {
        if (!validatePasswordMatch(form)) {
            isValid = false;
        }
    }
    
    if (form.querySelector('input[name="start_time"]') && form.querySelector('input[name="end_time"]')) {
        if (!validateTimeRange(form)) {
            isValid = false;
        }
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        isValid = false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    }
    
    // Password strength validation
    if (field.name === 'password' && value) {
        if (value.length < 6) {
            showFieldError(field, 'Password must be at least 6 characters long');
            isValid = false;
        }
    }
    
    // Employee ID validation
    if (field.name === 'employee_id' && value) {
        if (value.length < 3) {
            showFieldError(field, 'Employee ID must be at least 3 characters');
            isValid = false;
        }
    }
    
    if (isValid) {
        clearFieldError(field);
    }
    
    return isValid;
}

function validatePasswordMatch(form) {
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"]');
    
    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            showFieldError(confirmPassword, 'Passwords do not match');
            return false;
        }
    }
    return true;
}

function validateTimeRange(form) {
    const startTime = form.querySelector('input[name="start_time"]');
    const endTime = form.querySelector('input[name="end_time"]');
    
    if (startTime && endTime && startTime.value && endTime.value) {
        const start = new Date(`2000-01-01T${startTime.value}`);
        const end = new Date(`2000-01-01T${endTime.value}`);
        
        if (end <= start) {
            showFieldError(endTime, 'End time must be after start time');
            return false;
        }
    }
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Initialize Bootstrap Tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Session Timer Updates
 */
function initializeSessionTimers() {
    const sessionTimers = document.querySelectorAll('[id*="session"]');
    
    if (sessionTimers.length > 0) {
        // Update session timers every 30 seconds
        setInterval(updateSessionTimers, 30000);
    }
}

function updateSessionTimers() {
    const sessionDurationElements = document.querySelectorAll('#session-duration, #session-timer');
    
    sessionDurationElements.forEach(element => {
        const startTimeElement = document.querySelector('[data-session-start]');
        if (startTimeElement) {
            const startTime = new Date(startTimeElement.dataset.sessionStart);
            const now = new Date();
            const duration = (now - startTime) / (1000 * 60 * 60); // hours
            
            element.textContent = duration.toFixed(1);
        }
    });
}

/**
 * Table Filtering and Search
 */
function initializeTableFilters() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            filterTable(this);
        }, 300));
    });
}

function filterTable(searchInput) {
    const searchTerm = searchInput.value.toLowerCase();
    const table = searchInput.closest('.card').querySelector('table tbody');
    
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
    });
    
    // Update "no results" message
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    updateNoResultsMessage(table, visibleRows.length === 0 && searchTerm !== '');
}

function updateNoResultsMessage(table, shouldShow) {
    let noResultsRow = table.querySelector('.no-results-row');
    
    if (shouldShow && !noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `
            <td colspan="100%" class="text-center py-4 text-muted">
                <i class="fas fa-search fa-2x mb-2"></i><br>
                No results found for your search.
            </td>
        `;
        table.appendChild(noResultsRow);
    } else if (!shouldShow && noResultsRow) {
        noResultsRow.remove();
    }
}

/**
 * Modal Enhancements
 */
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            // Clear any previous form data when opening modals
            const forms = this.querySelectorAll('form');
            forms.forEach(form => {
                form.reset();
                form.classList.remove('was-validated');
                clearAllFieldErrors(form);
            });
        });
    });
}

function clearAllFieldErrors(form) {
    const errorDivs = form.querySelectorAll('.invalid-feedback');
    errorDivs.forEach(div => div.remove());
    
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
}

/**
 * Loading States
 */
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

/**
 * Form Submission with Loading States
 */
document.addEventListener('submit', function(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton && validateForm(form)) {
        showLoading(submitButton);
        
        // Re-enable after 5 seconds to prevent permanent disable
        setTimeout(() => {
            hideLoading(submitButton);
        }, 5000);
    }
});

/**
 * Auto-calculate hours for manual time entry
 */
function initializeTimeCalculation() {
    const startTimeInput = document.querySelector('input[name="start_time"]');
    const endTimeInput = document.querySelector('input[name="end_time"]');
    const breakHoursInput = document.querySelector('input[name="break_hours"]');
    
    if (startTimeInput && endTimeInput) {
        [startTimeInput, endTimeInput, breakHoursInput].forEach(input => {
            if (input) {
                input.addEventListener('change', calculateHours);
            }
        });
    }
}

function calculateHours() {
    const startTime = document.querySelector('input[name="start_time"]').value;
    const endTime = document.querySelector('input[name="end_time"]').value;
    const breakHours = parseFloat(document.querySelector('input[name="break_hours"]').value) || 0;
    
    if (startTime && endTime) {
        const start = new Date(`2000-01-01T${startTime}`);
        const end = new Date(`2000-01-01T${endTime}`);
        
        if (end > start) {
            const diffHours = (end - start) / (1000 * 60 * 60);
            const totalHours = Math.max(0, diffHours - breakHours);
            
            // Display calculated hours
            let hoursDisplay = document.querySelector('.calculated-hours');
            if (!hoursDisplay) {
                hoursDisplay = document.createElement('small');
                hoursDisplay.className = 'calculated-hours text-muted';
                document.querySelector('input[name="break_hours"]').parentNode.appendChild(hoursDisplay);
            }
            
            hoursDisplay.textContent = `Calculated: ${totalHours.toFixed(1)} hours`;
        }
    }
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function formatDuration(hours) {
    const h = Math.floor(hours);
    const m = Math.floor((hours - h) * 60);
    return `${h}h ${m}m`;
}

/**
 * Notification System
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Keyboard Shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + S to save forms
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            const submitButton = activeForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modalInstance = bootstrap.Modal.getInstance(openModal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }
});

/**
 * Dark Mode Toggle (Optional Enhancement)
 */
function initializeDarkMode() {
    const darkModeToggle = document.querySelector('#darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
        
        // Load saved preference
        const isDarkMode = localStorage.getItem('darkMode') === 'true';
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        }
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

/**
 * Initialize all time-related functionality
 */
setTimeout(() => {
    initializeTimeCalculation();
    initializeDarkMode();
}, 100);

/**
 * Performance Monitoring
 */
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.timing;
            const loadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page load time: ${loadTime}ms`);
            
            // Log slow loads (development only)
            if (loadTime > 3000) {
                console.warn('Slow page load detected. Consider optimizing resources.');
            }
        }, 0);
    });
}

/**
 * Error Handling for AJAX Requests (if needed in future)
 */
window.handleAjaxError = function(xhr, status, error) {
    let message = 'An error occurred. Please try again.';
    
    if (xhr.status === 401) {
        message = 'Session expired. Please log in again.';
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } else if (xhr.status === 403) {
        message = 'Access denied. You do not have permission to perform this action.';
    } else if (xhr.status === 404) {
        message = 'The requested resource was not found.';
    } else if (xhr.status >= 500) {
        message = 'Server error. Please contact support if this persists.';
    }
    
    showNotification(message, 'danger');
};

// Export functions for potential use in other scripts
window.WorkTracker = {
    showNotification,
    showLoading,
    hideLoading,
    validateForm,
    formatTime,
    formatDuration
};
