from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import Category, Item, ItemImage
from .stripe_service import create_payment_link_for_item


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'item_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    def item_count(self, obj):
        """Display number of items in this category."""
        return obj.items.count()
    item_count.short_description = 'Items'


class ItemImageInline(admin.TabularInline):
    """Inline admin for item images with thumbnail preview."""
    model = ItemImage
    extra = 1
    fields = ['image_preview', 'image', 'sort_order', 'is_primary']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Display thumbnail preview of image."""
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                obj.image.url
            )
        return '(No image)'
    image_preview.short_description = 'Preview'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price_amount', 'currency', 'status', 'created_at', 'payment_link_status']
    list_filter = ['status', 'category', 'currency', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'stripe_payment_link_id',
        'stripe_payment_link_url',
        'stripe_product_id',
        'stripe_price_id',
        'created_at',
        'updated_at',
        'sold_at',
    ]
    fieldsets = (
        ('Item Information', {
            'fields': ('title', 'slug', 'description', 'category', 'price_amount', 'currency', 'status')
        }),
        ('Stripe Integration', {
            'fields': (
                'stripe_payment_link_id',
                'stripe_payment_link_url',
                'stripe_product_id',
                'stripe_price_id',
            ),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'sold_at'),
            'classes': ('collapse',),
        }),
    )
    inlines = [ItemImageInline]
    
    def payment_link_status(self, obj):
        """Display payment link status."""
        if obj.stripe_payment_link_url:
            return format_html(
                '<a href="{}" target="_blank">View Link</a>',
                obj.stripe_payment_link_url
            )
        return 'Not created'
    payment_link_status.short_description = 'Payment Link'
    
    def save_model(self, request, obj, form, change):
        """
        Create Stripe Payment Link when item is saved.
        Only create if it doesn't already exist.
        
        The Payment Link will be automatically deactivated after the first
        successful payment via webhook to enforce single-payment limit.
        """
        # Save the item first so it has an ID
        super().save_model(request, obj, form, change)
        
        # Create Payment Link if it doesn't exist and item has required fields
        if not obj.stripe_payment_link_id and obj.title and obj.price_amount:
            try:
                payment_link_id, payment_link_url, product_id, price_id = \
                    create_payment_link_for_item(obj)
                obj.stripe_payment_link_id = payment_link_id
                obj.stripe_payment_link_url = payment_link_url
                obj.stripe_product_id = product_id
                obj.stripe_price_id = price_id
                obj.save()  # Save again with Stripe fields
                messages.success(
                    request,
                    f'Stripe Payment Link created successfully. '
                    f'Link: {payment_link_url}'
                )
            except Exception as e:
                messages.error(
                    request,
                    f'Error creating Stripe Payment Link: {str(e)}. '
                    f'Item saved but payment link not created.'
                )


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ['item', 'image_preview', 'sort_order', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['item__title']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Display thumbnail preview of image."""
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; object-fit: contain;" />',
                obj.image.url
            )
        return '(No image)'
    image_preview.short_description = 'Preview'
