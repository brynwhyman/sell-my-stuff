# Setting Up Stripe Webhooks

This guide explains how to set up Stripe webhooks for your ecommerce site.

## What Webhooks Do

Webhooks notify your site when a payment is completed. When a customer pays for an item, Stripe sends a webhook to your server, which automatically marks the item as SOLD.

## Option 1: Local Development (Testing)

For testing on your local computer, use the Stripe CLI.

### Step 1: Install Stripe CLI

**On Mac:**
```bash
brew install stripe/stripe-cli/stripe
```

**On Windows:**
Download from: https://github.com/stripe/stripe-cli/releases

**Or install via other methods:**
See: https://stripe.com/docs/stripe-cli

### Step 2: Login to Stripe CLI

```bash
stripe login
```

This will open your browser to authorize the CLI with your Stripe account.

### Step 3: Forward Webhooks to Your Local Server

In a **separate terminal window** (keep your Django server running in the first one), run:

```bash
stripe listen --forward-to localhost:8000/store/webhooks/stripe/
```

You'll see output like:
```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
```

### Step 4: Copy the Webhook Secret

Copy the `whsec_xxxxxxxxxxxxx` value and add it to your `.env` file:

```
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Important**: Keep the `stripe listen` command running while testing. It forwards webhooks from Stripe to your local server.

### Step 5: Test the Webhook

1. Create an item in Django admin
2. Complete a test payment using Stripe's test card: `4242 4242 4242 4242`
3. Watch the `stripe listen` terminal - you should see webhook events
4. Check your Django admin - the item should be marked as SOLD

## Option 2: Production (Live Site)

For a live website, set up webhooks in the Stripe Dashboard.

### Step 1: Get Your Webhook URL

Your webhook endpoint URL will be:
```
https://yourdomain.com/store/webhooks/stripe/
```

Replace `yourdomain.com` with your actual domain name.

### Step 2: Create Webhook in Stripe Dashboard

1. Go to https://dashboard.stripe.com
2. Click **Developers** → **Webhooks** (in the left sidebar)
3. Click **Add endpoint** (top right)
4. Enter your webhook URL: `https://yourdomain.com/store/webhooks/stripe/`
5. Under **Events to send**, click **Select events**
6. Check the box for: **`checkout.session.completed`**
7. Click **Add endpoint**

### Step 3: Get the Webhook Signing Secret

1. After creating the endpoint, click on it
2. Find the **Signing secret** section
3. Click **Reveal** to show the secret
4. Copy the secret (starts with `whsec_`)

### Step 4: Add to Your Production Environment

Add the webhook secret to your production `.env` file or environment variables:

```
STRIPE_WEBHOOK_SECRET=whsec_your_production_secret_here
```

### Step 5: Test the Webhook

1. In Stripe Dashboard → Webhooks → Your endpoint
2. Click **Send test webhook**
3. Select **`checkout.session.completed`**
4. Click **Send test webhook**
5. Check your Django admin to verify the item was marked as SOLD

## Testing Webhooks

### Test Cards

Use these Stripe test cards for testing payments:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

For all test cards:
- **Expiry**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any 5 digits (e.g., 12345)

### Verify Webhook is Working

1. Create an item in Django admin (status: LIVE)
2. Go to the item detail page on your site
3. Click "Buy Now" and complete payment with test card
4. Check Django admin - item should automatically change to SOLD
5. Check the `sold_at` timestamp is set

## Troubleshooting

### Webhook Not Received

1. **Check webhook secret is correct** in your `.env` file
2. **Verify webhook URL** is correct (no typos)
3. **Check Stripe Dashboard** → Webhooks → Your endpoint → Recent events
4. **Look for errors** in the webhook event details
5. **Check Django server logs** for webhook processing errors

### Webhook Returns 400 Error

- **Invalid signature**: Check that `STRIPE_WEBHOOK_SECRET` matches the secret from Stripe
- **Invalid payload**: Usually means the webhook secret is wrong

### Item Not Marked as SOLD

1. **Check webhook is being received**: Look in Stripe Dashboard → Webhooks → Recent events
2. **Check Django logs**: Look for errors in your terminal where `runserver` is running
3. **Verify price_id matches**: The webhook looks up items by `stripe_price_id` - make sure this is set when creating items

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
