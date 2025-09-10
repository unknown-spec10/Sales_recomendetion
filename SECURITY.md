# 🔐 Security Guide - API Key Management

## ⚠️ NEVER Commit API Keys to Git!

### ✅ **Secure Setup (Required Steps):**

1. **Create `.env` file locally:**
   ```bash
   cp .env.example .env
   ```

2. **Add your actual API key to `.env`:**
   ```bash
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=sales_recommendation
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

3. **Verify `.env` is in `.gitignore`:**
   ```bash
   # Should be listed in .gitignore (already added)
   .env
   ```

### 🌐 **For Streamlit Cloud:**
- **Don't use `.env` file**
- Add secrets in Streamlit Cloud dashboard:
  - Go to app settings → "Secrets"
  - Add in TOML format:
    ```toml
    GROQ_API_KEY = "gsk_your_actual_key_here"
    DB_HOST = "your_postgres_host"
    ```

### 🚫 **What NOT to Do:**
- ❌ Never hardcode API keys in `.py` files
- ❌ Never commit `.env` files
- ❌ Never share API keys in chat/email
- ❌ Never push secrets to public repos

### ✅ **What TO Do:**
- ✅ Use environment variables (`os.getenv()`)
- ✅ Keep API keys in `.env` (local) or Streamlit secrets (cloud)
- ✅ Use `.env.example` as a template
- ✅ Add sensitive files to `.gitignore`

### 🔄 **If You Accidentally Committed a Secret:**
1. **Immediately revoke/regenerate** the API key at provider
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch file_with_secret.py' --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
3. **Add to `.gitignore`** and commit proper version

### 🔑 **Get Groq API Key:**
1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for free account
3. Go to API Keys section
4. Create new key
5. Copy key (starts with `gsk_`)
6. Add to your `.env` file

---
**Remember: Security is everyone's responsibility! 🛡️**
