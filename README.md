# Sell My Stuff

A Django-based ecommerce site for selling one-off personal items using Stripe Payment Links.

### Features and how it works

1. Customer views items nice and simple catalogue
2. Clicks "Buy Now" button (only shown for Live items)
3. Redirected to Stripe Payment Link
4. Completes payment on Stripe
5. Stripe sends webhook to `/store/webhooks/stripe/` to handle marking items as Sold and sending confirmation emails (if configured)
7. Item remains visible in catalogue but shows "Sold" badge (shows people what they're missing out on!)

### Other cool stuff
- Optimised for viewing and creating new items via mobile - there's a nice item upload form with mobile camera support for logged-in admins
- Catalogue has quick catagory filters, and shows sold items to 
- Use the Django admin to manage items in detail
- Items support multiple images and little feature to set the primary image

## Local Installation

### Prerequisites

- Python 3.9 or higher
- pip
- Stripe account (for testing)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sellmystuff
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root with the following variables:
   
   **Required:**
   ```bash
   SECRET_KEY=your-secret-key-here
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   ITEM_UPLOAD_PASSWORD=your-password-here
   ```
   
   **Optional (for email notifications):**
   ```bash
   EMAIL_HOST=smtp-relay.brevo.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-brevo-email@example.com
   EMAIL_HOST_PASSWORD=your-brevo-smtp-key
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your-verified-sender@yourdomain.com
   ADMIN_EMAIL=admin@example.com
   ```
   
   **Note:** See [STRIPE_SETUP.md](STRIPE_SETUP.md) for detailed instructions on getting your Stripe keys. See [Email Configuration](#email-configuration) below for email setup details.

5. **Set up database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the site:**
   - Frontend: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Environment Variables

### Required Variables

- **`SECRET_KEY`** - Django secret key for cryptographic signing. Generate a secure random string (e.g., use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`).
- **`STRIPE_SECRET_KEY`** - Your Stripe API secret key (starts with `sk_test_` for test mode, `sk_live_` for production). Get from Stripe Dashboard → Developers → API keys.
- **`STRIPE_WEBHOOK_SECRET`** - Webhook signing secret (starts with `whsec_`). See [STRIPE_SETUP.md](STRIPE_SETUP.md) for how to get this.
- **`ITEM_UPLOAD_PASSWORD`** - Password required to access the `/add-item/` web form for creating items via the mobile interface.

### Optional Variables (Email Configuration)

Email notifications are sent when items are sold. The site works without email configuration, but notifications won't be sent.

- **`EMAIL_HOST`** - SMTP server hostname (default: `smtp-relay.brevo.com` for Brevo)
- **`EMAIL_PORT`** - SMTP server port (default: `587`)
- **`EMAIL_USE_TLS`** - Enable TLS encryption (default: `True`)
- **`EMAIL_HOST_USER`** - SMTP username (your Brevo email or API key)
- **`EMAIL_HOST_PASSWORD`** - SMTP password (your Brevo SMTP key)
- **`DEFAULT_FROM_EMAIL`** - Email address that appears as the sender (must be verified in your email service)
- **`ADMIN_EMAIL`** - Email address to receive sale notifications (admin notifications)

See [Email Configuration](#email-configuration) below for setup instructions.

## Stripe Configuration

For detailed Stripe setup instructions, including webhook configuration for local development and production, see [STRIPE_SETUP.md](STRIPE_SETUP.md).

## Email Configuration

The site sends email notifications when items are sold:

1. **Buyer confirmation email** - Sent to the customer who purchased the item
2. **Admin notification email** - Sent to the admin email address with purchase details

### How Email Sending Works

When a payment is completed via Stripe webhook:

1. The webhook handler processes the `checkout.session.completed` event
2. Item is marked as SOLD
3. Email notifications are sent to both buyer and admin (if email is configured)
4. Emails include item details, buyer information (name, email, phone), and pickup instructions

### Setting Up Email (Using Brevo)

Brevo is a straight-foward service to use, mostly because they offer a free tier with 300 emails/day.

Note that you'll need your own domain to connect with Brevo.

1. **Sign up at Brevo:** https://www.brevo.com/
2. **Verify your sender email:**
   - Go to Settings → Senders
   - Add and verify the email address you want to use as the sender
3. **Get SMTP credentials:**
   - Go to Settings → SMTP & API
   - Copy your SMTP server, port, and credentials
4. **Add to `.env` file:**
   ```bash
   EMAIL_HOST=smtp-relay.brevo.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-brevo-email@example.com
   EMAIL_HOST_PASSWORD=your-brevo-smtp-key
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your-verified-sender@yourdomain.com
   ADMIN_EMAIL=admin@example.com
   ```

### Using Other Email Services

You can use any SMTP service (Gmail, SendGrid, Mailgun, etc.) by updating the email environment variables accordingly. The site uses Django's standard SMTP backend.

### Testing Email Locally

To test email sending:

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Subject',
    'Test message',
    settings.DEFAULT_FROM_EMAIL,
    [settings.ADMIN_EMAIL],
    fail_silently=False,
)
```

If email is configured correctly, this will send a test email and return `1` (success).

### Email Content

**Buyer Email:**
- Subject: "Thanks for your purchase: [Item Title]"
- Includes: Item details, price, pickup instructions
- Sender name: "Julia and Bryn"

**Admin Email:**
- Subject: "Item Sold: [Item Title]"
- Includes: Item details, buyer information (name, email, phone), sale timestamp
- Includes link to Django admin for the item

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

**Via Web Form:**
1. Navigate to `/add-item/`
2. Enter the upload password
3. Fill in the form and upload images
4. Submit - item and Stripe Payment Link are created automatically

**Via Admin:**
1. Log into Django admin
2. Go to Store → Items → Add Item
3. Fill in title, description, category (optional), and price
4. Upload one or more images
5. Save - a Stripe Payment Link will be created automatically

## Important Notes

- **Payment Links are created automatically** when you save a new item
- **Webhooks are the source of truth** - items are marked SOLD via webhook, not frontend logic
- **Sold items stay visible** - they remain on the site with a "Sold" badge
- **One payment per item** - the webhook ensures items can only be sold once
- **No cart functionality** - each item is purchased individually

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
