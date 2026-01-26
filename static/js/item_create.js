/**
 * JavaScript for mobile item creation form.
 * Handles image selection, preview, and form submission.
 */

// Make selectedImages globally accessible
var selectedImages = [];

/**
 * Handle image selection from camera or gallery.
 * Make it globally accessible for inline handlers.
 */
window.handleImageSelection = function(event) {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Please select only image files');
            return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image is too large. Please use images under 5MB');
            return;
        }
        
        // Add to selected images
        selectedImages.push(file);
        updateImagePreview();
    });
    
    // Reset input so same file can be selected again
    event.target.value = '';
};

/**
 * Update the image preview grid.
 */
function updateImagePreview() {
    const container = document.getElementById('image-preview-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (selectedImages.length === 0) {
        return;
    }
    
    // Process each image with its index
    selectedImages.forEach((file, index) => {
        const reader = new FileReader();
        
        // Use closure to capture the correct index
        reader.onload = (function(fileIndex) {
            return function(e) {
                const previewItem = document.createElement('div');
                previewItem.className = 'image-preview-item';
                previewItem.dataset.index = fileIndex;
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = 'Preview';
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'remove-btn';
                removeBtn.innerHTML = '×';
                removeBtn.onclick = function() {
                    removeImage(fileIndex);
                };
                removeBtn.setAttribute('aria-label', 'Remove image');
                
                const primaryBadge = document.createElement('span');
                primaryBadge.className = 'primary-badge';
                primaryBadge.textContent = fileIndex === 0 ? 'Main' : '';
                
                previewItem.appendChild(img);
                previewItem.appendChild(removeBtn);
                if (fileIndex === 0) {
                    previewItem.appendChild(primaryBadge);
                }
                
                // Make clickable to set as primary
                previewItem.onclick = function(e) {
                    if (e.target !== removeBtn && e.target !== removeBtn.firstChild) {
                        setPrimaryImage(fileIndex);
                    }
                };
                
                container.appendChild(previewItem);
            };
        })(index);
        
        reader.readAsDataURL(file);
    });
}

/**
 * Remove an image from selection.
 */
function removeImage(index) {
    selectedImages.splice(index, 1);
    updateImagePreview();
}

/**
 * Set an image as primary (move to first position).
 */
function setPrimaryImage(index) {
    if (index === 0) return; // Already primary
    
    const image = selectedImages.splice(index, 1)[0];
    selectedImages.unshift(image);
    updateImagePreview();
}

/**
 * Update the form's file input with selected images.
 * Note: We'll use FormData in the form submission handler.
 */
function updateFormInput() {
    // The actual file upload will be handled via FormData on submit
    // This function is here for potential future use
}

/**
 * Initialize on page load.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Set up file inputs
    const cameraInput = document.getElementById('camera-input');
    const galleryInput = document.getElementById('gallery-input');
    
    if (cameraInput) {
        cameraInput.addEventListener('change', handleImageSelection);
    }
    
    if (galleryInput) {
        galleryInput.addEventListener('change', handleImageSelection);
    }
});
