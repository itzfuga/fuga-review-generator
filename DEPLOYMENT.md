# Shopify Review Generator - Deployment Guide

This guide will help you deploy your Shopify Review Generator app as a private web application.

## Prerequisites

1. A Shopify store with a private app created
2. Your Shopify private app credentials:
   - Shop domain (e.g., `your-store.myshopify.com`)
   - Access token from your private app

## Option 1: Deploy to Railway (Recommended)

### Step 1: Prepare your repository
```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect it's a Python app

### Step 3: Configure Environment Variables
In your Railway project dashboard:
1. Go to "Variables" tab
2. Add these variables:
   - `SHOPIFY_SHOP_DOMAIN` = `your-store.myshopify.com`
   - `SHOPIFY_ACCESS_TOKEN` = `your-private-app-token`

### Step 4: Deploy
Railway will automatically deploy your app. Get your app URL from the "Settings" tab.

## Option 2: Deploy to Render.com (Free tier)

### Step 1: Push to GitHub
Same as Railway - ensure your code is on GitHub.

### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - Name: `shopify-review-generator`
   - Runtime: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn shopify_backend_app:app`

### Step 3: Add Environment Variables
In the Environment section, add:
- `SHOPIFY_SHOP_DOMAIN` = `your-store.myshopify.com`
- `SHOPIFY_ACCESS_TOKEN` = `your-private-app-token`

### Step 4: Deploy
Click "Create Web Service". Render will build and deploy your app.

## Option 3: Deploy to Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account (paid plan required)

### Deploy Steps
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
heroku config:set SHOPIFY_ACCESS_TOKEN=your-private-app-token

# Deploy
git push heroku main
```

## Troubleshooting

### Railway deployment fails
1. Check the build logs in Railway dashboard
2. Ensure environment variables are set correctly
3. Make sure `runtime.txt` specifies a valid Python version

### App crashes after deployment
1. Check if environment variables are set
2. Look at the deployment logs for errors
3. Ensure your Shopify access token has the correct permissions

### CSV exports not working
The app creates files in an `exports` directory. On platforms like Railway/Render, these files are temporary. Consider using cloud storage for permanent file storage.

## Security Notes

- Never commit your Shopify credentials to Git
- Always use environment variables for sensitive data
- Keep your access tokens secure and rotate them regularly
- This app should only be accessible to authorized users

## Testing Your Deployment

Once deployed, visit your app URL and:
1. You should see the review generator interface
2. Click "Generate Reviews" 
3. The app will fetch your products and generate reviews
4. Download the CSV file

## Getting Your Shopify Private App Credentials

1. Log in to your Shopify admin
2. Go to Settings → Apps and sales channels
3. Click "Develop apps"
4. Create a private app or use existing one
5. Give it these permissions:
   - Read products
   - Read product listings
6. Copy the Admin API access token