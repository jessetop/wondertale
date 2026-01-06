# Children's Story Generator

A web application that generates personalized, age-appropriate stories for children ages 3-8 with customizable characters, topics, and optional illustrations.

## Features

- **Personalized Characters**: Add 1-5 characters with custom names and pronouns
- **Topic Selection**: Choose from space, community, dragons, or fairies themes
- **Keyword Integration**: Include 3 or 5 custom keywords in stories
- **Age-Appropriate Content**: All content filtered for children ages 3-8
- **Optional Illustrations**: AI-generated images to accompany stories
- **Text-to-Speech**: Read stories aloud with child-friendly voices
- **Tablet-Optimized**: Large, touch-friendly interface designed for tablets
- **Educational Value**: Each story includes a positive moral lesson

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

4. **Visit** `http://localhost:5000`

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for story and image generation
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `FLASK_ENV`: Environment (development/production)
- `MAX_STORY_LENGTH`: Maximum story length in words (default: 400)
- `DEFAULT_VOICE_SPEED`: Text-to-speech speed (default: 0.8)

## Deployment

### Railway.app (Recommended)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Render.com
1. Connect repository to Render
2. Use the included `render.yaml` configuration
3. Set environment variables in Render dashboard

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html        # Story creation form
│   └── story.html        # Story display
├── static/               # Static assets
│   ├── css/style.css     # Child-friendly styles
│   └── js/app.js         # Frontend interactions
├── services/             # Backend services
│   ├── story_generator.py
│   ├── image_generator.py
│   └── content_filter.py
└── .env                  # Environment variables
```

## Safety Features

- Content filtering for age-appropriate vocabulary
- Validation of user inputs and keywords
- Positive theme enforcement
- No scary or violent content allowed
- Simple sentence structures for early readers

## Technology Stack

- **Backend**: Python 3.11+ with Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Services**: OpenAI GPT-4 for stories, DALL-E 3 for images
- **Deployment**: Railway.app or Render.com
- **Styling**: CSS Grid/Flexbox for responsive design

## License

This project is licensed under the MIT License.