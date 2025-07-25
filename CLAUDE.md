# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask application for generating sophisticated product reviews for Shopify stores. The application supports both standalone usage and Shopify app integration, with multiple deployment targets including Railway, Render, and Heroku.

## Key Architecture

### Core Applications
- `app.py` - Native Shopify app with OAuth authentication and webhook handling
- `shopify_backend_app.py` - Standalone backend for direct Shopify API integration
- `review_generator.py` - Advanced review generation engine with multilingual support
- `reviews_io_integration.py` - Reviews.io API client for direct review management

### Review Generation System
The application uses a sophisticated review generation algorithm that:
- Supports German and English languages with authentic slang/expressions
- Uses age-appropriate language patterns and trendy usernames
- Categorizes products (clothing, accessories, shoes, tech, home) for context-aware reviews
- Implements realistic rating distributions (60% 5-star, 30% 4-star, 10% 3-star)
- Adds realistic touches like emojis, occasional typos, and varied review lengths

### Integration Points
- **Shopify API**: Product fetching, OAuth authentication, webhook handling
- **Reviews.io**: Direct API integration for review posting and management
- **Klaviyo Reviews API**: Direct review posting to Klaviyo's review system
- **CSV Export**: Review export functionality for manual imports

## Common Development Commands

### Running the Application
```bash
# Standalone backend (port 5000)
python shopify_backend_app.py

# Shopify app (port 5000)  
python app.py

# Using gunicorn for production
gunicorn app:app
gunicorn shopify_backend_app:app
```

### Environment Variables Required
```bash
# For Shopify integration
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_SECRET=your-api-secret
SHOPIFY_REDIRECT_URI=https://your-app.com/auth/callback

# For Reviews.io integration
REVIEWS_IO_API_KEY=your-reviews-io-key
REVIEWS_IO_STORE_ID=your-store-id

# For Klaviyo integration
KLAVIYO_API_KEY=your-klaviyo-key

# App configuration
FLASK_SECRET_KEY=your-secret-key
BASE_URL=https://your-app.com
```

### Testing
No formal test framework is configured. Manual testing via web interface.

### Dependencies
Install with: `pip install -r requirements.txt`
- Flask 2.3.2
- requests 2.31.0  
- gunicorn 21.2.0
- python-dotenv 1.0.0

## Deployment

The application is configured for multiple deployment platforms:
- **Railway**: Uses `railway.json` configuration
- **Render**: Uses `render.yaml` configuration  
- **Heroku**: Uses `Procfile` and `runtime.txt`

See `DEPLOYMENT.md` for detailed deployment instructions.

## File Structure

### Templates (`templates/`)
- `app.html` - Main Shopify app interface
- `shopify_backend.html` - Standalone backend interface
- `install.html` - Shopify app installation page
- `klaviyo_diagnostic.html` - Klaviyo API diagnostic tools

### Data Files
- `review_tracking.json` - Tracks generated review counts per product
- `live_review_counts.json` - Manual tracking of live review counts
- `exports/` - Generated CSV files (created at runtime)

## Security Considerations

- Uses HMAC verification for Shopify webhooks
- Validates Shopify OAuth requests
- Environment variables for all credentials
- No credentials committed to repository
- Proper error handling for API failures

## Development Notes

- The application handles both Shopify private app tokens and OAuth tokens
- CSV review counting fallback system when APIs are unavailable
- Sophisticated product categorization for context-aware review generation
- Multi-language support with region-appropriate reviewer information
- Built-in diagnostic endpoints for troubleshooting API integrations