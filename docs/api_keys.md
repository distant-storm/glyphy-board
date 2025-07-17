
# API Keys

This document outlines the API keys required for various InkyPi plugins and how to configure them.

## Environment Variables

API keys are stored in a `.env` file in the root directory of the project. Create this file if it doesn't exist:

```bash
touch .env
```

Add your API keys to this file using the format shown below for each service.

## Open AI API Key

Required for the AI plugins (if available)

- Sign up or log in to [OpenAI](https://platform.openai.com/signup)
- Navigate to [API Keys](https://platform.openai.com/api-keys)
- Click "Create new secret key"
- Give it a name and copy the key
- Store your api key in the .env file with the key OPEN_AI_SECRET

```
OPEN_AI_SECRET=your-key
```

## Google Calendar API

Required for the Calendar Plugin (if available)

Instructions for setting up Google Calendar API access will be provided when the calendar plugin is available.

## Configuration

After adding API keys to your `.env` file:

1. Restart the InkyPi service:
   ```bash
   sudo systemctl restart inkypi.service
   ```

2. The plugins should now be able to access their respective APIs.

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them publicly
- Regularly rotate your API keys for security