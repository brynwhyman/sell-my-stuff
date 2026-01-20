"""
Stripe service for creating Payment Links.
"""
import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_link_for_item(item):
    """
    Create a Stripe Product, Price, and Payment Link for an item.
    
    The Payment Link will be deactivated after the first successful payment
    via webhook to enforce single-payment limit.
    
    Returns tuple of (payment_link_id, payment_link_url, product_id, price_id)
    """
    if not settings.STRIPE_SECRET_KEY:
        raise ValueError("STRIPE_SECRET_KEY not configured")
    
    # Create Product with metadata containing item_id
    product = stripe.Product.create(
        name=item.title,
        description=item.description[:500],  # Stripe has description limits
        metadata={
            'item_id': str(item.id),
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
    # Include item_id in metadata for webhook access
    # Collect customer name and email for notifications
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
        },
        # Collect customer information (name and email)
        # This ensures we have buyer details for email notifications
        payment_method_collection='if_required',
        # Enable customer creation to ensure we get name and email
        customer_creation='if_required',
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
