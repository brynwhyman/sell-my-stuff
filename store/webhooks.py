"""
Stripe webhook handlers.

Webhooks are the source of truth for completed sales.
All payment verification happens server-side via verified webhook events.
"""
import logging
import stripe
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .models import Item
from .stripe_service import deactivate_payment_link

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    
    Verifies webhook signature using Stripe's signing secret.
    Listens for checkout.session.completed to mark items as SOLD.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponseBadRequest('Webhook secret not configured')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponseBadRequest('Invalid payload')
    except stripe.error.SignatureVerificationError:
        # Invalid signature - reject the request
        return HttpResponseBadRequest('Invalid signature')
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    # Other event types are ignored as per requirements
    
    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """
    Handle checkout.session.completed event.
    
    This is the source of truth for completed sales.
    Mark the item as SOLD idempotently and deactivate the Payment Link.
    
    Item identification strategy:
    1. First try to get item_id from session metadata (if available)
    2. Fall back to looking up by price_id from line items
    """
    item = None
    item_id = None
    
    # Strategy 1: Try to get item_id from session metadata
    # Metadata may be available if passed through Payment Link
    if 'metadata' in session and 'item_id' in session['metadata']:
        item_id = session['metadata']['item_id']
        try:
            item = Item.objects.get(id=item_id)
        except (Item.DoesNotExist, ValueError):
            # item_id not found or invalid, continue to strategy 2
            logger.warning(f"Item with id {item_id} from metadata not found, trying price_id lookup")
            item = None
    
    # Strategy 2: Look up by price_id from line items
    # This is the most reliable method as price_id is always available
    if item is None:
        try:
            # Retrieve line items for this checkout session
            line_items = stripe.checkout.Session.list_line_items(
                session['id'],
                limit=1
            )
            
            if not line_items.data or not line_items.data[0].price:
                # No line items or price information - cannot identify item
                return
            
            price_id = line_items.data[0].price.id
            
            # Find item by price_id
            try:
                item = Item.objects.get(stripe_price_id=price_id)
            except Item.DoesNotExist:
                # Item not found - cannot process this webhook
                logger.error(f"Item with price_id {price_id} not found in database. Webhook session: {session.get('id', 'unknown')}")
                return
            except Item.MultipleObjectsReturned:
                # Shouldn't happen (one price per item), but handle gracefully
                item = Item.objects.filter(stripe_price_id=price_id).first()
                if not item:
                    return
                    
        except stripe.error.StripeError as e:
            # Stripe API error - cannot retrieve line items
            logger.error(f"Stripe API error retrieving line items for session {session.get('id', 'unknown')}: {str(e)}")
            return
    
    # At this point, we have an item or we've returned early
    if item is None:
        return
    
    # Mark item as SOLD idempotently
    # This is safe to call multiple times - it only updates if needed
    if item.status != Item.STATUS_SOLD:
        item.status = Item.STATUS_SOLD
        if not item.sold_at:
            item.sold_at = timezone.now()
        item.save()
        
        # Deactivate the Payment Link to prevent further payments
        # This enforces the "one payment per item" requirement
        if item.stripe_payment_link_id:
            deactivate_payment_link(item.stripe_payment_link_id)
        
        # Extract buyer information for notifications
        customer_details = session.get('customer_details', {}) or {}
        buyer_name = customer_details.get('name') or 'Customer'
        buyer_email = customer_details.get('email') or session.get('customer_email') or ''
        buyer_phone = customer_details.get('phone') or ''
        
        # Send email notifications (if email is configured)
        send_sale_notifications(item, buyer_name, buyer_email, buyer_phone)
        logger.info(f"Item '{item.title}' sold to {buyer_name} ({buyer_email}, {buyer_phone})")
    
    # If item is already SOLD, this webhook is a duplicate
    # This is expected and handled gracefully (idempotent)


def send_sale_notifications(item, buyer_name, buyer_email, buyer_phone=''):
    """
    Send email notifications to buyer and admin when an item is sold.
    
    Args:
        item: The Item object that was sold
        buyer_name: Name of the buyer
        buyer_email: Email address of the buyer
        buyer_phone: Phone number of the buyer (optional)
    """
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        logger.warning("Email not configured - skipping sale notifications")
        return
    
    # Format sender with friendly name
    from_email = f"Julia and Bryn <{settings.DEFAULT_FROM_EMAIL}>"
    
    # Email to buyer (if email provided)
    if buyer_email:
        try:
            buyer_subject = f"Thanks for your purchase: {item.title}"
            buyer_message = f"""Hello {buyer_name},

Thanks for buying our stuff!

Item: {item.title}
Price: ${item.price_amount} {item.currency}

Next step: Please text Julia on 021 649 477 to arrange pickup.

Thanks
J&B
"""
            send_mail(
                buyer_subject,
                buyer_message,
                from_email,
                [buyer_email],
                fail_silently=False,
            )
            logger.info(f"Buyer notification email sent to {buyer_email}")
        except Exception as e:
            logger.error(f"Failed to send buyer notification email: {str(e)}")
    
    # Email to admin
    admin_email = settings.ADMIN_EMAIL or settings.DEFAULT_FROM_EMAIL
    if admin_email:
        try:
            admin_subject = f"Item Sold: {item.title}"
            admin_message = f"""A new sale has been completed!

Item: {item.title}
Price: ${item.price_amount} {item.currency}
Sold at: {item.sold_at.strftime('%Y-%m-%d %H:%M:%S') if item.sold_at else 'N/A'}

Buyer Information:
Name: {buyer_name}
Email: {buyer_email or 'Not provided'}
Phone: {buyer_phone or 'Not provided'}

Reminder: buyer has been asked to text Julia on 021 649 477 to arrange pickup.

View in admin: https://sell-my-stuff.onrender.com/admin/store/item/{item.id}/
"""
            send_mail(
                admin_subject,
                admin_message,
                from_email,
                [admin_email],
                fail_silently=False,
            )
            logger.info(f"Admin notification email sent to {admin_email}")
        except Exception as e:
            logger.error(f"Failed to send admin notification email: {str(e)}")


