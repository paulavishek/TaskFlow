# RAG (Retrieval Augmented Generation) Setup Guide

Your TaskFlow AI Assistant is already equipped with RAG capabilities! This guide will help you set up the Google Custom Search API to enable web search functionality.

---

## What is RAG?

**Retrieval Augmented Generation** combines:
1. **Retrieval** - Search for relevant information (web, KB, project data)
2. **Augmentation** - Inject that information into the AI prompt
3. **Generation** - Use Gemini to generate informed responses

Your chatbot uses three sources of retrieval:
- **Internal Project Data** - Tasks, team members, boards
- **Knowledge Base** - Documentation and past insights
- **Web Search** - Recent information and external resources (RAG via Google Custom Search)

---

## Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name: `TaskFlow-RAG` (or your preferred name)
5. Click "CREATE"
6. Wait for the project to be created

### Step 2: Enable Custom Search API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Custom Search API"
3. Click on "Custom Search API"
4. Click the "ENABLE" button
5. Wait for it to enable (may take a moment)

### Step 3: Create API Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. A dialog will appear with your new API key
4. Copy this key - you'll need it for `.env`

**Example:**
```
AIzaSyA_m0wrI-W5b6uyKQm_YftiUawn5dMIghA
```

### Step 4: Create a Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Create" or "Add"
3. Fill in the form:
   - **Search engine name:** `TaskFlow Search`
   - **Sites to search:** Leave as "Search the entire web" for full web access
   - **Language:** English
4. Click "CREATE"
5. Your new search engine will appear in the list
6. Click on it and look for the **Search engine ID (cx)** - usually shown as "Search engine details"

**Example:**
```
cx: 017643282632192136171:abc123xyz
```

### Step 5: Update Your `.env` File

Add these lines to your `.env` file:

```env
# Google Custom Search API - For RAG
GOOGLE_SEARCH_API_KEY=your_api_key_from_step_3
GOOGLE_SEARCH_ENGINE_ID=your_cx_from_step_4
ENABLE_WEB_SEARCH=True
```

**Complete Example:**
```env
GOOGLE_SEARCH_API_KEY=AIzaSyA_m0wrI-W5b6uyKQm_YftiUawn5dMIghA
GOOGLE_SEARCH_ENGINE_ID=017643282632192136171:abc123xyz
ENABLE_WEB_SEARCH=True
```

### Step 6: Test Your Setup

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Go to the AI Assistant chat: `http://localhost:8000/assistant/chat/`

3. Try a query that triggers web search:
   ```
   "What are the latest project management trends in 2025?"
   "Tell me about Agile methodology best practices"
   "What's new in AI for project management?"
   ```

4. Check the response - if web search worked, you should see sources cited!

---

## How RAG Works in TaskFlow

### Query Detection

The chatbot automatically detects when to use web search based on keywords:

**Triggers web search if query contains:**
- "latest", "recent", "current", "new", "2025"
- "trend", "news", "update", "web", "online"
- "what is", "how do", "tell me about"
- "best practices", "industry", "methodology", "tool"

**Example good queries for web search:**
- ✅ "What are the latest Python frameworks?"
- ✅ "Tell me about DevOps best practices 2025"
- ✅ "How do enterprise teams handle risk management?"

**Example queries that use project data instead:**
- ✅ "What tasks are assigned to me?"
- ✅ "Which team members are overloaded?"
- ✅ "What's the status of our project?"

### Context Flow

```
User Query
    ↓
Query Classification (web? project? KB?)
    ↓
Retrieve Context:
  - Project data (if project query)
  - Knowledge Base (if available)
  - Web search results (if web query + enabled)
    ↓
Build System Prompt with Context
    ↓
Send to Gemini AI
    ↓
Return Response + Sources
```

### Context Priority (RAG Order)

1. **Project Context** (High) - Your board's tasks, team, deadlines
2. **Knowledge Base** (Medium) - Your documented insights
3. **Web Search** (Medium) - Latest external information
4. **AI Reasoning** (Low) - Gemini's built-in knowledge

---

## Configuration Details

### In `kanban_board/settings.py`:

```python
# Google Custom Search API settings
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY', '')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
ENABLE_WEB_SEARCH = os.getenv('ENABLE_WEB_SEARCH', 'True').lower() == 'true'
```

### In `ai_assistant/utils/google_search.py`:

The `GoogleSearchClient` class handles:
- ✅ Caching results (1 hour TTL)
- ✅ Rate limiting with exponential backoff
- ✅ Error handling
- ✅ Result formatting for AI consumption

### In `ai_assistant/utils/chatbot_service.py`:

The `TaskFlowChatbotService` class:
- ✅ Detects query type (web vs project)
- ✅ Retrieves appropriate context
- ✅ Injects sources into response
- ✅ Tracks web search usage in analytics

---

## Troubleshooting

### Problem: "Web search is not working"

**Solution 1: Check API Key is valid**
```python
# In Django shell:
python manage.py shell
from django.conf import settings
print(settings.GOOGLE_SEARCH_API_KEY)  # Should show your key
```

**Solution 2: Check Search Engine ID**
- Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
- Verify your `cx` value is copied correctly

**Solution 3: Check Enable flag**
```python
# In Django shell:
from django.conf import settings
print(settings.ENABLE_WEB_SEARCH)  # Should be True
```

### Problem: "API quota exceeded"

Google Custom Search has a **free quota of 100 queries/day**.

**Solutions:**
1. Use caching (1-hour TTL - already enabled)
2. Upgrade to paid plan for higher limits
3. Temporarily disable web search:
   ```env
   ENABLE_WEB_SEARCH=False
   ```

### Problem: "No results returned"

This might mean:
1. Your search query is too specific or vague
2. The search engine isn't configured to search "entire web"
3. Rate limiting occurred

**Solution:**
- Check Google Cloud Console for quota usage
- Try broader search terms
- Reconfigure your search engine to include "entire web"

---

## RAG Sources Displayed

When web search is used, responses include:

```
**Recent Information from Web Search:**

**[Source 1] Title of Article**
URL: https://example.com/article
Summary: Brief snippet from the article

**[Source 2] Another Article**
URL: https://example.com/another
Summary: Another snippet...
```

---

## Advanced Configuration

### Restrict Search to Specific Domains

If you want search results only from specific sites:

1. Edit your search engine at [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Go to "Setup" → "Basics"
3. Change from "Search the entire web" to "Search only included sites"
4. Add domains:
   - `medium.com` (for articles)
   - `github.com` (for code examples)
   - `stackoverflow.com` (for dev Q&A)
   - Your company website, documentation sites, etc.

### Customize Cache TTL

Edit `ai_assistant/utils/google_search.py`:

```python
self.cache_ttl = 3600  # Change to desired seconds
# 60 = 1 minute
# 300 = 5 minutes
# 3600 = 1 hour (default)
# 86400 = 1 day
```

### Adjust Max Results

Edit `ai_assistant/utils/google_search.py`:

```python
self.max_results = 10  # Change to desired number
# In get_response, called with max_results=3 by default
```

---

## Analytics

Your chatbot tracks RAG usage in the database:

- **Messages with web search** - Tracked in `AIAssistantMessage.used_web_search`
- **Analytics dashboard** - Shows web search metrics
- **Sources cited** - Stored in analytics for audit trail

View in admin panel: `/admin/ai_assistant/aiassistantmessage/`

---

## Best Practices

### ✅ DO:
- Use descriptive search queries
- Let the system auto-detect when to search
- Cache frequently asked questions
- Monitor quota usage
- Test with development queries first

### ❌ DON'T:
- Hardcode API keys (always use `.env`)
- Make unnecessary searches (costs quota)
- Share your API key publicly
- Trust outdated web information without verification

---

## Summary

Your TaskFlow AI Assistant now has RAG capabilities:

| Feature | Status | Details |
|---------|--------|---------|
| **Project Data Retrieval** | ✅ Ready | Tasks, team, boards |
| **Knowledge Base Retrieval** | ✅ Ready | Documented insights |
| **Web Search (RAG)** | 🔧 Setup Needed | Needs API credentials |
| **Caching** | ✅ Enabled | 1-hour cache TTL |
| **Analytics Tracking** | ✅ Enabled | Track usage patterns |

**Next Steps:**
1. Get your API keys from Google Cloud
2. Update `.env` file with credentials
3. Test with web search queries
4. Monitor dashboard for usage patterns

Enjoy enhanced AI responses with latest information!
