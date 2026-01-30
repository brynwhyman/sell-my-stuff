# Debugging Email Issues

## Problem
- Stripe receipts not being received
- Custom email notifications not being sent (buyer or admin)

## Checklist

### 1. Have you deployed the latest code?
```bash
git status
git log --oneline -3
```

If you have uncommitted changes or haven't pushed to Render, **deploy first**.

### 2. Check Stripe Receipt Settings
Stripe automatic receipts are **separate** from our custom emails.

To enable:
1. Go to Stripe Dashboard → Settings → Emails
2. Enable "Successful payments" under Customer emails
3. This is a global Stripe setting, not per-payment-link

### 3. Check if Webhook is Working
When a payment completes, the webhook should:
- Mark item as SOLD in Django admin
- Send 2 emails (buyer + admin)

**Test webhook:**
```bash
# In Render logs, search for:
"Item"
"sold to"
"email sent"
```

If you see these logs, webhooks are working. If not, webhook isn't triggering.

### 4. Check Environment Variables on Render
Verify these are set in Render Dashboard → Environment:

```
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-smtp-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-verified-sender@yourdomain.com
ADMIN_EMAIL=your-admin-email@example.com
```

### 5. Test Locally First
```bash
cd /Users/juliajones/Desktop/sellmystuff
source venv/bin/activate
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Print email settings
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")

# Try sending test email
send_mail(
    'Test Subject',
    'Test message',
    settings.DEFAULT_FROM_EMAIL,
    [settings.ADMIN_EMAIL],
    fail_silently=False,
)
# Should print: 1 (means email sent successfully)
```

### 6. Check Brevo Dashboard
1. Go to https://app.brevo.com/
2. Navigate to "Email" → "Statistics"
3. Check if emails are being sent/delivered
4. Check "Logs" for any bounces or errors

### 7. Common Issues

**Issue: Webhook not triggering**
- Check webhook URL is correct: `https://sell-my-stuff.onrender.com/webhooks/stripe/`
- Check webhook is in **Test mode** (not Live mode)
- Check webhook events include `checkout.session.completed`

**Issue: Emails not sending even though webhook works**
- Check Render logs for email errors
- Verify sender email is verified in Brevo
- Check Brevo daily sending limit (300 emails/day on free tier)

**Issue: Stripe receipts not coming**
- This is separate from our custom emails
- Enable in Stripe Dashboard → Settings → Emails
- Receipts only work if customer email is collected (we do this)

## Quick Test

1. Create a test item
2. Complete a test payment (use Stripe test card: 4242 4242 4242 4242)
3. Check:
   - ✅ Item marked as SOLD in Django admin?
   - ✅ Render logs show "Item sold to..."?
   - ✅ Render logs show "email sent to..."?
   - ✅ Buyer email received?
   - ✅ Admin email received?
   - ✅ Stripe receipt received?

## Next Steps

Based on which step fails, you'll know where the problem is.
