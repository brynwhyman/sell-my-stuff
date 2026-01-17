# Render Deployment Guide

Step-by-step guide for deploying Sell My Stuff to Render.

**Note**: This file and `render.yaml` are Render-specific. See `RENDER_SPECIFIC.md` for what to delete when moving to another platform.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub (if not already done)
2. **Render Account**: Sign up at https://render.com
3. **Stripe Account**: Have your live Stripe keys ready

## Step 1: Create PostgreSQL Database

1. In Render Dashboard, click **New +** → **PostgreSQL**
2. Name it (e.g., "sell-my-stuff-db")
3. Choose a plan (Free tier is fine for POC)
4. Select region closest to you
5. Click **Create Database**
6. **Note the connection details** - you'll need:
   - Internal Database URL (for Render services)
   - External Database URL (if accessing from outside)

## Step 2: Create Web Service

1. In Render Dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository
3. Select the repository and branch

## Step 3: Configure Web Service

### Basic Settings:
- **Name**: sell-my-stuff (or your preferred name)
- **Region**: Same as your database
- **Branch**: main (or your default branch)
- **Root Directory**: (leave blank, or `./` if needed)
- **Runtime**: Python 3
- **Build Command**: 
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```
  gunicorn sellmystuff.wsgi:application
  ```

### Environment Variables:

Add these in the Render dashboard (Environment tab):

**Required:**
```
SECRET_KEY=your-strong-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
```

**Database (use Render's internal database URL):**
```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

**Or use DATABASE_URL (easier - Render provides this):**
- In your PostgreSQL service, copy the **Internal Database URL**
- Add as: `DATABASE_URL=postgresql://...` (full URL from Render)

**Stripe (use LIVE keys for production):**
```
STRIPE_SECRET_KEY=sk_live_your_live_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret
```

**Optional:**
```
SECURE_SSL_REDIRECT=True
```

### Generate Secret Key:

Run this locally to generate a strong secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 4: Deploy

1. Click **Create Web Service**
2. Render will:
   - Install dependencies
   - Run `collectstatic`
   - Start your app with gunicorn
3. Wait for deployment to complete (usually 2-5 minutes)

## Step 5: Run Migrations

After first deployment:

1. Go to your Web Service dashboard
2. Click **Shell** tab (or use Render CLI)
3. Run:
   ```bash
   python manage.py migrate
   ```
4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Step 6: Set Up Stripe Webhook

1. Get your Render app URL (e.g., `https://sell-my-stuff.onrender.com`)
2. Go to Stripe Dashboard → Developers → Webhooks
3. Add endpoint: `https://your-app-name.onrender.com/store/webhooks/stripe/`
4. Select event: `checkout.session.completed`
5. Copy the webhook signing secret
6. Add to Render environment variables as `STRIPE_WEBHOOK_SECRET`
7. **Redeploy** your service (Render will pick up the new env var)

## Step 7: Media Files (Important!)

**Render's filesystem is ephemeral** - uploaded files will be lost on restart.

### Option 1: Use Render's Persistent Disk (Simple for POC)
1. In your Web Service settings
2. Add a **Persistent Disk** (5GB free tier)
3. Mount it to `/opt/render/project/src/media`
4. Update your `.env` or settings to use this path

### Option 2: Use Cloud Storage (Recommended for Production)
- AWS S3
- Cloudinary
- Or similar service

For POC, Option 1 is fine.

## Step 8: Verify Deployment

Checklist:
- [ ] Site loads at your Render URL
- [ ] Static files (CSS, JS) load correctly
- [ ] Can access admin at `/admin/`
- [ ] Can create items
- [ ] Images upload and display
- [ ] Stripe Payment Links work
- [ ] Webhooks are received (check Stripe Dashboard)

## Troubleshooting

### Static Files Not Loading
- Check that `collectstatic` ran in build logs
- Verify `STATIC_ROOT` is set correctly
- Check WhiteNoise middleware is in `MIDDLEWARE`

### Database Connection Issues
- Verify `DATABASE_URL` or database credentials are correct
- Check database is in same region as web service
- Ensure database is running

### 500 Errors
- Check Render logs (Logs tab in dashboard)
- Verify all environment variables are set
- Check `DEBUG=False` is set (don't use `True` in production)

### Media Files Disappear
- This is expected with ephemeral filesystem
- Use Persistent Disk or cloud storage

## Render-Specific Notes

- **Auto-deploy**: Render auto-deploys on git push (if enabled)
- **Free tier**: Spins down after 15 minutes of inactivity (wakes on request)
- **Logs**: Available in dashboard under Logs tab
- **Shell access**: Use Shell tab to run Django commands

## Post-Deployment

1. Test creating an item
2. Test image upload
3. Test a payment with Stripe test card
4. Verify webhook marks item as SOLD
5. Monitor logs for any errors
