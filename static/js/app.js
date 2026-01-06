/**
 * Children's Story Generator - Frontend JavaScript
 * Handles form interactions, topic selection, and dynamic character inputs
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initializeTopicSelection();
    initializeCharacterInputs();
    initializeFormValidation();
});

/**
 * Handle topic button selection
 */
function initializeTopicSelection() {
    const topicButtons = document.querySelectorAll('.topic-btn');
    const selectedTopicInput = document.getElementById('selected-topic');
    
    topicButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all buttons
            topicButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Add selected class to clicked button
            this.classList.add('selected');
            
            // Update hidden input value
            const topic = this.getAttribute('data-topic');
            selectedTopicInput.value = topic;
            
            // Visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}

/**
 * Handle dynamic character input generation
 */
function initializeCharacterInputs() {
    const characterSelect = document.getElementById('characters');
    const characterInputsContainer = document.getElementById('character-inputs');
    
    if (!characterSelect || !characterInputsContainer) return;
    
    // Generate initial character inputs
    generateCharacterInputs(1);
    
    characterSelect.addEventListener('change', function() {
        const count = parseInt(this.value);
        generateCharacterInputs(count);
    });
}

/**
 * Generate character input fields based on selected count
 */
function generateCharacterInputs(count) {
    const container = document.getElementById('character-inputs');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (let i = 1; i <= count; i++) {
        const characterDiv = document.createElement('div');
        characterDiv.className = 'form-group character-group';
        
        characterDiv.innerHTML = `
            <h3>Character ${i}:</h3>
            <div class="character-inputs">
                <div class="input-group">
                    <label for="character_${i}_name">Name:</label>
                    <input type="text" 
                           id="character_${i}_name" 
                           name="character_${i}_name" 
                           placeholder="Enter character name"
                           required>
                </div>
                <div class="input-group">
                    <label for="character_${i}_pronouns">Pronouns:</label>
                    <select id="character_${i}_pronouns" 
                            name="character_${i}_pronouns" 
                            required>
                        <option value="">Choose pronouns</option>
                        <option value="he/him">he/him</option>
                        <option value="she/her">she/her</option>
                        <option value="they/them">they/them</option>
                    </select>
                </div>
            </div>
        `;
        
        container.appendChild(characterDiv);
    }
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const form = document.getElementById('story-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            // Show loading state
            showLoadingState();
            
            // Submit form (will be implemented in later tasks)
            alert('Story generation will be implemented in the next tasks!');
            hideLoadingState();
        }
    });
}

/**
 * Validate form inputs
 */
function validateForm() {
    const errors = [];
    
    // Validate topic selection
    const selectedTopic = document.getElementById('selected-topic').value;
    if (!selectedTopic) {
        errors.push('Please select a topic for your story.');
    }
    
    // Validate character inputs
    const characterCount = parseInt(document.getElementById('characters').value);
    for (let i = 1; i <= characterCount; i++) {
        const nameInput = document.getElementById(`character_${i}_name`);
        const pronounsSelect = document.getElementById(`character_${i}_pronouns`);
        
        if (!nameInput.value.trim()) {
            errors.push(`Please enter a name for Character ${i}.`);
        } else if (!/^[A-Za-z\s]+$/.test(nameInput.value.trim())) {
            errors.push(`Character ${i} name should only contain letters and spaces.`);
        }
        
        if (!pronounsSelect.value) {
            errors.push(`Please select pronouns for Character ${i}.`);
        }
    }
    
    // Validate keywords (3 or 5)
    const keywordInputs = document.querySelectorAll('[name^="keyword"]');
    const filledKeywords = Array.from(keywordInputs).filter(input => input.value.trim());
    
    if (filledKeywords.length !== 3 && filledKeywords.length !== 5) {
        errors.push('Please enter exactly 3 or 5 keywords.');
    }
    
    // Display errors or return validation result
    if (errors.length > 0) {
        displayErrors(errors);
        return false;
    }
    
    clearErrors();
    return true;
}

/**
 * Display validation errors
 */
function displayErrors(errors) {
    // Remove existing error display
    const existingErrors = document.querySelector('.error-messages');
    if (existingErrors) {
        existingErrors.remove();
    }
    
    // Create error display
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-messages';
    errorDiv.innerHTML = `
        <h3>Please fix these issues:</h3>
        <ul>
            ${errors.map(error => `<li>${error}</li>`).join('')}
        </ul>
    `;
    
    // Insert at top of form
    const form = document.getElementById('story-form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Scroll to errors
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Clear error messages
 */
function clearErrors() {
    const existingErrors = document.querySelector('.error-messages');
    if (existingErrors) {
        existingErrors.remove();
    }
}

/**
 * Show loading state during story generation
 */
function showLoadingState() {
    const submitBtn = document.querySelector('.create-story-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '✨ Creating Your Story... ✨';
        submitBtn.style.background = '#6b7280';
    }
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const submitBtn = document.querySelector('.create-story-btn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '🎨 CREATE STORY! 🎨';
        submitBtn.style.background = '';
    }
}