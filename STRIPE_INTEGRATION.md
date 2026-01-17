# Stripe Integration Documentation

This document describes the Stripe Payment Links integration for the Sell My Stuff ecommerce site.

## Architecture Overview

- **Payment Method**: Stripe Payment Links (not Checkout Sessions)
- **Enforcement**: Server-side via webhooks (not client-side)
- **Source of Truth**: `checkout.session.completed` webhook events
- **Single Payment Enforcement**: Payment Links are deactivated after first successful payment

## Payment Link Creation

When an item is created in Django admin:

1. **Stripe Product** is created with:
   - Name: item title
   - Description: item description (truncated to 500 chars)
   - Metadata: `item_id` (internal Django item ID)

2. **Stripe Price** is created with:
   - Product: the created product ID
   - Amount: item price in cents
   - Currency: item currency (lowercase)
   - Type: one-time payment (not recurring)

3. **Stripe Payment Link** is created with:
   - Line item: the created price, quantity 1
   - Metadata: `item_id` (internal Django item ID)

4. **Database Storage**:
   - `stripe_payment_link_id`: Payment Link ID
   - `stripe_payment_link_url`: Payment Link URL (for Buy button)
   - `stripe_product_id`: Product ID
   - `stripe_price_id`: Price ID (used for webhook item identification)

## Webhook Handling

### Endpoint
- URL: `/store/webhooks/stripe/`
- Method: POST
- CSRF: Exempt (required for Stripe webhooks)

### Signature Verification
- Uses `stripe.Webhook.construct_event()` with webhook signing secret
- Rejects requests with invalid signatures
- Returns 400 for invalid payloads or signatures

### Event Handling
- **Listens for**: `checkout.session.completed`
- **Other events**: Ignored (as per requirements)

### Item Identification Strategy

The webhook handler uses a two-step strategy to identify items:

1. **Primary**: Check session metadata for `item_id`
   - If available and valid, use it directly

2. **Fallback**: Look up by `price_id` from line items
   - Retrieve line items from checkout session
   - Extract `price_id` from first line item
   - Look up item in database by `stripe_price_id`

This ensures reliability even if metadata isn't available in the session object.

### Sale Processing

When `checkout.session.completed` is received:

1. **Identify item** using the strategy above
2. **Mark item as SOLD** (idempotent):
   - Only updates if status is not already SOLD
   - Sets `status = 'SOLD'`
   - Records `sold_at` timestamp (only if not already set)
3. **Deactivate Payment Link**:
   - Calls `stripe.PaymentLink.modify(payment_link_id, active=False)`
   - Prevents further payments on this link
   - If deactivation fails, item is still marked SOLD (webhook is source of truth)

### Idempotency

The webhook handler is fully idempotent:
- Safe to process the same event multiple times
- Checks item status before updating
- Handles duplicate webhooks gracefully
- Never charges or modifies Stripe objects

## Frontend Behavior

### Buy Button Display

- **Shown when**:
  - `item.status == 'LIVE'` AND
  - `item.stripe_payment_link_url` exists

- **Hidden when**:
  - `item.status == 'SOLD'` (shows "Sold" badge instead)

### No Client-Side Validation

- Frontend does NOT validate payment status
- Frontend does NOT check if item is available
- All validation is server-side via webhooks
- Buy button simply links to Stripe Payment Link URL

## Error Handling

### Webhook Errors

- **Invalid signature**: Returns 400, event not processed
- **Invalid payload**: Returns 400, event not processed
- **Item not found**: Logs error, returns 200 (prevents webhook retries)
- **Stripe API errors**: Logs error, returns 200 (prevents webhook retries)
- **Already SOLD**: Handled idempotently, returns 200

### Payment Link Creation Errors

- If Payment Link creation fails, item is still saved
- Admin shows error message
- Item can be manually updated later

### Payment Link Deactivation Errors

- If deactivation fails, item is still marked SOLD
- Webhook is source of truth, not Payment Link status
- Payment Link may remain active, but item is marked SOLD in database

## Important Notes

1. **Payment Links don't have a direct "max_payments" parameter**
   - We enforce single payment by deactivating the link after first sale
   - This is done via webhook, not at Payment Link creation time

2. **Webhooks can arrive late or multiple times**
   - Handler is idempotent to handle duplicates
   - Late webhooks are processed correctly (item may already be SOLD)

3. **Never trust client redirects**
   - Success/cancel URLs are not used for payment verification
   - Only webhook events are trusted

4. **Metadata accessibility**
   - `item_id` is stored in Product and Payment Link metadata
   - May not always be available in checkout session metadata
   - Fallback to `price_id` lookup ensures reliability

## Testing

### Local Development

Use Stripe CLI to forward webhooks:
```bash
stripe listen --forward-to localhost:8000/store/webhooks/stripe/
```

### Webhook Testing

1. Create an item in admin (Payment Link created automatically)
2. Use Stripe test card: `4242 4242 4242 4242`
3. Complete payment on Payment Link
4. Verify webhook is received and item is marked SOLD
5. Verify Payment Link is deactivated

## Security

- Webhook signatures are always verified
- CSRF protection disabled only for webhook endpoint (required)
- No sensitive data in frontend
- All payment processing happens on Stripe's servers
