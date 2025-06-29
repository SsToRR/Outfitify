# 🚀 Deployment Guide

This guide will help you deploy your Outfitify bot to various platforms.

## 📋 Prerequisites

Before deploying, make sure you have:

1. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)
2. **OpenAI API Key** from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Python 3.8+** installed
4. **Git** for version control

## 🏠 Local Deployment

### 1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd Outfitify
pip install -r requirements.txt
```

### 2. **Environment Configuration**
```bash
cp env_example.txt .env
# Edit .env with your API keys
```

### 3. **Run Locally**
```bash
python main.py
```

## ☁️ Cloud Deployment

### **Option 1: Heroku**

1. **Create Heroku App**
```bash
heroku create your-outfitify-bot
```

2. **Add Buildpacks**
```bash
heroku buildpacks:add heroku/python
```

3. **Set Environment Variables**
```bash
heroku config:set TELEGRAM_TOKEN=your_telegram_token
heroku config:set OPENAI_API_KEY=your_openai_api_key
```

4. **Deploy**
```bash
git push heroku main
```

5. **Scale**
```bash
heroku ps:scale worker=1
```

### **Option 2: Railway**

1. **Connect Repository**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository

2. **Set Environment Variables**
   - Add `TELEGRAM_TOKEN`
   - Add `OPENAI_API_KEY`

3. **Deploy**
   - Railway will automatically deploy from your main branch

### **Option 3: DigitalOcean App Platform**

1. **Create App**
   - Go to DigitalOcean App Platform
   - Connect your GitHub repository

2. **Configure**
   - Set Python as runtime
   - Add environment variables
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `python main.py`

3. **Deploy**
   - Click "Create Resources"

### **Option 4: Google Cloud Run**

1. **Create Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

2. **Build and Deploy**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/outfitify
gcloud run deploy outfitify --image gcr.io/PROJECT_ID/outfitify --platform managed
```

## 🔧 Environment Variables

Make sure to set these environment variables:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

## 📊 Monitoring

### **Health Checks**
Add a health check endpoint to your bot:

```python
@bot.message_handler(commands=['health'])
def health_check(message):
    bot.reply_to(message, "✅ Bot is running!")
```

### **Logging**
Enable logging for debugging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔒 Security Considerations

1. **Never commit API keys** to your repository
2. **Use environment variables** for sensitive data
3. **Enable webhook mode** for production (optional)
4. **Set up rate limiting** if needed
5. **Monitor API usage** to avoid unexpected costs

## 📈 Scaling

### **For High Traffic**
- Use webhook mode instead of polling
- Implement database connection pooling
- Add caching for frequently accessed data
- Consider using Redis for session management

### **Database Considerations**
- For production, consider PostgreSQL or MySQL
- Implement database migrations
- Set up automated backups

## 🐛 Troubleshooting

### **Common Issues**

1. **Bot not responding**
   - Check if environment variables are set
   - Verify bot token is correct
   - Check logs for errors

2. **AI not working**
   - Verify OpenAI API key
   - Check API usage limits
   - Ensure sufficient credits

3. **Database errors**
   - Check file permissions
   - Verify database path
   - Consider using external database

### **Logs**
```bash
# View logs on Heroku
heroku logs --tail

# View logs on Railway
railway logs

# View logs on DigitalOcean
doctl apps logs APP_ID
```

## 📞 Support

If you encounter deployment issues:

1. Check the platform's documentation
2. Review error logs
3. Verify environment variables
4. Test locally first
5. Create an issue in the repository

---

**Happy Deploying! 🎉** 