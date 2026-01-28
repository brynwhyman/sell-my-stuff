/**
 * Lightweight image lightbox for item detail page.
 * Click/tap the main image to open fullscreen.
 */

document.addEventListener('DOMContentLoaded', function () {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox) return;

  const closeBtn = lightbox.querySelector('.lightbox-close');
  const lightboxImg = lightbox.querySelector('.lightbox-image');
  const mainContainer = document.querySelector('.item-image-main');
  const mainImg = document.querySelector('.item-image-main img');

  if (!closeBtn || !lightboxImg || !mainContainer || !mainImg) return;

  let previousBodyOverflow = '';

  function openLightbox(src, alt) {
    lightboxImg.src = src;
    lightboxImg.alt = alt || 'Image';
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');

    previousBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // Focus close for accessibility
    closeBtn.focus();
  }

  function closeLightbox() {
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImg.src = '';

    document.body.style.overflow = previousBodyOverflow;

    // Return focus to main image container
    mainContainer.focus();
  }

  // Open on click/tap
  mainContainer.addEventListener('click', function () {
    openLightbox(mainImg.src, mainImg.alt);
  });

  // Open on keyboard (Enter/Space)
  mainContainer.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openLightbox(mainImg.src, mainImg.alt);
    }
  });

  // Close button
  closeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    closeLightbox();
  });

  // Click outside image closes
  lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });

  // Escape closes
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && lightbox.classList.contains('open')) {
      closeLightbox();
    }
  });
});

