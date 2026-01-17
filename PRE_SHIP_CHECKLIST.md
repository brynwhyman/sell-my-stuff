# Pre-Ship Checklist

## ✅ Code Quality Fixes Applied

### 1. Database Configuration
- ✅ Added `dj-database-url` to requirements.txt for robust DATABASE_URL parsing
- ✅ Improved DATABASE_URL parsing in settings.py with fallback handling
- ✅ Better compatibility with Render, Heroku, and other platforms

### 2. Webhook Error Handling
- ✅ Added logging to webhook handler for production debugging
- ✅ Logs warnings when item_id from metadata not found
- ✅ Logs errors when Stripe API calls fail
- ✅ Logs errors when items cannot be found by price_id

### 3. Category Ordering
- ✅ Fixed category ordering in ItemListView to respect model's `order` field
- ✅ Categories now display in correct order on frontend

## 📋 Pre-Deployment Checks

### Environment Variables
- [ ] `SECRET_KEY` - Generate strong key for production
- [ ] `DEBUG=False` - Must be False in production
- [ ] `ALLOWED_HOSTS` - Set to your domain(s)
- [ ] `STRIPE_SECRET_KEY` - Use LIVE keys (not test) in production
- [ ] `STRIPE_WEBHOOK_SECRET` - Get from Stripe Dashboard after setting webhook URL
- [ ] `DATABASE_URL` - Provided by hosting service (Render, Heroku, etc.)

### Database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test admin access

### Static Files
- [ ] Run `python manage.py collectstatic` before deploying
- [ ] Verify static files are served correctly in production

### Stripe Configuration
- [ ] Switch to LIVE mode in Stripe Dashboard
- [ ] Create webhook endpoint in Stripe Dashboard
- [ ] Set webhook URL: `https://yourdomain.com/store/webhooks/stripe/`
- [ ] Select event: `checkout.session.completed`
- [ ] Copy webhook signing secret to environment variables

### Testing
- [ ] Test creating an item in admin
- [ ] Verify Payment Link is created automatically
- [ ] Test category creation and filtering
- [ ] Test image uploads (multiple images, primary image selection)
- [ ] Test complete purchase flow with test card
- [ ] Verify webhook marks item as SOLD
- [ ] Verify Payment Link is deactivated after sale
- [ ] Test pagination on item list
- [ ] Test category filtering
- [ ] Test mobile responsiveness

### Security
- [ ] Verify `DEBUG=False` in production
- [ ] Check HTTPS is enabled
- [ ] Verify security headers are active (check response headers)
- [ ] Test that admin requires authentication

### Media Files (Render-specific)
- [ ] Set up Persistent Disk in Render for media files
- [ ] OR configure cloud storage (S3, Cloudinary) for production

## 🚀 Deployment Steps

1. **Push code to GitHub**
2. **Create PostgreSQL database** (if using Render)
3. **Create Web Service** in hosting platform
4. **Set environment variables** in hosting dashboard
5. **Deploy**
6. **Run migrations** via hosting shell/console
7. **Create superuser** via hosting shell/console
8. **Set up Stripe webhook** with production URL
9. **Test end-to-end** purchase flow

## 📝 Notes

- **Media Files**: Render's filesystem is ephemeral. Use Persistent Disk for POC or cloud storage for production.
- **Logging**: Webhook errors are now logged. Check logs if webhooks aren't working.
- **Database**: `dj-database-url` handles various DATABASE_URL formats automatically.

## 🔍 Post-Deployment Verification

- [ ] Site loads correctly
- [ ] Admin panel accessible
- [ ] Can create items with images
- [ ] Payment Links are created
- [ ] Test purchase completes successfully
- [ ] Item marked as SOLD after purchase
- [ ] Webhook received and processed
- [ ] Payment Link deactivated after sale
- [ ] Mobile view works correctly
- [ ] Category filtering works
- [ ] Images display correctly

## 📚 Documentation

All documentation files are up to date:
- ✅ README.md - References all other docs
- ✅ TESTING_GUIDE.md - Local testing instructions
- ✅ STRIPE_INTEGRATION.md - Technical Stripe details
- ✅ STRIPE_WEBHOOK_SETUP.md - Webhook setup guide
- ✅ POSTGRESQL_SETUP.md - Database setup
- ✅ PRODUCTION_DEPLOYMENT.md - General deployment guide
- ✅ RENDER_DEPLOYMENT.md - Render-specific deployment
- ✅ RENDER_SPECIFIC.md - Render cleanup guide
