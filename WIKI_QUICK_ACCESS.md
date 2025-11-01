# WIKI LOCATION & ACCESS SUMMARY

## ✅ WHERE TO FIND THE WIKI

### 🌐 In Your Browser:

```
YOUR TASKFLOW APP
│
├─ Top Navigation Bar (Dark Blue)
│  │
│  ├─ Dashboard
│  ├─ Boards
│  ├─ AI Assistant
│  ├─ ⭐ WIKI ← CLICK HERE! 📖
│  ├─ Messages
│  └─ Profile (dropdown)
│
└─ URLs:
   ├─ http://localhost:8000/wiki/
   ├─ http://localhost:8000/wiki/create/
   ├─ http://localhost:8000/wiki/categories/
   ├─ http://localhost:8000/wiki/search/
   └─ http://localhost:8000/wiki/meeting-notes/
```

---

## 🎯 EXACT STEPS TO ACCESS

### Step 1: Make Sure Server is Running
```bash
python manage.py runserver
```

### Step 2: Open Browser
- Go to: `http://localhost:8000/`

### Step 3: Log In (if needed)
- Enter your credentials
- Click "Sign In"

### Step 4: Click Wiki
- Look at the top navigation bar
- You'll see: Dashboard | Boards | AI Assistant | **WIKI** | Messages
- Click **WIKI** (with book icon 📖)

### Step 5: Done! 🎉
- You're now on the wiki page listing

---

## 📱 WHAT YOU'LL SEE

### Main Wiki Page (`/wiki/`)
```
┌─────────────────────────────────────────┐
│  Digital Kanban > WIKI (breadcrumb)     │
├─────────────────────────────────────────┤
│                                         │
│  📚 Wiki Pages                          │
│  ┌─────────────────────────────────┐   │
│  │ [Create New Page] [Categories]  │   │
│  │ [Search]                        │   │
│  │ [Meeting Notes]                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📋 Pages List:                         │
│  ┌─────────────────────────────────┐   │
│  │ (Empty initially - create first)│   │
│  │                                 │   │
│  │ Click "Create New Page" to add  │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎯 QUICK ACCESS URLS

| What | URL |
|------|-----|
| Main Wiki | http://localhost:8000/wiki/ |
| Create Page | http://localhost:8000/wiki/create/ |
| Categories | http://localhost:8000/wiki/categories/ |
| Search | http://localhost:8000/wiki/search/ |
| Meeting Notes | http://localhost:8000/wiki/meeting-notes/ |
| Admin Panel | http://localhost:8000/admin/ |

---

## ✨ FIRST-TIME SETUP (OPTIONAL)

### Initialize Default Categories
Run this in Django shell:
```bash
python manage.py shell
```

Then inside shell:
```python
from wiki.models import WikiCategory
from accounts.models import Organization

org = Organization.objects.first()
if org:
    categories = [
        'Getting Started',
        'Project Documentation',
        'Procedures & Workflows',
        'Technical Reference',
        'Meeting Minutes',
        'FAQ',
        'Resources'
    ]
    for cat_name in categories:
        WikiCategory.objects.get_or_create(
            organization=org,
            name=cat_name,
            defaults={'position': categories.index(cat_name)}
        )
    print("✅ Default categories created!")
```

Type: `exit()`

---

## 🎯 CREATE YOUR FIRST PAGE

1. Go to `/wiki/`
2. Click **"Create New Page"**
3. Fill in:
   - **Title**: e.g., "Getting Started"
   - **Category**: Select one
   - **Content**: Write in Markdown
4. Click **"Save Page"**
5. Done! ✅

---

## 📊 NAVIGATION HIERARCHY

```
Login → Dashboard
        ↓
     [Click Wiki Link]
        ↓
   Wiki Home Page
        ↓
    ┌───┴────┬────┬──────┬──────────┐
    ↓        ↓    ↓      ↓          ↓
 Create   Browse Link  Meeting   Search
  Page   Categories    Pages      Pages
    ↓
  View/Edit/Delete/History
```

---

## 🔐 USER REQUIREMENTS

To access the wiki, you need:
- ✅ Valid TaskFlow login
- ✅ Member of an organization
- ✅ Permission to access wiki (default enabled)

---

## 💾 DATA STRUCTURE

All wiki data is stored in Django database:

```
Database Tables Created:
├─ wiki_wikicategory (Categories)
├─ wiki_wikipage (Pages)
├─ wiki_wikipageversion (Version history)
├─ wiki_wikipageaccess (Permissions)
├─ wiki_wikiattachment (File uploads)
├─ wiki_wikilink (Task/Board links)
├─ wiki_meetingnotes (Meeting notes)
└─ wiki_wikilink_betweenpages (Cross-page refs)
```

---

## 🎉 SUCCESS INDICATORS

When you successfully access the wiki, you'll see:

✅ Wiki link in the navigation bar
✅ Wiki logo (book icon 📖)
✅ Wiki pages section
✅ Create/Search/Categories buttons
✅ Admin panel at `/admin/`

---

## 📞 IF YOU CAN'T FIND IT

1. **Check server is running**
   - Should see: "Starting development server at http://127.0.0.1:8000/"

2. **Verify you're logged in**
   - Should see your username in top right

3. **Clear browser cache**
   - Ctrl+Shift+Delete (Chrome/Firefox)
   - Cmd+Shift+Delete (Mac)

4. **Try direct URL**
   - Go to: `http://localhost:8000/wiki/`

5. **Check Django admin**
   - Go to: `http://localhost:8000/admin/`
   - Scroll to "Wiki" section to verify installation

---

## 📚 REFERENCE DOCUMENTS

- **WIKI_ACCESS_GUIDE.md** - Detailed access guide
- **WIKI_QUICK_START.md** - Quick start guide
- **WIKI_KNOWLEDGE_BASE_GUIDE.md** - Full documentation
- **WIKI_INTEGRATION_CHECKLIST.md** - Integration steps

---

**Status**: ✅ WIKI IS LIVE AND READY TO USE

**Next Step**: Click the Wiki link in your navigation bar and start creating!
