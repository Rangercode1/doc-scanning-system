// Document Scanner JavaScript functionality

// File upload validation
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (max 16MB)
                if (file.size > 16 * 1024 * 1024) {
                    alert('File size must be less than 16MB');
                    e.target.value = '';
                    return;
                }

                // Check file extension
                const allowedExtensions = ['txt', 'doc', 'docx', 'pdf'];
                const extension = file.name.split('.').pop().toLowerCase();
                if (!allowedExtensions.includes(extension)) {
                    alert('Invalid file type. Allowed types: ' + allowedExtensions.join(', '));
                    e.target.value = '';
                    return;
                }
            }
        });
    }
});

// Password confirmation validation
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('form');
    if (registerForm) {
        const password = registerForm.querySelector('#password');
        const confirmPassword = registerForm.querySelector('#confirm_password');
        
        if (password && confirmPassword) {
            registerForm.addEventListener('submit', function(e) {
                if (password.value !== confirmPassword.value) {
                    e.preventDefault();
                    alert('Passwords do not match');
                }
            });
        }
    }
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Progress bar animation
document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const value = bar.getAttribute('aria-valuenow');
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = value + '%';
        }, 100);
    });
});

// Document list item click handler
document.addEventListener('DOMContentLoaded', function() {
    const documentItems = document.querySelectorAll('.list-group-item[data-document-id]');
    documentItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const documentId = this.getAttribute('data-document-id');
            if (documentId) {
                window.location.href = '/documents/' + documentId;
            }
        });
    });
});

// Credit request form validation
document.addEventListener('DOMContentLoaded', function() {
    const creditRequestForm = document.querySelector('#credit-request-form');
    if (creditRequestForm) {
        creditRequestForm.addEventListener('submit', function(e) {
            const amount = parseInt(this.querySelector('#amount').value);
            if (isNaN(amount) || amount <= 0) {
                e.preventDefault();
                alert('Please enter a valid credit amount');
            }
        });
    }
});

// Admin dashboard chart initialization (if Chart.js is included)
document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.querySelector('#analytics-chart');
    if (chartCanvas && typeof Chart !== 'undefined') {
        // Initialize charts here if needed
        // This is just a placeholder for potential chart implementation
    }
}); 