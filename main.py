import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# استخدام الموديل الثابت والمستقر 100%
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت رجع للنظام المستقر وشغال: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك فهد! عيوني وياك، شكو ماكو؟")
            return

        try:
            # توجيه ذكي باللهجة العراقية وبدون تكرار الاسم إلا عند السؤال عنه
            prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً ومتحدث بلهجة عراقية طبيعية وعفوية. "
                "قواعدك:\n"
                "1. رد دائماً بنفس لغة أو لهجة الشخص (بالعراقي الطبيعي أو الإنجليزية حسب طلبه).\n"
                "2. لا تذكر اسم صانعك ومبرمجك (فهد / itzF18) إلا إذا سألك شخص بشكل صريح ومباشر عن الشخص الذي صنعك أو برمجك أو صممك.\n"
                f"أجب على هذا الكلام: {clean_prompt}"
            )
            
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                reply_text = response.text.strip()
            else:
                reply_text = "عيوني وياك، اكتب جملة واضحة حتى أجاوبك!"
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            await message.reply("عيوني وياك، صار ضغط خفيف، احاجيني مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
