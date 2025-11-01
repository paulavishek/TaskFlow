# 📚 How to Access the Wiki in TaskFlow

## ✅ Wiki is Now Live!

Your wiki feature is **fully integrated** and ready to use. Here's exactly where to find it:

---

## 🌐 Access Methods

### Method 1: Main Navigation Bar (Easiest)
1. **Log in to TaskFlow**
2. **Look at the top navigation bar** (dark blue)
3. **Click the "Wiki" link** with the book icon 📖
   - It's located between "AI Assistant" and "Messages"
   - URL: `http://localhost:8000/wiki/`

### Method 2: Direct URL Access
- **Main Wiki Page**: `http://localhost:8000/wiki/`
- **Create New Page**: `http://localhost:8000/wiki/create/`
- **Browse Categories**: `http://localhost:8000/wiki/categories/`
- **Search Wiki**: `http://localhost:8000/wiki/search/`
- **Meeting Notes**: `http://localhost:8000/wiki/meeting-notes/`

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Navigate to Wiki
- Click **Wiki** in the top navigation bar
- You'll see the main wiki page listing

### Step 2: Create Your First Page
- Click **"Create New Page"** button
- **Fill in the form:**
  - **Title**: Give your page a name
  - **Category**: Select or create a category
  - **Content**: Write in Markdown format
  - **Publish**: Check "Published" to make it visible
- Click **"Save"**

### Step 3: Explore Features
- **View page**: Click on any page to see full content
- **Edit page**: Click "Edit" on a page
- **Link to tasks**: Click "Link to Task/Board" on a page
- **Add meeting notes**: Go to Meeting Notes section
- **Search**: Use the search bar to find content

---

## 📍 Navigation Map

```
Wiki Homepage (http://localhost:8000/wiki/)
│
├─ 📄 Wiki Pages
│  ├─ Create Page (click "Create" button)
│  ├─ View Page (click page title)
│  ├─ Edit Page (click "Edit" button)
│  ├─ Delete Page (click "Delete" button)
│  ├─ View History (click "History" button)
│  └─ Restore Version (click "Restore" on history page)
│
├─ 🏷️ Categories
│  ├─ Browse Categories (click "Categories" button)
│  ├─ Create Category (click "Create" button)
│  └─ View Pages by Category (click category name)
│
├─ 🔗 Links & References
│  ├─ Link Page to Task (click "Link" button on page)
│  ├─ Link Page to Board (click "Link" button on page)
│  └─ View Linked Items (see "Related" section on page)
│
├─ 📋 Meeting Notes
│  ├─ View All Notes (click "Meeting Notes" button)
│  ├─ Create Notes (click "Create" button)
│  ├─ View Note Details (click note title)
│  └─ Search Notes (use search bar)
│
└─ 🔍 Search
   └─ Search Everything (click "Search" button)
```

---

## 🎨 Features Available

### 1. **Wiki Pages** 📄
- Create documentation with Markdown
- Organize by categories
- Create hierarchical pages (parent/child)
- Pin important pages
- Draft/Published states
- Add tags

### 2. **Categories** 🏷️
- Organize pages logically
- Custom icons and colors
- Default categories (Getting Started, Procedures, etc.)

### 3. **Links** 🔗
- Link wiki pages to tasks
- Link wiki pages to boards
- Add context/descriptions
- View linked items on both sides

### 4. **Meeting Notes** 📋
- Create meeting documentation
- Add attendees
- Record decisions
- Track action items
- Link to boards/pages

### 5. **Version Control** ⏮️
- Auto-save all changes
- View complete history
- Restore previous versions
- See who changed what

### 6. **Search** 🔍
- Search all wiki pages
- Search meeting notes
- Search tasks (if linked)
- Full-text search

---

## 🌟 Getting Started Checklist

- [ ] Log in to TaskFlow
- [ ] Click "Wiki" in navigation bar
- [ ] You should see a page listing (probably empty initially)
- [ ] Click "Create New Page" button
- [ ] Fill in title, category, content
- [ ] Click "Save Page"
- [ ] View your newly created page
- [ ] Click "Edit" to modify content
- [ ] Click "History" to see versions
- [ ] Click "Link" to link to a task or board

---

## 🎓 Markdown Basics (for Content)

Your wiki supports full Markdown syntax:

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*
~~Strikethrough~~

- Bullet list
- Item 2

1. Numbered list
2. Item 2

[Link text](http://example.com)
![Image alt](http://example.com/image.jpg)

`Inline code`

```
Code block
```

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

---

## 💡 Pro Tips

### Tip 1: Use Categories
- Create categories first (Getting Started, Procedures, Technical, etc.)
- Makes pages easier to organize and find

### Tip 2: Link to Tasks
- Click "Link" on a wiki page
- Select tasks or boards it relates to
- Users can navigate from task → wiki page

### Tip 3: Use Meeting Notes
- Store all meeting notes in one place
- Track decisions and action items
- Search across all meetings

### Tip 4: Version Control
- Don't worry about making mistakes
- Can always restore previous versions
- Click "History" to see all changes

### Tip 5: Search Everything
- Use the search feature to find content
- Searches across pages, notes, and linked items
- Very powerful for large knowledge bases

---

## 🔧 Admin Features

### Accessing Wiki Admin
1. Go to `http://localhost:8000/admin/`
2. Scroll to **Wiki** section
3. You can manage:
   - **Wiki Pages** - View, edit, delete all pages
   - **Wiki Categories** - Manage categories
   - **Meeting Notes** - Manage meeting records
   - **Wiki Attachments** - Manage file uploads
   - **Wiki Links** - Manage task/board connections
   - And more...

### Admin Capabilities
- Filter by organization
- Search by title/slug
- Bulk actions
- View statistics
- Manage permissions

---

## ❓ Troubleshooting

### I don't see the Wiki link in the navigation
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Log out and log back in
3. Refresh the page (Ctrl+R)
4. Check you're logged in

### I created a page but can't see it
**Solution:**
1. Make sure it's published (check "Published" checkbox)
2. Make sure it belongs to your organization
3. Try using the search feature

### Pages aren't showing markdown correctly
**Solution:**
1. Make sure you're using valid Markdown syntax
2. Check the preview while editing
3. Try refreshing the page

### I can't link a page to a task
**Solution:**
1. Make sure the task exists
2. Make sure the task belongs to your organization
3. Make sure the page is published

---

## 📞 Next Steps

1. **Read the full guide**: See `WIKI_KNOWLEDGE_BASE_GUIDE.md`
2. **Create your first page**: Use "Create New Page"
3. **Set up categories**: Organize your pages
4. **Link to tasks**: Connect wiki to your workflow
5. **Store meeting notes**: Document discussions

---

## 🎉 You're All Set!

The wiki is ready to use. Start creating documentation and organizing your knowledge!

**Questions?** Check the comprehensive guide: `WIKI_KNOWLEDGE_BASE_GUIDE.md`

---

**Navigation Quick Links:**
- Main Wiki: `/wiki/`
- Create Page: `/wiki/create/`
- Categories: `/wiki/categories/`
- Meeting Notes: `/wiki/meeting-notes/`
- Search: `/wiki/search/`

**Status: ✅ LIVE AND READY TO USE**
