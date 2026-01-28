# Brevo Authentication Checklist

## The Issue
```
Failed to send buyer notification email: (535, b'5.7.8 Authentication failed')
```

This error means Render **cannot authenticate** with Brevo's SMTP server.

## Step-by-Step Verification

### 1. Get CORRECT Brevo Credentials

Go to https://app.brevo.com/ and login.

#### A. Get your SMTP Login (EMAIL_HOST_USER)
1. Click your name (top right) → **SMTP & API**
2. Under "SMTP" section, look for **"Login"**
3. Copy the **exact** email shown there
   - Example: `julia@yourdomain.com` or `your-email@gmail.com`
   - This is your `EMAIL_HOST_USER`

#### B. Generate NEW SMTP Key (EMAIL_HOST_PASSWORD)
1. Still on the SMTP & API page
2. Under "Master Password", click **"Generate a new SMTP key"**
3. Give it a name like "Render Production"
4. Copy the ENTIRE key that appears (starts with `xsmtpsib-`)
   - Example: `xsmtpsib-a1b2c3d4e5f6g7h8-AbCdEfGhIjKlMnOp123456`
   - This is your `EMAIL_HOST_PASSWORD`
   - **Note**: This is NOT your Brevo account password!

### 2. Verify Sender Email

1. In Brevo, go to **Settings** → **Senders**
2. Make sure your sender email is listed and **verified** (green checkmark)
3. This should match your `DEFAULT_FROM_EMAIL`

If not verified:
- Click "Add a sender"
- Enter the email you want to send from
- Verify via the confirmation email Brevo sends

### 3. Update Render Environment Variables

1. Go to https://dashboard.render.com/
2. Click your **sell-my-stuff** service
3. Go to **Environment** tab
4. Click **each** variable to edit (or Add if missing):

**Copy these EXACTLY from Brevo:**

```
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your-brevo-login-email>
EMAIL_HOST_PASSWORD=<your-xsmtpsib-key>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=<your-verified-sender-email>
ADMIN_EMAIL=<where-you-want-admin-notifications>
```

**Example:**
```
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=julia@seatoun.co.nz
EMAIL_HOST_PASSWORD=xsmtpsib-abc123def456ghi789jkl012mno345pqr678stu901
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=julia@seatoun.co.nz
ADMIN_EMAIL=julia@seatoun.co.nz
```

### 4. Common Mistakes ❌

- [ ] Using Brevo account password instead of SMTP key
- [ ] Extra spaces before/after the SMTP key when pasting
- [ ] Using wrong email for EMAIL_HOST_USER (must match Brevo login)
- [ ] DEFAULT_FROM_EMAIL not verified in Brevo Senders
- [ ] Old/expired SMTP key (generate a fresh one)
- [ ] Typo in smtp-relay.brevo.com

### 5. After Updating

1. Click **Save Changes** in Render
2. Wait 2-3 minutes for redeploy to complete
3. Check deployment status shows "Live"
4. Make a test purchase
5. Check Render logs immediately

### 6. Still Not Working?

If authentication still fails after following ALL steps above:

**Option A: Try Gmail SMTP Instead**

If you have a Gmail account:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=<gmail-app-password>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
ADMIN_EMAIL=your-gmail@gmail.com
```

Note: You need to create an App Password in Gmail (not your regular password):
1. Go to Google Account → Security
2. Turn on 2-Step Verification (if not already)
3. Search "App passwords"
4. Generate an app password for "Mail"
5. Use that 16-character password

**Option B: Double-check Render is Using Latest Code**

Make sure you've committed and pushed all changes:
```bash
cd /Users/juliajones/Desktop/sellmystuff
git status
git add -A
git commit -m "Fix email settings"
git push
```

Then check Render Dashboard to ensure the latest commit deployed.
