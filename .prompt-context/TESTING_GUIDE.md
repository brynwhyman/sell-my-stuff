# Testing Guide for Non-Developers

This guide will help you test your ecommerce site step by step.

## Prerequisites

You'll need:
- Python 3.8 or higher installed on your computer
- A terminal/command prompt (Terminal on Mac, Command Prompt on Windows)

## Step 1: Open Terminal and Navigate to Your Project

1. **On Mac**: Open "Terminal" (search for it in Spotlight)
2. **On Windows**: Open "Command Prompt" or "PowerShell"

3. Navigate to your project folder:
   ```bash
   cd /Users/juliajones/Desktop/bryn
   ```

## Step 2: Create a Virtual Environment (One-Time Setup)

This keeps your project's dependencies separate from other Python projects.

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` at the start of your command line when it's active.

## Step 3: Upgrade pip (Recommended)

First, make sure pip is up to date:

```bash
pip install --upgrade pip
```

## Step 4: Install Required Packages

```bash
pip install -r requirements.txt
```

This installs Django, Stripe, and other required packages.

**If you get an error about "No matching distribution found":**
- Make sure your virtual environment is activated (you see `(venv)` in your terminal)
- Try upgrading pip first: `pip install --upgrade pip`
- Try installing packages one at a time to see which one fails

## Step 5: Set Up Environment Variables

1. Create a file named `.env` in your project folder (same level as `manage.py`)
2. Add these lines (replace with your actual values):

```
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe Configuration (get these from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Note**: For testing, you can use Stripe test keys. Sign up at https://stripe.com and get test API keys from the dashboard.

## Step 6: Set Up the Database

```bash
python manage.py migrate
```

This creates the database tables for items, images, etc.

## Step 7: Create an Admin Account

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username (e.g., "admin")
- Email address (optional)
- Password (enter it twice - it won't show as you type)

## Step 8: Start the Development Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

**Keep this terminal window open** - the server is running!

## Step 9: Test the Admin Interface

1. Open your web browser
2. Go to: http://127.0.0.1:8000/admin/
3. Log in with the username and password you created in Step 6

### Test Adding an Item:

1. Click on **"Items"** under the "STORE" section
2. Click **"Add Item"** (top right)
3. Fill in:
   - **Title**: "Test Item"
   - **Description**: "This is a test item"
   - **Price amount**: 29.99
   - **Currency**: USD
   - **Status**: Live
4. Scroll down to the **"Item images"** section
5. Click **"Add another Item image"**
6. Upload a test image (JPEG, PNG, or GIF under 5MB)
7. Set **Sort order**: 0
8. Check **Is primary**: Yes
9. Click **"Save"** at the bottom

**What to expect**: 
- The item is saved
- A Stripe Payment Link is created automatically (if Stripe keys are configured)
- You'll see a success message

### Test Image Management:

1. Edit the item you just created
2. Add more images with different sort orders (0, 1, 2, etc.)
3. Try marking different images as primary
4. Reorder images by changing sort_order values

## Step 10: Test the Public Site

1. In a new browser tab, go to: http://127.0.0.1:8000/
2. You should see your item listed
3. Click on the item to see the detail page
4. Check that:
   - The primary image shows as the main image
   - All images appear in the gallery (ordered by sort_order)
   - The price displays correctly
   - The "Buy Now" button appears (if status is LIVE and Stripe is configured)

## Step 11: Test Status Changes

1. Go back to admin: http://127.0.0.1:8000/admin/
2. Edit your test item
3. Change **Status** from "Live" to "Sold"
4. Save
5. Go back to the public site
6. Check that:
   - The item still appears in the list
   - It shows a "Sold" badge
   - The "Buy Now" button is hidden

## Step 12: Test Stripe Payment (Optional)

**Note**: This requires Stripe test account setup.

1. Make sure your item status is "Live"
2. On the item detail page, click "Buy Now"
3. You'll be redirected to Stripe's test payment page
4. Use Stripe's test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
   - ZIP: Any 5 digits
5. Complete the payment
6. Check that the webhook marks the item as SOLD

**For webhook testing locally**, you'll need to use Stripe CLI:
```bash
stripe listen --forward-to localhost:8000/store/webhooks/stripe/
```

This forwards Stripe webhooks to your local server.

## Troubleshooting

### "No matching distribution found" or "Module not found" errors
- Make sure your virtual environment is activated (you see `(venv)` in terminal)
- Upgrade pip: `pip install --upgrade pip`
- Make sure you have internet connection (pip needs to download packages)
- Try installing packages individually to identify the problem:
  ```bash
  pip install Django
  pip install python-decouple
  pip install stripe
  pip install Pillow
  ```

### "Port already in use" error
- Another process is using port 8000
- Stop other Django servers or use a different port: `python manage.py runserver 8001`

### Images not showing
- Make sure the `media` folder exists in your project directory
- Check that `MEDIA_URL` and `MEDIA_ROOT` are set correctly in settings

### Stripe errors
- Verify your Stripe API keys are correct
- Make sure you're using test keys (start with `sk_test_`)
- Check that webhook secret is set if testing webhooks

### Can't access admin
- Make sure you created a superuser account
- Check that you're using the correct username/password

## Quick Reference Commands

```bash
# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate

# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Update database (after model changes)
python manage.py migrate
```

## Next Steps

Once everything is working:
- Add more items with images
- Test different currencies
- Test the full purchase flow with Stripe
- Customize the design in `static/css/style.css`

## Getting Help

If you encounter issues:
1. Check the terminal for error messages
2. Verify all steps were completed
3. Make sure your virtual environment is activated
4. Check that the server is running (Step 7)
