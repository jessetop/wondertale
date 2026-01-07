# Railway Troubleshooting Guide

## Quick Diagnosis Steps

### 1. Check Health Endpoint
Visit: `https://your-app.railway.app/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "children-story-generator",
  "version": "1.0.0",
  "openai_configured": true,  // ← Should be true
  "environment": "production"
}
```

**If `openai_configured` is false:**
- OpenAI API key is not set or incorrect in Railway environment variables

### 2. Check Debug Endpoint (Temporary)
Visit: `https://your-app.railway.app/debug`

This will show detailed environment variable status.

### 3. Check Railway Logs
1. Go to Railway Dashboard
2. Select your project
3. Click "Deployments" → "View Logs"
4. Try generating a story and watch for error messages

## Common Issues & Solutions

### Issue 1: "openai_configured": false
**Cause:** API key not set in Railway environment variables

**Solution:**
1. Go to Railway Dashboard → Your Project → Variables
2. Add: `OPENAI_API_KEY` = `your_actual_openai_api_key_here`
3. Redeploy

### Issue 2: Import Errors
**Cause:** Missing dependencies or version conflicts

**Solution:**
1. Check Railway build logs for pip install errors
2. Verify requirements.txt has correct versions
3. Force redeploy

### Issue 3: OpenAI API Errors
**Cause:** API key invalid, billing issues, or rate limits

**Solution:**
1. Verify API key is correct in OpenAI dashboard
2. Check OpenAI billing status
3. Check OpenAI usage limits

### Issue 4: Worker Timeout Errors
**Error:** `WORKER TIMEOUT (pid:X)` or `Worker exited with code 1`
**Cause:** OpenAI API calls taking longer than Railway worker timeout

**Solution:**
1. **Immediate Fix:** The app now includes:
   - OpenAI client timeout set to 25 seconds
   - Gunicorn worker timeout increased to 60 seconds
   - Retry logic for failed API calls

2. **If still occurring:**
   - Check OpenAI API status at status.openai.com
   - Monitor Railway logs during story generation
   - Consider using shorter story lengths during high API load

3. **Emergency fallback:**
   - App will automatically use placeholder stories if OpenAI fails
   - Users will still get a story, just not AI-generated

### Issue 5: Story Generation Timeout
**Cause:** OpenAI API taking too long

**Solution:**
1. Check Railway logs for timeout errors
2. App now includes automatic retry logic
3. Fallback to placeholder stories on persistent failures

## Railway Environment Variables Checklist

Required variables in Railway Dashboard:
```
OPENAI_API_KEY = sk-proj-... (your actual key)
FLASK_SECRET_KEY = (secure random string)
```

Optional variables (can be in railway.toml):
```
FLASK_ENV = production
MAX_STORY_LENGTH = 400
DEFAULT_VOICE_SPEED = 0.8
PORT = 5000
```

## Debug Commands

### Test Locally First
```bash
# Test locally to ensure it works
python test_story_generation.py
```

### Check Railway Deployment
```bash
# If you have Railway CLI
railway logs
railway variables
```

## Emergency Fixes

### 1. Enable Debug Mode Temporarily
Add to Railway environment variables:
```
DEBUG_ENABLED = true
```

Then visit `/debug` endpoint for detailed diagnostics.

### 2. Rollback to Working Version
In Railway Dashboard:
1. Go to Deployments
2. Find last working deployment
3. Click "Redeploy"

### 3. Force Fresh Deploy
```bash
# Make a small change and push
git commit --allow-empty -m "Force redeploy"
git push
```

## Timeout Prevention & Monitoring

### Current Timeout Configurations
- **OpenAI Client Timeout:** 25 seconds
- **Gunicorn Worker Timeout:** 60 seconds  
- **Railway Health Check Timeout:** 300 seconds
- **Retry Logic:** Up to 3 attempts for OpenAI API calls

### Monitoring Tips
1. **Watch Railway Logs:** Look for these patterns:
   ```
   DEBUG: OpenAI API call attempt 1/3
   DEBUG: Story generated successfully
   ```

2. **Check Response Times:** Story generation should complete in 10-30 seconds

3. **Monitor Error Patterns:**
   - Frequent timeouts → OpenAI API issues
   - Worker restarts → Memory or timeout issues
   - Import errors → Dependency problems

### Performance Optimization
- Stories are cached at the template level
- Placeholder stories used as fallback
- Retry logic prevents single API failures
- Worker timeout allows for slow API responses

## Contact Information
If issues persist, check:
1. Railway status page
2. OpenAI status page
3. Application logs for specific error messages