# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter permission issues on Windows, try:
```bash
pip install --user -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Troubleshooting

### Flask Installation Issues
If you encounter issues installing Flask on Windows, try:
1. Run Command Prompt as Administrator
2. Use: `pip install --upgrade pip`
3. Then: `pip install -r requirements.txt`

### OpenAI API Key
- Get your API key from: https://platform.openai.com/api-keys
- Make sure you have credits in your OpenAI account
- Keep your API key secure and never commit it to version control

### Port Issues
If port 5000 is in use, set a different port in your `.env` file:
```
PORT=8000
```

## Development Mode

For development with auto-reload:
```bash
set FLASK_ENV=development
python app.py
```