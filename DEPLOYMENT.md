# Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Prepare Repository
- Fork this repository to your GitHub account
- Ensure all files are committed and pushed

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your forked repository
5. Set main file: `streamlit_app.py`
6. Click "Deploy!"

### 3. Configure Secrets (Important!)
After deployment, go to your app settings and add these secrets:

```toml
# Required for AI functionality
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"

# Optional: Database connection (remove if using demo mode)
DB_HOST = "your_postgres_host"
DB_PORT = "5432"
DB_NAME = "sales_recommendation"
DB_USER = "your_postgres_user"
DB_PASSWORD = "your_postgres_password"
```

### 4. Get Groq API Key
1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for free account
3. Go to API Keys section
4. Create new API key
5. Copy the key (starts with "gsk_")

### 5. Database Options
**Option A: Demo Mode (Recommended for testing)**
- Don't add database secrets
- App will use built-in demo data
- Works immediately without setup

**Option B: Cloud Database**
- Use free tier from: Neon, Supabase, Railway, or ElephantSQL
- Add connection details to secrets
- Run `populate_synthetic_data.py` to set up schema

### 6. Troubleshooting
- **App not starting**: Check if all secrets are properly set
- **AI not working**: Verify GROQ_API_KEY is correct
- **Database errors**: Try demo mode first (remove DB secrets)

### 7. Features Available
- ✅ AI-powered recommendations
- ✅ Configurable result count (1-10)
- ✅ Cross-company suggestions
- ✅ Real-time processing
- ✅ Mobile-responsive interface

Your app will be available at:
`https://[your-app-name].streamlit.app`
