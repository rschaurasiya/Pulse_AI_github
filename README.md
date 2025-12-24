# PulseAI

**PulseAI** is a modern, AI-powered news aggregation and summarization platform that transforms how you consume news. Built with Streamlit and powered by Groq's Llama 3.3 70B model, it delivers intelligent news summaries with multi-language audio support.

## Features

### Core Functionality
- **AI Summarization**: Leverages Groq (Llama 3.3 70B) to generate concise, accurate summaries of news articles
- **Multi-Source Aggregation**: Fetches news from NewsAPI, GNews, and various RSS feeds
- **Text-to-Speech**: Listen to summaries in English and Hindi using gTTS
- **User Authentication**: Secure Firebase-based authentication system
- **Personal Bookmarks**: Save and manage your favorite articles with user-scoped data isolation

### UI/UX
- **Modern Card-Based Design**: Clean, professional interface with smooth animations
- **Light/Dark Theme**: Toggle between themes with proper contrast and visibility
- **Category Navigation**: Browse Technology, Business, Science, Health, Sports, and World news
- **Pagination**: Efficient browsing with 10 articles per page

## Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key ([Get one here](https://console.groq.com/))
- Firebase Project with Firestore enabled ([Setup guide](https://firebase.google.com/))
- NewsAPI Key (Optional, for additional news sources)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Pulse_AI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   FIREBASE_WEB_API_KEY=your_firebase_web_api_key_here
   NEWS_API_KEY=your_newsapi_key_here  # Optional
   GNEWS_API_KEY=your_gnews_key_here    # Optional
   ```

4. **Set up Firebase**:
   - Download your Firebase service account key from Firebase Console → Project Settings → Service Accounts → Generate New Private Key
   - Save it as `serviceAccountKey.json` in the root directory
   - Enable Firestore Database in your Firebase Console
   - Enable Email/Password Authentication

### Running Locally

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository
Ensure your repository contains:
- `app.py` (main entry point)
- `requirements.txt` (all dependencies listed)
- **DO NOT** commit `serviceAccountKey.json` or `.env` to your repository

### Step 2: Configure Secrets

> **IMPORTANT**: The "Save" button will not work without proper Firebase credentials in secrets!

In your Streamlit Cloud dashboard (App Settings → Secrets), add:

```toml
# API Keys
GROQ_API_KEY = "your_groq_api_key"
FIREBASE_WEB_API_KEY = "your_firebase_web_api_key"
NEWS_API_ORG = "your_newsapi_key"  # Optional
GNEWS_IO = "your_gnews_key"        # Optional

# Firebase Service Account (REQUIRED for Save functionality)
# Copy all fields from your serviceAccountKey.json file
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

**Note**: The `private_key` field should contain the full key with `\n` for newlines. Streamlit will handle this automatically.

### Step 3: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select `app.py` as the main file
4. Click "Deploy"

## Project Structure

```
Pulse_AI/
├── app.py                      # Main application entry point
├── config/
│   └── settings.py            # Configuration and environment variables
├── services/
│   ├── firebase_manager.py    # Firebase authentication & Firestore operations
│   ├── gemini_summarizer.py   # AI summarization using Groq
│   ├── news_fetcher.py        # Multi-source news aggregation
│   ├── text_to_speech.py      # Audio generation with gTTS
│   └── translator.py          # Translation service using Groq
├── utils/
│   └── helpers.py             # UI utilities and CSS theming
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in repo)
└── serviceAccountKey.json     # Firebase service account (not in repo)
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | API key for Groq AI summarization |
| `FIREBASE_WEB_API_KEY` | Yes | Firebase Web API key for authentication |
| `NEWS_API_KEY` | No | NewsAPI key for additional news sources |
| `GNEWS_API_KEY` | No | GNews API key for alternative news sources |

## Technologies Used

- **Frontend**: Streamlit
- **AI/ML**: Groq (Llama 3.3 70B)
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth (Email/Password)
- **Text-to-Speech**: gTTS
- **News Sources**: NewsAPI, GNews, RSS Feeds

## Features in Detail

### Authentication System
- Secure email/password authentication via Firebase
- User-scoped data isolation in Firestore
- Persistent sessions with automatic logout

### AI Summarization
- Powered by Llama 3.3 70B via Groq
- Context-aware summaries with strict formatting
- Caching to avoid redundant API calls

### Audio Summaries
- English and Hindi language support
- On-demand generation with autoplay
- Translation using Groq for Hindi summaries

### Bookmark Management
- Save articles with automatic summarization
- Remove functionality in Saved Articles tab
- Persistent storage in Firestore per user

## Troubleshooting Streamlit Cloud Deployment

### Common Issues

1. **"Save" Button Not Working**:
   - Verify `[firebase]` section exists in Streamlit Secrets
   - Ensure all fields from `serviceAccountKey.json` are copied correctly
   - Check that `private_key` includes the full key with `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
   - Look for error messages in the app (now displayed in red boxes)

2. **"Database connection not initialized" Error**:
   - Firebase credentials are missing or incorrect in secrets
   - Verify the secrets format matches the example above
   - Ensure you're using `[firebase]` not `[firebase_credentials]`

3. **Missing Module Errors**:
   - Ensure all packages are in `requirements.txt`
   - Check for typos in package names

4. **API Key Errors**:
   - Verify all required keys (`GROQ_API_KEY`, `FIREBASE_WEB_API_KEY`) are in secrets
   - Check for trailing whitespace in keys
   - Ensure key names match exactly (case-sensitive)

5. **App Not Loading**:
   - Check Streamlit Cloud logs for errors
   - Ensure `app.py` is set as the main file
   - Wait for the app to fully restart after updating secrets

## License

This project is open-source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Streamlit Cloud logs
3. Verify all environment variables are set correctly

---

Built with ❤️ using Streamlit, Groq, and Firebase
