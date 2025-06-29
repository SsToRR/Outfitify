import openai
import json
import base64
from config import OPENAI_API_KEY

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_clothing_photo(self, photo_path):
        """Analyze a clothing item from photo file"""
        try:
            # Read and encode the image
            with open(photo_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = """
            Analyze this clothing item photo and provide detailed information.
            
            Please provide a JSON response with the following structure:
            {
                "name": "Full detailed name with brand if visible",
                "category": "One of: tops, bottoms, dresses, outerwear, shoes, accessories",
                "season": "spring/summer/fall/winter/all",
                "occasion": "casual/formal/business/party/sport",
                "tags": ["tag1", "tag2", "tag3"]
            }
            
            IMPORTANT RULES:
            1. Keep the FULL name with all details (color, brand, style, etc.)
            2. If a brand logo or name is visible, include it in the name
            3. Be specific about colors, materials, and styles
            4. Do NOT shorten or simplify the name
            5. Include any distinctive features you can see
            
            Examples:
            - "Black leather jacket with silver zippers"
            - "Blue cotton t-shirt with Nike logo"
            - "Red summer dress with floral pattern"
            
            Be specific and accurate in your analysis.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a fashion expert. Analyze clothing items from photos and provide detailed, accurate information. Always preserve full names with brands and details."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]}
                ],
                temperature=0.3
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            result = json.loads(json_str)
            
            # Apply brand corrections if needed
            brand_corrections = {
                'maison margiela': 'Maison Margiela',
                'nike': 'Nike',
                'adidas': 'Adidas',
                'puma': 'Puma',
                'reebok': 'Reebok',
                'converse': 'Converse',
                'vans': 'Vans',
                'levis': 'Levi\'s',
                'calvin klein': 'Calvin Klein',
                'tommy hilfiger': 'Tommy Hilfiger',
                'ralph lauren': 'Ralph Lauren',
                'gucci': 'Gucci',
                'prada': 'Prada',
                'balenciaga': 'Balenciaga',
                'yeezy': 'Yeezy',
                'off white': 'Off-White',
                'supreme': 'Supreme'
            }
            
            for wrong, correct in brand_corrections.items():
                result['name'] = result['name'].replace(wrong, correct)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing clothing photo: {e}")
            return {
                "name": "Unknown Item",
                "category": "accessories",
                "season": "all",
                "occasion": "casual",
                "tags": ["unknown"]
            }
    
    def analyze_photo(self, photo_path):
        """Alias for analyze_clothing_photo"""
        return self.analyze_clothing_photo(photo_path)
    
    def analyze_text_description(self, description):
        """Analyze a clothing item from text description"""
        prompt = f"""
        Analyze this clothing description and provide detailed information:
        
        Description: {description}
        
        Please provide a JSON response with the following structure:
        {{
            "name": "Full corrected name with brand if mentioned",
            "category": "One of: tops, bottoms, dresses, outerwear, shoes, accessories",
            "season": "spring/summer/fall/winter/all",
            "occasion": "casual/formal/business/party/sport",
            "tags": ["tag1", "tag2", "tag3"]
        }}
        
        IMPORTANT RULES:
        1. Keep the FULL name with all details (color, brand, style, etc.)
        2. If a brand is mentioned (like "maison margiela", "nike", "adidas"), include it in the name
        3. Make spelling corrections but preserve all information
        4. Do NOT shorten or simplify the name
        5. If the description is unclear, use the original description as the name
        
        Examples:
        - "Black pants maison margiela" → "Black pants Maison Margiela"
        - "Blue nike sneakers" → "Blue Nike sneakers"
        - "Red dress with flowers" → "Red dress with flowers"
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a fashion expert. Analyze clothing descriptions and provide detailed, accurate information. Always preserve full names with brands and details. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = content[start:end]
                try:
                    result = json.loads(json_str)
                    
                    # Ensure the name is not shortened - if it's too short, use original description
                    if len(result.get('name', '')) < len(description) * 0.7:  # If name is significantly shorter
                        # Try to correct spelling but keep full description
                        corrected_name = description.strip()
                        # Basic spelling corrections for common brands
                        brand_corrections = {
                            'maison margiela': 'Maison Margiela',
                            'nike': 'Nike',
                            'adidas': 'Adidas',
                            'puma': 'Puma',
                            'reebok': 'Reebok',
                            'converse': 'Converse',
                            'vans': 'Vans',
                            'levis': 'Levi\'s',
                            'calvin klein': 'Calvin Klein',
                            'tommy hilfiger': 'Tommy Hilfiger',
                            'ralph lauren': 'Ralph Lauren',
                            'gucci': 'Gucci',
                            'prada': 'Prada',
                            'balenciaga': 'Balenciaga',
                            'yeezy': 'Yeezy',
                            'off white': 'Off-White',
                            'supreme': 'Supreme'
                        }
                        
                        for wrong, correct in brand_corrections.items():
                            corrected_name = corrected_name.replace(wrong, correct)
                        
                        result['name'] = corrected_name
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    # Fall back to corrected original description
                    corrected_name = description.strip()
                    # Apply brand corrections
                    brand_corrections = {
                        'maison margiela': 'Maison Margiela',
                        'nike': 'Nike',
                        'adidas': 'Adidas',
                        'puma': 'Puma',
                        'reebok': 'Reebok',
                        'converse': 'Converse',
                        'vans': 'Vans',
                        'levis': 'Levi\'s',
                        'calvin klein': 'Calvin Klein',
                        'tommy hilfiger': 'Tommy Hilfiger',
                        'ralph lauren': 'Ralph Lauren',
                        'gucci': 'Gucci',
                        'prada': 'Prada',
                        'balenciaga': 'Balenciaga',
                        'yeezy': 'Yeezy',
                        'off white': 'Off-White',
                        'supreme': 'Supreme'
                    }
                    
                    for wrong, correct in brand_corrections.items():
                        corrected_name = corrected_name.replace(wrong, correct)
                    
                    return {
                        "name": corrected_name,
                        "category": "accessories",
                        "season": "all",
                        "occasion": "casual",
                        "tags": ["clothing", "item"]
                    }
            else:
                # No JSON found, use corrected original description
                corrected_name = description.strip()
                # Apply brand corrections
                brand_corrections = {
                    'maison margiela': 'Maison Margiela',
                    'nike': 'Nike',
                    'adidas': 'Adidas',
                    'puma': 'Puma',
                    'reebok': 'Reebok',
                    'converse': 'Converse',
                    'vans': 'Vans',
                    'levis': 'Levi\'s',
                    'calvin klein': 'Calvin Klein',
                    'tommy hilfiger': 'Tommy Hilfiger',
                    'ralph lauren': 'Ralph Lauren',
                    'gucci': 'Gucci',
                    'prada': 'Prada',
                    'balenciaga': 'Balenciaga',
                    'yeezy': 'Yeezy',
                    'off white': 'Off-White',
                    'supreme': 'Supreme'
                }
                
                for wrong, correct in brand_corrections.items():
                    corrected_name = corrected_name.replace(wrong, correct)
                
                return {
                    "name": corrected_name,
                    "category": "accessories",
                    "season": "all",
                    "occasion": "casual",
                    "tags": ["clothing", "item"]
                }
            
        except Exception as e:
            print(f"Error analyzing description: {e}")
            # Use corrected original description as fallback
            corrected_name = description.strip()
            # Apply brand corrections
            brand_corrections = {
                'maison margiela': 'Maison Margiela',
                'nike': 'Nike',
                'adidas': 'Adidas',
                'puma': 'Puma',
                'reebok': 'Reebok',
                'converse': 'Converse',
                'vans': 'Vans',
                'levis': 'Levi\'s',
                'calvin klein': 'Calvin Klein',
                'tommy hilfiger': 'Tommy Hilfiger',
                'ralph lauren': 'Ralph Lauren',
                'gucci': 'Gucci',
                'prada': 'Prada',
                'balenciaga': 'Balenciaga',
                'yeezy': 'Yeezy',
                'off white': 'Off-White',
                'supreme': 'Supreme'
            }
            
            for wrong, correct in brand_corrections.items():
                corrected_name = corrected_name.replace(wrong, correct)
            
            return {
                "name": corrected_name,
                "category": "accessories",
                "season": "all",
                "occasion": "casual",
                "tags": ["clothing", "item"]
            }
    
    def generate_outfit(self, user_clothes, user_request, user_preferences=None):
        """Generate an outfit based on user's clothes and request"""
        
        # Format user's clothes for the prompt
        clothes_info = []
        for item in user_clothes:
            # Handle both old tuple format and new dictionary format
            if isinstance(item, dict):
                # New dictionary format
                clothes_info.append(f"- {item['name']} ({item['category']}): {item['description']}")
            else:
                # Old tuple format (fallback)
                clothes_info.append(f"- {item[2]} ({item[3]}): {item[4]}")
        
        clothes_text = "\n".join(clothes_info)
        
        # Format user preferences
        preferences_text = ""
        if user_preferences:
            preferences_text = f"""
            User Preferences:
            - Style: {user_preferences[1] or 'Not specified'}
            - Colors: {user_preferences[2] or 'Not specified'}
            - Season: {user_preferences[3] or 'Not specified'}
            """
        
        prompt = f"""
        Create a stylish outfit based on the user's request and available clothing items.
        
        User Request: {user_request}
        
        Available Clothing Items:
        {clothes_text}
        
        {preferences_text}
        
        Please provide a JSON response with the following structure:
        {{
            "selected_items": [
                "Item name 1",
                "Item name 2",
                "Item name 3"
            ],
            "styling_tips": [
                "Tip 1",
                "Tip 2",
                "Tip 3"
            ]
        }}
        
        Make sure the outfit is practical, stylish, and matches the user's request.
        Only use items from the available clothing list.
        Return only the names of the items, not descriptions.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist. Create stylish, practical outfits based on available clothing items and user preferences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error generating outfit: {e}")
            return {
                "selected_items": [],
                "styling_tips": ["Keep it simple and comfortable"]
            }
    
    def suggest_outfit_improvements(self, current_outfit, user_clothes):
        """Suggest improvements to an existing outfit"""
        
        clothes_info = []
        for item in user_clothes:
            clothes_info.append(f"- {item[2]} ({item[3]}): {item[4]}")
        
        clothes_text = "\n".join(clothes_info)
        
        prompt = f"""
        Suggest improvements to this outfit:
        
        Current Outfit: {current_outfit}
        
        Available Clothing Items:
        {clothes_text}
        
        Please provide suggestions for:
        1. Alternative items that might work better
        2. Additional accessories that could enhance the look
        3. Styling tips for the current combination
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist. Provide helpful suggestions for improving outfits."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error suggesting improvements: {e}")
            return "Keep it simple and comfortable!"
    
    def generate_outfit_suggestions(self, user_clothes):
        """Generate general outfit suggestions based on user's wardrobe"""
        
        # Format user's clothes for the prompt
        clothes_info = []
        for item in user_clothes:
            # Handle both old tuple format and new dictionary format
            if isinstance(item, dict):
                # New dictionary format
                clothes_info.append(f"- {item['name']} ({item['category']}): {item['description']}")
            else:
                # Old tuple format (fallback)
                clothes_info.append(f"- {item[2]} ({item[3]}): {item[4]}")
        
        clothes_text = "\n".join(clothes_info)
        
        prompt = f"""
        Based on the user's wardrobe, suggest 5 different outfit combinations.
        
        Available Clothing Items:
        {clothes_text}
        
        Please provide 5 outfit suggestions in this format:
        1. [Outfit Name]: [Brief description of the combination]
        2. [Outfit Name]: [Brief description of the combination]
        3. [Outfit Name]: [Brief description of the combination]
        4. [Outfit Name]: [Brief description of the combination]
        5. [Outfit Name]: [Brief description of the combination]
        
        Make the suggestions diverse, practical, and stylish.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional fashion stylist. Create diverse, practical outfit suggestions based on available clothing items."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            # Split into individual suggestions
            suggestions = [line.strip() for line in content.split('\n') if line.strip() and line[0].isdigit()]
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating outfit suggestions: {e}")
            return [
                "Casual Weekend Look: Comfortable and relaxed style",
                "Professional Office Outfit: Clean and business-appropriate",
                "Evening Party Ensemble: Elegant and stylish",
                "Comfortable Home Style: Cozy and practical",
                "Smart Casual Look: Balanced between formal and relaxed"
            ] 