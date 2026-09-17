import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تهيئة العميل بالطريقة الرسمية الحديثة
client = genai.Client(api_key=GEMINI_API_KEY)

# أحدث الموديلات السريعة بالترتيب (مع 3.8 في المقدمة)
MODELS_FALLBACK = [
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بالنظام السريع وبأروع موديل: {bot.user.name}")

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

        # التوجيه الطبيعي (بدون ذكر اسمك إلا عند السؤال المباشر)
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً ومتحدث بلهجة عراقية طبيعية وعفوية. "
            "قواعدك:\n"
            "1. رد دائماً بنفس لغة أو لهجة الشخص (بالعراقي الطبيعي أو الإنجليزية حسب طلبه).\n"
            "2. لا تذكر اسم صانعك ومبرمجك (فهد / itzF18) إلا إذا سألك شخص بشكل صريح ومباشر عن الشخص الذي صنعك أو برمجك أو صممك."
        )

        reply_text = None
        success = False

        # تجربة الموديلات بالترتيب بدءاً من 3.8
        for model_name in MODELS_FALLBACK:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=clean_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                    ),
                )
                if response and response.text:
                    reply_text = response.text.strip()
                    success = True
                    break
            except Exception as e:
                print(f"⚠️ الموديل {model_name} واجه خطأ: {e}")
                continue

        if success and reply_text:
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."
            await message.reply(reply_text)
        else:
            # رسالة خطأ نظيفة ومخصصة للنصوص فقط
            await message.reply("عيوني وياك، صار ضغط خفيف، احاجيني مرة ثانية بتركيز!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
