// Service Worker Registration for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed: ', error);
            });
    });
}

// PWA Install Prompt
let deferredPrompt;
const installButton = document.createElement('button');
installButton.style.display = 'none';
installButton.classList.add('btn', 'btn-info', 'fixed-bottom', 'mx-auto', 'mb-2', 'install-button');
installButton.textContent = 'Install MySkinAge App';

// Show install prompt
window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Update UI to notify the user they can add to home screen
    installButton.style.display = 'block';
    document.body.appendChild(installButton);
    
    installButton.addEventListener('click', () => {
        // Hide our user interface that shows our install button
        installButton.style.display = 'none';
        // Show the prompt
        deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            } else {
                console.log('User dismissed the install prompt');
            }
            deferredPrompt = null;
        });
    });
});

// Network status monitoring for PWA
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offline-indicator');
    if (offlineIndicator) {
        if (navigator.onLine) {
            offlineIndicator.style.display = 'none';
        } else {
            offlineIndicator.style.display = 'block';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Check online status when page loads
    updateOnlineStatus();
    
    // Elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const loadingOverlay = document.getElementById('loading-overlay');
    const featureElements = document.querySelectorAll('[data-feature-value]');
    const historyBtn = document.getElementById('history-btn');
    const uploadBtn = document.getElementById('upload-btn');
    
    // Initialize tooltips and popovers if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Handle file selection
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            handleFileSelection(e.target.files[0]);
        });
    }
    
    // Handle drag and drop
    if (uploadArea) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
    }
    
    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Only show loading if a file has been selected
            if (fileInput.files.length > 0) {
                showLoading();
            }
        });
    }
    
    // Handle history button
    if (historyBtn) {
        historyBtn.addEventListener('click', function() {
            window.location.href = '/history';
        });
    }
    
    // Handle upload button (in history view)
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
    
    // Animate feature bars when the page loads (on results page)
    if (featureElements.length > 0) {
        animateFeatureBars();
    }
    
    // Functions
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        uploadArea.classList.add('dragover');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFileSelection(files[0]);
            fileInput.files = files; // Assign to the file input
        }
    }
    
    function handleFileSelection(file) {
        // Check if the file is an image
        if (!file.type.match('image.*')) {
            alert('Please select an image file (JPG or PNG)');
            return;
        }
        
        // Show preview of the image
        const reader = new FileReader();
        reader.onload = function(e) {
            // Show the preview container
            if (previewContainer) {
                previewContainer.classList.remove('d-none');
                imagePreview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
    }
    
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('d-none');
        }
    }
    
    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.classList.add('d-none');
        }
    }
    
    function animateFeatureBars() {
        setTimeout(() => {
            featureElements.forEach(element => {
                const value = element.getAttribute('data-feature-value');
                const fillElement = element.querySelector('.feature-fill');
                if (fillElement) {
                    fillElement.style.width = `${value * 100}%`;
                }
            });
        }, 300); // Small delay for better animation effect
    }
});
