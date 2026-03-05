import telebot
from telebot import types
import google.generativeai as genai

# --- الإعدادات الأساسية ---
API_KEY = "AIzaSyCu79HNwe810G4q0LsZbGw2Uf3qMfYad60" # مفتاح جيمناي الخاص بك
BOT_TOKEN = "8662890757:AAF6PEAv_StwIy6H6Yx0CGG5KkhmCzJ3Ub4" # توكن البوت
ADMIN_ID = 1983226660 # تم وضع الأيدي الخاص بك هنا لفتح لوحة التحكم لك فقط
CH_ID = "@moa_nbh" # يوزر قناتك للاشتراك الإجباري

# إعداد الذكاء الاصطناعي
genai.configure(api_key=API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)
users_file = "users.txt" # لحفظ المشتركين للإذاعة

# --- دالات مساعدة ---
def add_user(user_id):
    with open(users_file, "a+") as f:
        f.seek(0)
        if str(user_id) not in f.read():
            f.write(f"{user_id}\n")

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CH_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return True

# --- لوحة التحكم (الأزرار) ---
def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats"),
        types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast"),
        types.InlineKeyboardButton("🚫 إشعار الحظر: ✅", callback_data="none"),
        types.InlineKeyboardButton("🔔 إشعار الدخول: ✅", callback_data="none")
    )
    return markup

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user.id)
    # إشعار دخول للمطور
    bot.send_message(ADMIN_ID, f"🔔 عضو جديد دخل البوت:\nالاسم: {message.from_user.first_name}\nالأيدي: {message.from_user.id}")
    
    if not check_sub(message.from_user.id):
        bot.reply_to(message, f"⚠️ يجب أن تشترك في القناة أولاً:\n{CH_ID}")
        return

    welcome_text = "أهلاً بك في بوت التواصل والذكاء الاصطناعي! 🤖\nاستخدم الأزرار أدناه أو اسألني أي سؤال."
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "مرحباً أيها المطور! إليك لوحة التحكم:", reply_markup=admin_keyboard())
    else:
        bot.reply_to(message, welcome_text)

# --- معالجة الأزرار (Callback) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "stats":
        with open(users_file, "r") as f:
            count = len(f.readlines())
        bot.answer_callback_query(call.id, f"عدد المستخدمين: {count}")
    
    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "أرسل الرسالة التي تريد إذاعتها للجميع:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    with open(users_file, "r") as f:
        users = f.readlines()
    count = 0
    for user in users:
        try:
            bot.send_message(user.strip(), message.text)
            count += 1
        except:
            continue
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الإذاعة إلى {count} مستخدم.")

# --- الرد بالذكاء الاصطناعي ---
@bot.message_handler(func=lambda message: True)
def ai_reply(message):
    if not check_sub(message.from_user.id):
        bot.reply_to(message, "اشترك بالقناة أولاً!")
        return
    
    try:
        wait = bot.reply_to(message, "جاري التفكير... ⏳")
        response = ai_model.generate_content(message.text)
        bot.edit_message_text(response.text, chat_id=message.chat.id, message_id=wait.message_id)
    except:
        bot.reply_to(message, "حدث خطأ في الاتصال.")

print("البوت يعمل الآن...")
bot.polling()
