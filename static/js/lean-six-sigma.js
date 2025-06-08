// Simple Lean Six Sigma Graphics Enhancement
document.addEventListener('DOMContentLoaded', function() {
    // Function to enhance the Six Sigma SVG display
    function enhanceSixSigmaDisplay() {
        const svgContainer = document.querySelector('.six-sigma-image-container');
        const svgImage = svgContainer?.querySelector('img');
        const featureItems = document.querySelectorAll('.lean-six-sigma-section .d-flex');
        
        if (!svgContainer || !svgImage) return;
        
        // Add event listeners for improved interaction
        svgImage.addEventListener('load', function() {
            // Add loaded class for animation
            svgContainer.classList.add('svg-loaded');
            svgImage.style.opacity = 1;
        });
        
        // Fallback handling enhancement
        svgImage.addEventListener('error', function(e) {
            console.log('SVG failed to load, trying fallback image...');
        });
        
        // Add animation to feature items
        if (featureItems && featureItems.length) {
            featureItems.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateY(15px)';
                item.style.transition = `all 0.5s ease ${index * 0.1 + 0.2}s`;
                
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, 100);
            });
        }
    }
    
    // Add intersection observer for reveal animations
    const section = document.querySelector('.lean-six-sigma-section');
    if (section) {
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                section.classList.add('visible');
                enhanceSixSigmaDisplay();
                observer.unobserve(entries[0].target);
            }
        }, { threshold: 0.2 });
        
        observer.observe(section);
    }
});
