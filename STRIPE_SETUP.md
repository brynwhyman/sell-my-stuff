# Stripe Setup Guide

This guide explains how to set up Stripe for the Sell My Stuff ecommerce site.

## Overview

The site uses Stripe Payment Links for processing payments. When a customer completes a payment, Stripe sends a webhook to automatically mark the item as SOLD.

## Step 1: Get Your Stripe API Keys

1. Sign up at https://stripe.com (if you haven't already)
2. Go to Dashboard → Developers → API keys
3. Copy your **Secret Key** (starts with `sk_test_` for test mode, `sk_live_` for production)
4. Add it to your `.env` file as `STRIPE_SECRET_KEY`

## Step 2: Set Up Webhooks

### Local Development (Testing)

For testing on your local computer, use the Stripe CLI.

**Install Stripe CLI:**

On Mac:
```bash
brew install stripe/stripe-cli/stripe
```

On Windows:
Download from: https://github.com/stripe/stripe-cli/releases

**Login to Stripe:**
```bash
stripe login
```

**Forward webhooks to your local server:**

In a separate terminal (keep your Django server running), run:
```bash
stripe listen --forward-to localhost:8000/store/webhooks/stripe/
```

You'll see output like:
```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
```

**Add the webhook secret to `.env`:**
```
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Important:** Keep the `stripe listen` command running while testing. It forwards webhooks from Stripe to your local server.

### Production (Live Site)

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click **Add endpoint**
3. Enter your webhook URL: `https://yourdomain.com/store/webhooks/stripe/`
4. Under **Events to send**, select **`checkout.session.completed`**
5. Click **Add endpoint**
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add it to your production environment variables as `STRIPE_WEBHOOK_SECRET`

## Step 3: Test the Integration

1. Create an item in Django admin or via the web form
2. Go to the item detail page
3. Click "Buy Now" and complete payment using Stripe's test card: `4242 4242 4242 4242`
4. Check Django admin - the item should automatically be marked as SOLD

## Test Cards

Use these Stripe test cards for testing payments:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

For all test cards:
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any 5 digits (e.g., 12345)

## How It Works

### Payment Link Creation

When an item is created:

1. **Stripe Product** is created with:
   - Name: `#<item_id> - <item_title>` (includes item ID for easy identification)
   - Description: item description (truncated to 500 chars)
   - Metadata: `item_id`, `item_title`, `django_item_id`

2. **Stripe Price** is created with:
   - Product: the created product ID
   - Amount: item price in cents
   - Currency: item currency (lowercase)

3. **Stripe Payment Link** is created with:
   - Line item: the created price, quantity 1
   - Metadata: `item_id`
   - Phone number collection: enabled
   - Custom field: buyer name (required)
   - Invoice creation: enabled (for better tracking in Stripe Dashboard)

4. **Database Storage**:
   - `stripe_payment_link_id`: Payment Link ID
   - `stripe_payment_link_url`: Payment Link URL (for Buy button)
   - `stripe_product_id`: Product ID
   - `stripe_price_id`: Price ID (used for webhook item identification)

### Webhook Processing

When a payment is completed:

1. Stripe sends `checkout.session.completed` webhook to `/store/webhooks/stripe/`
2. Webhook signature is verified
3. Item is identified by `price_id` from the checkout session
4. Item is marked as SOLD (idempotent - safe to process multiple times)
5. Payment Link is deactivated to prevent further payments
6. Email notifications are sent to buyer and admin (if configured)

### Item Identification

The webhook handler identifies items using:

1. **Primary**: Check session metadata for `item_id`
2. **Fallback**: Look up by `price_id` from line items

This ensures reliability even if metadata isn't available.

## Email Notifications

The site can send email notifications when items are sold. Configure email settings in your `.env`:

```
EMAIL_HOST=smtp.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
ADMIN_EMAIL=admin@example.com
```

**Note:** Email is optional. The site will work without email configuration, but notifications won't be sent.

## Troubleshooting

### Webhook Not Received

1. Check webhook secret is correct in your `.env` file
2. Verify webhook URL is correct (no typos)
3. Check Stripe Dashboard → Webhooks → Your endpoint → Recent events
4. Look for errors in the webhook event details
5. Check Django server logs for webhook processing errors

### Webhook Returns 400 Error

- **Invalid signature**: Check that `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe
- **Invalid payload**: Usually means the webhook secret is wrong

### Item Not Marked as SOLD

1. Check webhook is being received: Look in Stripe Dashboard → Webhooks → Recent events
2. Check Django logs: Look for errors in your terminal where `runserver` is running
3. Verify price_id matches: The webhook looks up items by `stripe_price_id` - make sure this is set when creating items

### Local Development Issues

- **"Connection refused"**: Make sure Django server is running (`python manage.py runserver`)
- **"Webhook secret not configured"**: Make sure `STRIPE_WEBHOOK_SECRET` is in your `.env` file
- **No events showing**: Make sure `stripe listen` is running in a separate terminal

## Security Notes

- **Never commit `.env` file** to version control
- **Use different webhook secrets** for development and production
- **Webhook signatures are verified** - invalid signatures are rejected
- **Only process `checkout.session.completed` events** - other events are ignored

## Quick Reference

**Local Development:**
```bash
# Terminal 1: Run Django server
python manage.py runserver

# Terminal 2: Forward webhooks
stripe listen --forward-to localhost:8000/store/webhooks/stripe/
```

**Production:**
- Webhook URL: `https://yourdomain.com/store/webhooks/stripe/`
- Event: `checkout.session.completed`
- Get signing secret from Stripe Dashboard → Webhooks → Your endpoint
