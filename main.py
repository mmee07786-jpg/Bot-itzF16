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

# دالة ذكية تجلب أحدث موديل flash متوفر تلقائياً من حسابك
def get_latest_flash_model():
    try:
        models = client.models.list()
        for m in models:
            # نبحث عن أي موديل يحتوي على كلمة flash ويدعم توليد النصوص
            if "flash" in m.name and "generateContent" in m.supported_generation_methods:
                # تنظيف اسم الموديل ليناسب الاستدعاء الصحيح
                model_id = m.name.replace("models/", "")
                return model_id
    except Exception as e:
        print(f"⚠️ خطأ في جلب الموديلات تلقائياً: {e}")
    
    # موديل احتياطي مضمون في حال لم يعمل البحث التلقائي
    return "gemini-2.5-flash"

@bot.event
async def on_ready():
    active_model = get_latest_flash_model()
    print(f"🚀 | البوت اشتغل واختار أحدث موديل تلقائياً ({active_model}): {bot.user.name}")

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

        # التوجيه الطبيعي باللهجة العراقية
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً ومتحدث بلهجة عراقية طبيعية وعفوية. "
            "قواعدك:\n"
            "1. رد دائماً بنفس لغة أو لهجة الشخص (بالعراقي الطبيعي أو الإنجليزية حسب طلبه).\n"
            "2. لا تذكر اسم صانعك ومبرمجك (فهد / itzF18) إلا إذا سألك شخص بشكل صريح ومباشر عن الشخص الذي صنعك أو برمجك أو صممك."
        )

        try:
            # جلب أحدث موديل متوفر بشكل ديناميكي لكل رسالة أو الاعتماد عليه
            current_model = get_latest_flash_model()
            
            response = client.models.generate_content(
                model=current_model,
                contents=clean_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
            )
            
            if response and response.text:
                reply_text = response.text.strip()
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."
                await message.reply(reply_text)
            else:
                await message.reply("عيوني فهد، ما وصلني رد واضح، جرب دز رسالتك مرة ثانية!")

        except Exception as e:
            print(f"❌ خطأ أثناء توليد الرد: {e}")
            await message.reply("عيوني وياك، صار ضغط خفيف، احاجيني مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
