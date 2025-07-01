// Helper function to identify lean labels by common names if data attributes aren't working
function isLeanLabel(optionText) {
    const leanKeywords = [
        'value-added', 'value added', 'va',
        'necessary nva', 'necessary non-value', 'nnva', 
        'waste', 'eliminate', 'non-value',
        'lean', 'six sigma', 'kaizen',
        'dmaic', 'define', 'measure', 'analyze', 'improve', 'control',
        'muda', 'mura', 'muri',
        'poka-yoke', 'kanban', '5s', 'gemba'
    ];
    
    const text = optionText.toLowerCase().trim();
    return leanKeywords.some(keyword => text.includes(keyword));
}

// Lean Six Sigma Tools Toggle Function - Simplified for debugging
function toggleLeanSixSigmaFeatures() {
    console.log('=== TOGGLE FUNCTION CALLED ===');
    
    const isHidden = document.body.classList.contains('hide-lean-features');
    console.log('Current state - isHidden:', isHidden);
    
    if (isHidden) {
        console.log('SHOWING LSS features...');
        document.body.classList.remove('hide-lean-features');
        applyLSSShowing();
        localStorage.setItem('leanSigmaVisible', 'true');
    } else {
        console.log('HIDING LSS features...');
        document.body.classList.add('hide-lean-features');
        applyLSSHiding();
        localStorage.setItem('leanSigmaVisible', 'false');
    }
    
    // Update button text
    updateToggleButtonText();
}

function updateToggleButtonText() {
    const isHidden = document.body.classList.contains('hide-lean-features');
    const toggleTextSpan = document.getElementById('lss-toggle-text');
    
    console.log('updateToggleButtonText called - isHidden:', isHidden, 'toggleTextSpan found:', !!toggleTextSpan);
    
    if (toggleTextSpan) {
        if (isHidden) {
            console.log('Setting text to: Show Lean Six Sigma Tools');
            toggleTextSpan.textContent = 'Show Lean Six Sigma Tools';
        } else {
            console.log('Setting text to: Hide Lean Six Sigma Tools');
            toggleTextSpan.textContent = 'Hide Lean Six Sigma Tools';
        }
    } else {
        console.log('Toggle text span not found! Falling back to old method...');
        // Fallback to old method for backward compatibility
        const toggleBtn = document.querySelector('[onclick="toggleLeanSixSigmaFeatures()"]');
        if (toggleBtn) {
            if (isHidden) {
                console.log('Setting text to: Show Lean Six Sigma Tools');
                toggleBtn.innerHTML = '<i class="fas fa-eye me-2 text-secondary"></i>Show Lean Six Sigma Tools';
            } else {
                console.log('Setting text to: Hide Lean Six Sigma Tools');
                toggleBtn.innerHTML = '<i class="fas fa-industry me-2 text-secondary"></i>Hide Lean Six Sigma Tools';
            }
        }
    }
}

// Initialize Lean Six Sigma visibility on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== LSS TOGGLE INITIALIZED ===');
    
    const leanSigmaVisible = localStorage.getItem('leanSigmaVisible');
    console.log('localStorage leanSigmaVisible:', leanSigmaVisible);
    
    // Debug: List all options on the page
    const allSelects = document.querySelectorAll('select');
    console.log('All selects on page:', allSelects.length);
    allSelects.forEach((select, i) => {
        console.log(`Select ${i}:`, select.name, select.id);
        const options = select.querySelectorAll('option');
        options.forEach((option, j) => {
            console.log(`  Option ${j}: "${option.textContent}" value="${option.value}" data-category="${option.dataset.category}"`);
        });
    });
    
    if (leanSigmaVisible === 'false') {
        console.log('Auto-hiding LSS features on page load...');
        document.body.classList.add('hide-lean-features');
        
        // Force immediate hiding
        forceLSSHiding();
        
        // Also apply JavaScript hiding immediately for better reliability
        applyLSSHiding();
    }
    
    // Always update toggle button text on page load regardless of state
    // Use setTimeout to ensure DOM is fully ready
    setTimeout(() => {
        updateToggleButtonText();
    }, 100);
});

// Function to force immediate hiding of all LSS elements
function forceLSSHiding() {
    console.log('FORCE HIDING LSS elements immediately...');
    
    // Target all possible LSS elements with multiple selectors
    const lssSelectors = [
        '.lean-sigma-element',
        '#suggest-lss-classification',
        '#classify-spinner', 
        '#lss-suggestion-container',
        'button[id*="suggest-lss"]',
        'button[id*="classify"]',
        '.btn:has(.fa-robot)'
    ];
    
    lssSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        console.log(`Found ${elements.length} elements for selector: ${selector}`);
        elements.forEach((element, i) => {
            console.log(`  Force hiding element ${i}:`, element);
            element.style.display = 'none';
            element.style.visibility = 'hidden';
            element.style.opacity = '0';
            element.classList.add('d-none');
            // Also remove from DOM temporarily
            if (element.parentNode) {
                element.setAttribute('data-lss-hidden', 'true');
                element.style.position = 'absolute';
                element.style.left = '-9999px';
            }
        });
    });
}

// Function to apply LSS hiding via JavaScript
function applyLSSHiding() {
    console.log('Applying LSS hiding via JavaScript...');
    
    // Hide lean-sigma-element items
    const leanElements = document.querySelectorAll('.lean-sigma-element');
    console.log('Found lean-sigma-element elements:', leanElements.length);
    leanElements.forEach((element, i) => {
        console.log(`Hiding lean element ${i}:`, element);
        console.log(`  Element ID: ${element.id}, classes: ${element.className}`);
        element.style.display = 'none';
        element.style.visibility = 'hidden';
    });
    
    // Specifically target the Suggest LSS Classification button
    const suggestButton = document.getElementById('suggest-lss-classification');
    if (suggestButton) {
        console.log('Found Suggest LSS Classification button, hiding it forcefully');
        suggestButton.style.display = 'none !important';
        suggestButton.style.visibility = 'hidden';
        suggestButton.classList.add('d-none');
    } else {
        console.log('Suggest LSS Classification button NOT found');
    }
    
    // Hide lean label options and check if we should hide the entire Labels field
    const labelSelects = document.querySelectorAll('select[name="labels"], #id_labels');
    console.log('Found label selects:', labelSelects.length);
    
    labelSelects.forEach((select, selectIndex) => {
        console.log(`Processing select ${selectIndex}:`, select);
        const options = select.querySelectorAll('option');
        console.log(`  Found ${options.length} options`);
        
        let hasRegularLabels = false;
        let hasLeanLabels = false;
        
        options.forEach((option, optionIndex) => {
            const isLeanByAttribute = option.dataset.category === 'lean';
            const isLeanByName = isLeanLabel(option.textContent);
            const isLean = isLeanByAttribute || isLeanByName;
            
            if (isLean) {
                console.log(`  Hiding option ${optionIndex}: "${option.textContent}"`);
                option.style.display = 'none';
                option.style.visibility = 'hidden';
                option.disabled = true;
                option.selected = false;
                
                // Try removing from DOM as backup
                option.classList.add('lss-hidden');
                hasLeanLabels = true;
            } else {
                // Check if this is a regular label (not the default empty option)
                if (option.value && option.value.trim() !== '') {
                    hasRegularLabels = true;
                }
            }
        });
        
        // If there are only lean labels and no regular labels, hide the entire Labels field
        // Check both explicit container and crispy forms generated containers for this specific select
        let labelsContainer = null;
        
        // Try to find the container for this specific select element
        if (select.closest('#labels-field-container')) {
            labelsContainer = select.closest('#labels-field-container');
        } else if (select.closest('[data-field-name="labels"]')) {
            labelsContainer = select.closest('[data-field-name="labels"]');
        } else if (select.closest('#div_id_labels')) {
            labelsContainer = select.closest('#div_id_labels');
        } else {
            labelsContainer = select.closest('.form-group, .mb-3, .field-wrapper');
        }
        
        if (labelsContainer && hasLeanLabels && !hasRegularLabels) {
            console.log('No regular labels found, hiding entire Labels field for:', labelsContainer);
            labelsContainer.classList.add('labels-only-lean');
        }
    });
}

// Function to show LSS features
function applyLSSShowing() {
    console.log('Showing LSS features via JavaScript...');
    
    // Show lean-sigma-element items
    const leanElements = document.querySelectorAll('.lean-sigma-element');
    leanElements.forEach((element) => {
        element.style.display = '';
        element.style.visibility = '';
        element.style.opacity = '';
        element.style.position = '';
        element.style.left = '';
        element.classList.remove('d-none');
        element.removeAttribute('data-lss-hidden');
    });
    
    // Specifically target the Suggest LSS Classification button
    const suggestButton = document.getElementById('suggest-lss-classification');
    if (suggestButton) {
        console.log('Found Suggest LSS Classification button, showing it');
        suggestButton.style.display = '';
        suggestButton.style.visibility = '';
        suggestButton.style.opacity = '';
        suggestButton.style.position = '';
        suggestButton.style.left = '';
        suggestButton.classList.remove('d-none');
        suggestButton.removeAttribute('data-lss-hidden');
    }
    
    // Also target buttons with LSS-related IDs or classes
    const lssButtons = document.querySelectorAll('button[id*="suggest-lss"], button[id*="classify"]');
    lssButtons.forEach(button => {
        button.style.display = '';
        button.style.visibility = '';
        button.style.opacity = '';
        button.style.position = '';
        button.style.left = '';
        button.classList.remove('d-none');
        button.removeAttribute('data-lss-hidden');
    });
    
    // Show lean label options and the Labels field container
    const labelSelects = document.querySelectorAll('select[name="labels"], #id_labels');
    
    labelSelects.forEach((select) => {
        const options = select.querySelectorAll('option');
        
        options.forEach((option) => {
            const isLeanByAttribute = option.dataset.category === 'lean';
            const isLeanByName = isLeanLabel(option.textContent);
            const isLean = isLeanByAttribute || isLeanByName;
            
            if (isLean) {
                console.log(`  Showing option: "${option.textContent}"`);
                option.style.display = '';
                option.style.visibility = '';
                option.disabled = false;
                option.classList.remove('lss-hidden');
            }
        });
    });
    
    // Always show the Labels field container when LSS features are shown
    // Remove the labels-only-lean class from all possible containers
    const allContainers = document.querySelectorAll('#labels-field-container, [data-field-name="labels"], #div_id_labels, .form-group, .mb-3, .field-wrapper');
    allContainers.forEach(container => {
        if (container.classList.contains('labels-only-lean')) {
            console.log('Showing Labels field container:', container);
            container.classList.remove('labels-only-lean');
        }
    });
}
