import telebot
from telebot import types
import os
import json
from datetime import datetime
import time

from config import TELEGRAM_TOKEN, MAX_PHOTO_SIZE, SUPPORTED_PHOTO_FORMATS
from database import Database
from ai_service import AIService

# Initialize bot and services
bot = telebot.TeleBot(TELEGRAM_TOKEN)
db = Database()
ai_service = AIService()

# User states for conversation flow
user_states = {}

class UserState:
    def __init__(self):
        self.state = "idle"
        self.temp_data = {}
        self.waiting_for = None

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Initialize user state
    get_user_state(user_id)
    
    welcome_text = """
👗 Welcome to Outfitify! 

I'm your AI fashion assistant that helps you:
• 📸 Add clothes to your wardrobe (photos or descriptions)
• 📦 Add multiple items at once
• ✏️ Edit your existing wardrobe
• 🎨 Create amazing outfits
• 💡 Get styling suggestions

Let's start building your digital wardrobe!
"""
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📸 Add Photo")
    btn2 = types.KeyboardButton("✍️ Add Description")
    btn3 = types.KeyboardButton("📦 Bulk Upload")
    btn4 = types.KeyboardButton("🎨 Create Outfit")
    btn5 = types.KeyboardButton("📚 My Wardrobe")
    btn6 = types.KeyboardButton("💡 Suggestions")
    btn7 = types.KeyboardButton("❓ Help")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Handle /help command"""
    help_text = """
🤖 Outfitify Bot Help

📸 **Adding Clothes:**
• Single Photo: Upload one photo at a time
• Single Description: Describe one item at a time
• 📦 Bulk Upload: Add multiple items quickly
  - Bulk Photos: Upload 1-10 photos at once
  - Bulk Descriptions: Add 1-10 items via text

📚 **Managing Your Wardrobe:**
• My Wardrobe: View, edit, and delete all your clothes
  - Click ✏️ to edit any item
  - Click 🗑️ to delete any item
• All wardrobe management is now in one place!

🎨 **Creating Outfits:**
• Create Outfit: Get AI-generated outfit suggestions
• Suggestions: Get outfit ideas based on your wardrobe

💡 **Tips:**
• Use clear, well-lit photos for better analysis
• Be specific in descriptions for accurate categorization
• Bulk upload supports 1-10 items per session
• You can edit any item details after adding them
• All wardrobe actions are now in the "My Wardrobe" section

❓ Need more help? Just ask!
"""
    
    bot.send_message(message.from_user.id, help_text)

@bot.message_handler(func=lambda message: message.text == "📸 Add Photo")
def add_photo_handler(message):
    """Handle photo addition request"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    state.state = "waiting_for_photo"
    state.waiting_for = "photo"
    
    bot.send_message(user_id, 
                    "📸 Please send me a photo of your clothing item.\n\n"
                    "I'll analyze it with AI and show you the details!")

@bot.message_handler(func=lambda message: message.text == "✍️ Add Description")
def add_description_handler(message):
    """Handle add description button"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    state.state = "waiting_for_description"
    state.waiting_for = "description"
    
    bot.send_message(user_id, 
                    "✍️ Please describe the clothing item you want to add.\n\n"
                    "For example:\n"
                    "• 'A blue cotton t-shirt with a small logo'\n"
                    "• 'Black leather jacket with silver zippers'\n"
                    "• 'Red summer dress with floral pattern'")

@bot.message_handler(func=lambda message: message.text == "📦 Bulk Upload")
def bulk_upload_handler(message):
    """Handle bulk upload button"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📸 Bulk Photos (1-10)")
    btn2 = types.KeyboardButton("✍️ Bulk Descriptions (1-10)")
    btn3 = types.KeyboardButton("❌ Cancel")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(user_id, 
                    "📦 Choose your bulk upload method:\n\n"
                    "📸 Bulk Photos: Upload 1-10 photos at once\n"
                    "✍️ Bulk Descriptions: Add 1-10 items via text\n\n"
                    "You can send multiple photos/descriptions and I'll process them all together!",
                    reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📸 Bulk Photos (1-10)")
def bulk_photos_handler(message):
    """Handle bulk photos button"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    state.state = "bulk_photos"
    state.waiting_for = "photos"
    state.temp_data = {'photos': [], 'max_photos': 10}
    
    bot.send_message(user_id, 
                    "📸 Send me 1-10 photos of your clothes!\n\n"
                    "You can send them one by one or in groups.\n"
                    "Maximum: 10 photos\n"
                    "When you're done, type 'Done' to process all photos.\n"
                    "Type '❌ Cancel' to stop.\n\n"
                    f"📸 Photos added: 0/{state.temp_data['max_photos']}")

@bot.message_handler(func=lambda message: message.text == "✍️ Bulk Descriptions (1-10)")
def bulk_descriptions_handler(message):
    """Handle bulk descriptions button"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    state.state = "bulk_descriptions"
    state.waiting_for = "descriptions"
    state.temp_data = {'descriptions': [], 'max_descriptions': 10}
    
    bot.send_message(user_id, 
                    "✍️ Send me 1-10 clothing descriptions!\n\n"
                    "Format: One item per line, for example:\n"
                    "Blue cotton t-shirt\n"
                    "Black leather jacket\n"
                    "Red summer dress\n\n"
                    "Maximum: 10 descriptions\n"
                    "When you're done, type 'Done' to process all items.\n"
                    "Type '❌ Cancel' to stop.\n\n"
                    f"✍️ Descriptions added: 0/{state.temp_data['max_descriptions']}")

@bot.message_handler(func=lambda message: message.text == "🎨 Create Outfit")
def create_outfit_handler(message):
    """Handle outfit creation request"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Check if user has clothes
    clothes = db.get_user_clothes(user_id)
    
    if not clothes:
        bot.send_message(user_id, "📚 Your wardrobe is empty! Add some clothes first to create outfits.")
        return
    
    # Ask for outfit request
    state.state = "waiting_for_outfit_request"
    state.waiting_for = "outfit_request"
    
    bot.send_message(user_id, 
                    "🎨 What kind of outfit would you like me to create?\n\n"
                    "Examples:\n"
                    "• 'Casual weekend look'\n"
                    "• 'Professional office outfit'\n"
                    "• 'Evening party ensemble'\n"
                    "• 'Comfortable weekend look'")

@bot.message_handler(func=lambda message: message.text == "📚 My Wardrobe")
def wardrobe_handler(message):
    """Handle wardrobe view request"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Get user's clothes
    clothes = db.get_user_clothes(user_id)
    
    if not clothes:
        bot.send_message(user_id, "📚 Your wardrobe is empty! Add some clothes first.")
        return
    
    # Show clothes with action buttons
    wardrobe_text = f"📚 Your Wardrobe ({len(clothes)} items):\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for item in clothes:
        # Create buttons for each item
        edit_btn = types.InlineKeyboardButton(
            f"✏️ {item['name']} (ID: {item['id']})", 
            callback_data=f"edit_item_{item['id']}"
        )
        delete_btn = types.InlineKeyboardButton(
            f"🗑️ Delete {item['name']}", 
            callback_data=f"delete_item_{item['id']}"
        )
        markup.add(edit_btn, delete_btn)
    
    markup.add(types.InlineKeyboardButton("❌ Close", callback_data="close_wardrobe"))
    
    bot.send_message(user_id, wardrobe_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🗑️ Delete Clothes")
def delete_clothes_handler(message):
    """Handle delete clothes request"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Get user's clothes
    clothes = db.get_user_clothes(user_id)
    
    if not clothes:
        bot.send_message(user_id, "📚 Your wardrobe is empty! Nothing to delete.")
        return
    
    # Show clothes with delete options
    delete_text = "🗑️ Select item to delete:\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for item in clothes:
        btn_text = f"🗑️ {item['name']} (ID: {item['id']})"
        callback_data = f"delete_item_{item['id']}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
    
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete"))
    
    bot.send_message(user_id, delete_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💡 Suggestions")
def suggestions_handler(message):
    """Handle outfit suggestions request"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Get user's clothes
    clothes = db.get_user_clothes(user_id)
    
    if not clothes:
        bot.send_message(user_id, "📚 Your wardrobe is empty! Add some clothes first to get suggestions.")
        return
    
    # Generate outfit suggestions
    bot.send_message(user_id, "💡 Generating outfit suggestions... Please wait!")
    
    suggestions = ai_service.generate_outfit_suggestions(clothes)
    
    if suggestions:
        suggestion_text = "💡 Outfit Suggestions:\n\n"
        
        for i, suggestion in enumerate(suggestions[:5], 1):  # Show top 5 suggestions
            suggestion_text += f"{i}. {suggestion}\n\n"
        
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("🎨 Create Outfit", callback_data="create_from_suggestion")
        btn2 = types.InlineKeyboardButton("🔄 More Suggestions", callback_data="more_suggestions")
        markup.add(btn1, btn2)
        
        bot.send_message(user_id, suggestion_text, reply_markup=markup)
    else:
        bot.send_message(user_id, "❌ Sorry, I couldn't generate suggestions right now. Try again later!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Handle photo uploads"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Get the largest photo size
    photo = message.photo[-1]
    file_id = photo.file_id
    
    # Download the photo
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Save photo to local storage
    photo_filename = f"photos/{user_id}_{int(time.time())}_{file_id}.jpg"
    os.makedirs("photos", exist_ok=True)
    
    with open(photo_filename, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    if state.state == "waiting_for_photo":
        # Single photo upload
        bot.send_message(user_id, "🔍 Analyzing your photo... Please wait!")
        
        # Analyze the photo
        analysis = ai_service.analyze_photo(photo_filename)
        
        if analysis:
            # Store analysis in state
            state.temp_data['analysis'] = analysis
            state.temp_data['photo_path'] = photo_filename
            state.temp_data['photo_file_id'] = file_id
            
            # Show analysis and ask for confirmation
            confirm_text = f"""
✅ Analysis Results:

📋 Item Details:
• Name: {analysis['name']}
• Category: {analysis['category']}
• Season: {analysis['season']}
• Occasion: {analysis['occasion']}
• Tags: {', '.join(analysis['tags'])}

Is this correct? You can edit any field if needed.
"""
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("✅ Save as is")
            btn2 = types.KeyboardButton("✏️ Edit details")
            btn3 = types.KeyboardButton("❌ Cancel")
            markup.add(btn1, btn2, btn3)
            
            state.state = "confirming_photo_analysis"
            state.waiting_for = "confirmation"
            
            bot.send_message(user_id, confirm_text, reply_markup=markup)
        else:
            bot.send_message(user_id, "❌ Sorry, I couldn't analyze this photo. Please try again with a clearer image.")
            state.state = "idle"
            state.waiting_for = None
    
    elif state.state == "bulk_photos":
        # Bulk photo upload
        current_count = len(state.temp_data['photos'])
        max_photos = state.temp_data['max_photos']
        
        if current_count >= max_photos:
            bot.send_message(user_id, f"❌ Maximum {max_photos} photos reached! Type 'Done' to process them.")
            return
        
        state.temp_data['photos'].append({
            'file_id': file_id,
            'path': photo_filename
        })
        
        new_count = len(state.temp_data['photos'])
        bot.send_message(user_id, f"📸 Photo {new_count} added! ({new_count}/{max_photos})\n\nSend more photos or type 'Done' when finished.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Handle all text messages"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    text = message.text
    
    if text == "❓ Help":
        help_command(message)
        return
    
    # Handle different states
    if state.state == "waiting_for_description":
        # Analyze the description
        analysis = ai_service.analyze_text_description(text)
        
        # Store analysis in state
        state.temp_data['analysis'] = analysis
        state.temp_data['user_description'] = text
        
        # Show analysis and ask for confirmation
        confirm_text = f"""
✅ I analyzed your description: "{text}"

📋 Analysis Results:
• Name: {analysis['name']}
• Category: {analysis['category']}
• Season: {analysis['season']}
• Occasion: {analysis['occasion']}
• Tags: {', '.join(analysis['tags'])}

Is this correct? You can edit any field if needed.
"""
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("✅ Save as is")
        btn2 = types.KeyboardButton("✏️ Edit details")
        btn3 = types.KeyboardButton("❌ Cancel")
        markup.add(btn1, btn2, btn3)
        
        state.state = "confirming_description"
        state.waiting_for = "confirmation"
        
        bot.send_message(user_id, confirm_text, reply_markup=markup)
    
    elif state.state == "confirming_photo_analysis" or state.state == "confirming_description":
        if text == "✅ Save as is":
            # Save the item
            analysis = state.temp_data['analysis']
            
            # Add to database
            item_id = db.add_clothing_item(
                user_id=user_id,
                name=analysis['name'],
                category=analysis['category'],
                description=f"{analysis['name']} - {analysis['category']}",
                photo_file_id=state.temp_data.get('photo_file_id'),
                photo_path=state.temp_data.get('photo_path'),
                tags=analysis['tags']
            )
            
            # Reset state
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            # Show main menu
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, 
                            f"✅ Successfully added '{analysis['name']}' to your wardrobe!\n\n"
                            f"Category: {analysis['category'].title()}\n"
                            f"Item ID: {item_id}",
                            reply_markup=markup)
        
        elif text == "✏️ Edit details":
            # Start editing process
            state.state = "editing_item"
            state.waiting_for = "edit_field"
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📝 Name")
            btn2 = types.KeyboardButton("📂 Category")
            btn3 = types.KeyboardButton("🏷️ Tags")
            btn4 = types.KeyboardButton("🌤️ Season")
            btn5 = types.KeyboardButton("🎯 Occasion")
            btn6 = types.KeyboardButton("❌ Cancel Edit")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
            
            bot.send_message(user_id, 
                            "✏️ What would you like to edit?",
                            reply_markup=markup)
        
        elif text == "❌ Cancel":
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, "❌ Cancelled. What would you like to do?", reply_markup=markup)
    
    elif state.state == "editing_item":
        if state.waiting_for == "edit_value":
            # Update the field value
            field = state.temp_data['editing_field']
            analysis = state.temp_data['analysis']
            
            if field == "tags":
                # Handle tags as a list
                analysis[field] = [tag.strip() for tag in text.split(',')]
            else:
                analysis[field] = text.lower() if field in ['category', 'season', 'occasion'] else text
            
            state.temp_data['analysis'] = analysis
            state.waiting_for = "edit_field"
            
            # Show updated analysis
            confirm_text = f"""
✅ Updated Analysis Results:

📋 Item Details:
• Name: {analysis['name']}
• Category: {analysis['category']}
• Season: {analysis['season']}
• Occasion: {analysis['occasion']}
• Tags: {', '.join(analysis['tags'])}

Is this correct? You can edit any field if needed.
"""
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("✅ Save as is")
            btn2 = types.KeyboardButton("✏️ Edit details")
            btn3 = types.KeyboardButton("❌ Cancel")
            markup.add(btn1, btn2, btn3)
            
            state.state = "confirming_photo_analysis" if state.temp_data.get('photo_path') else "confirming_description"
            state.waiting_for = "confirmation"
            
            bot.send_message(user_id, confirm_text, reply_markup=markup)
        
        elif text == "❌ Cancel Edit":
            # Go back to confirmation
            analysis = state.temp_data['analysis']
            confirm_text = f"""
✅ Analysis Results:

📋 Item Details:
• Name: {analysis['name']}
• Category: {analysis['category']}
• Season: {analysis['season']}
• Occasion: {analysis['occasion']}
• Tags: {', '.join(analysis['tags'])}

Is this correct? You can edit any field if needed.
"""
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("✅ Save as is")
            btn2 = types.KeyboardButton("✏️ Edit details")
            btn3 = types.KeyboardButton("❌ Cancel")
            markup.add(btn1, btn2, btn3)
            
            state.state = "confirming_photo_analysis" if state.temp_data.get('photo_path') else "confirming_description"
            state.waiting_for = "confirmation"
            
            bot.send_message(user_id, confirm_text, reply_markup=markup)
        
        elif text in ["📝 Name", "📂 Category", "🏷️ Tags", "🌤️ Season", "🎯 Occasion"]:
            # Store which field to edit
            field_map = {
                "📝 Name": "name",
                "📂 Category": "category", 
                "🏷️ Tags": "tags",
                "🌤️ Season": "season",
                "🎯 Occasion": "occasion"
            }
            
            state.temp_data['editing_field'] = field_map[text]
            state.waiting_for = "edit_value"
            
            if text == "📂 Category":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                categories = ["tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"]
                buttons = [types.KeyboardButton(cat.title()) for cat in categories]
                markup.add(*buttons)
                bot.send_message(user_id, "📂 Choose the category:", reply_markup=markup)
            elif text == "🌤️ Season":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                seasons = ["spring", "summer", "fall", "winter", "all"]
                buttons = [types.KeyboardButton(season.title()) for season in seasons]
                markup.add(*buttons)
                bot.send_message(user_id, "🌤️ Choose the season:", reply_markup=markup)
            elif text == "🎯 Occasion":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                occasions = ["casual", "formal", "business", "party", "sport"]
                buttons = [types.KeyboardButton(occasion.title()) for occasion in occasions]
                markup.add(*buttons)
                bot.send_message(user_id, "🎯 Choose the occasion:", reply_markup=markup)
            else:
                bot.send_message(user_id, f"Enter the new {field_map[text].lower()}:")
    
    elif state.state == "waiting_for_outfit_request":
        # Generate outfit based on request
        user_clothes = db.get_user_clothes(user_id)
        
        bot.send_message(user_id, "🎨 Creating your outfit... Please wait!")
        
        outfit = ai_service.generate_outfit(user_clothes, text, None)
        
        if outfit and outfit.get("selected_items"):
            outfit_text = "🎨 Your Outfit:\n\n"
            
            outfit_text += "👕 Items to wear:\n"
            for item in outfit['selected_items']:
                outfit_text += f"  • {item}\n"
            
            if outfit.get('styling_tips'):
                outfit_text += "\n💡 Styling Tips:\n"
                for tip in outfit['styling_tips']:
                    outfit_text += f"  • {tip}\n"
            
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("💾 Save Outfit", callback_data="save_outfit")
            btn2 = types.InlineKeyboardButton("🔄 New Outfit", callback_data="new_outfit")
            markup.add(btn1, btn2)
            
            bot.send_message(user_id, outfit_text, reply_markup=markup)
        else:
            bot.send_message(user_id, "❌ Sorry, I couldn't create an outfit with your request. Try a different description!")
        
        # Reset state
        state.state = "idle"
        state.waiting_for = None
    
    elif state.state == "bulk_descriptions":
        if text == "Done":
            if not state.temp_data['descriptions']:
                bot.send_message(user_id, "❌ No descriptions added. Please add some descriptions first.")
                return
            
            # Store the count before processing
            descriptions_count = len(state.temp_data['descriptions'])
            
            # Process all descriptions
            bot.send_message(user_id, f"🔍 Processing {descriptions_count} items... Please wait!")
            
            success_count = 0
            added_items = []  # Track successfully added items
            
            for description in state.temp_data['descriptions']:
                analysis = ai_service.analyze_text_description(description)
                if analysis:
                    item_id = db.add_clothing_item(
                        user_id=user_id,
                        name=analysis['name'],
                        category=analysis['category'],
                        description=description,
                        photo_file_id=None,
                        photo_path=None,
                        tags=analysis['tags']
                    )
                    if item_id:
                        success_count += 1
                        added_items.append(analysis['name'])
            
            # Reset state
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            # Show main menu
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            # Create the result message with item list
            if added_items:
                result_message = f"✅ Successfully added {success_count} out of {descriptions_count} items to your wardrobe!\n\n"
                result_message += "📋 You added:\n"
                for i, item_name in enumerate(added_items, 1):
                    result_message += f"{i}. {item_name}\n"
            else:
                result_message = f"❌ Failed to add any items. Please try again with better descriptions."
            
            bot.send_message(user_id, result_message, reply_markup=markup)
        
        elif text == "❌ Cancel":
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, "❌ Bulk upload cancelled.", reply_markup=markup)
        
        else:
            # Add description to bulk list
            current_count = len(state.temp_data['descriptions'])
            max_descriptions = state.temp_data['max_descriptions']
            
            if current_count >= max_descriptions:
                bot.send_message(user_id, f"❌ Maximum {max_descriptions} descriptions reached! Type 'Done' to process them.")
                return
            
            state.temp_data['descriptions'].append(text)
            new_count = len(state.temp_data['descriptions'])
            bot.send_message(user_id, f"✍️ Description {new_count} added! ({new_count}/{max_descriptions})\n\nSend more descriptions or type 'Done' when finished.")
    
    elif state.state == "bulk_photos":
        if text == "Done":
            if not state.temp_data['photos']:
                bot.send_message(user_id, "❌ No photos added. Please add some photos first.")
                return
            
            # Store the count before processing
            photo_count = len(state.temp_data['photos'])
            
            # Process all photos
            bot.send_message(user_id, f"🔍 Processing {photo_count} photos... Please wait!")
            
            success_count = 0
            added_items = []  # Track successfully added items
            
            for i, photo_data in enumerate(state.temp_data['photos'], 1):
                analysis = ai_service.analyze_photo(photo_data['path'])
                if analysis:
                    item_id = db.add_clothing_item(
                        user_id=user_id,
                        name=analysis['name'],
                        category=analysis['category'],
                        description=f"{analysis['name']} - {analysis['category']}",
                        photo_file_id=photo_data['file_id'],
                        photo_path=photo_data['path'],
                        tags=analysis['tags']
                    )
                    if item_id:
                        success_count += 1
                        added_items.append(analysis['name'])
            
            # Reset state
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            # Show main menu
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            # Create the result message with item list
            if added_items:
                result_message = f"✅ Successfully added {success_count} out of {photo_count} items to your wardrobe!\n\n"
                result_message += "📋 You added:\n"
                for i, item_name in enumerate(added_items, 1):
                    result_message += f"{i}. {item_name}\n"
            else:
                result_message = f"❌ Failed to add any items. Please try again with clearer photos."
            
            bot.send_message(user_id, result_message, reply_markup=markup)
        
        elif text == "❌ Cancel":
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, "❌ Bulk upload cancelled.", reply_markup=markup)
    
    elif state.state == "editing_existing_item":
        # Handle editing existing wardrobe items
        if text == "❌ Cancel Edit":
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, "❌ Edit cancelled.", reply_markup=markup)
        
        elif text in ["📝 Name", "📂 Category", "🏷️ Tags", "📄 Description"]:
            # Store which field to edit
            field_map = {
                "📝 Name": "name",
                "📂 Category": "category", 
                "🏷️ Tags": "tags",
                "📄 Description": "description"
            }
            
            state.temp_data['editing_field'] = field_map[text]
            state.waiting_for = "edit_existing_value"
            
            if text == "📂 Category":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                categories = ["tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"]
                buttons = [types.KeyboardButton(cat.title()) for cat in categories]
                markup.add(*buttons)
                bot.send_message(user_id, "📂 Choose the category:", reply_markup=markup)
            else:
                bot.send_message(user_id, f"Enter the new {field_map[text].lower()}:")
        
        elif state.waiting_for == "edit_existing_value":
            # Update the existing item
            field = state.temp_data['editing_field']
            item_id = state.temp_data['editing_item_id']
            
            if field == "tags":
                # Handle tags as a list
                new_value = [tag.strip() for tag in text.split(',')]
            else:
                new_value = text.lower() if field in ['category', 'season', 'occasion'] else text
            
            # Update in database
            success = db.update_clothing_item(user_id, item_id, field, new_value)
            
            if success:
                bot.send_message(user_id, f"✅ Updated {field} successfully!")
            else:
                bot.send_message(user_id, f"❌ Failed to update {field}. Please try again.")
            
            # Reset state
            state.state = "idle"
            state.temp_data = {}
            state.waiting_for = None
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton("📸 Add Photo")
            btn2 = types.KeyboardButton("✍️ Add Description")
            btn3 = types.KeyboardButton("📦 Bulk Upload")
            btn4 = types.KeyboardButton("🎨 Create Outfit")
            btn5 = types.KeyboardButton("📚 My Wardrobe")
            btn6 = types.KeyboardButton("💡 Suggestions")
            btn7 = types.KeyboardButton("❓ Help")
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
            
            bot.send_message(user_id, "What would you like to do next?", reply_markup=markup)
    
    else:
        # Default response for unrecognized commands
        bot.send_message(user_id, 
                        "I didn't understand that. Please use the menu buttons or type /help for assistance!")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle callback queries"""
    user_id = call.from_user.id
    state = get_user_state(user_id)
    
    if call.data == "save_outfit":
        bot.answer_callback_query(call.id, "Outfit saved! ✅")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    elif call.data == "new_outfit":
        bot.answer_callback_query(call.id, "Creating new outfit...")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        
        # Ask for new outfit request
        state.state = "waiting_for_outfit_request"
        state.waiting_for = "outfit_request"
        
        bot.send_message(user_id, 
                        "🎨 What kind of outfit would you like me to create?\n\n"
                        "Examples:\n"
                        "• 'Casual weekend look'\n"
                        "• 'Professional office outfit'\n"
                        "• 'Evening party ensemble'\n"
                        "• 'Comfortable weekend look'")
    
    elif call.data.startswith("edit_item_"):
        # Handle editing existing item
        item_id = int(call.data.split("_")[2])
        
        # Get item details
        item = db.get_clothing_item(user_id, item_id)
        if not item:
            bot.answer_callback_query(call.id, "Item not found!")
            return
        
        # Store item info in state
        state.state = "editing_existing_item"
        state.temp_data['editing_item_id'] = item_id
        state.temp_data['current_item'] = item
        
        # Show item details and edit options
        item_text = f"""
📋 Item Details (ID: {item_id}):

• Name: {item['name']}
• Category: {item['category']}
• Description: {item['description']}
• Tags: {', '.join(item['tags']) if item['tags'] else 'None'}

What would you like to edit?
"""
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton("📝 Name")
        btn2 = types.KeyboardButton("📂 Category")
        btn3 = types.KeyboardButton("🏷️ Tags")
        btn4 = types.KeyboardButton("📄 Description")
        btn5 = types.KeyboardButton("❌ Cancel Edit")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, item_text, reply_markup=markup)
    
    elif call.data.startswith("delete_item_"):
        # Handle deleting existing item
        item_id = int(call.data.split("_")[2])
        
        # Delete the item
        success, message_text = db.delete_clothing_item(user_id, item_id)
        
        if success:
            bot.answer_callback_query(call.id, "Item deleted! ✅")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(user_id, f"✅ {message_text}")
        else:
            bot.answer_callback_query(call.id, "Failed to delete! ❌")
            bot.send_message(user_id, f"❌ {message_text}")
    
    elif call.data == "cancel_delete":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "Delete cancelled!")
    
    elif call.data == "close_wardrobe":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, "Wardrobe closed!")

@bot.message_handler(func=lambda message: message.text == "✏️ Edit Wardrobe")
def edit_wardrobe_handler(message):
    """Handle edit wardrobe button"""
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Get user's clothes
    clothes = db.get_user_clothes(user_id)
    
    if not clothes:
        bot.send_message(user_id, "📚 Your wardrobe is empty! Add some clothes first.")
        return
    
    # Show clothes with edit options
    wardrobe_text = "📚 Your Wardrobe - Click to edit:\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for item in clothes:
        btn_text = f"✏️ {item['name']} (ID: {item['id']})"
        callback_data = f"edit_item_{item['id']}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
    
    markup.add(types.InlineKeyboardButton("❌ Close", callback_data="close_wardrobe"))
    
    bot.send_message(user_id, wardrobe_text, reply_markup=markup)

if __name__ == "__main__":
    print("🤖 Outfitify Bot is starting...")
    print("📱 Bot is running. Press Ctrl+C to stop.")
    
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}") 