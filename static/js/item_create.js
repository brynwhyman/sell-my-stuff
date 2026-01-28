/**
 * JavaScript for mobile item creation form.
 * Handles image selection and preview.
 *
 * We let the browser submit the form normally so Django redirects
 * to the item detail page after a successful save.
 */

// Global list of selected images
var selectedImages = [];

/**
 * Sync selectedImages into the file input so Django receives them.
 */
function syncInputFiles() {
    const input = document.getElementById('images-input');
    if (!input) return;

    const dataTransfer = new DataTransfer();
    selectedImages.forEach(file => {
        dataTransfer.items.add(file);
    });

    input.files = dataTransfer.files;
}

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

    selectedImages.forEach((file, index) => {
        const reader = new FileReader();

        reader.onload = function(e) {
            const previewItem = document.createElement('div');
            previewItem.className = 'image-preview-item';
            previewItem.dataset.index = index;

            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = 'Preview';

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-btn';
            removeBtn.innerHTML = '×';
            removeBtn.onclick = function(ev) {
                ev.stopPropagation();
                removeImage(index);
            };
            removeBtn.setAttribute('aria-label', 'Remove image');

            const primaryBadge = document.createElement('span');
            primaryBadge.className = 'primary-badge';
            primaryBadge.textContent = index === 0 ? 'Main' : '';

            previewItem.appendChild(img);
            previewItem.appendChild(removeBtn);
            if (index === 0) {
                previewItem.appendChild(primaryBadge);
            }

            // Click to set as primary
            previewItem.onclick = function() {
                setPrimaryImage(index);
            };

            container.appendChild(previewItem);
        };

        reader.readAsDataURL(file);
    });
}

/**
 * Handle new files selected from the input.
 */
function handleFilesSelected(files) {
    const validFiles = [];

    Array.from(files).forEach(file => {
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

        validFiles.push(file);
    });

    // Add to global list and sync input
    selectedImages = selectedImages.concat(validFiles);
    syncInputFiles();
    updateImagePreview();
}

/**
 * Remove an image from selection.
 */
function removeImage(index) {
    selectedImages.splice(index, 1);
    syncInputFiles();
    updateImagePreview();
}

/**
 * Set an image as primary (move to first position).
 */
function setPrimaryImage(index) {
    if (index === 0) return;

    const image = selectedImages.splice(index, 1)[0];
    selectedImages.unshift(image);
    syncInputFiles();
    updateImagePreview();
}

/**
 * Open camera on mobile (uses capture attribute).
 */
window.openCamera = function() {
    const input = document.getElementById('images-input');
    if (!input) return;
    input.setAttribute('capture', 'environment');
    input.click();
};

/**
 * Open gallery / file picker.
 */
window.openGallery = function() {
    const input = document.getElementById('images-input');
    if (!input) return;
    input.removeAttribute('capture');
    input.click();
};

/**
 * Initialize on page load.
 */
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('images-input');
    if (input) {
        input.addEventListener('change', function(event) {
            handleFilesSelected(event.target.files);
            // Clear the input so selecting the same file again works
            event.target.value = '';
        });
    }
});
