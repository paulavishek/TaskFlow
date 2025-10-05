# Google OAuth Setup Guide for TaskFlow

## Step-by-Step Configuration

### 1. Google Cloud Console Setup

#### A. Authorized JavaScript Origins
Add these URLs (one per line):
```
http://localhost:8000
http://127.0.0.1:8000
```

#### B. Authorized Redirect URIs
Add these URLs (one per line):
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

### 2. Get Your Credentials

After clicking "Create", you'll receive:
- **Client ID**: `xxxxx-yyyyy.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-xxxxxxxxxxxxxxxxxxxxx`

### 3. Update Your .env File

Open your `.env` file and add/update these lines:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH2_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-actual-client-secret
```

**Important:** Replace the values with your actual credentials from Google Cloud Console!

### 4. Verify Django Settings

Your `settings.py` should already have this (it does):

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'FETCH_USERINFO': True,
    }
}
```

### 5. Set Up Social Application in Django Admin

**IMPORTANT:** You also need to configure the social app in Django admin:

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Go to Django Admin:**
   ```
   http://localhost:8000/admin
   ```

3. **Navigate to:** Sites → Social applications → Add social application

4. **Fill in the form:**
   - **Provider:** Google
   - **Name:** Google (or any name you like)
   - **Client id:** [Paste your Client ID from Google]
   - **Secret key:** [Paste your Client Secret from Google]
   - **Sites:** Select "example.com" and move it to "Chosen sites"
   
5. **Click Save**

### 6. Test the Login

1. **Go to your login page:**
   ```
   http://localhost:8000/accounts/login/
   ```

2. **Click "Sign in with Google"**

3. **You should be redirected to Google's login page**

4. **After authentication, you'll be redirected back to TaskFlow**

### 7. Common Issues & Solutions

#### Issue: "redirect_uri_mismatch" error
**Solution:** 
- Check that redirect URIs match exactly (including trailing slash!)
- Verify you're using the correct port (8000, not 3000)
- Clear browser cache and try again

#### Issue: "invalid_client" error
**Solution:**
- Verify Client ID and Secret are correct in .env
- Make sure .env file is in the project root
- Restart Django server after updating .env

#### Issue: Google login button doesn't appear
**Solution:**
- Create Social Application in Django admin (Step 5)
- Check that django-allauth is in INSTALLED_APPS
- Verify Google provider is configured

#### Issue: "Site matching query does not exist"
**Solution:**
In Django admin, go to Sites and make sure there's a site with:
- Domain: localhost:8000
- Display name: TaskFlow Local

### 8. For Production Deployment

When deploying to production, add your production URLs:

#### Authorized JavaScript Origins:
```
https://your-domain.com
https://www.your-domain.com
```

#### Authorized Redirect URIs:
```
https://your-domain.com/accounts/google/login/callback/
https://www.your-domain.com/accounts/google/login/callback/
```

Also update your Django Site in admin to match your production domain.

### 9. Security Checklist

- [ ] Never commit .env file to git (.gitignore should exclude it)
- [ ] Use HTTPS in production
- [ ] Restrict OAuth consent screen to your domain if possible
- [ ] Regularly rotate Client Secret if compromised
- [ ] Monitor OAuth usage in Google Cloud Console

### 10. Testing Checklist

- [ ] Google login button appears on login page
- [ ] Clicking button redirects to Google
- [ ] After Google auth, redirects back to TaskFlow
- [ ] User is created/logged in successfully
- [ ] User profile is created with organization
- [ ] Email and username are populated correctly

---

## Quick Reference

**Development URLs:**
- JavaScript Origin: `http://localhost:8000`
- Redirect URI: `http://localhost:8000/accounts/google/login/callback/`

**Files to Update:**
- `.env` - Add Client ID and Secret
- Django Admin - Create Social Application

**Test URL:**
- http://localhost:8000/accounts/login/

---

## Need Help?

If you encounter issues:
1. Check Django server logs for errors
2. Check browser console for JavaScript errors
3. Verify all steps above are completed
4. Check .env file is loaded (print settings in Django shell)

---

*Last Updated: October 5, 2025*
*For TaskFlow - Gemini-Powered Kanban Board*
