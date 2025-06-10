/**
 * JavaScript functionality for AI-powered features in TaskFlow
 */

document.addEventListener('DOMContentLoaded', function() {
    // AI Task Description Generator
    initAITaskDescription();
    
    // AI Comment Summarizer
    initAICommentSummarizer();
    
    // AI LSS Classification Suggestion
    initAILssClassification();
    
    // AI Board Analytics Insights
    initBoardAnalyticsInsights();
});

/**
 * Initialize AI Task Description Generator
 */
function initAITaskDescription() {
    const generateButton = document.getElementById('generate-ai-description');
    const titleInput = document.getElementById('id_title');
    const descriptionTextarea = document.getElementById('id_description');
    const aiSpinner = document.getElementById('ai-spinner');
    
    if (generateButton && titleInput && descriptionTextarea) {
        generateButton.addEventListener('click', function() {
            const title = titleInput.value.trim();
            
            if (!title) {
                alert('Please enter a task title first.');
                return;
            }
            
            // Show spinner
            aiSpinner.classList.remove('d-none');
            generateButton.disabled = true;
            
            // Make API call to our backend endpoint
            fetch('/api/generate-task-description/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ title: title })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.description) {
                    descriptionTextarea.value = data.description;
                } else {
                    alert('Could not generate description. Please try again or enter description manually.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again or enter description manually.');
            })
            .finally(() => {
                // Hide spinner
                aiSpinner.classList.add('d-none');
                generateButton.disabled = false;
            });
        });
    }
}

/**
 * Initialize AI Comment Summarizer
 */
function initAICommentSummarizer() {
    const summarizeButton = document.getElementById('summarize-comments');
    const summaryContainer = document.getElementById('comment-summary-container');
    const summaryText = document.getElementById('comment-summary-text');
    const summarySpinner = document.getElementById('summary-spinner');
    
    if (summarizeButton && summaryContainer && summaryText) {
        summarizeButton.addEventListener('click', function() {
            const taskId = summarizeButton.getAttribute('data-task-id');
            
            if (!taskId) return;
            
            // Show spinner
            if (summarySpinner) summarySpinner.classList.remove('d-none');
            summarizeButton.disabled = true;
            
            // Make API call
            fetch(`/api/summarize-comments/${taskId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.summary) {
                    summaryText.innerHTML = data.summary;
                    summaryContainer.classList.remove('d-none');
                } else {
                    alert('Could not generate summary. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating summary.');
            })
            .finally(() => {
                // Hide spinner
                if (summarySpinner) summarySpinner.classList.add('d-none');
                summarizeButton.disabled = false;
            });
        });
    }
}

/**
 * Initialize AI Lean Six Sigma Classification
 */
function initAILssClassification() {
    const classifyButton = document.getElementById('suggest-lss-classification');
    const suggestionContainer = document.getElementById('lss-suggestion-container');
    const suggestionText = document.getElementById('lss-suggestion-text');
    const classifySpinner = document.getElementById('classify-spinner');
    
    if (!classifyButton || !suggestionContainer || !suggestionText) return;
    
    // Check if we're on the task creation page
    const titleInput = document.getElementById('id_title');
    const descriptionTextarea = document.getElementById('id_description');
    const isTaskCreation = titleInput && descriptionTextarea;
    
    // Check if we're on the task detail page
    const taskId = classifyButton.getAttribute('data-task-id');
    const isTaskDetail = !!taskId;
    
    if (!(isTaskCreation || isTaskDetail)) return;
    
    classifyButton.addEventListener('click', function() {
        let title = '';
        let description = '';
        
        if (isTaskCreation) {
            // Get data from inputs on creation page
            title = titleInput.value.trim();
            description = descriptionTextarea ? descriptionTextarea.value.trim() : '';
            
            if (!title) {
                alert('Please enter a task title first.');
                return;
            }
        } else if (isTaskDetail) {
            // For task detail page, get the title and description from the form
            const titleField = document.querySelector('input[name="title"]');
            const descriptionField = document.querySelector('textarea[name="description"]');
            
            if (titleField) title = titleField.value.trim();
            if (descriptionField) description = descriptionField.value.trim();
            
            if (!title) {
                alert('Could not find task title.');
                return;
            }
        }
        
        // Show spinner
        if (classifySpinner) classifySpinner.classList.remove('d-none');
        classifyButton.disabled = true;
        
        // Make API call
        fetch('/api/suggest-lss-classification/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ 
                title: title,
                description: description
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.classification && data.justification) {
                let suggestionHtml = `This activity is likely <strong>${data.classification}</strong>. `;
                suggestionHtml += data.justification;
                
                suggestionText.innerHTML = suggestionHtml;
                suggestionContainer.classList.remove('d-none');
            } else {
                alert('Could not generate LSS classification. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating LSS classification.');
        })
        .finally(() => {
            // Hide spinner
            if (classifySpinner) classifySpinner.classList.add('d-none');
            classifyButton.disabled = false;
        });
    });
}

/**
 * Initialize AI Board Analytics Insights
 */
function initBoardAnalyticsInsights() {
    const insightsButton = document.getElementById('generate-insights');
    const insightsContainer = document.getElementById('insights-container');
    const insightsText = document.getElementById('insights-text');
    const insightsSpinner = document.getElementById('insights-spinner');
    const noInsights = document.getElementById('no-insights');
    
    if (insightsButton && insightsContainer && insightsText) {
        insightsButton.addEventListener('click', function() {
            const boardId = insightsButton.getAttribute('data-board-id');
            
            if (!boardId) return;
            
            // Show spinner
            if (insightsSpinner) insightsSpinner.classList.remove('d-none');
            if (noInsights) noInsights.classList.add('d-none');
            insightsButton.disabled = true;
            
            // Make API call
            fetch(`/api/board-analytics-insights/${boardId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.insights) {
                    insightsText.innerHTML = data.insights;
                    insightsContainer.classList.remove('d-none');
                } else {
                    alert('Could not generate insights. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while generating insights.');
            })
            .finally(() => {
                // Hide spinner
                if (insightsSpinner) insightsSpinner.classList.add('d-none');
                insightsButton.disabled = false;
            });
        });
    }
}
