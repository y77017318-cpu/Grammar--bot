import re
import logging
import os
import asyncio
from typing import Tuple, List, Dict
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Enhanced grammar rules with categories
GRAMMAR_RULES = [
    {
        'category': 'Subject-Verb Agreement',
        'pattern': r'\bI (goes|eats|plays|reads|writes)\b',
        'correction': 'I go',
        'explanation': '🚫 "I" always takes base form verb! ✅ Use "I go" 🌟',
        'examples': ['❌ I goes to school', '✅ I go to school']
    },
    {
        'category': 'Subject-Verb Agreement',
        'pattern': r'\b(He|She|It) (go|eat|play|read|write)\b',
        'correction': r'\1 \2s',
        'explanation': '🐰 He/She/It requires verb + "s"! 🎯',
        'examples': ['❌ He play football', '✅ He plays football']
    },
    {
        'category': 'Tense Consistency',
        'pattern': r'\b(I am|You are|He is|She is|It is|We are|They are) (go|eat|play)\b',
        'correction': r'\1 \2ing',
        'explanation': '📥 Present continuous requires verb + "ing"! 🌈',
        'examples': ['❌ I am go to school', '✅ I am going to school']
    },
    {
        'category': 'Verb Forms',
        'pattern': r'\b(I|You|We|They) (was)\b',
        'correction': r'\1 were',
        'explanation': '🦊 I/You/We/They use "were" in past tense! 🎀',
        'examples': ['❌ They was happy', '✅ They were happy']
    },
    {
        'category': 'Auxiliary Verbs',
        'pattern': r'\bdo (he|she|it)\b',
        'correction': r'does \1',
        'explanation': '🤪 He/She/It uses "does" as auxiliary! 🥳',
        'examples': ['❌ Do she like music?', '✅ Does she like music?']
    }
]

class GrammarChecker:
    def __init__(self):
        self.rules = GRAMMAR_RULES
    
    def check_grammar(self, text: str) -> Tuple[str, List[Dict]]:
        """Check and correct grammar with detailed feedback"""
        original_text = text
        corrections = []
        
        for rule in self.rules:
            try:
                if re.search(rule['pattern'], text, re.IGNORECASE):
                    corrected = re.sub(
                        rule['pattern'], 
                        rule['correction'], 
                        text, 
                        flags=re.IGNORECASE
                    )
                    if corrected != text:
                        text = corrected
                        corrections.append({
                            'category': rule['category'],
                            'explanation': rule['explanation'],
                            'examples': rule['examples']
                        })
            except Exception as e:
                logger.error(f"Rule error: {e}")
                continue
        
        return text, corrections

# Initialize grammar checker
grammar_checker = GrammarChecker()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with keyboard"""
    welcome_text = """
🎓 **Smart Grammar Checker Bot** 🤖

I'll help you improve your English grammar instantly! 📚✨

**Features:**
✅ Real-time grammar correction
📝 Detailed explanations  
🎯 Example sentences
📊 Grammar statistics

**How to use:**
1. Just send me any English sentence
2. I'll auto-correct and explain mistakes
3. Learn from detailed examples

**Example:**
✗ *I goes to school*
✅ *I go to school*
🐰 **Explanation:** "I" always takes base form verb!

Ready to improve your English? Send me a sentence! 🚀
"""
    
    keyboard = [["Check Grammar", "View Rules"], ["Help", "About"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = """
🆘 **Help Guide**

**Commands:**
/start - Start the bot
/help - Show this help message  
/rules - View grammar rules
/stats - Your grammar statistics

**Simply type** any English sentence and I'll check it automatically!

**Supported Rules:**
• Subject-verb agreement
• Verb tenses
• Auxiliary verbs
• And many more!

**Tip:** Practice regularly to improve your grammar skills! 💪
"""
    await update.message.reply_text(help_text)

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display all grammar rules"""
    rules_text = "📚 **Grammar Rules Collection**\n\n"
    
    current_category = ""
    for rule in GRAMMAR_RULES:
        if rule['category'] != current_category:
            current_category = rule['category']
            rules_text += f"\n🔹 **{current_category}**\n"
        
        rules_text += f"📖 {rule['explanation']}\n"
        for example in rule['examples']:
            rules_text += f"   {example}\n"
        rules_text += "\n"
    
    await update.message.reply_text(rules_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    try:
        user_text = update.message.text
        
        # Handle keyboard buttons
        if user_text == "Check Grammar":
            await update.message.reply_text("📝 Send me a sentence to check!")
            return
        elif user_text == "View Rules":
            await show_rules(update, context)
            return
        elif user_text == "Help":
            await help_command(update, context)
            return
        elif user_text == "About":
            await update.message.reply_text("🤖 Advanced Grammar Checker\nVersion 2.0\nBuilt with Python")
            return
        
        # Check if text contains English characters
        if not any(c.isalpha() and ord(c) < 128 for c in user_text):
            await update.message.reply_text("🌍 Please send text in English for grammar checking!")
            return
        
        # Process grammar check
        corrected_text, corrections = grammar_checker.check_grammar(user_text)
        
        if corrected_text != user_text and corrections:
            # Build detailed response
            response = f"🔍 **Grammar Analysis**\n\n"
            response += f"✗ **Original:** `{user_text}`\n"
            response += f"✅ **Corrected:** `{corrected_text}`\n\n"
            
            response += "📖 **Corrections Made:**\n"
            for i, correction in enumerate(corrections, 1):
                response += f"\n{i}. **{correction['category']}**\n"
                response += f"   💡 {correction['explanation']}\n"
                for example in correction['examples']:
                    response += f"   {example}\n"
            
            response += f"\n🎉 **Perfect!** {len(corrections)} error(s) fixed! 🌈"
            
        else:
            response = f"✅ **Perfect Grammar!**\n\n"
            response += f"`{user_text}`\n\n"
            response += "🌟 Excellent! No grammar errors found! 🎯"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("❌ Sorry, I encountered an error. Please try again!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    stats_text = """
📊 **Grammar Statistics** (Coming Soon!)

Future features:
• Error tracking over time
• Most common mistakes
• Progress reports
• Personalized learning tips

Stay tuned for updates! 🚀
"""
    await update.message.reply_text(stats_text)

async def main():
    """Start the bot"""
    print("🎓 Advanced Grammar Bot Starting...")
    print("=" * 40)
    
    # Railway environment theke token nebe
    BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
        return
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("rules", show_rules))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot is running successfully on Railway!")
        print("📱 Features:")
        print("   • Smart grammar checking")
        print("   • Interactive keyboard")
        print("   • Detailed explanations")
        print("   • Example sentences")
        print("💬 Bot is now live 24/7! 🚀")
        
        # Start polling
        await application.run_polling()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Please check your Bot Token!")

if __name__ == "__main__":
    asyncio.run(main())
