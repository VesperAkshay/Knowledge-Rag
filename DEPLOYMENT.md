# 🚀 DEPLOYMENT CHECKLIST

## ✅ Pre-Deployment Steps (DONE)
- [x] Created `requirements.txt`
- [x] Created `render.yaml`
- [x] Updated frontend to use environment variables
- [x] Created deployment documentation

---

## 📦 PART 1: Deploy Backend on Render (15 minutes)

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Get Started" 
3. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New +" button (top right)
2. Select "Web Service"
3. Click "Connect GitHub"
4. Search for and select: `VesperAkshay/Knowledge-Rag`
5. Click "Connect"

### Step 3: Configure Service
```
Name: rag-knowledge-backend
Region: Oregon (US West) - or closest to you
Branch: main
Root Directory: (leave empty)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Step 4: Add Environment Variables
Click "Advanced" → Add these environment variables:

```
GOOGLE_API_KEY = your_google_api_key_here
CHROMADB_API_KEY = your_chromadb_api_key_here
CHROMADB_TENANT = your_chromadb_tenant_id_here
CHROMADB_DATABASE = your_database_name_here
LANGSMITH_TRACING = true
LANGSMITH_API_KEY = your_langsmith_api_key_here (optional)
```

⚠️ **Get your values from your `.env` file** - Don't commit real keys!

### Step 5: Deploy
1. Select "Free" plan
2. Click "Create Web Service"
3. Wait 5-10 minutes for deployment
4. **COPY YOUR BACKEND URL** (e.g., `https://rag-knowledge-backend.onrender.com`)

### Step 6: Test Backend
Visit: `https://YOUR-BACKEND-URL.onrender.com/docs`
- You should see the FastAPI Swagger documentation

---

## 🎨 PART 2: Deploy Frontend on Vercel (10 minutes)

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub

### Step 2: Import Project
1. Click "Add New..." → "Project"
2. Find and select: `VesperAkshay/Knowledge-Rag`
3. Click "Import"

### Step 3: Configure Build Settings
```
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: (leave as default .next)
Install Command: npm install
Node Version: 18.x
```

### Step 4: Add Environment Variable
Click "Environment Variables" and add:

```
Name: NEXT_PUBLIC_API_URL
Value: https://YOUR-BACKEND-URL.onrender.com
```
⚠️ **IMPORTANT**: Replace with your actual Render backend URL from Part 1, Step 5!

### Step 5: Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. You'll get a URL like: `https://knowledge-rag.vercel.app`

### Step 6: Test Your App
1. Visit your Vercel URL
2. You should see the login page
3. Register a new account
4. Add your API credentials in settings
5. Try uploading a document
6. Try asking a question

---

## 🔧 PART 3: Push Changes to GitHub

Run these commands in your terminal:

```bash
# Add all changes
git add .

# Commit
git commit -m "Add deployment configuration"

# Push to GitHub
git push origin main
```

This will automatically trigger re-deployment on both Render and Vercel!

---

## ⚠️ Important Notes

### For Render (Backend):
- ✅ Free tier sleeps after 15 minutes of inactivity
- ✅ First request after sleep takes 30-60 seconds
- ✅ Your app will restart automatically
- ✅ Database is stored locally (SQLite persists)

### For Vercel (Frontend):
- ✅ Always fast and available
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Instant cache updates

### CORS Configuration:
The backend is already configured to accept requests from any origin. If you need to restrict it:

1. Edit `backend/core/config.py`
2. Change `CORS_ORIGINS: list = ["*"]` to your Vercel URL:
   ```python
   CORS_ORIGINS: list = ["https://knowledge-rag.vercel.app"]
   ```

---

## 🎉 You're Done!

Your app is now live at:
- **Frontend**: `https://YOUR-APP.vercel.app`
- **Backend**: `https://YOUR-APP.onrender.com`

### What Users Can Do:
1. Register/Login
2. Add their API credentials (Google & ChromaDB)
3. Upload documents (PDF, DOCX, TXT)
4. Add URLs to knowledge base
5. Chat with AI using their documents
6. AI automatically searches web when needed

### Maintenance:
- Every `git push` automatically redeploys
- Check Render dashboard for backend logs
- Check Vercel dashboard for frontend logs
- Monitor your API usage on Google Cloud Console

---

## 📞 Troubleshooting

### Backend not responding?
- Check Render logs
- Verify environment variables are set
- Test the `/docs` endpoint

### Frontend can't connect to backend?
- Verify `NEXT_PUBLIC_API_URL` in Vercel
- Check CORS settings
- Check browser console for errors

### Database issues?
- Render's free tier resets storage on redeploy
- Consider upgrading to paid tier for persistent disk
- Or use external PostgreSQL database

---

## 🚀 Next Steps (Optional)

1. **Custom Domain**
   - Vercel: Settings → Domains → Add your domain
   - Render: Settings → Custom Domain

2. **Upgrade Plans**
   - Render: $7/month for persistent storage
   - Vercel: Stay on free (it's generous!)

3. **Add Monitoring**
   - Sentry for error tracking
   - LogRocket for user sessions
   - Google Analytics for usage

4. **Database Migration**
   - Move SQLite to PostgreSQL
   - Use Render's PostgreSQL (free tier)
   - Update connection string

Good luck! 🎉
