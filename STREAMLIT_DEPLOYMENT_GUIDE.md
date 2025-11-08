# 🚀 Streamlit Cloud Deployment Guide

Complete guide to deploy Tech Deal Forge on Streamlit Community Cloud.

---

## 📋 Prerequisites (Already Done! ✅)

- [x] GitHub repository created and pushed
- [x] `streamlit_dashboard.py` exists
- [x] `requirements.txt` includes all dependencies
- [x] `.gitignore` configured properly
- [x] Database (13.74 MB) committed to repo

---

## 🌐 Step 1: Sign Up for Streamlit Community Cloud (2 min)

1. **Visit:** https://share.streamlit.io/
2. **Click:** "Sign in" (top right)
3. **Choose:** "Continue with GitHub"
4. **Authorize:** Grant Streamlit access to your GitHub repositories
5. **Done!** You'll be redirected to the Streamlit Cloud dashboard

---

## 🎯 Step 2: Deploy Your App (5 min)

### **2.1: Create New App**

1. Click the **"New app"** button (big blue button, top right)
2. You'll see a deployment form with three main sections:

### **2.2: Fill in Repository Details**

**Repository:**
```
congardiner/Senior-Project---Tech-Deal-Forge
```

**Branch:**
```
main
```

**Main file path:**
```
streamlit_dashboard.py
```

### **2.3: Choose Your App URL**

**App URL (subdomain):**
```
https://tech-deal-forge.streamlit.app
```
*Choose any available name you like (lowercase, hyphens only)*

**Alternative names you could use:**
- `deal-forge`
- `tech-deals`
- `deals-dashboard`
- `your-name-deals`

### **2.4: Advanced Settings (Optional)**

Click **"Advanced settings"** to expand:

**Python version:**
```
3.11
```
*(Or leave default - it will auto-detect from your code)*

**Secrets:** 
```
Leave empty for now
```
*(We'll add Supabase credentials here later if you set that up)*

### **2.5: Deploy!**

Click the **"Deploy!"** button at the bottom

---

## ⏱️ Step 3: Wait for Build (3-5 minutes)

You'll see a live build log showing:

```
🔄 Cloning repository...
✅ Repository cloned

🔄 Installing Python 3.11...
✅ Python installed

🔄 Installing dependencies from requirements.txt...
  ⏳ Installing streamlit (1.40.0)...
  ⏳ Installing pandas (2.2.2)...
  ⏳ Installing plotly (5.24.1)...
  ⏳ Installing botasaurus (4.4.4)...
  ⏳ Installing beautifulsoup4...
✅ Dependencies installed

🔄 Starting app...
✅ App is live!

🎉 Your app is now running at:
   https://tech-deal-forge.streamlit.app
```

**Common Build Messages:**

✅ **"Cloning repository"** - Downloading your code from GitHub  
✅ **"Installing dependencies"** - Installing packages from requirements.txt  
✅ **"Starting app"** - Running streamlit_dashboard.py  
✅ **"App is live"** - SUCCESS! Your app is deployed

---

## ✅ Step 4: Verify Your Deployment (5 min)

### **4.1: Check Homepage**

Visit your app URL and verify:

- [x] **Page loads** without errors
- [x] **Header displays**: "🔨 Deal Forge"
- [x] **Metrics show**: Total Deals, With Prices, Average Price
- [x] **Last update time** displays correctly

### **4.2: Test Sidebar Filters**

- [x] **Search box** - Type something, press Enter
- [x] **Price slider** - Drag to filter price range
- [x] **Website checkboxes** - Toggle Slickdeals/Best Buy
- [x] **Category dropdown** - Select different categories
- [x] **Download CSV** - Click and verify file downloads

### **4.3: Test All Tabs**

Click through each tab and verify it loads:

1. [x] **📊 Overview** - Charts and deal cards display
2. [x] **💰 Price History** - Price trends over time
3. [x] **📈 Trends** - Category and website trends
4. [x] **🏆 Top Deals** - Best deals by category
5. [x] **📊 Analytics** - Statistical analysis
6. [x] **🔍 Advanced Search** - Detailed filtering
7. [x] **ℹ️ About** - Project information

### **4.4: Check Data Loads**

- [x] Deal cards show product info (title, price, image)
- [x] Charts render properly (line charts, bar charts, pie charts)
- [x] Tables have data (not empty)
- [x] Images load (product thumbnails)

---

## 🎨 Step 5: Customize Your Deployment (Optional)

### **Share Your App**

Your app is now **publicly accessible**! Anyone can visit:
```
https://tech-deal-forge.streamlit.app
```

Share this link:
- ✅ In your README.md
- ✅ On your resume/portfolio
- ✅ In your project presentation
- ✅ With friends/colleagues

### **Add Streamlit Badge to README**

Add this to your README.md:

```markdown
## 🌐 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tech-deal-forge.streamlit.app)

**Try it now:** https://tech-deal-forge.streamlit.app
```

### **Update GitHub Repository Info**

1. Go to your GitHub repo
2. Click **⚙️ Settings** (repo settings, not account)
3. Scroll to **About** section (top right of main repo page)
4. Click **⚙️ (gear icon)** next to About
5. Add:
   - **Website:** `https://tech-deal-forge.streamlit.app`
   - **Topics:** `streamlit`, `python`, `data-visualization`, `web-scraping`, `dashboard`
   - **Description:** "Real-time tech deals aggregator with analytics dashboard"
6. Click **Save changes**

---

## 🔄 Step 6: Automatic Updates (Already Configured!)

Every time you push to GitHub, Streamlit Cloud **automatically redeploys**!

### **How it works:**

```bash
# 1. Make changes locally
git add .
git commit -m "Update dashboard styling"
git push origin main

# 2. Streamlit Cloud detects the push
# 3. Automatically rebuilds your app (2-3 minutes)
# 4. Your live app updates with new changes!
```

### **Watch the Auto-Deploy:**

In Streamlit Cloud dashboard:
- Click **"Manage app"** → **"Logs"**
- See real-time rebuild when you push to GitHub

### **Force a Reboot:**

If something seems stuck:
1. Streamlit Cloud → **Manage app**
2. Click **"Reboot"** (top right menu)
3. Wait 1-2 minutes for app to restart

---

## 🐛 Common Issues & Solutions

### ❌ **Issue: "ModuleNotFoundError: No module named 'XXX'"**

**Cause:** Missing dependency in requirements.txt

**Fix:**
1. Add the package to `requirements.txt`:
   ```txt
   XXX>=1.0.0
   ```
2. Commit and push:
   ```bash
   git add requirements.txt
   git commit -m "Add missing dependency"
   git push
   ```
3. Wait for auto-redeploy

---

### ❌ **Issue: "FileNotFoundError: output/deals.db"**

**Cause:** Database not committed to Git

**Fix:**
1. Check your `.gitignore` allows `output/deals.db`:
   ```
   !output/deals.db
   ```
2. Commit the database:
   ```bash
   git add output/deals.db
   git commit -m "Add database for Streamlit Cloud"
   git push
   ```

**Alternative:** If database is too large (>100MB), use sample data:
- Your `init_cloud_db.py` automatically generates sample data if DB is missing
- This is already built into your dashboard!

---

### ❌ **Issue: "App is sleeping 😴"**

**Cause:** Free tier apps sleep after 7 days of inactivity

**Fix:**
- Just visit the URL - it wakes up in 30 seconds automatically
- This is normal behavior for free tier

---

### ❌ **Issue: App loads but shows "No data available"**

**Cause:** Database exists but is empty

**Fix:**
1. Run your scrapers locally:
   ```bash
   python slickdeals_webscraper.py
   python bestbuy_api_scraper.py
   ```
2. Commit updated database:
   ```bash
   git add output/deals.db
   git commit -m "Update database with fresh deals"
   git push
   ```

---

### ❌ **Issue: "Out of resources" or "Memory error"**

**Cause:** App using too much RAM (free tier limit: 1GB)

**Fix:**
1. Reduce data loaded at once (limit queries)
2. Clear Streamlit cache more frequently
3. Optimize DataFrame operations
4. Consider upgrading to paid tier for more resources

---

### ❌ **Issue: Build fails with "requirements.txt not found"**

**Cause:** File path issue or .gitignore excluding it

**Fix:**
1. Ensure `requirements.txt` is in root directory
2. Check it's not in `.gitignore`
3. Commit it:
   ```bash
   git add requirements.txt
   git commit -m "Add requirements.txt"
   git push
   ```

---

## 📊 Streamlit Cloud Dashboard

### **View App Metrics**

1. Go to https://share.streamlit.io/
2. Click on your app
3. See:
   - **Viewers:** Active users right now
   - **Total views:** All-time view count
   - **CPU usage:** Resource consumption
   - **Memory usage:** RAM usage

### **View Logs**

Real-time Python output and errors:
1. Click your app → **"Manage app"**
2. Click **"Logs"** in top menu
3. See `print()` statements, errors, warnings

### **App Settings**

1. Click **"Settings"** (⚙️ icon)
2. Options:
   - **Secrets:** Add API keys, database credentials
   - **Python version:** Change if needed
   - **Sharing:** Get shareable link
   - **Delete app:** Remove deployment

---

## 🔐 Step 7: Add Secrets (For Future Supabase Setup)

When you set up Supabase (cloud database):

### **7.1: Add Secrets in Streamlit Cloud**

1. Streamlit Cloud → Your app → **"Settings"** → **"Secrets"**
2. Add this TOML configuration:

```toml
# Supabase Configuration
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "your-anon-key-here"

# Optional: Environment settings
[environment]
USE_CLOUD_DB = "true"
ENVIRONMENT = "production"
```

3. Click **"Save"**
4. App automatically reboots with new secrets

### **7.2: Access Secrets in Code**

Your dashboard can read these secrets:

```python
import streamlit as st

# Check if running on Streamlit Cloud
if hasattr(st, 'secrets'):
    # Running on Streamlit Cloud
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
else:
    # Running locally
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
```

---

## 🎓 Best Practices

### **Development Workflow**

```bash
# 1. Develop locally
streamlit run streamlit_dashboard.py

# 2. Test thoroughly
# 3. Commit changes
git add .
git commit -m "Add new feature"

# 4. Push to GitHub
git push origin main

# 5. Wait 2-3 min for Streamlit Cloud to auto-deploy
# 6. Test live app at your URL
```

### **Keep Your App Fast**

- ✅ Use `@st.cache_data` for expensive operations
- ✅ Limit data loaded (don't load entire database at once)
- ✅ Optimize queries with SQL filters
- ✅ Compress images before displaying

### **Monitor Your App**

- ✅ Check logs regularly for errors
- ✅ Monitor resource usage
- ✅ Test after each deployment
- ✅ Keep dependencies updated

---

## 💰 Streamlit Pricing

### **Community Cloud (FREE)** ⭐ You're using this!

- ✅ **Unlimited apps**
- ✅ **Public sharing**
- ✅ **1GB RAM per app**
- ✅ **1 CPU per app**
- ✅ **Auto-deploy from GitHub**
- ⚠️ Apps sleep after 7 days inactivity
- ⚠️ Apps are **public only**

### **Teams ($20/user/month)**

- Everything in Free, plus:
- ✅ **Private apps** (password protected)
- ✅ **More resources** (4GB RAM)
- ✅ **Custom domains**
- ✅ **SSO authentication**
- ✅ **Priority support**

For your project, **FREE tier is perfect!** 🎉

---

## ✅ Deployment Checklist

Before clicking "Deploy":

- [ ] All Python files committed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `.streamlit/config.toml` exists (optional, for theme)
- [ ] `.gitignore` excludes secrets but allows database
- [ ] Database committed (if < 100MB) OR sample data enabled
- [ ] README.md updated with project description
- [ ] Code tested locally: `streamlit run streamlit_dashboard.py`

After deployment:

- [ ] App URL loads successfully
- [ ] All tabs work
- [ ] Filters and search work
- [ ] Data displays correctly
- [ ] Download CSV works
- [ ] No errors in logs
- [ ] Added live URL to README.md

---

## 🎉 Success!

Your Tech Deal Forge dashboard is now **live on the internet**! 🚀

**Your live app:**
```
https://tech-deal-forge.streamlit.app
```

**What you can do now:**

1. ✅ **Share** your live demo link on resume/portfolio
2. ✅ **Present** your project with the live URL
3. ✅ **Update** anytime by pushing to GitHub
4. ✅ **Monitor** usage and performance
5. ✅ **Upgrade** with Supabase for cloud database (optional)

---

## 📚 Additional Resources

**Streamlit Docs:**
- https://docs.streamlit.io/
- https://docs.streamlit.io/streamlit-community-cloud

**Streamlit Gallery:**
- https://streamlit.io/gallery

**Deployment Examples:**
- https://github.com/streamlit/streamlit-example

**Community:**
- https://discuss.streamlit.io/

---

## 🆘 Need Help?

**Deployment issues?**
1. Check Streamlit Cloud logs
2. Test locally first: `streamlit run streamlit_dashboard.py`
3. Review error messages in build log
4. Check requirements.txt has all packages

**Questions?**
- Streamlit Forum: https://discuss.streamlit.io/
- GitHub Issues: Your repo → Issues tab

---

**Happy Deploying! 🎊**

Your Tech Deal Forge is now **live** and **accessible worldwide**!
