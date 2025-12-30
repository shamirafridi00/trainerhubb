# 🚀 TrainerHub Local Development - Quick Start

## ⚡ Fast Setup (Recommended)

```bash
# Start both servers automatically
./run_local.sh
```

That's it! The script will:
- ✅ Start Django backend on `http://localhost:8000` (HTMX landing)
- ✅ Start React frontend on `http://localhost:3000` (React dashboard)
- ✅ Set up database and static files
- ✅ No Docker needed, no hosts file changes needed

## 🧪 Test the Hybrid Architecture

1. **Visit Landing**: `http://localhost:8000`
   - Beautiful HTMX page with animations
   - SEO-optimized for search engines

2. **Click "Get Started"**
   - React login modal appears instantly
   - No page reload needed

3. **Register/Login**
   - API call to Django backend
   - Automatic redirect to React app

4. **Dashboard**: `http://localhost:3000/dashboard`
   - Full React SPA experience
   - Fast, modern interface

## 🛠️ Manual Alternative

If you prefer to run servers separately:

```bash
# Terminal 1 - Django Backend
source venv/bin/activate
python manage.py runserver 8000 --settings=config.settings.development

# Terminal 2 - React Frontend
cd trainer-app
npm run dev
```

## 🔧 Troubleshooting

**"Site cannot be reached"**
- Make sure `./run_local.sh` is running
- Check that ports 8000 and 3000 are free
- Try `http://127.0.0.1:8000` directly

**React modal not working**
- Check browser console for errors
- Ensure Django API is responding on port 8000
- Check that `npm run dev` is running

**Database issues**
- Run: `python manage.py migrate --settings=config.settings.development`

## 📚 More Info

- Detailed docs: `docs/LOCAL_DEVELOPMENT.md`
- Hosts setup: `HOSTS_SETUP.txt` (for advanced subdomain testing)

---

Happy coding! 🏋️‍♀️💪
