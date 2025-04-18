// Global variables to store chart instances
if (typeof columnChart === 'undefined') {
    var columnChart = null;
}
if (typeof priorityChart === 'undefined') {
    var priorityChart = null;
}

// Check if event listeners are already attached
if (typeof kanbanInitialized === 'undefined') {
    var kanbanInitialized = false;
    
    document.addEventListener('DOMContentLoaded', function() {
        // Only initialize if not already done
        if (!kanbanInitialized) {
            kanbanInitialized = true;
            
            // Initialize Kanban Board functionality if board exists
            if (document.querySelector('.kanban-board')) {
                initKanbanBoard();
                initColumnOrdering();
                setupTaskProgress();
            }
            
            // Initialize charts if they exist
            if (document.querySelector('#tasksColumnChart')) {
                initCharts();
            }
        }
    });
}

function initKanbanBoard() {
    const tasks = document.querySelectorAll('.kanban-task');
    const columns = document.querySelectorAll('.kanban-column-tasks');
    
    // Initialize drag for all tasks
    tasks.forEach(task => {
        task.setAttribute('draggable', 'true');
        task.addEventListener('dragstart', dragStart);
        task.addEventListener('dragend', dragEnd);
    });
    
    // Initialize drop for all columns
    columns.forEach(column => {
        column.addEventListener('dragover', dragOver);
        column.addEventListener('dragenter', dragEnter);
        column.addEventListener('dragleave', dragLeave);
        column.addEventListener('drop', drop);
    });
}

// Initialize column ordering functionality
function initColumnOrdering() {
    const refreshButton = document.getElementById('refresh-columns-btn');
    if (!refreshButton) return;
    
    // Add event listener to the refresh button
    refreshButton.addEventListener('click', function() {
        rearrangeColumns();
    });
    
    // Validate input to ensure only numbers between min and max are entered
    const positionInputs = document.querySelectorAll('.column-position-input');
    positionInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const value = parseInt(e.target.value);
            const min = parseInt(e.target.min);
            const max = parseInt(e.target.max);
            
            if (isNaN(value) || value < min) {
                e.target.value = min;
            } else if (value > max) {
                e.target.value = max;
            }
        });
    });
}

// Rearrange columns based on position inputs
function rearrangeColumns() {
    // Get all position inputs
    const positionInputs = document.querySelectorAll('.column-position-input');
    if (!positionInputs.length) return;
    
    // Create an array to store column positions
    const columnPositions = [];
    
    // Collect column IDs and desired positions
    positionInputs.forEach(input => {
        const columnId = input.dataset.columnId;
        const position = parseInt(input.value);
        
        if (columnId && !isNaN(position)) {
            columnPositions.push({ id: columnId, position: position });
        }
    });
    
    // Check for duplicate positions
    const positions = columnPositions.map(col => col.position);
    const hasDuplicates = positions.some((pos, index) => positions.indexOf(pos) !== index);
    
    if (hasDuplicates) {
        alert('Error: Each column must have a unique position number.');
        return;
    }
    
    // Sort the columns by position
    columnPositions.sort((a, b) => a.position - b.position);
    
    // Get the kanban board and all columns
    const kanbanBoard = document.getElementById('kanban-board');
    const addColumnBtn = document.querySelector('.add-column-btn');
    
    if (!kanbanBoard || !addColumnBtn) return;
    
    // Rearrange the columns in the DOM
    columnPositions.forEach(colPos => {
        const columnElement = document.getElementById(`column-${colPos.id}`);
        if (columnElement) {
            // Add to the end (before the Add Column button)
            kanbanBoard.insertBefore(columnElement, addColumnBtn);
        }
    });
    
    // Get the board ID
    const boardId = window.location.pathname.split('/').filter(Boolean)[1];
    
    // Save the new positions to the server
    saveColumnPositions(columnPositions, boardId);
}

// Save all column positions to the server
function saveColumnPositions(columnPositions, boardId) {
    // Create an array of column position data
    const positionData = columnPositions.map((col, index) => {
        return {
            columnId: col.id,
            position: index // Use the array index as the new position (0-based)
        };
    });
    
    // Send AJAX request to update all column positions
    fetch('/columns/reorder-multiple/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            columns: positionData,
            boardId: boardId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Columns rearranged successfully');
            
            // Update the position badges
            updateColumnPositionBadges();
            
            // Show success message
            showNotification('Columns rearranged successfully', 'success');
        } else {
            console.error('Error rearranging columns:', data.error);
            showNotification('Error rearranging columns', 'error');
        }
    })
    .catch(error => {
        console.error('Error rearranging columns:', error);
        showNotification('Error rearranging columns', 'error');
    });
}

// Update the position badges on columns after reordering
function updateColumnPositionBadges() {
    const columns = document.querySelectorAll('.kanban-column');
    columns.forEach((column, index) => {
        const badge = column.querySelector('.column-position-badge');
        if (badge) {
            badge.textContent = index + 1;
        }
    });
}

// Show a notification message
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, 3000);
}

// Task Drag and Drop Handlers
function dragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.id);
    e.dataTransfer.effectAllowed = 'move';
    
    // Add dragging class for styling
    e.target.classList.add('dragging');
    
    // Delay opacity change for better UX
    setTimeout(() => {
        e.target.style.opacity = '0.4';
    }, 0);
}

function dragEnd(e) {
    e.target.classList.remove('dragging');
    e.target.style.opacity = '1';
}

function dragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

function dragEnter(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function dragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function drop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const taskId = e.dataTransfer.getData('text/plain').replace('task-', '');
    const columnId = e.currentTarget.dataset.columnId;
    const taskElement = document.getElementById(`task-${taskId}`);
    
    if (taskElement) {
        e.currentTarget.appendChild(taskElement);
        
        // Update task position in backend
        updateTaskPosition(taskId, columnId);
    }
}

function updateTaskPosition(taskId, columnId) {
    // Send AJAX request to update task position
    fetch('/tasks/move/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            taskId: taskId,
            columnId: columnId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Task moved successfully');
        } else {
            console.error('Error moving task:', data.error);
        }
    })
    .catch(error => {
        console.error('Error moving task:', error);
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Charts for analytics
function initCharts() {
    // If Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        // Check for existing charts and destroy them if they exist
        if (columnChart) {
            columnChart.destroy();
        }
        if (priorityChart) {
            priorityChart.destroy();
        }
        
        // Tasks by Column Chart
        const columnsCtx = document.getElementById('tasksColumnChart').getContext('2d');
        const columnsData = JSON.parse(document.getElementById('columnsData').textContent);
        
        columnChart = new Chart(columnsCtx, {
            type: 'bar',
            data: {
                labels: columnsData.map(item => item.name),
                datasets: [{
                    label: 'Tasks',
                    data: columnsData.map(item => item.count),
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        precision: 0
                    }
                }
            }
        });
        
        // Tasks by Priority Chart
        const priorityCtx = document.getElementById('tasksPriorityChart');
        
        // Check if priority chart element exists before creating the chart
        if (priorityCtx) {
            const priorityData = JSON.parse(document.getElementById('priorityData').textContent);
            
            priorityChart = new Chart(priorityCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: priorityData.map(item => item.priority.charAt(0).toUpperCase() + item.priority.slice(1)),
                    datasets: [{
                        data: priorityData.map(item => item.count),
                        backgroundColor: [
                            'rgba(40, 167, 69, 0.7)',  // Low
                            'rgba(255, 193, 7, 0.7)',  // Medium
                            'rgba(253, 126, 20, 0.7)', // High
                            'rgba(220, 53, 69, 0.7)'   // Urgent
                        ],
                        borderColor: [
                            'rgba(40, 167, 69, 1)',
                            'rgba(255, 193, 7, 1)',
                            'rgba(253, 126, 20, 1)',
                            'rgba(220, 53, 69, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
    }
}

// Task progress handling
function setupTaskProgress() {
    // Set up increase progress buttons
    document.querySelectorAll('.increase-progress').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            updateTaskProgress(taskId, 'increase');
        });
    });
    
    // Set up decrease progress buttons
    document.querySelectorAll('.decrease-progress').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            updateTaskProgress(taskId, 'decrease');
        });
    });
}

function updateTaskProgress(taskId, direction) {
    fetch(`/tasks/${taskId}/update-progress/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            direction: direction
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the progress bar
            const task = document.getElementById(`task-${taskId}`);
            if (task) {
                const progressBar = task.querySelector('.progress-bar');
                const progressText = task.querySelector('.task-progress-container small');
                
                if (progressBar && progressText) {
                    // Remove existing color classes
                    progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-success');
                    // Add new color class
                    progressBar.classList.add(data.colorClass);
                    // Update width
                    progressBar.style.width = `${data.progress}%`;
                    // Update text
                    progressText.textContent = `${data.progress}% complete`;
                }
            }
        } else {
            console.error('Error updating task progress:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating task progress:', error);
    });
}