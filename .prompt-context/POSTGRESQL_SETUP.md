# PostgreSQL Setup Guide

This guide explains how to set up PostgreSQL for your Sell My Stuff ecommerce site.

## Why PostgreSQL?

PostgreSQL is recommended for production use because:
- Better performance with multiple concurrent users
- More robust data integrity
- Better suited for production deployments
- Supports more advanced features if needed later

SQLite is fine for local development, but PostgreSQL is better for production.

## Installation

### Mac (using Homebrew)

```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows

Download and install from: https://www.postgresql.org/download/windows/

## Create Database and User

1. **Open PostgreSQL command line:**
   ```bash
   psql postgres
   ```

2. **Create a database:**
   ```sql
   CREATE DATABASE sellmystuff_db;
   ```

3. **Create a user:**
   ```sql
   CREATE USER sellmystuff_user WITH PASSWORD 'your_secure_password_here';
   ```

4. **Grant privileges:**
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE sellmystuff_db TO sellmystuff_user;
   ```

5. **Exit PostgreSQL:**
   ```sql
   \q
   ```

## Configure Django

Add these to your `.env` file:

```
# PostgreSQL Configuration
DB_NAME=sellmystuff_db
DB_USER=sellmystuff_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432
```

**Or use a DATABASE_URL (alternative format):**

```
DATABASE_URL=postgresql://sellmystuff_user:your_secure_password_here@localhost:5432/sellmystuff_db
```

## Install Python Package

Make sure `psycopg2-binary` is installed:

```bash
pip install -r requirements.txt
```

This should install `psycopg2-binary` which is the PostgreSQL adapter for Python.

## Run Migrations

After setting up PostgreSQL and configuring `.env`:

```bash
python manage.py migrate
```

This will create all the database tables in PostgreSQL.

## Verify It's Working

Check that Django is using PostgreSQL:

```bash
python manage.py dbshell
```

You should see a PostgreSQL prompt. Type `\dt` to see tables, or `\q` to exit.

## Using SQLite for Local Development

If you want to keep using SQLite for local development and PostgreSQL for production:

1. **Don't add PostgreSQL config to local `.env`** - Django will use SQLite
2. **Add PostgreSQL config only in production** - Django will automatically use it

The settings are configured to use SQLite if no PostgreSQL configuration is found.

## Production Deployment

For production:

1. Set up PostgreSQL on your server
2. Create database and user
3. Add PostgreSQL credentials to production `.env` file
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`

## Troubleshooting

### "psycopg2 not found" error

Install the package:
```bash
pip install psycopg2-binary
```

### "Connection refused" error

- Make sure PostgreSQL is running: `brew services list` (Mac) or `sudo systemctl status postgresql` (Linux)
- Check that `DB_HOST` and `DB_PORT` are correct
- Verify PostgreSQL is listening on the correct port (default: 5432)

### "Authentication failed" error

- Double-check `DB_USER` and `DB_PASSWORD` in `.env`
- Make sure the user has privileges on the database

### "Database does not exist" error

- Create the database first (see "Create Database and User" above)
- Verify `DB_NAME` matches the database you created

## Security Notes

- **Never commit `.env` file** with database passwords
- Use strong passwords for production
- Consider using environment variables instead of `.env` file in production
- Restrict database access to only necessary IPs in production
