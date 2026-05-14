import telebot
from telebot import types
import json
from datetime import datetime

# بياناتك
API_TOKEN = '7071617327:AAGy2Z5ljCj691lJXdYVWf6trSEWNhd0qsc'
ADMIN_ID = '1995454152'

bot = telebot.TeleBot(API_TOKEN)

# دالة مطورة لحفظ الطلبات بشكل منظم
def save_order(user_id, username, service_name, price):
    order = {
        "user_id": user_id,
        "username": username,
        "service": service_name,
        "price": price,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("orders.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(order, ensure_ascii=False) + "\n")

@bot.message_handler(content_types=['web_app_data'])
def handle_data(message):
    try:
        # محاولة قراءة البيانات كـ JSON
        data = json.loads(message.web_app_data.data)
        name = data.get('service', 'خدمة مجهولة')
        price = int(data.get('price', 0))

        bot.send_invoice(
            message.chat.id,
            title="طلب Tmwelx",
            description=f"تجهيز: {name}",
            invoice_payload="pay_payload",
            provider_token="", 
            currency="XTR",
            prices=[telebot.types.LabeledPrice(label=name, amount=price)]
        )
        save_order(message.from_user.id, message.from_user.username, name, price)
    except json.JSONDecodeError:
        # في حال كان المتجر لا يزال يرسل نصاً قديماً
        bot.send_message(message.chat.id, "يرجى تحديث المتجر (إغلاقه وفتحه) لإرسال الطلب بشكل صحيح.")
# الخطوات الضرورية لإتمام الدفع
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "🎉 تم استلام النجوم بنجاح! جارٍ تنفيذ طلبك.")
    bot.send_message(ADMIN_ID, f"💰 عملية دفع ناجحة من @{message.from_user.username} للخدمة: {message.successful_payment.invoice_payload}")

print("البوت يعمل بنظام النجوم والـ JSON المطور...")
bot.infinity_polling()