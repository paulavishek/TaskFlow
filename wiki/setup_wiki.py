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


def create_default_categories():
    """Create default wiki categories for all organizations"""
    
    organizations = Organization.objects.all()
    categories_template = [
        {
            'name': 'Getting Started',
            'icon': 'rocket',
            'color': '#3498db',
            'position': 0,
            'description': 'Getting started guide and onboarding documentation'
        },
        {
            'name': 'Project Documentation',
            'icon': 'folder-open',
            'color': '#2ecc71',
            'position': 1,
            'description': 'General project documentation and guidelines'
        },
        {
            'name': 'Procedures & Workflows',
            'icon': 'sitemap',
            'color': '#f39c12',
            'position': 2,
            'description': 'Standard procedures and workflow documentation'
        },
        {
            'name': 'Technical Reference',
            'icon': 'code',
            'color': '#9b59b6',
            'position': 3,
            'description': 'Technical documentation and references'
        },
        {
            'name': 'Meeting Minutes',
            'icon': 'file-alt',
            'color': '#e74c3c',
            'position': 4,
            'description': 'Organized meeting minutes and decisions'
        },
        {
            'name': 'FAQ',
            'icon': 'question-circle',
            'color': '#16a085',
            'position': 5,
            'description': 'Frequently asked questions and answers'
        },
        {
            'name': 'Resources',
            'icon': 'link',
            'color': '#34495e',
            'position': 6,
            'description': 'External resources, tools, and links'
        },
    ]
    
    created_count = 0
    
    for org in organizations:
        for category_data in categories_template:
            category, created = WikiCategory.objects.get_or_create(
                organization=org,
                name=category_data['name'],
                defaults={
                    'icon': category_data['icon'],
                    'color': category_data['color'],
                    'position': category_data['position'],
                    'description': category_data['description'],
                }
            )
            if created:
                print(f'✓ Created category "{category.name}" for {org.name}')
                created_count += 1
            else:
                print(f'• Category "{category.name}" already exists for {org.name}')
    
    return created_count


def main():
    print('=' * 60)
    print('Wiki & Knowledge Base Setup')
    print('=' * 60)
    print()
    
    # Create default categories
    print('Creating default categories...')
    print()
    count = create_default_categories()
    
    print()
    print('=' * 60)
    print(f'Setup complete! Created {count} categories.')
    print('=' * 60)
    print()
    print('Next steps:')
    print('1. Navigate to /wiki/ to start creating wiki pages')
    print('2. Go to /admin/ to manage categories and pages')
    print('3. Link wiki pages to tasks and boards')
    print('4. Start storing meeting notes')
    print()


if __name__ == '__main__':
    main()
