/**
 * AI-Enhanced Timeline Analysis JavaScript
 * Handles critical path analysis and project timeline generation
 */

// Ensure DOM is loaded before initializing
document.addEventListener('DOMContentLoaded', function() {
    initializeTimelineAnalysis();
});

function initializeTimelineAnalysis() {
    // Critical Path Analysis Handler
    const analyzeCriticalPathBtn = document.getElementById('analyze-critical-path-btn');
    if (analyzeCriticalPathBtn) {
        analyzeCriticalPathBtn.addEventListener('click', handleCriticalPathAnalysis);
    }
    
    // Timeline Generation Handler  
    const generateTimelineBtn = document.getElementById('generate-timeline-btn');
    if (generateTimelineBtn) {
        generateTimelineBtn.addEventListener('click', handleTimelineGeneration);
    }
}

function handleCriticalPathAnalysis() {
    const boardId = this.getAttribute('data-board-id');
    const spinner = document.getElementById('critical-path-spinner');
    const placeholder = document.getElementById('timeline-analysis-placeholder');
    const container = document.getElementById('critical-path-container');
    
    toggleSpinner(spinner, this, true);
    
    fetch('/api/analyze-critical-path/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ board_id: boardId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        
        placeholder.classList.add('d-none');
        container.classList.remove('d-none');
        
        renderCriticalPathResults(data);
    })
    .catch(error => handleError(error, placeholder))
    .finally(() => toggleSpinner(spinner, this, false));
}

function handleTimelineGeneration() {
    const boardId = this.getAttribute('data-board-id');
    const spinner = document.getElementById('timeline-spinner');
    const placeholder = document.getElementById('timeline-analysis-placeholder');
    const container = document.getElementById('timeline-container');
    
    toggleSpinner(spinner, this, true);
    
    fetch('/api/generate-project-timeline/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ board_id: boardId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        
        placeholder.classList.add('d-none');
        container.classList.remove('d-none');
        
        renderTimelineResults(data);
    })
    .catch(error => handleError(error, placeholder))
    .finally(() => toggleSpinner(spinner, this, false));
}

function renderCriticalPathResults(data) {
    // Populate critical path content
    const criticalPathContent = document.getElementById('critical-path-content');
    if (data.critical_path && data.critical_path.length > 0) {
        criticalPathContent.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="fas fa-route me-2"></i>Critical Path Identified</h6>
                <div class="critical-path-tasks">
                    ${data.critical_path.map((task, index) => `
                        <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-primary me-2">${index + 1}</span>
                            <strong>${escapeHtml(task.task_title)}</strong>
                            <span class="text-muted ms-2">(${task.duration_hours}h)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else {
        criticalPathContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>No clear critical path identified. Consider adding task dependencies and estimated durations.
            </div>
        `;
    }
    
    // Populate project insights
    const projectInsights = document.getElementById('project-insights-content');
    if (data.project_insights) {
        const insights = data.project_insights;
        projectInsights.innerHTML = `
            <div class="card border-info">
                <div class="card-body p-3">
                    <div class="row text-center">
                        <div class="col-6 border-end">
                            <div class="h6 mb-0 text-info">${insights.total_duration_hours || 0}h</div>
                            <small class="text-muted">Total Duration</small>
                        </div>
                        <div class="col-6">
                            <div class="h6 mb-0 text-success">${insights.critical_path_duration || 0}h</div>
                            <small class="text-muted">Critical Path</small>
                        </div>
                    </div>
                    <hr>
                    <div class="row text-center">
                        <div class="col-6 border-end">
                            <div class="h6 mb-0 text-warning">${insights.high_risk_tasks || 0}</div>
                            <small class="text-muted">High Risk Tasks</small>
                        </div>
                        <div class="col-6">
                            <div class="h6 mb-0 text-primary">${insights.schedule_buffer_hours || 0}h</div>
                            <small class="text-muted">Schedule Buffer</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Populate recommendations
    const recommendationsContent = document.getElementById('schedule-recommendations-content');
    if (data.recommendations && data.recommendations.length > 0) {
        recommendationsContent.innerHTML = data.recommendations.map(rec => `
            <div class="alert alert-${rec.impact === 'high' ? 'warning' : 'info'} mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${escapeHtml(rec.title)}</h6>
                        <p class="mb-1 small">${escapeHtml(rec.description)}</p>
                        <small class="text-muted">
                            Impact: <span class="badge bg-${rec.impact === 'high' ? 'danger' : rec.impact === 'medium' ? 'warning' : 'info'}">${rec.impact}</span>
                            Effort: <span class="badge bg-secondary">${rec.effort}</span>
                        </small>
                    </div>
                    <span class="badge bg-primary">${rec.priority}</span>
                </div>
            </div>
        `).join('');
    } else {
        recommendationsContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>No specific recommendations at this time. Your project timeline looks good!
            </div>
        `;
    }
}

function renderTimelineResults(data) {
    // Populate timeline phases
    const phasesContent = document.getElementById('timeline-phases-content');
    if (data.timeline_phases && data.timeline_phases.length > 0) {
        phasesContent.innerHTML = data.timeline_phases.map(phase => `
            <div class="card mb-3">
                <div class="card-body p-3">
                    <h6 class="card-title text-primary">${escapeHtml(phase.phase_name)}</h6>
                    <p class="card-text small text-muted mb-2">
                        ${phase.start_date} to ${phase.end_date}
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-${getStatusColor(phase.phase_status)}">
                            ${phase.phase_status.replace('_', ' ').toUpperCase()}
                        </span>
                        <small class="text-muted">
                            Confidence: <span class="badge bg-${getConfidenceColor(phase.completion_confidence)}">${phase.completion_confidence}</span>
                        </small>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        phasesContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>No timeline phases identified. Consider organizing tasks into logical phases.
            </div>
        `;
    }
    
    // Populate resource timeline
    const resourceContent = document.getElementById('resource-timeline-content');
    if (data.resource_timeline && data.resource_timeline.length > 0) {
        resourceContent.innerHTML = data.resource_timeline.map(resource => `
            <div class="card mb-3">
                <div class="card-body p-3">
                    <h6 class="card-title">${escapeHtml(resource.team_member)}</h6>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="small text-muted">Utilization</span>
                        <span class="badge bg-${getUtilizationColor(resource.utilization_percentage)}">
                            ${resource.utilization_percentage}%
                        </span>
                    </div>
                    ${resource.recommendations && resource.recommendations.length > 0 ? `
                        <div class="small text-muted">
                            <strong>Recommendations:</strong>
                            <ul class="mb-0 ps-3">
                                ${resource.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    } else {
        resourceContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>No resource timeline data available.
            </div>
        `;
    }
    
    // Populate milestones
    const milestonesContent = document.getElementById('milestones-content');
    if (data.critical_milestones && data.critical_milestones.length > 0) {
        milestonesContent.innerHTML = data.critical_milestones.map(milestone => `
            <div class="alert alert-${getConfidenceColor(milestone.confidence)} mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${escapeHtml(milestone.milestone)}</h6>
                        <p class="mb-1 small">Target: ${milestone.target_date} | Forecast: ${milestone.forecasted_date}</p>
                        <small class="text-muted">${escapeHtml(milestone.impact_if_delayed)}</small>
                    </div>
                    <span class="badge bg-${getConfidenceColor(milestone.confidence)}">
                        ${milestone.confidence.toUpperCase()}
                    </span>
                </div>
            </div>
        `).join('');
    } else {
        milestonesContent.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>No critical milestones identified. Consider marking important tasks as milestones.
            </div>
        `;
    }
}

// Utility Functions
function toggleSpinner(spinner, button, show) {
    if (show) {
        spinner.classList.remove('d-none');
        button.disabled = true;
    } else {
        spinner.classList.add('d-none');
        button.disabled = false;
    }
}

function handleError(error, placeholder) {
    console.error('AI Timeline Error:', error);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger mt-3';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error: ${escapeHtml(error.message)}`;
    placeholder.appendChild(errorDiv);
}

function getCSRFToken() {
    return window.CSRF_TOKEN || document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusColor(status) {
    switch(status) {
        case 'completed': return 'success';
        case 'in_progress': return 'warning';
        default: return 'secondary';
    }
}

function getConfidenceColor(confidence) {
    switch(confidence) {
        case 'high': return 'success';
        case 'medium': return 'warning';
        default: return 'danger';
    }
}

function getUtilizationColor(percentage) {
    if (percentage > 90) return 'danger';
    if (percentage > 70) return 'warning';
    return 'success';
}
