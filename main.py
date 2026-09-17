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
    print(f"🚀 | البوت شغال والـ Cogs جاهزة: {bot.user.name}")
    
    # تحميل ملف الصور (Cog) بشكل آلي
    try:
        await bot.load_extension("image_cog")
        print("🎨 | تم تحميل نظام الصور بنجاح!")
    except Exception as e:
        print(f"❌ | فشل تحميل نظام الصور: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن حصراً للنصوص
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        async with message.channel.typing():
            try:
                prompt = (
                    "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                    "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                    "أجب بسرعة وبدون مقدمات معقدة على هذا الكلام: "
                    f"{clean_prompt}"
                )
                
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text if reply_text else "عيوني وياك!")
                
            except Exception as e:
                print(f"Text Error: {e}")
                await message.reply("عيوني وياك، صار عندي لود ثواني ورجعتلك!")

    # هذه الدالة مهمة حتى تستقبل الـ Cogs الأوامر بشكل طبيعي
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
