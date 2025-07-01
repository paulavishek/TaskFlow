# TaskFlow Setup Guide

This guide will help you set up TaskFlow locally for development or deployment.

## Prerequisites

- Python 3.8+
- Git
- pip (Python package manager)
- Virtual environment (recommended)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/avishekpaul1310/TaskFlow.git
cd TaskFlow
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```bash
   # Required - Generate a secure secret key
   SECRET_KEY=your-long-random-secret-key-here
   
   # Development settings
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Gemini API Key (for AI features)
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # Google OAuth (optional for development)
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
   ```

### 5. Database Setup

```bash
# Create database tables
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser!

## Detailed Configuration

### Getting API Keys

#### Gemini API Key (Required for AI Features)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create or select a project
3. Generate an API key
4. Add to your `.env` file as `GEMINI_API_KEY`

#### Google OAuth Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
6. Add client ID and secret to `.env`

### Email Configuration (Optional)
For password reset functionality:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test kanban
python manage.py test accounts
```

### Demo Data
Create demo data for testing:
```bash
python setup_ai_demo.py
```

### AI Features Testing
Test AI features with demo scripts:
```bash
python demo_ai_features.py
python demo_ai_analytics.py
```

## Production Deployment

### Google App Engine
The project includes `app.yaml` for Google App Engine deployment:

```bash
# Deploy to Google App Engine
gcloud app deploy
```

### Environment Variables for Production
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-app-id.appspot.com
SECRET_KEY=your-production-secret-key
GEMINI_API_KEY=your-production-gemini-key
```

## Project Structure

```
TaskFlow/
├── accounts/           # User authentication and profiles
├── kanban/             # Main Kanban board functionality
├── kanban_board/       # Django project settings
├── static/             # CSS, JS, and image files
├── templates/          # HTML templates
├── requirements.txt    # Python dependencies
├── manage.py          # Django management script
├── .env.example       # Environment variables template
└── README.md          # Project documentation
```

## Key Features

- 🧠 **Gemini AI Integration**: Smart task suggestions and analytics
- 📊 **Advanced Analytics**: AI-powered insights and reporting
- 🔒 **Google OAuth**: Secure authentication
- 👥 **Team Collaboration**: Multi-user support with organizations
- 📱 **Responsive Design**: Works on desktop and mobile
- 🎯 **Lean Six Sigma**: Process optimization features

## Troubleshooting

### Common Issues

1. **Module not found errors**: Ensure virtual environment is activated
2. **Database errors**: Run `python manage.py migrate`
3. **Static files not loading**: Run `python manage.py collectstatic`
4. **Gemini API errors**: Check your API key and quota

### Getting Help

- Check the [GitHub Issues](https://github.com/avishekpaul1310/TaskFlow/issues)
- Review the [README.md](README.md) for more details
- Check Django logs for detailed error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is open source. See the repository for license details.
