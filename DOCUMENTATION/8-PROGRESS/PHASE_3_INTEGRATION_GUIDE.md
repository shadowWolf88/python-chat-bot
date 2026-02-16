# Phase 3: API Route Integration Guide

## Quick Start

Add these routes to `api.py` to serve the new messaging interfaces:

---

## Route 1: Patient Messaging Page

```python
@app.route('/messages')
def messaging_page():
    """Main messaging interface for patients"""
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    # Get user role for template rendering
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        cur.execute('SELECT role FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        user_role = user['role'] if user else 'user'
    finally:
        conn.close()
    
    return render_template('messaging.html', 
                          username=username,
                          user_role=user_role)
```

**Location**: Add after existing page routes (around line 800-900 in api.py)

**Access**: `https://healing-space.org/messages`

**Security**:
- ✅ Requires active session
- ✅ Redirects to login if not authenticated
- ✅ Includes username in template context

---

## Route 2: Clinician Messaging Dashboard

```python
@app.route('/clinician/messaging')
def clinician_messaging():
    """Patient messaging dashboard for clinicians"""
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    # Verify clinician role
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        cur.execute('SELECT role FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        if not user or user['role'] != 'clinician':
            return jsonify({'error': 'Access denied'}), 403
    finally:
        conn.close()
    
    return render_template('clinician-messaging.html', 
                          username=username)
```

**Location**: Add after patient routes (around line 1000-1100 in api.py)

**Access**: `https://healing-space.org/clinician/messaging`

**Security**:
- ✅ Requires session
- ✅ Checks user role (must be 'clinician')
- ✅ Returns 403 if unauthorized

---

## Route 3: Admin Messaging Console

```python
@app.route('/admin/messaging')
def admin_messaging():
    """System-wide messaging administration console"""
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    # Verify admin role
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        cur.execute('SELECT role FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Access denied'}), 403
    finally:
        conn.close()
    
    return render_template('admin-messaging.html', 
                          username=username)
```

**Location**: Add after clinician routes (around line 1100-1200 in api.py)

**Access**: `https://healing-space.org/admin/messaging`

**Security**:
- ✅ Requires session
- ✅ Checks user role (must be 'admin')
- ✅ Returns 403 if unauthorized

---

## Additional Helper Routes (Optional but Recommended)

### Route 4: Get User List (for template autocomplete)

```python
@app.route('/api/users/search')
def search_users():
    """Search for users by username (for recipient autocomplete)"""
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'users': []})
    
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        cur.execute('''
            SELECT username, display_name 
            FROM users 
            WHERE username ILIKE %s OR display_name ILIKE %s
            AND username != %s
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%', username))
        
        users = [dict(row) for row in cur.fetchall()]
        return jsonify({'users': users})
    finally:
        conn.close()
```

**Usage**: Called by messaging.js when user types in recipient field
**Response**:
```json
{
  "users": [
    {"username": "patient_123", "display_name": "John Doe"},
    {"username": "patient_456", "display_name": "Jane Smith"}
  ]
}
```

---

### Route 5: Get User's Patients (for clinician dashboard)

```python
@app.route('/api/clinician/patients')
def get_clinician_patients():
    """Get list of patients assigned to clinician"""
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Verify clinician role
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        cur.execute('SELECT role FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        if not user or user['role'] != 'clinician':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get assigned patients with last message and unread count
        cur.execute('''
            SELECT 
                u.username,
                u.display_name as name,
                u.last_login,
                CASE WHEN u.last_login > NOW() - INTERVAL '1 day' THEN true ELSE false END as is_active,
                (SELECT COUNT(*) FROM messages 
                 WHERE from_user=u.username AND to_user=%s AND is_read=false) as unread_count,
                (SELECT sent_at FROM messages 
                 WHERE (from_user=u.username OR to_user=u.username)
                 ORDER BY sent_at DESC LIMIT 1) as last_message_time,
                (SELECT risk_level FROM risk_assessments 
                 WHERE username=u.username 
                 ORDER BY assessment_date DESC LIMIT 1) as risk_level
            FROM clinician_patients cp
            JOIN users u ON u.username = cp.patient_username
            WHERE cp.clinician_username = %s
            ORDER BY u.last_login DESC
        ''', (username, username))
        
        patients = [dict(row) for row in cur.fetchall()]
        return jsonify({'patients': patients})
    finally:
        conn.close()
```

**Usage**: Called by clinician-messaging.html on page load
**Filter Support**:
```python
# Add this inside the function to support filters:
filter_type = request.args.get('filter', 'all')

if filter_type == 'unread':
    cur.execute(...WHERE unread_count > 0...)
elif filter_type == 'today':
    cur.execute(...WHERE last_message_time > NOW() - INTERVAL '1 day'...)
elif filter_type == 'flagged':
    cur.execute(...WHERE is_flagged = true...)
```

---

### Route 6: Messaging Statistics

```python
@app.route('/api/messages/stats')
def get_message_stats():
    """Get messaging statistics for user"""
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = get_db_connection()
    cur = get_wrapped_cursor(conn)
    try:
        # Count various metrics
        cur.execute('''
            SELECT
                (SELECT COUNT(*) FROM messages 
                 WHERE from_user=%s OR to_user=%s) as total_messages,
                (SELECT COUNT(*) FROM messages 
                 WHERE to_user=%s AND is_read=false) as unread_messages,
                (SELECT COUNT(DISTINCT conversation_id) FROM messages 
                 WHERE from_user=%s OR to_user=%s) as active_conversations
        ''', (username, username, username, username, username))
        
        stats = dict(cur.fetchone())
        return jsonify(stats)
    finally:
        conn.close()
```

**Usage**: Display on dashboard cards
**Response**:
```json
{
  "total_messages": 1250,
  "unread_messages": 12,
  "active_conversations": 24
}
```

---

## Navigation Integration

Update the main navigation in templates to include messaging links:

### In base template or layout:
```html
<nav class="navbar">
    <div class="navbar-container">
        <a href="/" class="navbar-logo">Healing Space</a>
        <ul class="navbar-menu">
            <li><a href="/dashboard">Dashboard</a></li>
            <li><a href="/therapy">Therapy</a></li>
            <li><a href="/messages" class="nav-item">
                💬 Messages
                <span class="unread-badge" id="nav-unread" style="display:none;">0</span>
            </a></li>
            <li><a href="/wellness">Wellness</a></li>
            
            {% if user_role == 'clinician' %}
            <li><a href="/clinician/messaging">👥 Patient Messaging</a></li>
            {% endif %}
            
            {% if user_role == 'admin' %}
            <li><a href="/admin/messaging">⚙️ Messaging Console</a></li>
            {% endif %}
            
            <li><a href="/settings">Settings</a></li>
            <li><a href="/logout">Logout</a></li>
        </ul>
    </div>
</nav>

<script>
// Update unread badge on navbar
function updateNavUnreadBadge() {
    fetch('/api/messages/inbox?limit=1')
        .then(r => r.json())
        .then(d => {
            const badge = document.getElementById('nav-unread');
            const count = d.total_unread || 0;
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        });
}

// Update every 30 seconds
setInterval(updateNavUnreadBadge, 30000);
updateNavUnreadBadge(); // Initial load
</script>
```

---

## Testing the Routes

### Test Patient Route
```bash
# Login first, get session cookie
curl -c cookies.txt -d "username=patient1&password=..." \
  https://healing-space.org/login

# Access messaging page
curl -b cookies.txt https://healing-space.org/messages
# Expected: 200 OK with messaging.html
```

### Test Clinician Route
```bash
# Login as clinician
curl -c cookies.txt -d "username=clinician1&password=..." \
  https://healing-space.org/login

# Access clinician messaging
curl -b cookies.txt https://healing-space.org/clinician/messaging
# Expected: 200 OK with clinician-messaging.html

# Login as patient and try to access
curl -c cookies.txt -d "username=patient1&password=..." \
  https://healing-space.org/login

curl -b cookies.txt https://healing-space.org/clinician/messaging
# Expected: 403 Forbidden
```

### Test Admin Route
```bash
# Login as admin
curl -c cookies.txt -d "username=admin&password=..." \
  https://healing-space.org/login

# Access admin console
curl -b cookies.txt https://healing-space.org/admin/messaging
# Expected: 200 OK with admin-messaging.html
```

---

## Common Issues & Solutions

### Issue 1: Template not found
```
jinja2.exceptions.TemplateNotFound: messaging.html
```
**Solution**: Ensure files are in `/templates/` directory:
```bash
ls -la templates/messaging.html
ls -la templates/clinician-messaging.html
ls -la templates/admin-messaging.html
```

### Issue 2: CSS/JS not loading
```
404 Not Found: /static/js/messaging.js
```
**Solution**: Ensure files are in `/static/` directory:
```bash
ls -la static/js/messaging.js
ls -la static/css/messaging.css
```

### Issue 3: CSRF token missing
```
Errors in browser console: CSRF token invalid
```
**Solution**: Ensure CSRF token is set in template:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

### Issue 4: API endpoints returning 403
```
Error: Access denied
```
**Solution**: Verify user role in database:
```sql
SELECT username, role FROM users WHERE username='test_user';
```

---

## Summary

**Total New Routes**: 6 (3 required, 3 optional)  
**Total Lines**: ~250 lines of Python code  
**Integration Time**: 15-30 minutes  
**Testing Time**: 10-15 minutes  

**Next Steps**:
1. Add 3 page routes (messaging_page, clinician_messaging, admin_messaging)
2. Add 3 helper routes (search_users, get_clinician_patients, get_message_stats)
3. Update base navigation with messaging links
4. Test each route with different user roles
5. Commit and deploy to Railway

**Status**: Ready for integration ✅

