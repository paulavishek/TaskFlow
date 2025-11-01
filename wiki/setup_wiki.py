#!/usr/bin/env python
"""
Setup script for Wiki & Knowledge Base feature
Run this after installing the wiki app to initialize default data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kanban_board.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Organization
from wiki.models import WikiCategory


def main():
    print('=' * 60)
    print('Wiki & Knowledge Base Setup')
    print('=' * 60)
    print()
    
    print('Wiki & Knowledge Base feature is ready!')
    print()
    print('IMPORTANT: You can now create categories manually!')
    print()
    print('Next steps:')
    print('1. Navigate to /wiki/categories/ to manage categories')
    print('2. Click "New Category" to create your first category')
    print('3. Then go to /wiki/create/ to start creating wiki pages')
    print('4. Link wiki pages to tasks and boards')
    print('5. Store meeting notes in the wiki')
    print()
    print('=' * 60)
    print()


if __name__ == '__main__':
    main()
