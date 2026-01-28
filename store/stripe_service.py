"""
Stripe service for creating Payment Links.
"""
import stripe
from django.conf import settings
from decimal import Decimal


def create_payment_link_for_item(item):
    """
    Create a Stripe Product, Price, and Payment Link for an item.
    
    The Payment Link will be deactivated after the first successful payment
    via webhook to enforce single-payment limit.
    
    Returns tuple of (payment_link_id, payment_link_url, product_id, price_id)
    """
    if not settings.STRIPE_SECRET_KEY:
        raise ValueError("STRIPE_SECRET_KEY not configured")

    # Set API key at call time (avoids stale settings in long-running processes)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Create Product with metadata containing item_id
    # Include item ID in name for easy identification in Stripe Dashboard
    product = stripe.Product.create(
        name=f"#{item.id} - {item.title}",
        description=item.description[:500] if item.description else f"Item #{item.id}",
        metadata={
            'item_id': str(item.id),
            'item_title': item.title,
        }
    )
    
    # Create Price (one-time payment, not recurring)
    # Convert Decimal to integer cents
    amount_cents = int(item.price_amount * 100)
    
    price = stripe.Price.create(
        product=product.id,
        unit_amount=amount_cents,
        currency=item.currency.lower(),
    )
    
    # Create Payment Link
    # Collect customer name, email, and phone number for pickup coordination
    # Include item_id in metadata for webhook access
    # Note: Payment Links don't have a direct "max_payments" parameter.
    # We enforce single payment by deactivating the link after first sale via webhook.
    payment_link = stripe.PaymentLink.create(
        line_items=[
            {
                'price': price.id,
                'quantity': 1,
            }
        ],
        metadata={
            'item_id': str(item.id),
            'item_title': item.title,
            'django_item_id': str(item.id),  # Easy to spot in dashboard
        },
        # Collect phone number (for pickup coordination)
        phone_number_collection={
            'enabled': True,
        },
        # Collect customer details (name and email)
        custom_fields=[
            {
                'key': 'buyer_name',
                'label': {'type': 'custom', 'custom': 'Full Name'},
                'type': 'text',
            },
        ],
        # Add invoice creation for better tracking in Stripe Dashboard
        invoice_creation={
            'enabled': True,
            'invoice_data': {
                'description': f"Item #{item.id} - {item.title}",
                'metadata': {
                    'item_id': str(item.id),
                },
            },
        },
        # Enable Stripe automatic email receipts
        after_completion={
            'type': 'hosted_confirmation',
            'hosted_confirmation': {
                'custom_message': 'Thanks for your purchase! Please text Julia on 021 649 477 to arrange pickup.',
            },
        },
    )
    
    return (
        payment_link.id,
        payment_link.url,
        product.id,
        price.id,
    )


def deactivate_payment_link(payment_link_id):
    """
    Deactivate a Payment Link to prevent further payments.
    Called after an item is sold via webhook.
    """
    if not settings.STRIPE_SECRET_KEY:
        return
    
    try:
        stripe.PaymentLink.modify(
            payment_link_id,
            active=False
        )
    except stripe.error.StripeError:
        # If deactivation fails, log but don't raise
        # The item is already marked as SOLD, which is the source of truth
        pass
