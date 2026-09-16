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
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! شترید أسألك؟")
            return

        try:
            # الرد السريع باللهجة العراقية
            response = model.generate_content(f"أنت مساعد ذكي تتكلم باللهجة العراقية فقط وبدون تكلف. أجب على هذا الكلام: {clean_prompt}")
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("عذراً، صار عندي ضغط بالاتصال، جرب تمنشن مرة ثانية.")

    await bot.process_commands(message)

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"Restarting... {e}")
