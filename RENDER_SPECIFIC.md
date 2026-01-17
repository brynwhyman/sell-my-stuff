# Render-Specific Files

This document lists files that are specific to Render deployment and can be safely deleted when moving to another platform.

## Files to Delete When Leaving Render

### 1. `render.yaml`
- **Purpose**: Render's configuration file
- **Delete when**: Moving to Heroku, Railway, AWS, etc.
- **Note**: Other platforms have their own config files

### 2. `RENDER_DEPLOYMENT.md`
- **Purpose**: Step-by-step Render deployment guide
- **Delete when**: No longer using Render
- **Note**: Keep `PRODUCTION_DEPLOYMENT.md` (general deployment info)

## Files That Stay (Used by Other Platforms Too)

### `requirements.txt`
- **Contains**: `gunicorn` (needed for any production deployment)
- **Keep**: Yes - needed for Heroku, Railway, AWS, etc.

### `sellmystuff/settings.py`
- **Contains**: DATABASE_URL parsing (works with Render, Heroku, Railway)
- **Keep**: Yes - useful for multiple platforms

### `PRODUCTION_DEPLOYMENT.md`
- **Contains**: General production deployment info
- **Keep**: Yes - applies to all platforms

## Quick Cleanup Script

When you're ready to remove Render-specific files:

```bash
# Delete Render-specific files
rm render.yaml
rm RENDER_DEPLOYMENT.md
rm RENDER_SPECIFIC.md  # This file itself
```

## What to Keep

- All code files (`store/`, `sellmystuff/`, `templates/`, `static/`)
- `requirements.txt` (gunicorn needed for production)
- `PRODUCTION_DEPLOYMENT.md` (general deployment guide)
- `README.md`, `TESTING_GUIDE.md`, etc.
- Database models and migrations

## Alternative: Use a Branch

If you want to keep Render config separate:

1. Create a `render` branch with Render-specific files
2. Deploy from that branch
3. Delete the branch when done

This keeps your main branch clean.
