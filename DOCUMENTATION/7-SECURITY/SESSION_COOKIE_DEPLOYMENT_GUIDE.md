# Session Cookie Issue - Production Fix

## Problem
Users on `https://www.healing-space.org.uk` are getting 401 errors on all API endpoints because the session cookie is not being sent with requests.

## Root Cause
The session cookie domain is not configured to work across subdomains. When a user logs in on `www.healing-space.org.uk`, the session cookie is set with domain limitations that prevent it from being sent to API endpoints.

## Solution

### For Railway Deployment

1. **Set Environment Variable on Railway Dashboard:**
   ```
   SESSION_COOKIE_DOMAIN=.healing-space.org.uk
   ```

   This allows the session cookie to work across all subdomains:
   - `www.healing-space.org.uk`
   - `api.healing-space.org.uk`
   - `admin.healing-space.org.uk`
   - Any other subdomain

2. **Restart the Application:**
   - Redeploy after setting the environment variable
   - Railway will automatically restart the container

### Configuration Details

The application now supports:
- `SESSION_COOKIE_DOMAIN` - Configure in api.py line 299
- `SESSION_COOKIE_SECURE` - Automatically set based on DEBUG flag
- `SESSION_COOKIE_SAMESITE` - Set to 'Lax' for CSRF protection
- `SESSION_COOKIE_HTTPONLY` - Set to True for security

### Code Changes (Already Applied)

**api.py line 299:**
```python
app.config['SESSION_COOKIE_DOMAIN'] = os.getenv('SESSION_COOKIE_DOMAIN', None)
```

**templates/index.html line 15592:**
```javascript
// Improved error messaging with logout link
container.innerHTML = '<p style="color: #e74c3c; padding: 20px;">⚠️ Session expired. Please <a href="/logout" style="color: #667eea; text-decoration: underline;">log in again</a></p>';
```

**api.py line 2268-2281:**
```python
@app.route('/api/auth/status', methods=['GET'])
def get_auth_status():
    """Check current authentication status (DEBUG endpoint)"""
    username = session.get('username')
    role = session.get('role')
    is_authenticated = bool(username and role)
    
    return jsonify({
        'authenticated': is_authenticated,
        'username': username,
        'role': role,
        'session_exists': bool(session),
        'debug_mode': DEBUG
    }), 200
```

## Verification Steps

After deploying:

1. **Check Application Status:**
   ```bash
   curl https://www.healing-space.org.uk/api/auth/status
   # Should return JSON with authentication info
   ```

2. **Check Session Cookie:**
   - Open DevTools → Application → Cookies
   - Look for a cookie named `session` (not just `csrf_token`)
   - It should have domain: `.healing-space.org.uk` (with dot prefix)

3. **Test Message Loading:**
   - Log in to the app
   - Navigate to Messages tab
   - Inbox should load (not show "Please log in again")

4. **Monitor Logs:**
   - Check Railway logs for any session-related errors
   - Look for successful database connection messages

## Expected Behavior After Fix

1. User logs in at `www.healing-space.org.uk`
2. Session cookie is created with domain `.healing-space.org.uk`
3. Cookie is automatically sent to all API endpoints
4. API returns 200 OK instead of 401
5. User can access messages, home data, wellness rituals, etc.

## Testing Checklist

- [ ] Session cookie appears in browser DevTools
- [ ] Cookie domain includes `.healing-space.org.uk`
- [ ] `curl /api/auth/status` returns `authenticated: true`
- [ ] Messages inbox loads without errors
- [ ] No more "Please log in again" errors
- [ ] User stays logged in when navigating between pages
- [ ] Session persists across subdomain requests

## If Issue Persists

1. **Check Environment Variable:**
   ```bash
   # On Railway dashboard, verify:
   SESSION_COOKIE_DOMAIN=.healing-space.org.uk
   ```

2. **Clear Browser Cookies:**
   - Delete all cookies for `healing-space.org.uk`
   - Log out and log back in
   - Try accessing messages again

3. **Check Application Startup Logs:**
   - Look for "Application starting - DEBUG=False"
   - Verify no errors during initialization
   - Check database connection is successful

4. **Run Debug Endpoint:**
   ```bash
   curl -b "session=<your_session_cookie>" https://www.healing-space.org.uk/api/auth/status
   ```

## Related Changes

- Commit: `ff6b96f` - Session cookie domain configuration
- Commit: `ff6b96f` - Added /api/auth/status debug endpoint
- Commit: `ff6b96f` - Improved error messaging on 401 errors

---

*Last Updated: February 12, 2026*
