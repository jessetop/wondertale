# Railway Worker Timeout Fixes

## Problem
Railway was showing worker timeout errors:
```
[CRITICAL] WORKER TIMEOUT (pid:4)
[ERROR] Worker (pid:4) exited with code 1
```

This happens when OpenAI API calls take longer than Railway's default worker timeout.

## Root Cause
- OpenAI API calls can take 10-30+ seconds
- Railway's default worker timeout is 30 seconds
- No timeout configuration on OpenAI client
- No retry logic for failed API calls

## Solutions Implemented

### 1. OpenAI Client Timeout Configuration
**File:** `services/story_generator.py`
```python
self.client = OpenAI(
    api_key=api_key,
    timeout=25.0  # 25 seconds timeout (Railway default worker timeout is 30s)
)
```

### 2. Gunicorn Worker Timeout
**Files:** `Procfile`, `railway.toml`
```bash
# Procfile
web: gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 2 --worker-class sync app:app

# railway.toml
healthcheckTimeout = 300
startCommand = "gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 2 --worker-class sync app:app"
```

### 3. Retry Logic for OpenAI API Calls
**File:** `services/story_generator.py`
```python
max_retries = 2
for attempt in range(max_retries + 1):
    try:
        response = self.client.chat.completions.create(...)
        break  # Success, exit retry loop
    except Exception as api_error:
        if attempt == max_retries:
            raise api_error
        time.sleep(1)  # Brief wait before retry
```

### 4. Enhanced Logging
**File:** `app.py`
```python
start_time = time.time()
# ... story generation ...
generation_time = time.time() - start_time
print(f"DEBUG: Story generated successfully in {generation_time:.2f}s")
```

### 5. Updated Troubleshooting Guide
**File:** `railway_troubleshooting.md`
- Added worker timeout error section
- Added monitoring and prevention tips
- Added performance optimization notes

## Timeout Configuration Summary

| Component | Timeout | Purpose |
|-----------|---------|---------|
| OpenAI Client | 25 seconds | Prevent API calls from hanging |
| Gunicorn Worker | 60 seconds | Allow time for OpenAI + processing |
| Railway Health Check | 300 seconds | Allow for app startup |
| Retry Logic | 3 attempts | Handle temporary API failures |

## Expected Results

1. **Reduced Worker Timeouts:** OpenAI calls will timeout before Railway workers
2. **Better Error Handling:** Failed API calls will retry automatically
3. **Graceful Degradation:** Placeholder stories if OpenAI consistently fails
4. **Better Monitoring:** Detailed logs for debugging timeout issues

## Deployment

Changes are automatically deployed to Railway when pushed to main branch.

Monitor Railway logs after deployment to verify:
```
DEBUG: OpenAI API call attempt 1/3
DEBUG: Story generated successfully in 12.34s
```

## Rollback Plan

If issues persist, the app will automatically fall back to placeholder stories, ensuring users always get a story even if OpenAI is unavailable.