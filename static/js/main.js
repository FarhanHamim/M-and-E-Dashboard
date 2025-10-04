// Main JavaScript for M&E Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize charts
    initializeCharts();
    
    // Initialize data tables
    initializeDataTables();
    
    // Initialize notifications
    initializeNotifications();
});

// Tooltip functionality
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltipText = event.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'absolute z-50 px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg';
    tooltip.textContent = tooltipText;
    tooltip.id = 'tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('border-red-500');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-red-500 text-sm mt-1 field-error';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('border-red-500');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Chart initialization
function initializeCharts() {
    const chartElements = document.querySelectorAll('[data-chart]');
    
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart');
        const chartData = JSON.parse(element.getAttribute('data-chart-data'));
        
        createChart(element, chartType, chartData);
    });
}

function createChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    
    const config = {
        type: type,
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: data.title || ''
                }
            },
            scales: type !== 'pie' && type !== 'doughnut' ? {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#E0E0E0'
                    }
                },
                x: {
                    grid: {
                        color: '#E0E0E0'
                    }
                }
            } : {}
        }
    };
    
    new Chart(ctx, config);
}

// Data tables
function initializeDataTables() {
    const tables = document.querySelectorAll('[data-table]');
    
    tables.forEach(table => {
        addTableFeatures(table);
    });
}

function addTableFeatures(table) {
    // Add search functionality
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search...';
    searchInput.className = 'form-input mb-4';
    
    const tableContainer = table.parentNode;
    tableContainer.insertBefore(searchInput, table);
    
    searchInput.addEventListener('input', function() {
        filterTable(table, this.value);
    });
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const matches = text.includes(searchTerm.toLowerCase());
        row.style.display = matches ? '' : 'none';
    });
}

// Notifications
function initializeNotifications() {
    // Auto-hide success messages after 5 seconds
    const successMessages = document.querySelectorAll('.alert-success');
    successMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// Utility functions
function formatNumber(number) {
    return new Intl.NumberFormat().format(number);
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// AJAX helper functions
function makeAjaxRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        });
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Export functions
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    downloadFile(csv, filename + '.csv', 'text/csv');
}

function exportToPDF(elementId, filename) {
    // This would require a PDF library like jsPDF
    console.log('PDF export functionality would be implemented here');
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

// Dashboard specific functions
function updateDashboardStats() {
    // This function would fetch and update dashboard statistics
    console.log('Updating dashboard stats...');
}

function refreshCharts() {
    // This function would refresh all charts on the dashboard
    console.log('Refreshing charts...');
}

// Global error handler
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // You could show a user-friendly error message here
});

// Export functions to global scope for use in templates
window.MEDashboard = {
    formatNumber,
    formatCurrency,
    formatDate,
    formatPercentage,
    makeAjaxRequest,
    exportToCSV,
    exportToPDF,
    updateDashboardStats,
    refreshCharts
};
