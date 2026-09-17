import os
import discord
from discord.ext import commands
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت izf18 اشتغل بالطريقة الصح: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("ها عيوني، وياك! شكو ماكو؟")
            return

        try:
            prompt = (
                "أنت مساعد ذكي باللهجة العراقية. أجب على هذا السؤال مباشرة وبدون مقدمات وبدون تكرار كلام المستخدم:\n"
                f"{clean_prompt}"
            )
            
            # استخدام الموديل الصحيح والمعتمد 1.5-flash
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            
            if response and response.text:
                reply_text = response.text.strip()
            else:
                reply_text = "حبيبي الرد اجا فارغ!"

            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error Details: {error_msg}")
            await message.reply(f"عذراً فهد، صار خطأ: `{error_msg[:80]}`")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
