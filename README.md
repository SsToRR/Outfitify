# 🤖 Outfitify - AI Fashion Assistant Bot

A comprehensive Telegram bot that helps you manage your wardrobe and create amazing outfits using AI-powered analysis and suggestions.

## ✨ Features

### 📸 **Smart Clothing Management**
- **Photo Analysis**: Upload photos of your clothes and get AI-powered analysis
- **Text Descriptions**: Describe your clothes and get detailed categorization
- **Bulk Upload**: Add 1-10 photos or descriptions at once for efficient wardrobe building
- **Full Name Preservation**: Keeps brand names and full details (e.g., "Black pants Maison Margiela")

### 📚 **Wardrobe Management**
- **View Wardrobe**: See all your clothes with inline edit/delete buttons
- **Edit Items**: Modify name, category, tags, and description of any item
- **Delete Items**: Remove clothes directly from the wardrobe view
- **Integrated Interface**: All wardrobe actions in one convenient place

### 🎨 **AI-Powered Outfit Creation**
- **Smart Outfit Generation**: Get outfit suggestions based on your wardrobe
- **Custom Requests**: Ask for specific styles (casual, formal, party, etc.)
- **Styling Tips**: Receive AI-generated styling advice
- **Outfit Suggestions**: Get multiple outfit ideas for different occasions

### 🔧 **Advanced Features**
- **Brand Recognition**: Automatically corrects and preserves brand names
- **Category Classification**: Tops, bottoms, dresses, outerwear, shoes, accessories
- **Tag System**: Automatic tagging for better organization
- **Season & Occasion**: Smart categorization for different contexts

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Clone the repository
git clone <your-repo-url>
cd Outfitify

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env_example.txt .env
```

### 2. **Configure Bot**
Edit `.env` file with your credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

### 3. **Run the Bot**
```bash
python main.py
```

## 📱 How to Use

### **Adding Clothes**
1. **Single Photo**: Send a photo → AI analyzes → Confirm details
2. **Single Description**: Describe item → AI categorizes → Confirm details
3. **Bulk Photos**: Upload 1-10 photos → Type "Done" → Get list of added items
4. **Bulk Descriptions**: Send 1-10 descriptions → Type "Done" → Get list of added items

### **Managing Wardrobe**
1. **View**: Click "📚 My Wardrobe" to see all items
2. **Edit**: Click "✏️" next to any item to modify details
3. **Delete**: Click "🗑️" next to any item to remove it

### **Creating Outfits**
1. **Click "🎨 Create Outfit"**
2. **Describe your request** (e.g., "casual weekend look")
3. **Get AI-generated outfit** with styling tips
4. **Save or create new outfit**

### **Getting Suggestions**
1. **Click "💡 Suggestions"**
2. **Get 5 outfit ideas** based on your wardrobe
3. **Create outfits** from suggestions

## 🛠️ Technical Details

### **Architecture**
- **Telegram Bot**: Python-telegram-bot for messaging
- **AI Service**: OpenAI GPT-4o for analysis and outfit generation
- **Database**: SQLite for local storage
- **Image Processing**: Base64 encoding for AI analysis

### **File Structure**
```
Outfitify/
├── main.py              # Main bot logic
├── ai_service.py        # AI analysis and generation
├── database.py          # Database operations
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # Environment variables (create from env_example.txt)
├── photos/             # User uploaded photos
└── outfitify.db        # SQLite database
```

### **Database Schema**
- **users**: User information
- **clothes**: Clothing items with metadata
- **outfits**: Saved outfit combinations
- **user_preferences**: User style preferences

## 🔧 Configuration

### **Environment Variables**
- `TELEGRAM_TOKEN`: Your Telegram bot token from @BotFather
- `OPENAI_API_KEY`: Your OpenAI API key for AI features

### **Bot Settings**
- **Photo Size Limit**: 10MB maximum
- **Bulk Upload Limit**: 1-10 items per session
- **Supported Formats**: JPEG, PNG for photos

## 🎯 Use Cases

### **Personal Wardrobe Management**
- Organize your entire wardrobe digitally
- Get outfit suggestions for any occasion
- Track what you own and what you wear

### **Fashion Enthusiasts**
- Experiment with different combinations
- Get AI-powered styling advice
- Discover new ways to wear existing items

### **Minimalist Wardrobes**
- Optimize your clothing collection
- Create versatile outfit combinations
- Reduce decision fatigue

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- Python-telegram-bot library
- Fashion community for inspiration

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the error logs
3. Create an issue in the repository

---

**Made with ❤️ for fashion lovers everywhere!** 