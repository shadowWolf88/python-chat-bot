# DNS Setup Guide - Connect Custom Domain to Railway

## Step 1: Get Your Railway Domain

1. Go to your Railway dashboard: https://railway.app
2. Select your project (python-chat-bot)
3. Click on your service (api.py deployment)
4. Go to the **Settings** tab
5. Scroll to **Domains** section
6. You'll see your default Railway domain (e.g., `your-app.up.railway.app`)

## Step 2: Add Custom Domain in Railway

1. In the same **Domains** section, click **+ Custom Domain**
2. Enter your purchased domain (e.g., `yourdomain.com` or `www.yourdomain.com`)
3. Railway will show you DNS records you need to add
4. Keep this page open - you'll need these values

**Railway typically requires:**
- For root domain (`yourdomain.com`): CNAME or A record
- For subdomain (`www.yourdomain.com`): CNAME record

## Step 3: Configure DNS at Your Domain Registrar

### Common Registrars:

#### **GoDaddy:**
1. Log in to GoDaddy
2. Go to **My Products** → **Domains**
3. Click **DNS** next to your domain
4. Click **Add** to create new record
5. Add the records Railway provided:
   - **Type**: CNAME (or A if Railway gave you an IP)
   - **Name**: @ (for root) or www (for subdomain)
   - **Value**: Your Railway domain (e.g., `your-app.up.railway.app`)
   - **TTL**: 600 seconds (10 minutes)
6. Click **Save**

#### **Namecheap:**
1. Log in to Namecheap
2. Go to **Domain List** → Click **Manage** on your domain
3. Go to **Advanced DNS** tab
4. Click **Add New Record**
5. Add:
   - **Type**: CNAME Record
   - **Host**: @ (for root) or www (for subdomain)
   - **Value**: Your Railway domain
   - **TTL**: Automatic
6. Click **Save**

#### **Cloudflare:**
1. Log in to Cloudflare
2. Select your domain
3. Go to **DNS** → **Records**
4. Click **Add record**
5. Add:
   - **Type**: CNAME
   - **Name**: @ (for root) or www (for subdomain)
   - **Target**: Your Railway domain
   - **Proxy status**: Orange cloud (Proxied) ✅
   - **TTL**: Auto
6. Click **Save**

#### **Google Domains:**
1. Log in to Google Domains
2. Select your domain
3. Click **DNS** in the left menu
4. Scroll to **Custom resource records**
5. Add:
   - **Name**: @ (for root) or www (for subdomain)
   - **Type**: CNAME
   - **TTL**: 1H
   - **Data**: Your Railway domain
6. Click **Add**

#### **Other Registrars:**
Look for:
- DNS Settings / DNS Management / Name Server Management
- Add CNAME record pointing to your Railway domain

## Step 4: Common DNS Records Needed

### Option A: Subdomain Only (Recommended for beginners)
```
Type:  CNAME
Name:  www
Value: your-app.up.railway.app
TTL:   600 or Auto
```

### Option B: Root Domain (requires special handling)
Some registrars don't allow CNAME on root domain. Options:

**If Railway provides A records:**
```
Type:  A
Name:  @
Value: XXX.XXX.XXX.XXX (IP from Railway)
TTL:   600
```

**If using Cloudflare/CNAME flattening:**
```
Type:  CNAME
Name:  @
Value: your-app.up.railway.app
TTL:   Auto
```

### Both Root and Subdomain:
Add both records above, plus optionally redirect one to the other.

## Step 5: SSL Certificate (HTTPS)

Railway automatically provisions SSL certificates via Let's Encrypt once DNS is verified.

**This takes 5-10 minutes after DNS propagation.**

You'll see in Railway dashboard:
- ✅ DNS verified
- ✅ Certificate issued
- Your site will be accessible via HTTPS

## Step 6: Verification & Testing

### Check DNS Propagation (takes 5 minutes to 48 hours)

**Online tools:**
- https://www.whatsmydns.net (check from multiple locations)
- https://dnschecker.org

**Command line:**
```bash
# Check CNAME record
dig www.yourdomain.com CNAME

# Check A record
dig yourdomain.com A

# Check from specific DNS server (Google)
dig @8.8.8.8 yourdomain.com
```

**Expected output:**
```
www.yourdomain.com.  600  IN  CNAME  your-app.up.railway.app.
```

### Test Your Site:
```bash
# Check if responding
curl -I https://yourdomain.com

# Or visit in browser
https://yourdomain.com
```

## Common Issues & Solutions

### ❌ "Domain not verified" in Railway
- **Cause**: DNS not propagated yet
- **Solution**: Wait 10-30 minutes, Railway checks automatically

### ❌ "Too many redirects"
- **Cause**: Cloudflare SSL mode incorrect
- **Solution**: Set Cloudflare SSL to "Full" or "Full (strict)"

### ❌ "CNAME not allowed on root domain"
- **Cause**: Some DNS providers don't support it
- **Solution**: 
  1. Use Railway's A record instead (if provided)
  2. Use a subdomain (www.yourdomain.com)
  3. Switch to Cloudflare (supports CNAME flattening)

### ❌ Certificate provisioning failed
- **Cause**: DNS not pointing correctly
- **Solution**: Verify CNAME points to Railway domain, wait for DNS propagation

### ❌ "This site can't be reached"
- **Cause**: DNS not propagated or incorrect value
- **Solution**: 
  1. Check DNS records in your registrar
  2. Verify Railway domain is correct
  3. Wait 24-48 hours for full global propagation

## Quick Reference Commands

```bash
# Check what your domain resolves to
nslookup yourdomain.com

# Check CNAME specifically
nslookup -type=CNAME www.yourdomain.com

# Flush local DNS cache (if testing)
# Linux:
sudo systemd-resolve --flush-caches

# Mac:
sudo dscacheutil -flushcache

# Windows:
ipconfig /flushdns
```

## Recommended Setup

**Best practice for production:**

1. **Primary domain**: `yourdomain.com` (root)
   - Add A record pointing to Railway IP
   
2. **WWW redirect**: `www.yourdomain.com`
   - Add CNAME pointing to Railway domain
   
3. **Use Cloudflare** (optional but recommended):
   - Free CDN
   - DDoS protection
   - Automatic HTTPS
   - CNAME flattening for root domain

## Need Help?

1. **Railway Discord**: https://discord.gg/railway
2. **Railway Docs**: https://docs.railway.app/deploy/custom-domains
3. **Your registrar's support** (they can help with DNS records)

## Example: Complete Setup

**Domain**: `healingspace.com`
**Railway domain**: `python-chat-bot-production.up.railway.app`

**DNS Records to add:**
```
Type   Name   Value                                        TTL
CNAME  www    python-chat-bot-production.up.railway.app   600
CNAME  @      python-chat-bot-production.up.railway.app   600
```

**Timeline:**
- ⏱️ 0 min: Add DNS records
- ⏱️ 5-10 min: DNS starts propagating
- ⏱️ 10-15 min: Railway verifies domain
- ⏱️ 15-20 min: SSL certificate issued
- ✅ 20-30 min: Site live on custom domain with HTTPS

---

## One-Time Setup Checklist

- [ ] Log in to Railway, get your deployment URL
- [ ] Add custom domain in Railway dashboard
- [ ] Note the DNS records Railway shows
- [ ] Log in to your domain registrar
- [ ] Add CNAME record (or A record if required)
- [ ] Wait 10-30 minutes for DNS propagation
- [ ] Verify domain shows "verified" in Railway
- [ ] Check SSL certificate is issued
- [ ] Test site at https://yourdomain.com
- [ ] Update links in your app if needed

**That's it! Your site will be live on your custom domain.**
