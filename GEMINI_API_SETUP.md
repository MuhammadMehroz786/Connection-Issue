# Google Gemini API Setup Guide

## Getting Your Gemini API Key

### Step 1: Go to Google AI Studio

Visit: https://aistudio.google.com/apikey

### Step 2: Sign In

- Sign in with your Google account
- Accept the terms of service if prompted

### Step 3: Create API Key

1. Click **"Get API key"** or **"Create API key"**
2. Select **"Create API key in new project"** (or use existing project)
3. Copy the API key (starts with `AIza...`)

### Step 4: Add to .env File

```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Verify Your API Key

Test if your key works:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```

If valid, you'll see a list of available models.

## Common Issues

### Error: "API key not valid"

**Causes**:
1. API key is incorrect or has typos
2. API key has extra spaces
3. API key is not enabled for Gemini API
4. Billing is not enabled (if required)

**Solutions**:
1. Copy the key again from Google AI Studio
2. Check for spaces: `GOOGLE_API_KEY=AIza...` (no spaces around `=`)
3. Enable Gemini API in Google Cloud Console
4. Check if billing is required for your usage

### Error: "Quota exceeded"

**Solution**: 
- Gemini has free tier limits
- Wait for quota to reset (usually daily)
- Or upgrade to paid tier

### Error: "Model not found"

**Solution**:
- Make sure you're using `gemini-2.5-flash-image` model
- Check if model is available in your region

## API Limits (Free Tier)

- **Requests per minute**: 15
- **Requests per day**: 1,500
- **Tokens per minute**: 1 million

## Disable AI Image Generation (Optional)

If you don't want to use Gemini for image generation, you can:

1. **Skip AI enhancement**: Don't click "Create AI Dupe" button
2. **Push products directly**: Use "Send All to Shopify" without AI enhancement
3. **Remove Gemini requirement**: Comment out `GOOGLE_API_KEY` validation in app.py

## Alternative: Use Without Gemini

If you want to push products without AI image generation:

1. Don't use the "Create AI Dupe" feature
2. Push products directly from the Products page
3. Products will use original images (no AI enhancement)

## Cost Estimation

### Free Tier
- 1,500 requests/day = FREE
- Good for testing and small batches

### Paid Tier
- Gemini 2.5 Flash: ~$0.001 per image
- 1000 images = ~$1.00

## Summary

✅ Get API key from: https://aistudio.google.com/apikey
✅ Add to `.env`: `GOOGLE_API_KEY=AIza...`
✅ No spaces, no quotes
✅ Test with curl command
✅ Check free tier limits

---

**Need help?** Check Google AI Studio documentation: https://ai.google.dev/
