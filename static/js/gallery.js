/**
 * Image Gallery Functionality
 * Allows clicking thumbnails to change the main image
 */

document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.querySelector('.item-image-main img');
    const thumbnails = document.querySelectorAll('.gallery-thumbnail');
    
    if (!mainImage || thumbnails.length === 0) {
        return; // No gallery on this page
    }
    
    // Set first thumbnail as active
    if (thumbnails.length > 0) {
        thumbnails[0].classList.add('active');
    }
    
    // Handle thumbnail clicks
    thumbnails.forEach(function(thumbnail) {
        thumbnail.addEventListener('click', function() {
            const newSrc = this.src;
            
            // Update main image with fade effect
            mainImage.style.opacity = '0';
            
            setTimeout(function() {
                mainImage.src = newSrc;
                mainImage.classList.add('fade-in');
                mainImage.style.opacity = '1';
                
                // Remove fade-in class after animation
                setTimeout(function() {
                    mainImage.classList.remove('fade-in');
                }, 300);
            }, 150);
            
            // Update active thumbnail
            thumbnails.forEach(function(thumb) {
                thumb.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
    
    // Handle keyboard navigation for thumbnails
    thumbnails.forEach(function(thumbnail, index) {
        thumbnail.setAttribute('tabindex', '0');
        thumbnail.setAttribute('role', 'button');
        thumbnail.setAttribute('aria-label', 'View image ' + (index + 1));
        
        thumbnail.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
});
