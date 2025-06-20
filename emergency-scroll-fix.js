// Emergency fix for column scroll positioning issue
// Run this in your browser console to immediately fix the floating scroll bar

console.log('🔧 Running emergency column scroll fix...');

// Step 1: Force cleanup all existing scroll styles
function emergencyCleanup() {
    const columns = document.querySelectorAll('.kanban-column-tasks');
    const wrappers = document.querySelectorAll('.kanban-column');
    
    console.log(`Found ${columns.length} columns to cleanup`);
    
    // Clean all columns
    columns.forEach((column, i) => {
        column.classList.remove('scrollable');
        column.removeAttribute('style');
        console.log(`✓ Cleaned column ${i + 1}`);
    });
    
    // Clean all wrappers
    wrappers.forEach((wrapper, i) => {
        wrapper.classList.remove('has-scroll');
        wrapper.style.position = 'relative';
        wrapper.style.overflow = 'visible';
        console.log(`✓ Cleaned wrapper ${i + 1}`);
    });
    
    console.log('✓ All columns cleaned');
}

// Step 2: Reapply scrolling with adjusted threshold
function reapplyScrolling() {
    const columns = document.querySelectorAll('.kanban-column-tasks');
    
    columns.forEach((column, i) => {
        const tasks = column.querySelectorAll('.kanban-task');
        const taskCount = tasks.length;
        
        console.log(`Column ${i + 1}: ${taskCount} tasks`);
        
        if (taskCount > 5) { // Using threshold of 5 instead of 4
            console.log(`  → Making column ${i + 1} scrollable`);
            column.classList.add('scrollable');
            column.style.height = '400px';
            column.style.overflowY = 'auto';
            column.style.overflowX = 'hidden';
            column.style.position = 'relative';
            column.style.width = '100%';
            column.style.boxSizing = 'border-box';
            
            const wrapper = column.closest('.kanban-column');
            if (wrapper) {
                wrapper.classList.add('has-scroll');
                wrapper.style.position = 'relative';
                wrapper.style.overflow = 'visible';
            }
        }
    });
    
    console.log('✓ Scrolling reapplied');
}

// Execute the fix
emergencyCleanup();
setTimeout(reapplyScrolling, 100);

console.log('🎉 Emergency fix completed! Scroll bars should now be properly positioned.');
console.log('💡 If you still see issues, try refreshing the page.');
