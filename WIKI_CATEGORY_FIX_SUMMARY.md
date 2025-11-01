# Wiki Category Dropdown - Fixed

## Problem
The wiki page creation form showed an empty category dropdown with dashes `----------` instead of actual categories.

## Root Causes Identified

### 1. No Categories Existed
The database had no WikiCategory records for the user's organization. The setup script `wiki/setup_wiki.py` had not been run.

### 2. Slug Uniqueness Constraint Issue
The WikiCategory and WikiPage models had `slug = models.SlugField(unique=True)` which created a **global unique constraint**. This caused conflicts when multiple organizations tried to use the same category names (which auto-slug to the same value).

## Solutions Implemented

### 1. Fixed Model Constraints
**File:** `wiki/models.py`

Changed from:
```python
# ❌ WRONG - globally unique slug
class WikiCategory(models.Model):
    slug = models.SlugField(unique=True)  # Unique across all orgs!
    
class WikiPage(models.Model):
    slug = models.SlugField(unique=True)  # Unique across all orgs!
```

Changed to:
```python
# ✅ CORRECT - unique per organization
class WikiCategory(models.Model):
    slug = models.SlugField()  # Not globally unique
    
    class Meta:
        unique_together = ('organization', 'name', 'slug')  # Unique per org

class WikiPage(models.Model):
    slug = models.SlugField()  # Not globally unique
    
    class Meta:
        unique_together = ('organization', 'slug')  # Unique per org
```

### 2. Created Migration
```bash
python manage.py makemigrations wiki
python manage.py migrate wiki
```

Migration file: `wiki/migrations/0002_alter_wikicategory_unique_together_and_more.py`

### 3. Initialized Default Categories
Ran the setup script to create default categories for all organizations:

```bash
python manage.py shell -c "from wiki.setup_wiki import main; main()"
```

**Categories Created:**
- Getting Started
- Project Documentation
- Procedures & Workflows
- Technical Reference
- Meeting Minutes
- FAQ
- Resources

**Per Organization:**
- Dev Team: 7 categories
- Marketing Team: 7 categories

## Verification

✅ 14 total categories created (7 per organization)
✅ Categories properly filtered by organization in forms
✅ No slug constraint violations
✅ Wiki page form now shows categories in dropdown

## Testing

1. Go to `/wiki/create/`
2. The category dropdown should now show:
   - Getting Started
   - Project Documentation
   - Procedures & Workflows
   - Technical Reference
   - Meeting Minutes
   - FAQ
   - Resources

## Files Modified

1. `wiki/models.py` - Updated WikiCategory and WikiPage Meta classes
2. `wiki/migrations/0002_alter_wikicategory_unique_together_and_more.py` - New migration (auto-generated)

## How Category Selection Works

```
User in "Dev Team" organization
    ↓
Creates wiki page
    ↓
Form.get_form_kwargs() passes organization to form
    ↓
WikiPageForm.__init__() filters categories by organization
    ↓
self.fields['category'].queryset = WikiCategory.objects.filter(organization=organization)
    ↓
Dropdown shows only "Dev Team" categories
```

**Result:** Each organization sees only their own categories!
