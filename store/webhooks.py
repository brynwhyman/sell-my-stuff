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
    
    # If item is already SOLD, this webhook is a duplicate
    # This is expected and handled gracefully (idempotent)
