import telebot

# بياناتك الصحيحة
API_TOKEN = '7071617327:AAGy2Z5ljCj691lJXdYVWf6trSEWNhd0qsc'
ADMIN_ID = '1995454152'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    # استخدام الرابط المباشر الخاص بك
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url="https://k10k100.github.io/telegram-web-app-bot-example/")
    markup.add(telebot.types.InlineKeyboardButton("فتح متجر Tmwelx 💎", web_app=web_app))
    
    bot.send_message(message.chat.id, "مرحباً بك في متجر تمويلكس!\nاضغط على الزر بالأسفل لبدء التسوق:", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_data(message):
    # استلام الطلب من المتجر
    order_details = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ تم استلام طلبك: {order_details}")
    
    # إرسال إشعار لك كمسؤول (ADMIN)
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد وصل!\nالطلب: {order_details}\nمن المستخدم: @{message.from_user.username}")

print("Bot is running...")
bot.infinity_polling()