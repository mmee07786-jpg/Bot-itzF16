import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تهيئة العميل بالطريقة الرسمية الحديثة
client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت izf18 شغال وبكل قوة: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        async with message.channel.typing():
            try:
                system_instruction = (
                    "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                    "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                    "أجب بسرعة وبدون مقدمات معقدة."
                )
                
                # استخدام النموذج المباشر والصريح gemini-2.0-flash
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=clean_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                    )
                )
                
                reply_text = response.text.strip()
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text if reply_text else "عيوني وياك!")
                
            except Exception as e:
                print(f"GenAI Error Detail: {e}")
                await message.reply(f"عذراً حبيبي، صار عندي خطأ بالاتصال: `{str(e)[:50]}`")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
