/**
 * AI-Powered Smart Resource Analysis JavaScript Functions
 *  * This module provides frontend functionality for smart resource management,
 * including workload balancing, assignment optimization, and resource reallocation.
 */

// Initialize resource analysis features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initResourceAnalysis();
});

/**
 * Initialize all resource analysis features
 */
function initResourceAnalysis() {
    console.log('Initializing AI-Powered Smart Resource Analysis...');
    
    // Initialize assignment optimization
    initAssignmentOptimization();
    
    // Initialize workload balancing
    initWorkloadBalancing();
    
    // Initialize resource reallocation
    initResourceReallocation();
    
    // Initialize team resource overview
    initTeamResourceOverview();
    
    // Initialize user profile management
    initUserProfileManagement();
}

/**
 * Initialize bottleneck analysis feature
 */
/**
 * Initialize assignment optimization feature
 */
function initAssignmentOptimization() {
    const optimizeBtn = document.getElementById('optimize-assignments-btn');
    if (!optimizeBtn) return;
    
    optimizeBtn.addEventListener('click', function() {
        const boardId = this.dataset.boardId;
        if (!boardId) {
            alert('Board ID not found. Please refresh the page.');
            return;
        }
        
        // Get selected task IDs if any
        const selectedTasks = getSelectedTaskIds();
        
        optimizeTaskAssignments(boardId, selectedTasks, function(error, data) {
            if (error) {
                console.error('Assignment optimization error:', error);
                alert('Failed to optimize assignments: ' + error.message);
                return;
            }
            
            displayAssignmentOptimization(data);
        });
    });
}

/**
 * Optimize task assignments using AI
 */
function optimizeTaskAssignments(boardId, taskIds, callback) {
    const spinner = document.getElementById('optimization-spinner');
    const button = document.getElementById('optimize-assignments-btn');
    
    if (spinner) spinner.classList.remove('d-none');
    if (button) button.disabled = true;
    
    const requestData = { board_id: parseInt(boardId) };
    if (taskIds && taskIds.length > 0) {
        requestData.task_ids = taskIds;
    }
    
    fetch('/api/optimize-task-assignments/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        if (callback) callback(null, data);
    })
    .catch(error => {
        console.error('Error optimizing assignments:', error);
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        if (callback) callback(error, null);
    });
}

/**
 * Display assignment optimization results
 */
function displayAssignmentOptimization(data) {
    const container = document.getElementById('assignment-optimization-container');
    const placeholder = document.getElementById('assignment-optimization-placeholder');
    const content = document.getElementById('assignment-optimization-content');
    
    if (!container || !content) return;
    
    // Store data globally for metric explanations
    window.currentOptimizationData = data;
    
    let html = `
        <div class="row mb-4">
            <div class="col-12">
                <h5><i class="fas fa-users-cog me-2"></i>Assignment Optimization Results</h5>
                <div class="row">
                    <div class="col-md-3">
                        <div class="card text-center metric-card" data-metric="tasks-analyzed" onclick="showMetricExplanation('tasks-analyzed', ${data.optimization_summary.total_tasks_analyzed})">
                            <div class="card-body">
                                <i class="fas fa-question-circle metric-help-icon"></i>
                                <h3 class="text-primary">${data.optimization_summary.total_tasks_analyzed}</h3>
                                <p class="card-text">Tasks Analyzed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center metric-card" data-metric="assignments-changed" onclick="showMetricExplanation('assignments-changed', ${data.optimization_summary.assignments_changed})">
                            <div class="card-body">
                                <i class="fas fa-question-circle metric-help-icon"></i>
                                <h3 class="text-success">${data.optimization_summary.assignments_changed}</h3>
                                <p class="card-text">Assignments Changed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center metric-card" data-metric="skill-match" onclick="showMetricExplanation('skill-match', ${data.optimization_summary.average_skill_match_improvement})">
                            <div class="card-body">
                                <i class="fas fa-question-circle metric-help-icon"></i>
                                <h3 class="text-info">${data.optimization_summary.average_skill_match_improvement}%</h3>
                                <p class="card-text">Skill Match Improvement</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center metric-card" data-metric="workload-balance" onclick="showMetricExplanation('workload-balance', ${data.optimization_summary.workload_balance_score})">
                            <div class="card-body">
                                <i class="fas fa-question-circle metric-help-icon"></i>
                                <h3 class="text-warning">${data.optimization_summary.workload_balance_score}/10</h3>
                                <p class="card-text">Workload Balance Score</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add detailed optimization results if available
    if (data.optimization_details && data.optimization_details.length > 0) {
        html += `
            <div class="row mb-4">
                <div class="col-12">
                    <h6><i class="fas fa-exchange-alt me-2"></i>Optimization Details</h6>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Task</th>
                                    <th>Previous Assignee</th>
                                    <th>New Assignee</th>
                                    <th>Skill Match</th>
                                    <th>Workload Impact</th>
                                    <th>Reasoning</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        data.optimization_details.forEach(detail => {
            html += `
                <tr>
                    <td><strong>${detail.task_title}</strong></td>
                    <td>${detail.previous_assignee || 'Unassigned'}</td>
                    <td><span class="badge badge-success">${detail.new_assignee}</span></td>
                    <td><span class="badge badge-${getSkillMatchBadgeClass(detail.skill_match_score)}">${detail.skill_match_score}%</span></td>
                    <td><span class="badge badge-${detail.workload_impact === 'improved' ? 'success' : detail.workload_impact === 'neutral' ? 'secondary' : 'warning'}">${detail.workload_impact}</span></td>
                    <td>${detail.reasoning}</td>
                </tr>
            `;
        });
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Add recommendations section
    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="row mb-4">
                <div class="col-12">
                    <h6><i class="fas fa-lightbulb me-2"></i>Optimization Recommendations</h6>
                    <div class="list-group">
        `;
        
        data.recommendations.forEach(rec => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${rec.title}</h6>
                        <small class="text-muted">Priority: ${rec.priority}</small>
                    </div>
                    <p class="mb-1">${rec.description}</p>
                    ${rec.expected_impact ? `<small class="text-success">Expected Impact: ${rec.expected_impact}</small>` : ''}
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
    }
    
    content.innerHTML = html;
    container.classList.remove('d-none');
    if (placeholder) placeholder.classList.add('d-none');
}

/**
 * Initialize workload balancing feature
 */
function initWorkloadBalancing() {
    const balanceBtn = document.getElementById('balance-workload-btn');
    if (!balanceBtn) return;
    
    balanceBtn.addEventListener('click', function() {
        const boardId = this.dataset.boardId;
        if (!boardId) {
            alert('Board ID not found. Please refresh the page.');
            return;
        }
        
        balanceTeamWorkload(boardId, function(error, data) {
            if (error) {
                console.error('Workload balancing error:', error);
                alert('Failed to balance workload: ' + error.message);
                return;
            }
            
            displayWorkloadBalancing(data);
        });
    });
}

/**
 * Balance team workload using AI
 */
function balanceTeamWorkload(boardId, callback) {
    const spinner = document.getElementById('balance-spinner');
    const button = document.getElementById('balance-workload-btn');
    
    if (spinner) spinner.classList.remove('d-none');
    if (button) button.disabled = true;
    
    fetch('/api/balance-team-workload/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ board_id: parseInt(boardId) })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        if (callback) callback(null, data);
    })
    .catch(error => {
        console.error('Error balancing workload:', error);
        if (spinner) spinner.classList.add('d-none');
        if (button) button.disabled = false;
        
        if (callback) callback(error, null);
    });
}

/**
 * Display workload balancing results
 */
function displayWorkloadBalancing(data) {
    // Implementation similar to other display functions
    console.log('Workload balancing results:', data);
    // ... (detailed implementation would go here)
}

/**
 * Utility functions for resource analysis
 */
function getCSRFToken() {
    // Try multiple sources for CSRF token
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    
    if (window.CSRF_TOKEN) {
        return window.CSRF_TOKEN;
    } else if (csrfInput) {
        return csrfInput.value;
    } else if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    } else {
        // Try to get from cookie as last resort
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
    }
    return '';
}

function getSeverityBadgeClass(severity) {
    switch (severity) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        case 'low': return 'success';
        default: return 'secondary';
    }
}

function getSeverityBorderClass(severity) {
    switch (severity) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        case 'low': return 'success';
        default: return 'secondary';
    }
}

function getSkillMatchBadgeClass(score) {
    if (score >= 90) return 'success';
    if (score >= 70) return 'info';
    if (score >= 50) return 'warning';
    return 'danger';
}

function getUtilizationBadgeClass(utilization) {
    if (utilization > 100) return 'danger';
    if (utilization > 85) return 'warning';
    if (utilization > 50) return 'success';
    return 'info';
}

function getSelectedTaskIds() {
    // Get selected task IDs from checkboxes or other selection mechanism
    const selectedCheckboxes = document.querySelectorAll('.task-checkbox:checked');
    return Array.from(selectedCheckboxes).map(cb => parseInt(cb.value));
}

// Additional feature initialization functions would go here...
function initResourceReallocation() {
    // Implementation for resource reallocation
}

function initTeamResourceOverview() {
    // Implementation for team resource overview
}

function initUserProfileManagement() {
    // Implementation for user profile management
}

/**
 * Show metric explanation in modal
 */
function showMetricExplanation(metricType, value) {
    const modal = new bootstrap.Modal(document.getElementById('metricExplanationModal'));
    const titleElement = document.getElementById('metricTitle');
    const iconElement = document.getElementById('metricIcon');
    const contentElement = document.getElementById('metricExplanationContent');
    
    // Use globally stored data
    const data = window.currentOptimizationData || {};
    
    let title, icon, content;
    
    switch (metricType) {
        case 'tasks-analyzed':
            title = 'Tasks Analyzed';
            icon = 'fas fa-tasks';
            content = generateTasksAnalyzedExplanation(value, data);
            break;
        case 'assignments-changed':
            title = 'Assignments Changed';
            icon = 'fas fa-exchange-alt';
            content = generateAssignmentsChangedExplanation(value, data);
            break;
        case 'skill-match':
            title = 'Skill Match Improvement';
            icon = 'fas fa-bullseye';
            content = generateSkillMatchExplanation(value, data);
            break;
        case 'workload-balance':
            title = 'Workload Balance Score';
            icon = 'fas fa-balance-scale';
            content = generateWorkloadBalanceExplanation(value, data);
            break;
        default:
            title = 'Metric Information';
            icon = 'fas fa-info-circle';
            content = '<p>No detailed explanation available for this metric.</p>';
    }
    
    titleElement.textContent = title;
    iconElement.className = icon + ' me-2';
    contentElement.innerHTML = content;
    
    modal.show();
}

/**
 * Generate explanation for Tasks Analyzed metric
 */
function generateTasksAnalyzedExplanation(value, data) {
    try {
        const totalTasks = data.board_statistics?.total_tasks || 'unknown';
        const activeTasks = data.board_statistics?.active_tasks || 'unknown';
        
        return `
            <div class="metric-explanation">
                <div class="row mb-3">
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <h4 class="text-primary">${value}</h4>
                            <small class="text-muted">Tasks Analyzed</small>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <h6>What this means:</h6>
                        <p>This represents the number of tasks that our AI system examined during the assignment optimization process.</p>
                    </div>
                </div>
                
                <div class="alert alert-info">
                    <h6><i class="fas fa-info-circle me-2"></i>Analysis Scope</h6>
                    <ul class="mb-0">
                        <li><strong>Total tasks in board:</strong> ${totalTasks}</li>
                        <li><strong>Active tasks analyzed:</strong> ${activeTasks}</li>
                        <li><strong>Analysis depth:</strong> Skills, workload, dependencies, and deadlines</li>
                        <li><strong>AI considerations:</strong> Team member availability, skill matching, and workload balance</li>
                    </ul>
                </div>
                
                <div class="mt-3">
                    <h6>Why this matters:</h6>
                    <p>A higher number indicates a more comprehensive analysis. The AI examines task requirements, complexity, and dependencies to make optimal assignment recommendations.</p>
                </div>
            </div>
        `;
    } catch (error) {
        return `
            <div class="alert alert-info">
                <h6>Tasks Analyzed: ${value}</h6>
                <p>This metric shows how many tasks were examined by the AI optimization system. More analyzed tasks typically lead to better assignment recommendations.</p>
                <div class="mt-3">
                    <h6>What the AI analyzes:</h6>
                    <ul>
                        <li>Task complexity and requirements</li>
                        <li>Team member skills and availability</li>
                        <li>Current workload distribution</li>
                        <li>Task dependencies and deadlines</li>
                        <li>Historical performance data</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

/**
 * Generate explanation for Assignments Changed metric
 */
function generateAssignmentsChangedExplanation(value, data) {
    try {
        const totalAnalyzed = data.optimization_summary?.total_tasks_analyzed || 0;
        const changePercentage = totalAnalyzed > 0 ? ((value / totalAnalyzed) * 100).toFixed(1) : 0;
        
        return `
            <div class="metric-explanation">
                <div class="row mb-3">
                    <div class="col-md-4">
                        <div class="text-center p-3 bg-light rounded">
                            <h4 class="text-success">${value}</h4>
                            <small class="text-muted">Assignments Changed</small>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <h6>What this means:</h6>
                        <p>The AI recommended changing ${value} task assignments out of ${totalAnalyzed} analyzed tasks (${changePercentage}% optimization rate).</p>
                    </div>
                </div>
                
                <div class="alert alert-success">
                    <h6><i class="fas fa-exchange-alt me-2"></i>Optimization Benefits</h6>
                    <ul class="mb-0">
                        <li><strong>Better skill matching:</strong> Tasks assigned to team members with relevant skills</li>
                        <li><strong>Improved workload balance:</strong> More even distribution of work</li>
                        <li><strong>Reduced bottlenecks:</strong> Preventing overload of key team members</li>
                        <li><strong>Faster completion:</strong> Optimal assignments can reduce project timelines</li>
                    </ul>
                </div>
                
                <div class="mt-3">
                    <h6>Interpretation:</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-success" style="width: ${Math.min(changePercentage, 100)}%"></div>
                    </div>
                    <p class="small text-muted">
                        ${changePercentage < 10 ? 'Low optimization needed - assignments are already well-balanced' :
                          changePercentage < 30 ? 'Moderate optimization - some improvements identified' :
                          'High optimization potential - significant improvements possible'}
                    </p>
                </div>
            </div>
        `;
    } catch (error) {
        return `
            <div class="alert alert-success">
                <h6>Assignments Changed: ${value}</h6>
                <p>This shows how many task assignments were optimized. Changes are made to improve skill matching, workload balance, and overall team efficiency.</p>
                <div class="mt-3">
                    <h6>Why assignments are changed:</h6>
                    <ul>
                        <li>Better skill-to-task matching</li>
                        <li>More balanced workload distribution</li>
                        <li>Reduced team member overload</li>
                        <li>Improved project delivery timelines</li>
                        <li>Enhanced team member satisfaction</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

/**
 * Generate explanation for Skill Match Improvement metric
 */
function generateSkillMatchExplanation(value, data) {
    const improvementLevel = value > 20 ? 'excellent' : value > 10 ? 'good' : value > 5 ? 'moderate' : 'minimal';
    const badgeClass = value > 20 ? 'success' : value > 10 ? 'info' : value > 5 ? 'warning' : 'secondary';
    
    return `
        <div class="metric-explanation">
            <div class="row mb-3">
                <div class="col-md-4">
                    <div class="text-center p-3 bg-light rounded">
                        <h4 class="text-info">${value}%</h4>
                        <small class="text-muted">Skill Match Improvement</small>
                    </div>
                </div>
                <div class="col-md-8">
                    <h6>What this means:</h6>
                    <p>On average, the skill-to-task matching improved by ${value}% through AI optimization.</p>
                    <span class="badge badge-${badgeClass}">${improvementLevel.toUpperCase()} improvement</span>
                </div>
            </div>
            
            <div class="alert alert-info">
                <h6><i class="fas fa-bullseye me-2"></i>Skill Matching Factors</h6>
                <ul class="mb-0">
                    <li><strong>Technical skills:</strong> Programming languages, frameworks, tools</li>
                    <li><strong>Domain expertise:</strong> Industry knowledge and experience</li>
                    <li><strong>Soft skills:</strong> Communication, leadership, problem-solving</li>
                    <li><strong>Experience level:</strong> Years of experience and project complexity</li>
                    <li><strong>Past performance:</strong> Historical success with similar tasks</li>
                </ul>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Impact of Better Skill Match:</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>Faster task completion</li>
                                <li><i class="fas fa-check text-success me-2"></i>Higher quality deliverables</li>
                                <li><i class="fas fa-check text-success me-2"></i>Reduced rework and errors</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <ul class="list-unstyled">
                                <li><i class="fas fa-check text-success me-2"></i>Improved team morale</li>
                                <li><i class="fas fa-check text-success me-2"></i>Better skill development</li>
                                <li><i class="fas fa-check text-success me-2"></i>Lower project risk</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate explanation for Workload Balance Score metric
 */
function generateWorkloadBalanceExplanation(value, data) {
    const balanceLevel = value >= 8 ? 'excellent' : value >= 6 ? 'good' : value >= 4 ? 'fair' : 'poor';
    const badgeClass = value >= 8 ? 'success' : value >= 6 ? 'info' : value >= 4 ? 'warning' : 'danger';
    
    return `
        <div class="metric-explanation">
            <div class="row mb-3">
                <div class="col-md-4">
                    <div class="text-center p-3 bg-light rounded">
                        <h4 class="text-warning">${value}/10</h4>
                        <small class="text-muted">Balance Score</small>
                    </div>
                </div>
                <div class="col-md-8">
                    <h6>What this means:</h6>
                    <p>This score measures how evenly work is distributed across your team after optimization.</p>
                    <span class="badge badge-${badgeClass}">${balanceLevel.toUpperCase()} balance</span>
                </div>
            </div>
            
            <div class="alert alert-warning">
                <h6><i class="fas fa-balance-scale me-2"></i>Balance Factors</h6>
                <ul class="mb-0">
                    <li><strong>Workload distribution:</strong> Hours allocated vs. team capacity</li>
                    <li><strong>Task complexity:</strong> Mental load and difficulty balance</li>
                    <li><strong>Deadline pressure:</strong> Urgent vs. non-urgent task distribution</li>
                    <li><strong>Skill utilization:</strong> Everyone working within their expertise</li>
                    <li><strong>Growth opportunities:</strong> Balanced learning and stretch assignments</li>
                </ul>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Score Interpretation:</h6>
                    <div class="progress mb-2" style="height: 20px;">
                        <div class="progress-bar bg-${badgeClass}" style="width: ${value * 10}%">${value}/10</div>
                    </div>
                    <div class="small text-muted">
                        <div class="d-flex justify-content-between">
                            <span>Poor (1-3)</span>
                            <span>Fair (4-5)</span>
                            <span>Good (6-7)</span>
                            <span>Excellent (8-10)</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-3">
                <h6>Recommendations:</h6>
                ${value >= 8 ? 
                    '<p class="text-success">Excellent balance! Your team workload is well-distributed. Continue monitoring as new tasks are added.</p>' :
                    value >= 6 ?
                    '<p class="text-info">Good balance with room for improvement. Consider redistributing some high-complexity tasks.</p>' :
                    value >= 4 ?
                    '<p class="text-warning">Fair balance. Some team members may be overloaded while others are underutilized.</p>' :
                    '<p class="text-danger">Poor balance detected. Immediate workload redistribution recommended to prevent burnout.</p>'
                }
            </div>
        </div>
    `;
}
