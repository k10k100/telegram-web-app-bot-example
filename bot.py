import telebot
from telebot import types
import json
import os
import pandas as pd
from datetime import datetime

# بياناتك الأساسية
API_TOKEN = '7071617327:AAGy2Z5ljCj691lJXdYVWf6trSEWNhd0qsc'
ADMIN_ID = '1995454152' 

bot = telebot.TeleBot(API_TOKEN)

# دالة حفظ الطلبات
def save_order(user_id, username, service_name, price):
    order = {
        "user_id": user_id,
        "username": username or "لا يوجد",
        "service": service_name,
        "price": price,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("orders.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(order, ensure_ascii=False) + "\n")

# --- لوحة تحكم الإدارة الاحترافية ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) == ADMIN_ID:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_broadcast = types.InlineKeyboardButton("📢 إرسال إعلان للكل", callback_data="broadcast")
        btn_stats = types.InlineKeyboardButton("👥 إحصائيات العملاء", callback_data="user_stats")
        btn_export = types.InlineKeyboardButton("📊 تصدير Excel", callback_data="export_excel")
        btn_clear = types.InlineKeyboardButton("🗑️ مسح السجل", callback_data="clear_json")
        markup.add(btn_broadcast, btn_stats, btn_export, btn_clear)
        
        bot.send_message(message.chat.id, "🛠️ **غرفة التحكم الاحترافية**\nاختر المهمة المطلوبة:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    if str(call.from_user.id) != ADMIN_ID: return

    # 1. إرسال إعلان لجميع المستخدمين الذين طلبوا سابقاً
    if call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "📝 أرسل نص الإعلان الآن (نص فقط):")
        bot.register_next_step_handler(msg, process_broadcast)

    # 2. إحصائيات العملاء والأرباح
    elif call.data == "user_stats":
        if not os.path.exists("orders.json"):
            bot.answer_callback_query(call.id, "لا يوجد بيانات")
            return
        
        user_counts = {}
        total_stars = 0
        with open("orders.json", "r", encoding="utf-8") as f:
            for line in f:
                order = json.loads(line)
                user = order.get('username')
                user_counts[user] = user_counts.get(user, 0) + 1
                total_stars += order.get('price', 0)
        
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats_msg = f"💰 **إجمالي الأرباح:** {total_stars} نجمة\n\n"
        stats_msg += "🔝 **أفضل 10 مشترين:**\n"
        for user, count in sorted_users:
            stats_msg += f"▫️ @{user}: {count} طلبات\n"
        
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="Markdown")

    elif call.data == "export_excel":
        # (كود التصدير السابق)
        pass

def process_broadcast(message):
    text = message.text
    if not os.path.exists("orders.json"): return
    
    users = set()
    with open("orders.json", "r", encoding="utf-8") as f:
        for line in f: users.add(json.loads(line)['user_id'])
    
    count = 0
    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 **إعلان من الإدارة:**\n\n{text}", parse_mode="Markdown")
            count += 1
        except: continue
    
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الإعلان لـ {count} مستخدم.")

# --- تشغيل المتجر والنجوم ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(url="رابط_صفحتك_على_جيت_هاب")
    menu_button = types.KeyboardButton(text="🛒 فتح المتجر الاحترافي", web_app=web_app)
    markup.add(menu_button)
    bot.send_message(message.chat.id, "💎 أهلاً بك في Tmwelx Pro\nأفضل وأسرع متجر لخدمات التواصل الاجتماعي.", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_data(message):
    data = json.loads(message.web_app_data.data)
    name = data.get('service')
    price = int(data.get('price'))

    bot.send_invoice(
        message.chat.id,
        title=f"تأكيد طلب: {name}",
        description="اضغط دفع لإتمام العملية بالنجوم",
        invoice_payload=f"order_{name}",
        provider_token="", 
        currency="XTR",
        prices=[types.LabeledPrice(label=name, amount=price)]
    )
    save_order(message.from_user.id, message.from_user.username, name, price)

bot.infinity_polling()