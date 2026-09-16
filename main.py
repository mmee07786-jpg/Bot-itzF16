import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تهيئة المفتاح بالطريقة القياسية
genai.configure(api_key=GEMINI_API_KEY)

# استخدام اسم الموديل الصريح والمباشر
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ | البوت شغال وجاهز: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيونى وياك، شكو ماكو؟")
            return

        try:
            # إرسال النص مباشرة إلى جيميناي مع طلب اللهجة العراقية
            prompt = f"أنت مساعد ذكي تتكلم باللهجة العراقية العفوية حصراً وبدون تكلف. أجب على هذا الكلام باختصار: {clean_prompt}"
            response = model.generate_content(prompt)
            
            reply_text = response.text.strip()
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            print(f"Error: {e}")
            await message.reply(f"حبيبي صار خطأ بالاستجابة: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
