# Fuga Studios Review Generator - Shopify App

A native Shopify app that generates high-quality, authentic product reviews with multi-language support and sophisticated content generation.

## Features

- **Native Shopify Integration**: Embedded app with OAuth authentication
- **Multi-language Support**: English and German review generation
- **Sophisticated Content**: Context-aware reviews based on product categories
- **Authentic Profiles**: Realistic reviewer names and usernames
- **CSV Export**: Ready for Reviews.io import
- **Professional UI**: Built with Shopify Polaris design system

## Setup Instructions

### 1. Create Shopify Partner Account & App

1. Go to [Shopify Partners](https://partners.shopify.com)
2. Create a partner account if you don't have one
3. Create a new app:
   - App type: "Custom app" 
   - App name: "Fuga Review Generator"
   - App URL: `https://your-app.com/app`
   - Allowed redirection URL(s): `https://your-app.com/auth/callback`
   - Webhook endpoint: `https://your-app.com/webhooks/app/uninstalled`

4. Note down your API key and API secret

### 2. Environment Configuration

1. Copy `.env.example` to `.env`
2. Fill in your Shopify app credentials:
   ```
   SHOPIFY_API_KEY=your_api_key_from_partners
   SHOPIFY_API_SECRET=your_api_secret_from_partners
   SHOPIFY_REDIRECT_URI=https://your-app.com/auth/callback
   BASE_URL=https://your-app.com
   FLASK_SECRET_KEY=random_secret_key_for_sessions
   ```

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will be available at `http://localhost:5000`

### 4. Deployment to Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard:
   - `SHOPIFY_API_KEY`
   - `SHOPIFY_API_SECRET` 
   - `SHOPIFY_REDIRECT_URI`
   - `BASE_URL`
   - `FLASK_SECRET_KEY`

3. Railway will automatically deploy from your main branch

### 5. Update Shopify App URLs

Once deployed, update your Shopify app settings:
- App URL: `https://your-railway-app.com/app`
- Allowed redirection URL(s): `https://your-railway-app.com/auth/callback`
- Webhook endpoint: `https://your-railway-app.com/webhooks/app/uninstalled`

## File Structure

```
├── app.py                 # Main Shopify app with OAuth
├── review_generator.py    # Advanced review generation engine
├── templates/
│   ├── install.html      # App installation page
│   └── app.html          # Main embedded app interface
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README_SHOPIFY_APP.md # This file
```

## How It Works

1. **Installation**: Merchants install the app via Shopify Partners or direct URL
2. **OAuth Flow**: App authenticates with merchant's store using OAuth 2.0
3. **Product Sync**: App fetches products from Shopify Admin API
4. **Review Generation**: Sophisticated algorithm creates authentic reviews based on:
   - Product category detection
   - Multi-language content (EN/DE)
   - Realistic reviewer profiles
   - Rating distribution (60% 5-star, 30% 4-star, 10% 3-star)
5. **CSV Export**: Reviews saved in Reviews.io compatible format

## Review Generation Features

### Multi-Language Support
- **English**: Natural, trendy language with modern slang
- **German**: Authentic German expressions and youth language

### Product Category Detection
- Clothing items get fashion-specific reviews
- Accessories get style-focused content
- Generic products get universal positive feedback

### Authentic Reviewer Profiles
- 60% trendy usernames (dark_angel666, aesthetic_vibe)
- 40% realistic names with initials
- Location-based email generation
- Age-appropriate language patterns

### Content Sophistication
- 15% empty reviews (realistic behavior)
- Product-specific content based on title analysis
- Emoji usage (higher on 5-star reviews)
- Occasional typos for realism
- Varied sentence structures

## API Endpoints

- `GET /` - App installation/auth
- `GET /auth/callback` - OAuth callback
- `GET /app` - Main app interface  
- `GET /api/products` - Get products with review counts
- `POST /api/generate/<product_id>` - Generate reviews for product
- `POST /webhooks/app/uninstalled` - Handle app uninstallation

## Security Features

- HMAC verification for all webhook requests
- Session-based authentication
- Shopify request verification
- Environment variable protection
- Secure OAuth 2.0 flow

## Migration from Old System

The new Shopify app replaces the previous Flask webapp and provides:

1. **Native Integration**: No more external website, fully embedded in Shopify admin
2. **Better UX**: Shopify Polaris design system for familiar interface
3. **Improved Security**: Proper OAuth instead of manual token management
4. **Enhanced Reviews**: More sophisticated content generation
5. **Direct Integration**: Ready for Reviews.io API integration

## Next Steps

1. Deploy to Railway
2. Test OAuth flow with a development store
3. Integrate Reviews.io API for direct review posting
4. Add review management features
5. Submit for Shopify App Store approval (optional)