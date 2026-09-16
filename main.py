import os
import discord
from discord.ext import commands
import google.generativeai as genai

# جلب المفاتيح من الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ربط مفتاح جوجل
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"البوت جاهز وشغال: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # الرد فقط عند المنشن
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        # إخراج النص المكتوب بدون المنشن
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! شترید أسألك؟")
            return

        try:
            # إرسال الرسالة لجوجل جيميني واستلام الجواب فوراً باللهجة العراقية
            response = model.generate_content(f"أنت مساعد ذكي تتكلم باللهجة العراقية فقط وبدون تكلف. أجب على هذا الكلام: {clean_prompt}")
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            # طباعة الخطأ بالكونسول لتعرفه، وإرسال رد بسيط للمستخدم
            print(f"Error: {e}")
            await model_fallback_reply(message, clean_prompt)

    await bot.process_commands(message)

async def model_fallback_reply(message, text):
    try:
        # محاولة ثانية سريعة جداً في حال حصل ضغط
        fallback_model = genai.GenerativeModel("gemini-1.5-flash")
        res = fallback_model.generate_content(text)
        await message.reply(res.text.strip())
    except:
        await message.reply("عذرأً حبيبي، تأكد من صحة مفتاح الـ API الخاص بـ Gemini في إعدادات الاستضافة (Variables).")

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(fRestarting... {e})
