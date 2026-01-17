# Sell My Stuff - Personal Items Ecommerce Site

A Django-based ecommerce site for selling one-off personal items using Stripe Payment Links.

## Features

- Item listing and detail pages (shows both live and sold items)
- Stripe Payment Links integration - each item gets its own payment link
- Webhook-based sales tracking - items marked as SOLD automatically via Stripe webhooks
- Admin interface for creating items with photo uploads
- Automatic Stripe Product/Price/Payment Link creation on item creation

## Architecture

- **No shopping cart** - each item is purchased individually
- **One item = one sale** - items can only be sold once
- **Stripe Payment Links** - customers are redirected to Stripe-hosted payment pages
- **Webhook-driven** - Stripe webhooks mark items as SOLD (source of truth)
- **Sold items remain visible** - items stay on the site but are clearly marked as Sold

## Quick Start

**For detailed step-by-step instructions, see [TESTING_GUIDE.md](TESTING_GUIDE.md)**

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the project root
   - Add your settings (see `.env.example` for format)
   - Required: `SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
   - Optional: PostgreSQL settings (see [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md))

4. **Set up database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start the server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the site:**
   - Frontend: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Documentation

This project includes comprehensive documentation:

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Step-by-step guide for testing the site locally (non-developer friendly)
- **[STRIPE_INTEGRATION.md](STRIPE_INTEGRATION.md)** - Detailed documentation of Stripe Payment Links integration
- **[STRIPE_WEBHOOK_SETUP.md](STRIPE_WEBHOOK_SETUP.md)** - Complete guide for setting up Stripe webhooks (local and production)
- **[POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)** - Guide for setting up PostgreSQL database
- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - General production deployment guide and checklist
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Step-by-step guide for deploying to Render (POC deployment)
- **[RENDER_SPECIFIC.md](RENDER_SPECIFIC.md)** - Lists Render-specific files that can be deleted when moving platforms

## Stripe Configuration

### Step 1: Get Your Stripe API Keys

1. Sign up at https://stripe.com (if you haven't already)
2. Go to Dashboard → Developers → API keys
3. Copy your **Secret Key** (starts with `sk_test_` for test mode)
4. Add it to `.env` as `STRIPE_SECRET_KEY`

### Step 2: Set Up Webhooks for Local Development

**For local testing, use Stripe CLI (no domain needed!):**

1. **Install Stripe CLI:**
   ```bash
   # On Mac:
   brew install stripe/stripe-cli/stripe
   ```
   Or download from: https://github.com/stripe/stripe-cli/releases

2. **Login to Stripe:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to your local server:**
   ```bash
   stripe listen --forward-to localhost:8000/store/webhooks/stripe/
   ```
   This will output a webhook secret (starts with `whsec_`)

4. **Add the webhook secret to `.env`:**
   ```
   STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
   ```

5. **Restart your Django server** to pick up the new environment variable

**Keep the `stripe listen` command running** in a separate terminal while testing.

### Step 3: Set Up Webhooks for Production (Later)

When you deploy your site to a real domain:

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/store/webhooks/stripe/`
3. Select event: `checkout.session.completed`
4. Copy the webhook signing secret to your production `.env` as `STRIPE_WEBHOOK_SECRET`

**See [STRIPE_WEBHOOK_SETUP.md](STRIPE_WEBHOOK_SETUP.md) for detailed instructions.**

**For production deployment, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)**

## Project Structure

```
sellmystuff/
├── sellmystuff/       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/             # Main store app
│   ├── models.py      # Item, ItemImage models
│   ├── views.py       # Views for listing and detail
│   ├── urls.py        # URL routing
│   ├── admin.py       # Admin with Stripe integration
│   ├── stripe_service.py  # Stripe Payment Link creation
│   └── webhooks.py    # Stripe webhook handlers
├── templates/         # HTML templates
├── static/           # CSS, JS, images
└── manage.py
```

## Usage

### Creating Items

1. Log into Django admin
2. Go to Store → Categories → Add Category (create categories first)
3. Go to Store → Items → Add Item
4. Fill in:
   - Title
   - Description
   - Category (optional)
   - Price
   - Currency (defaults to NZD)
5. Upload one or more images (set sort_order and is_primary)
6. Save - a Stripe Payment Link will be created automatically

### How Sales Work

1. Customer views item on public site
2. Clicks "Buy Now" button (only shown for LIVE items)
3. Redirected to Stripe Payment Link
4. Completes payment on Stripe
5. Stripe sends webhook to `/store/webhooks/stripe/`
6. Item is automatically marked as SOLD
7. Item remains visible but shows "Sold" badge

**See [STRIPE_INTEGRATION.md](STRIPE_INTEGRATION.md) for technical details.**

## Important Notes

- **Payment Links are created automatically** when you save a new item in admin
- **Webhooks are the source of truth** - items are marked SOLD via webhook, not frontend logic
- **Sold items stay visible** - they remain on the site with a "Sold" badge
- **One payment per item** - the webhook ensures items can only be sold once
- **No cart functionality** - each item is purchased individually

## Development Notes

- **Database**: Uses SQLite by default for local development. PostgreSQL is recommended for production (see [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md))
- **Static Files**: Configured with WhiteNoise for efficient static file serving in production. Run `python manage.py collectstatic` before deploying.
- **Security**: Production security settings are automatically enabled when `DEBUG=False` (HTTPS, security headers, HSTS, etc.) - see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Deployment**: For Render deployment, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md). For general production deployment, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- Media files stored in `media/` directory
- Stripe Payment Links don't have a built-in "max payments" option, but the webhook ensures items are only sold once
- The site shows all items (live and sold) - sold items are clearly marked
- Items can be categorized and filtered by category on the public site