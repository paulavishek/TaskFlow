/**
 * Forecast Dashboard JavaScript
 * Handles interactive features for the team capacity forecast
 */

function initForecastDashboard() {
    // Initialize any interactive elements
    console.log('Forecast dashboard initialized');
    
    // Set capacity bar widths from data attributes
    document.querySelectorAll('.capacity-fill[data-utilization]').forEach(function(element) {
        const utilization = parseFloat(element.getAttribute('data-utilization')) || 0;
        const cappedWidth = Math.min(utilization, 100);
        element.style.width = cappedWidth + '%';
    });
    
    // Set up event delegation for alert action buttons
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        if (target.matches('[data-action="acknowledge"]')) {
            const alertId = target.getAttribute('data-alert-id');
            acknowledgeAlert(alertId);
        } else if (target.matches('[data-action="resolve"]')) {
            const alertId = target.getAttribute('data-alert-id');
            resolveAlert(alertId);
        }
    });
    
    // Auto-refresh capability could be added here
    // setInterval(refreshForecasts, 300000); // Refresh every 5 minutes
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initForecastDashboard);
} else {
    initForecastDashboard();
}

function refreshForecasts() {
    console.log('Refreshing forecasts...');
    location.reload();
}

function generateNewForecast(boardId) {
    if (confirm('Generate new forecasts? This will refresh all capacity and workload data.')) {
        fetch('/kanban/board/' + boardId + '/forecast/generate/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Forecasts generated successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred', 'error');
        });
    }
}

function showNotification(message, type) {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

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

function acknowledgeAlert(alertId) {
    const boardId = document.querySelector('[data-board-id]').getAttribute('data-board-id');
    
    if (confirm('Mark this alert as acknowledged?')) {
        fetch('/kanban/board/' + boardId + '/alerts/' + alertId + '/acknowledge/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                location.reload();
            } else {
                alert('Error: ' + (d.error || d.message));
            }
        })
        .catch(e => alert('Error: ' + e));
    }
}

function resolveAlert(alertId) {
    const boardId = document.querySelector('[data-board-id]').getAttribute('data-board-id');
    
    if (confirm('Mark this alert as resolved?')) {
        fetch('/kanban/board/' + boardId + '/alerts/' + alertId + '/resolve/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                location.reload();
            } else {
                alert('Error: ' + (d.error || d.message));
            }
        })
        .catch(e => alert('Error: ' + e));
    }
}
