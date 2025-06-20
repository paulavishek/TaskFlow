console.log('=== Column Scroll Feature Debug ===');

// Check if configuration exists
if (typeof COLUMN_SCROLL_CONFIG !== 'undefined') {
    console.log('✅ COLUMN_SCROLL_CONFIG found:', COLUMN_SCROLL_CONFIG);
} else {
    console.log('❌ COLUMN_SCROLL_CONFIG not found');
}

// Check columns
const columns = document.querySelectorAll('.kanban-column-tasks');
console.log(`Found ${columns.length} columns`);

columns.forEach((column, index) => {
    const tasks = column.querySelectorAll('.kanban-task');
    const taskCount = tasks.length;
    const isScrollable = column.classList.contains('scrollable');
    
    console.log(`Column ${index + 1}: ${taskCount} tasks, scrollable: ${isScrollable}`);
    
    if (taskCount > 4) {
        console.log(`  → Should be scrollable (${taskCount} > 4)`);
        if (!isScrollable) {
            console.log('  ⚠️ Missing scrollable class');
        }
    } else {
        console.log(`  → Should NOT be scrollable (${taskCount} <= 4)`);
        if (isScrollable) {
            console.log('  ⚠️ Unnecessary scrollable class');
        }
    }
});

// Test manual trigger
if (typeof window.kanbanUpdateColumnScrolling === 'function') {
    console.log('✅ Global function available');
    console.log('Triggering manual update...');
    window.kanbanUpdateColumnScrolling();
} else {
    console.log('❌ Global function not available');
}
