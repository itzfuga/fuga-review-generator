# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask application for generating sophisticated product reviews for Shopify stores. The application supports both standalone usage and Shopify app integration, with multiple deployment targets including Railway, Render, and Heroku.

## Key Architecture

### Core Applications
- `app.py` - Native Shopify app with OAuth authentication and webhook handling (port 5000)
- `shopify_backend_app.py` - Standalone backend for direct Shopify API integration (port 5000)
- `review_generator.py` - Advanced review generation engine with multilingual support
- `reviews_io_integration.py` - Reviews.io API client class for direct review management
- `old_review.py` - Legacy review generator (uses Faker library for internationalization)

### Application Architecture Pattern
Both main applications (`app.py` and `shopify_backend_app.py`) follow a similar Flask structure:
- **Product Endpoints**: `/api/products` - Fetch products from Shopify
- **Generation Endpoints**: `/api/generate/<product_id>` - Generate reviews for specific products
- **Diagnostic Endpoints**: `/api/debug-*`, `/klaviyo-diagnostic` - API integration testing
- **Export Endpoints**: `/download/<filename>` - CSV export functionality

### Review Generation System
The application uses two review generation engines:
1. **Modern Engine** (`review_generator.py`):
   - Supports German and English with authentic Gen Z slang
   - Context-aware product categorization (clothing, accessories, shoes, tech, home)
   - Realistic rating distributions (60% 5-star, 30% 4-star, 10% 3-star)
   - Sophisticated name generation and realistic touches (emojis, typos)

2. **Legacy Engine** (`old_review.py`):
   - Uses Faker library for multi-regional support (DE, EN, PL, RU)
   - More traditional review patterns
   - Used as fallback/comparison system

### Data Persistence Layer
- `review_tracking.json` - Tracks generated review counts per product
- `live_review_counts.json` - Manual tracking of live review counts
- CSV fallback system when APIs are unavailable
- Dynamic export file generation in `exports/` directory

### Integration Points
- **Shopify API**: Product fetching, OAuth authentication, webhook handling
- **Reviews.io**: Direct API integration via `ReviewsIOClient` class
- **Klaviyo Reviews API**: Direct review posting with diagnostic endpoints
- **CSV Export**: Review export functionality for manual imports

## Common Development Commands

### Running the Application
```bash
# Install dependencies first
pip install -r requirements.txt

# Standalone backend (port 5000) with Klaviyo diagnostics
python shopify_backend_app.py

# Native Shopify app (port 5000) with OAuth flow
python app.py

# Production deployment options
gunicorn app:app --bind 0.0.0.0:$PORT
gunicorn shopify_backend_app:app --bind 0.0.0.0:$PORT
```

### Key Development Endpoints
```bash
# Shopify Backend App (shopify_backend_app.py)
http://localhost:5000/                    # Main interface
http://localhost:5000/klaviyo-diagnostic # Klaviyo API diagnostics
http://localhost:5000/api/products        # List Shopify products
http://localhost:5000/api/generate/ID     # Generate reviews for product

# Native Shopify App (app.py)
http://localhost:5000/                    # Installation page
http://localhost:5000/app                # Main app interface (post-auth)
http://localhost:5000/auth/callback      # OAuth callback
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

### Development Workflow
1. **Setup**: `pip install -r requirements.txt`
2. **Configuration**: Set required environment variables (see above)
3. **Choose Application**:
   - Use `shopify_backend_app.py` for direct API access and diagnostics
   - Use `app.py` for full Shopify app OAuth integration
4. **Testing**: Manual testing via web interface (no formal test framework)
5. **Debugging**: Use Klaviyo diagnostic endpoints for API troubleshooting

### Dependencies
- Flask 2.3.2 - Web framework
- requests 2.31.0 - HTTP client for API calls
- gunicorn 21.2.0 - Production WSGI server
- python-dotenv 1.0.0 - Environment variable management
- Faker (required by `old_review.py`) - Not in requirements.txt, needs manual installation

## Deployment

The application is configured for multiple deployment platforms:
- **Railway**: Uses `railway.json` configuration (defaults to `app.py`)
- **Render**: Uses `render.yaml` configuration (configured for `shopify_backend_app.py`)
- **Heroku**: Uses `Procfile` (defaults to `app.py`) and `runtime.txt` (Python 3.11.5)

**Note**: The Procfile defaults to `app:app`, so update it if you want to deploy `shopify_backend_app.py` instead.

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

### Authentication Patterns
- **Native App** (`app.py`): Uses OAuth flow with HMAC verification for security
- **Backend App** (`shopify_backend_app.py`): Uses direct API tokens for immediate access
- Both apps handle Shopify webhook verification and API rate limiting

### Review Generation Architecture
- **Dual Engine System**: Modern (`review_generator.py`) vs Legacy (`old_review.py`)
- **Fallback Strategy**: CSV counting when APIs are down, manual tracking via JSON files
- **Internationalization**: Context-aware language generation (Gen Z slang vs traditional)
- **Product Categorization**: Automatic product type detection for relevant review context

### API Integration Patterns
- **ReviewsIOClient**: Class-based API wrapper with error handling
- **Klaviyo Integration**: Direct API calls with diagnostic endpoints for troubleshooting
- **Shopify API**: Handles both GraphQL and REST API patterns

### Important Implementation Details
- **CSV Export Naming**: Generated files use UUID pattern (e.g., `review_export_150f0ab9-09fe-445b-8854-d9ee9890ceb0.csv`)
- **Review Tracking**: Local JSON files persist generated review counts between sessions
- **Port Configuration**: Both apps run on port 5000 by default
- **Session Management**: Flask sessions used for OAuth state management in `app.py`
- **Error Handling**: APIs fail gracefully with CSV fallback for review counting