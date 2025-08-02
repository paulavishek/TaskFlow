from django.core.management.base import BaseCommand
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup Google OAuth2 social application for django-allauth'

    def handle(self, *args, **options):
        # Get Google OAuth credentials from environment variables
        client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
        client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', None)
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR(
                    'Google OAuth2 credentials not found in environment variables.\n'
                    'Please set GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_SECRET in your .env file.'
                )
            )
            return

        # Check if Google social app already exists
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Created new Google OAuth2 social application.')
            )
        else:
            # Update existing app with new credentials
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            self.stdout.write(
                self.style.SUCCESS('Updated existing Google OAuth2 social application.')
            )

        # Add the current site to the social app
        current_site = Site.objects.get_current()
        google_app.sites.add(current_site)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Google OAuth2 social application is now configured for site: {current_site.domain}'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\nDon\'t forget to:\n'
                '1. Add your actual Google OAuth2 credentials to the .env file\n'
                '2. Configure authorized redirect URIs in Google Cloud Console:\n'
                f'   - http://{current_site.domain}:8000/accounts/google/login/callback/\n'
                f'   - http://127.0.0.1:8000/accounts/google/login/callback/\n'
                f'   - http://localhost:8000/accounts/google/login/callback/'
            )
        )
