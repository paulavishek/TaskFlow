# Wiki & Knowledge Base - Quick Start Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install Markdown==3.5.1
```

### 2. Run Migrations
```bash
python manage.py makemigrations wiki
python manage.py migrate wiki
```

### 3. Create Default Categories (Optional)
```bash
python manage.py shell
>>> exec(open('wiki/setup_wiki.py').read())
```

### 4. Access the Wiki
- **Main Wiki**: http://localhost:8000/wiki/
- **Create Page**: http://localhost:8000/wiki/create/
- **Categories**: http://localhost:8000/wiki/categories/
- **Meeting Notes**: http://localhost:8000/wiki/meeting-notes/
- **Search**: http://localhost:8000/wiki/search/
- **Admin**: http://localhost:8000/admin/

---

## 📝 Creating Your First Wiki Page

1. Go to **Wiki** → **New Page**
2. Enter:
   - **Title**: Your page title
   - **Category**: Select or create category
   - **Content**: Write in Markdown
   - **Tags**: Add searchable tags
3. Click **Create Page**

### Markdown Basics

| Element | Syntax |
|---------|--------|
| Bold | `**text**` |
| Italic | `*text*` |
| Code | `` `code` `` |
| Heading | `# Heading` |
| List | `- Item` |
| Link | `[text](url)` |
| Image | `![alt](url)` |

---

## 🔗 Linking Wiki to Tasks/Boards

### Option 1: From Wiki Page
1. View wiki page
2. Click **Link** button
3. Select Task or Board
4. Add description
5. Save

### Option 2: From Task/Board
1. Open task or board detail view
2. Click **Related Wiki** button (future)
3. Select wiki pages to link
4. Save

---

## 📋 Meeting Notes

### Creating Meeting Notes
1. Go to **Wiki** → **Meeting Notes** → **New**
2. Fill in:
   - Title
   - Date/Time
   - Attendees (usernames)
   - Content (Markdown)
   - Decisions
   - Action Items (optional)
3. Click **Create**

### Linking to Pages/Boards
- Select related board when creating
- Link to wiki pages for documentation
- Reference in related content sections

---

## 🔍 Search

### Search Everything
- Go to `/wiki/search/`
- Type your query
- Results include:
  - Wiki pages
  - Meeting notes
  - Tasks
  - Boards

### Filter by Category
- Click category in sidebar
- Or use category filter in search

### Filter by Tags
- Click tag on page detail
- Or search for specific tag

---

## 📊 Version Control

### View History
1. Click **History** on page detail
2. See all versions with:
   - Change description
   - Who made the change
   - When it was changed

### Restore Previous Version
1. Go to page history
2. Click **Restore** on desired version
3. Confirm restoration

---

## 🎯 Best Practices

### For Wiki Pages
- ✅ Use clear, descriptive titles
- ✅ Organize with headers
- ✅ Add tags for discoverability
- ✅ Link to related pages
- ✅ Keep content up-to-date
- ✅ Include code examples
- ✅ Add images and diagrams
- ❌ Don't write very long pages (use sub-pages instead)
- ❌ Don't duplicate information

### For Meeting Notes
- ✅ Include date/time
- ✅ List all attendees
- ✅ Record key decisions
- ✅ Note action items
- ✅ Add next steps
- ✅ Link to related wiki pages
- ❌ Don't make it too long
- ❌ Don't forget to save attendees

### For Categories
- ✅ Create logical groupings
- ✅ Use descriptive names
- ✅ Assign appropriate icons
- ✅ Use consistent colors
- ❌ Don't create too many categories
- ❌ Don't use similar category names

---

## 🔧 Admin Management

### Django Admin
- Access: `/admin/`
- Manage all wiki models
- Bulk actions available
- Filtering and search
- Read-only audit fields

### Common Admin Tasks
- **Create categories**: Go to Wiki Categories → Add
- **Publish pages**: Edit page → Check is_published
- **Pin pages**: Edit page → Check is_pinned
- **View access**: Go to Wiki Page Access model

---

## 🐛 Common Issues

### Markdown not rendering
- ✓ Check Markdown package is installed: `pip list | grep Markdown`
- ✓ Restart Django server

### Can't find a page
- ✓ Check if page is published (is_published = True)
- ✓ Try searching instead
- ✓ Check category filter

### Links not showing
- ✓ Verify WikiLink was created in admin
- ✓ Check organization is set correctly
- ✓ Refresh page

### Tags not working
- ✓ Ensure tags are properly formatted as list
- ✓ Check tags don't contain special characters

---

## 📱 Features at a Glance

| Feature | Status | Notes |
|---------|--------|-------|
| Create/Edit Pages | ✅ Ready | Full Markdown support |
| Categories | ✅ Ready | Customizable icons/colors |
| Link to Tasks | ✅ Ready | One-way links (page → task) |
| Link to Boards | ✅ Ready | One-way links (page → board) |
| Meeting Notes | ✅ Ready | Full featured |
| Version Control | ✅ Ready | Full history with restore |
| Search | ✅ Ready | Full-text across all content |
| Attachments | ✅ Ready | File uploads supported |
| Permissions | 🚀 Future | Role-based access control |
| Comments | 🚀 Future | Page discussion threads |
| Real-time Collab | 🚀 Future | Simultaneous editing |
| API | 🚀 Future | REST API endpoints |

---

## 📚 Resources

- **Markdown Guide**: https://www.markdownguide.org/
- **Django Docs**: https://docs.djangoproject.com/
- **Bootstrap Docs**: https://getbootstrap.com/

---

## 💡 Pro Tips

1. **Use parent pages** to organize related content hierarchically
2. **Pin important pages** for quick access
3. **Use tags consistently** across pages
4. **Link related pages** to create a knowledge graph
5. **Archive old meeting notes** in wiki pages
6. **Create templates** for recurring content
7. **Use categories** to organize by project/topic
8. **Add descriptions** when linking to tasks/boards

---

## 🎓 Learning Path

### Beginner (Day 1)
- [ ] Create first wiki page
- [ ] Explore Markdown syntax
- [ ] Create a few pages in different categories
- [ ] Try tagging

### Intermediate (Week 1)
- [ ] Link pages to tasks and boards
- [ ] Create meeting notes
- [ ] Use version control
- [ ] Try hierarchical pages (sub-pages)

### Advanced (Week 2+)
- [ ] Create comprehensive knowledge base
- [ ] Set up search for your team
- [ ] Use for documentation
- [ ] Integrate with processes
- [ ] Train team members

---

## 🚦 Next Steps

1. **Create Project Documentation**
   - Overview pages
   - Process documentation
   - Technical guides
   - FAQ

2. **Set Up Meeting Notes Process**
   - Start recording meetings
   - Link to relevant projects
   - Track decisions
   - Action items

3. **Build Knowledge Base**
   - Organize existing docs
   - Create user guides
   - Add examples
   - Link related content

4. **Train Team**
   - Show how to create pages
   - Demo search features
   - Explain linking system
   - Gather feedback

---

## 📞 Support

For issues or feature requests, contact your project administrator or check the main documentation.

---

**Last Updated**: November 2025
**Version**: 1.0
