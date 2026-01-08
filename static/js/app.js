/**
 * WonderTales - Frontend JavaScript
 * Minimal JavaScript for compatibility with new templates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Theme management is handled in base.html
    // Form interactions are handled in individual templates
    
    // Add any global functionality here if needed
    console.log('WonderTales loaded successfully!');
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add print functionality
    window.printStory = function() {
        window.print();
    };
});