/**
 * Infinite Scroll Functionality
 * Loads more items as user scrolls near the bottom of the page
 */

(function() {
    'use strict';

    // Configuration
    const SCROLL_THRESHOLD = 200; // Load when 200px from bottom
    const DEBOUNCE_DELAY = 100; // Debounce scroll events

    // State
    let isLoading = false;
    let hasMoreItems = true;
    let currentPage = 1;
    let scrollTimeout = null;

    // Get current category from URL
    function getCategoryFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('category') || '';
    }

    // Build URL for fetching next page
    function buildNextPageURL(page) {
        const url = new URL(window.location.href);
        url.searchParams.set('page', page);
        const category = getCategoryFromURL();
        if (category) {
            url.searchParams.set('category', category);
        }
        return url.toString();
    }

    // Create item card HTML
    function createItemCard(item) {
        const imageHTML = item.primary_image_url
            ? `<img src="${escapeHtml(item.primary_image_url)}" alt="${escapeHtml(item.title)}" class="item-image">`
            : '<div class="item-image-placeholder">No Image</div>';

        const soldBadge = item.is_sold
            ? '<span class="item-badge item-badge-sold">Sold</span>'
            : '';

        const cardClass = item.is_sold ? 'item-card item-card-sold' : 'item-card';

        return `
            <div class="${cardClass}">
                <a href="${escapeHtml(item.detail_url)}">
                    <div class="item-image-container">
                        ${imageHTML}
                    </div>
                    <div class="item-card-content">
                        <h3>${escapeHtml(item.title)}</h3>
                        <p class="item-price">$${escapeHtml(item.price_amount)}</p>
                        ${soldBadge}
                    </div>
                </a>
            </div>
        `;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Show loading spinner
    function showLoadingSpinner() {
        const spinner = document.getElementById('infinite-scroll-spinner');
        if (spinner) {
            spinner.style.display = 'flex';
        }
    }

    // Hide loading spinner
    function hideLoadingSpinner() {
        const spinner = document.getElementById('infinite-scroll-spinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    }

    // Show "no more items" message
    function showNoMoreItems() {
        const message = document.getElementById('infinite-scroll-end');
        if (message) {
            message.style.display = 'block';
        }
    }

    // Hide "no more items" message
    function hideNoMoreItems() {
        const message = document.getElementById('infinite-scroll-end');
        if (message) {
            message.style.display = 'none';
        }
    }

    // Load next page of items
    async function loadNextPage() {
        if (isLoading || !hasMoreItems) {
            return;
        }

        isLoading = true;
        showLoadingSpinner();
        hideNoMoreItems();

        try {
            const nextPage = currentPage + 1;
            const url = buildNextPageURL(nextPage);

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.items && data.items.length > 0) {
                const itemGrid = document.querySelector('.item-grid');
                if (itemGrid) {
                    // Append new items
                    data.items.forEach(function(item) {
                        const cardHTML = createItemCard(item);
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = cardHTML.trim();
                        itemGrid.appendChild(tempDiv.firstElementChild);
                    });

                    // Update state
                    currentPage = nextPage;
                    hasMoreItems = data.has_next;

                    // Update URL without reload (for bookmarking)
                    if (data.has_next) {
                        window.history.pushState(
                            { page: nextPage },
                            '',
                            url
                        );
                    }
                }
            } else {
                hasMoreItems = false;
            }

            if (!hasMoreItems) {
                showNoMoreItems();
            }
        } catch (error) {
            console.error('Error loading more items:', error);
            // Show error message to user
            const errorMsg = document.getElementById('infinite-scroll-error');
            if (errorMsg) {
                errorMsg.style.display = 'block';
                errorMsg.textContent = 'Failed to load more items. Please try again.';
            }
        } finally {
            isLoading = false;
            hideLoadingSpinner();
        }
    }

    // Check if user is near bottom of page
    function checkScrollPosition() {
        if (isLoading || !hasMoreItems) {
            return;
        }

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;

        const distanceFromBottom = documentHeight - (scrollTop + windowHeight);

        if (distanceFromBottom < SCROLL_THRESHOLD) {
            loadNextPage();
        }
    }

    // Debounced scroll handler
    function handleScroll() {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(checkScrollPosition, DEBOUNCE_DELAY);
    }

    // Initialize infinite scroll
    function init() {
        const itemGrid = document.querySelector('.item-grid');
        if (!itemGrid) {
            return; // No item grid on this page
        }

        // Check if there are more items initially
        const paginationInfo = document.querySelector('.pagination');
        if (paginationInfo) {
            // Check if there's a "next" link to determine if more items exist
            const hasNextLink = paginationInfo.querySelector('a[href*="page="]');
            hasMoreItems = !!hasNextLink;
        } else {
            // No pagination info means either no items or only one page
            // Check if we have items - if yes and no pagination, assume no more items
            const items = itemGrid.querySelectorAll('.item-card');
            // If we have exactly paginate_by items (12), there might be more
            // We'll let the first scroll check determine this
            hasMoreItems = items.length >= 12; // Assume more if we have a full page
        }

        // Set up scroll listener
        window.addEventListener('scroll', handleScroll, { passive: true });

        // Check initial scroll position (in case page is already scrolled)
        checkScrollPosition();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
