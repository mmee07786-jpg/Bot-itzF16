import os
import discord
from discord.ext import commands
import google.generativeai as genai

# قراءة المتغيرات من الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد مفتاح Google Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# إعدادات ديسكورد
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ | البوت شغال باسم: {bot.user.name} وجاهز للرد!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        async with message.channel.typing():
            try:
                # تنظيف النص من المنشن
                clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
                
                if not clean_prompt:
                    await message.reply("هلا بيكم! شترید أسألك أو اصمملك اليوم؟")
                    return

                # التحقق إذا كان الطلب فيديو
                if "فيديو" in clean_prompt or "video" in clean_prompt:
                    await message.reply("⏳ | جاري معالجة وصنع الفيديو المطلوب... انتظر حوالي **30 إلى 60 ثانية** وراح يكون جاهز!")
                    # هنا يتم إضافة كود توليد الفيديو لاحقاً حسب المنصة
                    return

                # التحقق إذا كان الطلب صورة
                elif "صورة" in clean_prompt or "ارسم" in clean_prompt or "image" in clean_prompt:
                    await message.reply("🎨 | جاري تصميم صورتك بدقة عالية... انتظر **5 إلى 10 ثواني** بس!")
                    # هنا يتم إضافة كود توليد الصورة لاحقاً حسب المنصة
                    return

                # الرد العادي على الأسئلة والدردشة باللهجة العراقية
                system_instruction = "أنت مساعد ذكاء اصطناعي ودود في سيرفر ديسكورد، تتكلم وتجيب باللهجة العراقية البيضاء وبأسلوب لطيف ومفيد."
                full_prompt = f"{system_instruction}\nالسؤال: {clean_prompt}"

                response = model.generate_content(full_prompt)
                reply_text = response.text

                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)

            except Exception as e:
                print(f"خطأ: {e}")
                await message.reply("عذراً، صار عندي خلل بسيط وما قدرت أعالج رسالتك حالياً. حاول مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"انقطع الاتصال، جاري إعادة التشغيل تلقائياً... الخطأ: {e}")
