# Production Deployment Guide

This guide covers important production deployment considerations for the Sell My Stuff ecommerce site.

## Pre-Deployment Checklist

### 1. Environment Variables

Ensure your production `.env` file or hosting environment variables include:

```env
# Required
SECRET_KEY=your-strong-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# Stripe (use LIVE keys, not test keys)
STRIPE_SECRET_KEY=sk_live_your_live_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# Optional: Disable SSL redirect if behind a proxy that handles it
SECURE_SSL_REDIRECT=True
```

### 2. Generate a Strong Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Use this output as your `SECRET_KEY` in production.

### 3. Database Setup

- Set up PostgreSQL database (see [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md))
- Run migrations: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

### 4. Static Files

Before deploying, collect static files:

```bash
python manage.py collectstatic --noinput
```

This gathers all static files (CSS, JS) into the `staticfiles/` directory.

**Note**: The project uses WhiteNoise to serve static files efficiently in production, so you don't need a separate web server for static files.

### 5. Media Files

- Ensure your hosting service can handle file uploads
- Or configure cloud storage (AWS S3, Cloudinary) for media files
- Update `MEDIA_ROOT` and `MEDIA_URL` if using cloud storage

## Production Security Settings

The following security settings are **automatically enabled** when `DEBUG=False`:

### HTTPS/SSL
- `SECURE_SSL_REDIRECT`: Automatically redirects HTTP to HTTPS
- `SESSION_COOKIE_SECURE`: Session cookies only sent over HTTPS
- `CSRF_COOKIE_SECURE`: CSRF cookies only sent over HTTPS

### Security Headers
- `X-Frame-Options: DENY`: Prevents clickjacking
- `X-Content-Type-Options: nosniff`: Prevents MIME type sniffing
- `X-XSS-Protection`: Enables browser XSS filter
- `Referrer-Policy`: Controls referrer information

### HSTS (HTTP Strict Transport Security)
- Forces browsers to use HTTPS for 1 year
- Includes subdomains
- Preload enabled

### Cookie Security
- `HttpOnly` flags on session and CSRF cookies
- `SameSite` protection against CSRF attacks

### Password Requirements
- Minimum 12 characters in production
- All Django password validators active

**No action needed** - these activate automatically when `DEBUG=False`.

## Static Files Configuration

### WhiteNoise

The project uses [WhiteNoise](http://whitenoise.evans.io/) to serve static files efficiently in production. This means:

- **No separate web server needed** for static files (like nginx)
- **Automatic compression** and caching
- **Works with most hosting services** (Heroku, Railway, Render, etc.)

### How It Works

1. **Development**: Django serves static files normally
2. **Production**: WhiteNoise middleware serves static files efficiently
3. **Collection**: Run `collectstatic` to gather all static files before deployment

### Deployment Steps

1. **Collect static files** (usually done automatically by hosting service):
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Verify static files are collected**:
   - Check that `staticfiles/` directory exists
   - Contains your CSS, JS, and other static assets

3. **Deploy** - WhiteNoise will automatically serve these files

### Hosting Service Compatibility

WhiteNoise works with:
- ✅ Heroku
- ✅ Railway
- ✅ Render
- ✅ DigitalOcean App Platform
- ✅ Most PaaS services

If your hosting service requires a separate static file server, you can:
- Disable WhiteNoise and configure nginx/Apache
- Or use a CDN (CloudFront, Cloudflare) for static files

## Stripe Production Setup

### 1. Switch to Live Keys

- Get your **live** API keys from Stripe Dashboard
- Replace test keys (`sk_test_`) with live keys (`sk_live_`)
- Update `STRIPE_SECRET_KEY` in production environment

### 2. Set Up Production Webhook

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/store/webhooks/stripe/`
3. Select event: `checkout.session.completed`
4. Copy the webhook signing secret
5. Add to production environment as `STRIPE_WEBHOOK_SECRET`

### 3. Test Production Webhook

- Use Stripe Dashboard to send a test webhook
- Verify it's received and processed correctly
- Check that items are marked as SOLD

## Common Hosting Services

### Heroku

1. Install Heroku CLI
2. Create app: `heroku create your-app-name`
3. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables: `heroku config:set KEY=value`
5. Deploy: `git push heroku main`
6. Run migrations: `heroku run python manage.py migrate`

### Railway

1. Connect GitHub repository
2. Add PostgreSQL service
3. Set environment variables in dashboard
4. Deploy automatically on push

### Render

1. Create new Web Service
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. Start command: `gunicorn sellmystuff.wsgi:application`

## Post-Deployment

### 1. Verify Everything Works

- [ ] Site loads correctly
- [ ] Static files (CSS, images) load
- [ ] Can log into admin
- [ ] Can create items
- [ ] Images upload correctly
- [ ] Stripe Payment Links work
- [ ] Webhooks are received
- [ ] Items marked as SOLD after payment

### 2. Monitor

- Check server logs for errors
- Monitor Stripe Dashboard for webhook events
- Verify payments are processing correctly

### 3. Backup

- Set up database backups (most hosting services do this automatically)
- Consider backing up media files if not using cloud storage

## Troubleshooting

### Static Files Not Loading

1. Run `python manage.py collectstatic`
2. Check `STATIC_ROOT` is set correctly
3. Verify WhiteNoise middleware is in `MIDDLEWARE`
4. Check file permissions on `staticfiles/` directory

### Security Settings Causing Issues

If behind a proxy/load balancer:
- Set `SECURE_PROXY_SSL_HEADER` correctly
- May need to disable `SECURE_SSL_REDIRECT` if proxy handles it

### Database Connection Issues

- Verify PostgreSQL credentials
- Check database exists
- Verify network access (firewall rules)

### Webhook Not Working

- Verify webhook URL is correct
- Check webhook secret matches
- Look for errors in server logs
- Test webhook from Stripe Dashboard

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Stripe Production Guide](https://stripe.com/docs/keys)
