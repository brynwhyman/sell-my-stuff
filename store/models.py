from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal
from .validators import validate_image_file_type, validate_image_file_size


class Category(models.Model):
    """
    Represents a category for items.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)  # For ordering categories
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Represents a single personal item for sale.
    Each item is unique and can only be sold once.
    """
    STATUS_LIVE = 'LIVE'
    STATUS_SOLD = 'SOLD'
    STATUS_CHOICES = [
        (STATUS_LIVE, 'Live'),
        (STATUS_SOLD, 'Sold'),
    ]
    
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    price_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='NZD')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_LIVE
    )
    
    # Stripe Payment Link fields
    stripe_payment_link_id = models.CharField(max_length=255, blank=True)
    stripe_payment_link_url = models.URLField(blank=True)
    stripe_product_id = models.CharField(max_length=255, blank=True)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for this item's detail page."""
        from django.urls import reverse
        return reverse('store:item_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Item.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    @property
    def is_live(self):
        """Check if item is live and available for purchase."""
        return self.status == self.STATUS_LIVE
    
    @property
    def primary_image(self):
        """Get the primary image, or first image by sort_order."""
        # First try to find explicitly marked primary image
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        # Fall back to lowest sort_order
        return self.images.order_by('sort_order', 'created_at').first()


class ItemImage(models.Model):
    """
    Represents an image for an item.
    Items can have multiple images with ordering and primary designation.
    """
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='items/',
        validators=[validate_image_file_type, validate_image_file_size]
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['item', 'sort_order']),
        ]
    
    def __str__(self):
        return f"{self.item.title} - Image {self.sort_order}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per item."""
        super().save(*args, **kwargs)
        # If this is marked as primary, unmark others
        if self.is_primary:
            ItemImage.objects.filter(
                item=self.item,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
