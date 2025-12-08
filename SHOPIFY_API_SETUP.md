# Shopify Admin API Setup Guide

## Getting Your Shopify Admin API Access Token

### Step 1: Create a Custom App

1. Go to your Shopify Admin: `https://your-store.myshopify.com/admin`
2. Click **Settings** (bottom left)
3. Click **Apps and sales channels**
4. Click **Develop apps** (top right)
5. Click **Create an app**
6. Enter app name: `Product Automation` (or any name)
7. Click **Create app**

### Step 2: Configure API Scopes

1. Click **Configure Admin API scopes**
2. Scroll down and enable these scopes:

**Required Scopes:**
- ✅ `write_products` - Create and update products
- ✅ `read_products` - Read product data

**Optional (but recommended):**
- ✅ `write_inventory` - Manage inventory
- ✅ `read_inventory` - Read inventory levels
- ✅ `write_product_listings` - Publish products
- ✅ `read_product_listings` - Read published products

3. Click **Save**

### Step 3: Install the App

1. Click **Install app** (top right)
2. Click **Install** to confirm

### Step 4: Get Your Access Token

1. After installation, you'll see **Admin API access token**
2. Click **Reveal token once**
3. **COPY THIS TOKEN IMMEDIATELY** - you can only see it once!
4. The token looks like: `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 5: Add to Your .env File

```env
SHOPIFY_SHOP_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Important Notes

### Token Security
- ⚠️ **Never share your access token**
- ⚠️ **Never commit it to git**
- ⚠️ **Store it in .env file only**
- ⚠️ **You can only see it once** - save it immediately

### Token Format
```
Correct: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Wrong: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx (missing shpat_ prefix)
```

### Shop URL Format
```
Correct: https://your-store.myshopify.com
Wrong: your-store.myshopify.com (missing https://)
Wrong: https://your-store.com (must use .myshopify.com)
```

## Testing Your Token

### Test with cURL
```bash
curl -X GET "https://your-store.myshopify.com/admin/api/2024-07/products.json?limit=1" \
  -H "X-Shopify-Access-Token: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

If successful, you'll see product data. If not, check:
- Token is correct
- Shop URL is correct
- Scopes are enabled

### Test in the App
1. Start the app: `python app.py`
2. Login (Mahad/Mahad)
3. Go to Products page
4. Try pushing a product to Shopify
5. Check logs for success/error messages

## Troubleshooting

### Error: "Invalid API key or access token"
**Solution**: 
- Check token is copied correctly (including `shpat_` prefix)
- Check no extra spaces in .env file
- Regenerate token if needed

### Error: "Insufficient permissions"
**Solution**:
- Go back to app settings
- Enable `write_products` scope
- Reinstall the app

### Error: "Shop not found"
**Solution**:
- Check SHOPIFY_SHOP_URL format
- Must be: `https://your-store.myshopify.com`
- Not your custom domain

### How to Regenerate Token

If you lost your token:
1. Go to Shopify Admin → Settings → Apps and sales channels
2. Click **Develop apps**
3. Click your app name
4. Click **API credentials** tab
5. Under **Admin API access token**, click **Revoke**
6. Click **Create new access token**
7. Copy the new token

## API Rate Limits

Shopify has rate limits:
- **REST Admin API**: 2 requests per second
- **GraphQL Admin API**: 50 points per second

This app automatically handles rate limits with:
- 0.6 second delay between requests
- Stays under 2 requests/second limit

## Scopes Explained

### write_products
- Create new products
- Update existing products
- Delete products
- Add product images
- Set product variants

### read_products
- Get product details
- Search products
- List all products
- Read product variants

### write_inventory
- Update inventory quantities
- Set inventory tracking
- Manage inventory locations

### read_inventory
- Check stock levels
- View inventory locations
- Read inventory history

## Security Best Practices

1. **Use environment variables**
   ```env
   # .env file (never commit this)
   SHOPIFY_ACCESS_TOKEN=shpat_xxx
   ```

2. **Add .env to .gitignore**
   ```
   .env
   *.env
   .env.local
   ```

3. **Rotate tokens regularly**
   - Regenerate every 90 days
   - Regenerate if compromised

4. **Use minimal scopes**
   - Only enable what you need
   - Don't enable `write_orders` if not needed

5. **Monitor API usage**
   - Check Shopify Admin → Apps
   - Review API call logs

## Production Deployment

### Railway/Heroku
Set environment variables in dashboard:
```
SHOPIFY_SHOP_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Docker
Pass as environment variables:
```bash
docker run -e SHOPIFY_ACCESS_TOKEN=shpat_xxx myapp
```

## Support

### Shopify API Documentation
- https://shopify.dev/docs/api/admin-rest
- https://shopify.dev/docs/apps/auth/admin-app-access-tokens

### Common Issues
- Token format: Must start with `shpat_`
- URL format: Must be `https://store.myshopify.com`
- Scopes: Must have `write_products` enabled

---

**You're all set!** 🎉

Your Shopify Admin API token is ready to use. Add it to your `.env` file and start automating!
