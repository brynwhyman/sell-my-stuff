# Fix Email Authentication Error

## Problem
```
Failed to send buyer notification email: (535, b'5.7.8 Authentication failed')
Failed to send admin notification email: (535, b'5.7.8 Authentication failed')
```

This means Render cannot authenticate with Brevo's SMTP server.

## Solution

### Step 1: Get Correct Brevo SMTP Credentials

1. Go to https://app.brevo.com/
2. Click your name (top right) → **SMTP & API**
3. Under **SMTP**, you'll see:
   - **SMTP Server**: `smtp-relay.brevo.com`
   - **Port**: `587`
   - **Login**: Your Brevo email (e.g., `your-email@domain.com`)
   - **SMTP Key**: Click "Generate a new SMTP key" if you don't have one

**Important**: The SMTP key is **NOT** your Brevo password. It's a special key that looks like:
```
xsmtpsib-a1b2c3d4e5f6g7h8-AbCdEfGhIjKlMnOp
```

### Step 2: Update Render Environment Variables

1. Go to Render Dashboard: https://dashboard.render.com/
2. Click on your **sell-my-stuff** web service
3. Go to **Environment** tab
4. Update/Add these variables:

```
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-brevo-email@domain.com
EMAIL_HOST_PASSWORD=xsmtpsib-YOUR-ACTUAL-SMTP-KEY-HERE
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-verified-sender@yourdomain.com
ADMIN_EMAIL=julia@yourdomain.com
```

**Critical**:
- `EMAIL_HOST_USER` = Your Brevo login email
- `EMAIL_HOST_PASSWORD` = The SMTP key (starts with `xsmtpsib-`), NOT your Brevo password
- `DEFAULT_FROM_EMAIL` = Must be verified in Brevo (Settings → Senders)

### Step 3: Save and Redeploy

After updating environment variables in Render:
1. Click **Save Changes**
2. Render will automatically redeploy
3. Wait for deployment to complete

### Step 4: Test Again

1. Make a test purchase
2. Check Render logs (should now show "email sent to...")
3. Check your inbox for emails

## Common Mistakes

❌ **Using Brevo password instead of SMTP key**
- Don't use your Brevo account password
- Use the SMTP key from Brevo → SMTP & API

❌ **Email not verified in Brevo**
- `DEFAULT_FROM_EMAIL` must be added as a verified sender in Brevo
- Go to Brevo → Settings → Senders → Add a sender

❌ **Copy-paste errors**
- Make sure there are no extra spaces in the SMTP key
- Copy the entire key including the `xsmtpsib-` prefix

## Quick Test (Optional)

To test SMTP locally first:

```bash
cd /Users/juliajones/Desktop/sellmystuff
source venv/bin/activate
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# This will show if env vars are loaded
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"Has password: {bool(settings.EMAIL_HOST_PASSWORD)}")

# Try sending
send_mail(
    'Test from Django',
    'If you receive this, SMTP works!',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
    fail_silently=False,
)
```

If this works locally but not on Render, the issue is definitely the environment variables on Render.
