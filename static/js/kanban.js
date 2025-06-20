// Global variables to store chart instances
if (typeof columnChart === 'undefined') {
    var columnChart = null;
}
if (typeof priorityChart === 'undefined') {
    var priorityChart = null;
}

// Configuration for column scrolling
if (typeof COLUMN_SCROLL_CONFIG === 'undefined') {
    var COLUMN_SCROLL_CONFIG = {
        TASK_THRESHOLD: 5,        // Number of tasks before scroll appears (changed from 4 to 5)
        MAX_HEIGHT: 400,          // Maximum height in pixels when scrollable
        MIN_HEIGHT: 200,          // Minimum height in pixels for empty columns
        ENABLE_INDICATORS: true   // Show scroll indicators
    };
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
                // Force cleanup any existing scroll states first
                setTimeout(() => {
                    if (typeof forceCleanupAllColumns === 'function') {
                        forceCleanupAllColumns();
                    }
                }, 100);
                
                initKanbanBoard();
                initColumnOrdering();
                setupTaskProgress();
                // Add keyboard support for accessibility
                addKeyboardSupport();
                
                // Initialize column scrolling after other components and cleanup
                setTimeout(() => {
                    initColumnScrolling();
                }, 800);
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
    
    // Initialize column scrolling based on task count
    initColumnScrolling();
    
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
        
        // Add drop zone indicators
        addDropZoneIndicator(column);
    });
    
    // Add scroll indicators for auto-scroll
    addScrollIndicators();
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
if (typeof draggedElement === 'undefined') {
    var draggedElement = null;
}
if (typeof autoScrollInterval === 'undefined') {
    var autoScrollInterval = null;
}

function dragStart(e) {
    draggedElement = e.target;
    e.dataTransfer.setData('text/plain', e.target.id);
    e.dataTransfer.effectAllowed = 'move';
    
    // Add dragging class for styling
    e.target.classList.add('dragging');
    
    // Show drop zone indicators
    showDropZoneIndicators();
    
    // Start auto-scroll monitoring
    startAutoScroll();
    
    // Delay opacity change for better UX
    setTimeout(() => {
        e.target.style.opacity = '0.7';
    }, 0);
}

function dragEnd(e) {
    draggedElement = null;
    e.target.classList.remove('dragging');
    e.target.style.opacity = '1';
    
    // Hide drop zone indicators
    hideDropZoneIndicators();
    
    // Stop auto-scroll
    stopAutoScroll();
    
    // Clean up any drag-over states
    document.querySelectorAll('.kanban-column-tasks').forEach(col => {
        col.classList.remove('drag-over', 'drag-over-extended');
    });
}

function dragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    // Handle auto-scroll based on mouse position
    handleAutoScrollOnDrag(e);
}

function dragEnter(e) {
    e.preventDefault();
    const column = e.currentTarget;
    column.classList.add('drag-over');
    
    // If column is short, extend it temporarily
    const tasks = column.querySelectorAll('.kanban-task:not(.dragging)');
    if (tasks.length < 3) { // If column has few tasks
        column.classList.add('drag-over-extended');
    }
    
    // Show drop indicator for this column
    const indicator = column.querySelector('.drop-zone-indicator');
    if (indicator) {
        indicator.classList.add('active');
    }
}

function dragLeave(e) {
    const column = e.currentTarget;
    
    // Only remove drag-over if we're actually leaving the column
    // (not just moving to a child element)
    if (!column.contains(e.relatedTarget)) {
        column.classList.remove('drag-over', 'drag-over-extended');
        
        // Hide drop indicator
        const indicator = column.querySelector('.drop-zone-indicator');
        if (indicator) {
            indicator.classList.remove('active');
        }
    }
}

function drop(e) {
    e.preventDefault();
    const column = e.currentTarget;
    column.classList.remove('drag-over', 'drag-over-extended');
    
    const taskId = e.dataTransfer.getData('text/plain').replace('task-', '');
    const columnId = column.dataset.columnId;
    const taskElement = document.getElementById(`task-${taskId}`);
    
    if (taskElement && taskElement !== draggedElement) {
        return; // Prevent dropping on itself
    }
    
    if (taskElement) {
        // Smooth animation for the drop
        taskElement.style.transform = 'scale(0.95)';
        taskElement.style.transition = 'transform 0.2s ease';
        
        // Calculate drop position within the column
        const rect = column.getBoundingClientRect();
        const mouseY = e.clientY - rect.top;
        const tasks = Array.from(column.querySelectorAll('.kanban-task:not(.dragging)'));
        
        let insertIndex = tasks.length; // Default to end
        
        for (let i = 0; i < tasks.length; i++) {
            const taskRect = tasks[i].getBoundingClientRect();
            const taskY = taskRect.top - rect.top + column.scrollTop;
            
            if (mouseY < taskY + taskRect.height / 2) {
                insertIndex = i;
                break;
            }
        }
        
        // Insert at the calculated position
        if (insertIndex < tasks.length) {
            column.insertBefore(taskElement, tasks[insertIndex]);
        } else {
            column.appendChild(taskElement);
        }
        
        // Reset transform after a short delay
        setTimeout(() => {
            taskElement.style.transform = '';
            taskElement.style.transition = '';
        }, 200);
          // Update task position in backend
        updateTaskPosition(taskId, columnId, insertIndex);
        
        // Update column scrolling immediately for visual feedback
        setTimeout(() => {
            updateColumnScrolling();
        }, 100);
    }
    
    // Hide drop indicator
    const indicator = column.querySelector('.drop-zone-indicator');
    if (indicator) {
        indicator.classList.remove('active');
    }
}

// Column Scrolling Management
function initColumnScrolling() {
    try {
        console.log('Initializing column scrolling...');
        
        // Set CSS custom properties based on configuration
        document.documentElement.style.setProperty('--column-scroll-max-height', COLUMN_SCROLL_CONFIG.MAX_HEIGHT + 'px');
        document.documentElement.style.setProperty('--column-scroll-min-height', COLUMN_SCROLL_CONFIG.MIN_HEIGHT + 'px');
        
        console.log('CSS properties set:', {
            maxHeight: COLUMN_SCROLL_CONFIG.MAX_HEIGHT + 'px',
            minHeight: COLUMN_SCROLL_CONFIG.MIN_HEIGHT + 'px'
        });
        
        // Initial update
        updateColumnScrolling();
        
        // Listen for task operations (avoid recursion)
        document.addEventListener('taskMoved', function() {
            setTimeout(updateColumnScrolling, 100);
        });
        
        console.log('Column scrolling initialized successfully');
        
    } catch (error) {
        console.error('Error in initColumnScrolling:', error);
    }
}

function updateColumnScrolling() {
    try {
        console.log('Updating column scrolling...');
        
        const columns = document.querySelectorAll('.kanban-column-tasks');
        console.log(`Found ${columns.length} columns`);
        
        columns.forEach((column, index) => {
            const tasks = column.querySelectorAll('.kanban-task');
            const taskCount = tasks.length;
            const columnWrapper = column.closest('.kanban-column');
            
            console.log(`Column ${index + 1}: ${taskCount} tasks`);
              // Add or remove scrollable class based on task count
            if (taskCount > COLUMN_SCROLL_CONFIG.TASK_THRESHOLD) {
                console.log(`  → Making column ${index + 1} scrollable`);
                column.classList.add('scrollable');
                
                // Clear any conflicting styles first
                column.style.minHeight = '';
                column.style.flexGrow = '';
                column.style.maxHeight = '';
                
                // Apply only essential scrolling styles
                column.style.height = COLUMN_SCROLL_CONFIG.MAX_HEIGHT + 'px';
                column.style.overflowY = 'auto';
                column.style.overflowX = 'hidden';
                
                // Ensure the column wrapper doesn't interfere
                if (columnWrapper) {
                    columnWrapper.classList.add('has-scroll');
                    columnWrapper.style.position = 'relative';
                    columnWrapper.style.overflow = 'visible';
                }
                  } else {
                console.log(`  → Removing scroll from column ${index + 1}`);
                column.classList.remove('scrollable');
                
                // Thorough cleanup of all scroll-related styles
                column.style.height = '';
                column.style.maxHeight = '';
                column.style.minHeight = '';
                column.style.overflowY = '';
                column.style.overflowX = '';
                column.style.border = '';
                column.style.borderRadius = '';
                column.style.padding = '';
                column.style.backgroundColor = '';
                column.style.contain = '';
                column.style.position = '';
                column.style.width = '';
                column.style.boxSizing = '';
                
                // Reset to default natural sizing
                column.style.minHeight = COLUMN_SCROLL_CONFIG.MIN_HEIGHT + 'px';
                
                if (columnWrapper) {
                    columnWrapper.classList.remove('has-scroll');
                    // Also cleanup wrapper styles that might interfere
                    columnWrapper.style.position = '';
                    columnWrapper.style.overflow = '';
                }
            }
        });
        
        console.log('Column scrolling update completed');
        
    } catch (error) {
        console.error('Error in updateColumnScrolling:', error);
    }
}

// Make function globally accessible
window.kanbanUpdateColumnScrolling = updateColumnScrolling;

// Force cleanup function to reset all column styles
function forceCleanupAllColumns() {
    console.log('Force cleaning up all column styles...');
    
    const columns = document.querySelectorAll('.kanban-column-tasks');
    columns.forEach((column, index) => {
        console.log(`  → Force cleaning column ${index + 1}`);
        
        // Remove all scroll-related classes
        column.classList.remove('scrollable');
        // Add force reset class temporarily
        column.classList.add('force-reset');
        
        // Clear all inline styles
        column.removeAttribute('style');
        
        // Get wrapper and clean it too
        const columnWrapper = column.closest('.kanban-column');
        if (columnWrapper) {
            columnWrapper.classList.remove('has-scroll');
            columnWrapper.classList.add('force-reset');
            // Don't remove all styles from wrapper, just overflow-related ones
            columnWrapper.style.position = '';
            columnWrapper.style.overflow = '';
        }
    });
    
    // After a short delay, remove reset classes and reapply proper scrolling
    setTimeout(() => {
        columns.forEach(column => {
            column.classList.remove('force-reset');
            const columnWrapper = column.closest('.kanban-column');
            if (columnWrapper) {
                columnWrapper.classList.remove('force-reset');
            }
        });
        
        // Reapply proper scrolling
        updateColumnScrolling();
    }, 200);
}

// Make cleanup function globally accessible
window.kanbanForceCleanup = forceCleanupAllColumns;

function addScrollIndicators(column) {
    // Temporarily disabled to debug scroll bar positioning issues
    // This function will be re-enabled once the core scrolling is working properly
    return;
}

function removeScrollIndicators(column) {
    const columnWrapper = column.closest('.kanban-column');
    if (columnWrapper) {
        const topIndicator = columnWrapper.querySelector('.scroll-indicator-top');
        const bottomIndicator = columnWrapper.querySelector('.scroll-indicator-bottom');
        
        if (topIndicator) topIndicator.remove();
        if (bottomIndicator) bottomIndicator.remove();
    }
}

function updateScrollIndicators(column, topIndicator, bottomIndicator) {
    const scrollTop = column.scrollTop;
    const scrollHeight = column.scrollHeight;
    const clientHeight = column.clientHeight;
    const scrollBottom = scrollHeight - scrollTop - clientHeight;
    
    // Show top indicator if not at top
    if (scrollTop > 10) {
        topIndicator.style.opacity = '1';
    } else {
        topIndicator.style.opacity = '0';
    }
    
    // Show bottom indicator if not at bottom
    if (scrollBottom > 10) {
        bottomIndicator.style.opacity = '1';
    } else {
        bottomIndicator.style.opacity = '0';
    }
}

// Helper Functions for Enhanced Drag and Drop

function addDropZoneIndicator(column) {
    const indicator = document.createElement('div');
    indicator.className = 'drop-zone-indicator';
    indicator.innerHTML = '<i class="fas fa-plus"></i> Drop here';
    column.style.position = 'relative';
    column.appendChild(indicator);
}

function showDropZoneIndicators() {
    document.querySelectorAll('.drop-zone-indicator').forEach(indicator => {
        const column = indicator.parentElement;
        const tasks = column.querySelectorAll('.kanban-task:not(.dragging)');
        
        // Show indicator for columns with few tasks
        if (tasks.length < 4) {
            indicator.style.display = 'flex';
        }
    });
}

function hideDropZoneIndicators() {
    document.querySelectorAll('.drop-zone-indicator').forEach(indicator => {
        indicator.classList.remove('active');
        indicator.style.display = 'none';
    });
}

function addScrollIndicators() {
    // Add scroll indicators to the page
    const topIndicator = document.createElement('div');
    topIndicator.className = 'scroll-indicator top';
    topIndicator.innerHTML = '<i class="fas fa-chevron-up"></i> Scroll up';
    document.body.appendChild(topIndicator);
    
    const bottomIndicator = document.createElement('div');
    bottomIndicator.className = 'scroll-indicator bottom';
    bottomIndicator.innerHTML = '<i class="fas fa-chevron-down"></i> Scroll down';
    document.body.appendChild(bottomIndicator);
}

function startAutoScroll() {
    // Start monitoring mouse position for auto-scroll
    document.addEventListener('dragover', handleAutoScrollOnDrag);
}

function stopAutoScroll() {
    // Stop auto-scroll monitoring
    document.removeEventListener('dragover', handleAutoScrollOnDrag);
    
    if (autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
    }
    
    // Hide scroll indicators
    document.querySelectorAll('.scroll-indicator').forEach(indicator => {
        indicator.style.display = 'none';
    });
}

function handleAutoScrollOnDrag(e) {
    const scrollThreshold = 100; // pixels from edge
    const scrollSpeed = 5;
    const viewportHeight = window.innerHeight;
    const mouseY = e.clientY;
    
    // Clear existing interval
    if (autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
    }
    
    // Check if we need to scroll up
    if (mouseY < scrollThreshold) {
        document.querySelector('.scroll-indicator.top').style.display = 'block';
        autoScrollInterval = setInterval(() => {
            window.scrollBy(0, -scrollSpeed);
        }, 16);
    }
    // Check if we need to scroll down
    else if (mouseY > viewportHeight - scrollThreshold) {
        document.querySelector('.scroll-indicator.bottom').style.display = 'block';
        autoScrollInterval = setInterval(() => {
            window.scrollBy(0, scrollSpeed);
        }, 16);
    } else {
        // Hide scroll indicators
        document.querySelectorAll('.scroll-indicator').forEach(indicator => {
            indicator.style.display = 'none';
        });
    }
}

function updateTaskPosition(taskId, columnId, position = 0) {
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
            columnId: columnId,
            position: position
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Task moved successfully');
            // Show success notification
            showNotification('Task moved successfully', 'success');
            
            // Update column scrolling after task move
            updateColumnScrolling();
            
            // Dispatch custom event for task moved
            document.dispatchEvent(new CustomEvent('taskMoved', {
                detail: { taskId, columnId, position }
            }));
        } else {
            console.error('Error moving task:', data.error);
            showNotification('Error moving task: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error moving task:', error);
        showNotification('Error moving task', 'error');
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
        try {
            // Check for existing charts and destroy them if they exist
            if (columnChart && typeof columnChart.destroy === 'function') {
                columnChart.destroy();
                columnChart = null;
            }
            if (priorityChart && typeof priorityChart.destroy === 'function') {
                priorityChart.destroy();
                priorityChart = null;
            }
            
            // Tasks by Column Chart
            const columnsCanvas = document.getElementById('tasksColumnChart');
            if (columnsCanvas) {
                const columnsCtx = columnsCanvas.getContext('2d');
                const columnsDataElement = document.getElementById('columnsData');
                
                if (columnsDataElement && columnsDataElement.textContent) {
                    const columnsData = JSON.parse(columnsDataElement.textContent);
                    
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
                }
            }
            
            // Tasks by Priority Chart
            const priorityCanvas = document.getElementById('tasksPriorityChart');
            
            // Check if priority chart element exists before creating the chart
            if (priorityCanvas) {
                const priorityDataElement = document.getElementById('priorityData');
                
                if (priorityDataElement && priorityDataElement.textContent) {
                    const priorityData = JSON.parse(priorityDataElement.textContent);
                      priorityChart = new Chart(priorityCanvas.getContext('2d'), {
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
        } catch (error) {
            console.error('Error initializing charts:', error);
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

// Keyboard Support for Accessibility
function addKeyboardSupport() {
    document.addEventListener('keydown', function(e) {
        const activeElement = document.activeElement;
        
        // Handle task selection and movement with keyboard
        if (activeElement && activeElement.classList.contains('kanban-task')) {
            switch(e.key) {
                case 'ArrowRight':
                    e.preventDefault();
                    moveTaskToNextColumn(activeElement);
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    moveTaskToPrevColumn(activeElement);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    focusPreviousTask(activeElement);
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    focusNextTask(activeElement);
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    // Open task detail or trigger edit
                    const taskId = activeElement.id.replace('task-', '');
                    window.location.href = `/tasks/${taskId}/`;
                    break;
            }
        }
    });
    
    // Make tasks focusable for keyboard navigation
    document.querySelectorAll('.kanban-task').forEach(task => {
        task.setAttribute('tabindex', '0');
        task.addEventListener('focus', function() {
            this.style.outline = '2px solid #007bff';
            this.style.outlineOffset = '2px';
        });
        task.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
}

function moveTaskToNextColumn(taskElement) {
    const currentColumn = taskElement.closest('.kanban-column');
    const nextColumn = currentColumn.nextElementSibling;
    
    if (nextColumn && nextColumn.classList.contains('kanban-column')) {
        const nextColumnTasks = nextColumn.querySelector('.kanban-column-tasks');
        const taskId = taskElement.id.replace('task-', '');
        const columnId = nextColumnTasks.dataset.columnId;
        
        // Move DOM element
        nextColumnTasks.appendChild(taskElement);
        
        // Update backend
        updateTaskPosition(taskId, columnId, 0);
        
        // Maintain focus
        taskElement.focus();
        
        showNotification('Task moved to next column', 'success');
    }
}

function moveTaskToPrevColumn(taskElement) {
    const currentColumn = taskElement.closest('.kanban-column');
    const prevColumn = currentColumn.previousElementSibling;
    
    if (prevColumn && prevColumn.classList.contains('kanban-column')) {
        const prevColumnTasks = prevColumn.querySelector('.kanban-column-tasks');
        const taskId = taskElement.id.replace('task-', '');
        const columnId = prevColumnTasks.dataset.columnId;
        
        // Move DOM element
        prevColumnTasks.appendChild(taskElement);
        
        // Update backend
        updateTaskPosition(taskId, columnId, 0);
        
        // Maintain focus
        taskElement.focus();
        
        showNotification('Task moved to previous column', 'success');
    }
}

function focusPreviousTask(taskElement) {
    const allTasks = Array.from(document.querySelectorAll('.kanban-task'));
    const currentIndex = allTasks.indexOf(taskElement);
    
    if (currentIndex > 0) {
        allTasks[currentIndex - 1].focus();
    }
}

function focusNextTask(taskElement) {
    const allTasks = Array.from(document.querySelectorAll('.kanban-task'));
    const currentIndex = allTasks.indexOf(taskElement);
    
    if (currentIndex < allTasks.length - 1) {
        allTasks[currentIndex + 1].focus();
    }
}

// Enhanced Column Height Management
function equalizeColumnHeights() {
    const columns = document.querySelectorAll('.kanban-column-tasks');
    if (columns.length === 0) return;
    
    // Don't equalize heights for scrollable columns
    columns.forEach(column => {
        if (!column.classList.contains('scrollable')) {
            column.style.height = 'auto'; // Reset height for non-scrollable columns
            
            // Set minimum height to ensure drop zones are accessible
            const minHeight = Math.max(COLUMN_SCROLL_CONFIG.MIN_HEIGHT, 200);
            column.style.minHeight = minHeight + 'px';
        }
        // Leave scrollable columns unchanged - they manage their own height
    });
}

// Debounced resize handler for responsive column heights
if (typeof resizeTimeout === 'undefined') {
    var resizeTimeout;
}
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(equalizeColumnHeights, 150);
});

// Call equalize heights on initial load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(equalizeColumnHeights, 100);
    });
} else {
    setTimeout(equalizeColumnHeights, 100);
}