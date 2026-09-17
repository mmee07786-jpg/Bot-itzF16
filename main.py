import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        try:
            prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً. أجب باللهجة العراقية وبدون تكرار كلام المستخدم:\n"
                f"{clean_prompt}"
            )
            
            response = model.generate_content(prompt)
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
            
        except Exception as e:
            # نطبع الخطأ بالكونسول حتى نشوفه بـ Railway بدال ما يكرر رسالة وهمية
            print(f"EXACT ERROR: {e}")
            await message.reply(f"صار خطأ يمعود: {str(e)[:60]}")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
