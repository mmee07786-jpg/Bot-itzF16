import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# دالة ذكية تبحث عن أول موديل نصي شغال ومتاح على مفتاحك حصراً
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    print(f"✅ | تم العثور على الموديل الشغال: {m.name}")
                    return genai.GenerativeModel(m.name)
    except Exception as e:
        print(f"⚠️ خطأ بالبحث عن الموديل: {e}")
    
    # موديل احتياطي مضمون كملجأ أخير
    return genai.GenerativeModel("gemini-1.5-flash")

model = get_working_model()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال وبأفضل شكل: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟ / Hey there!")
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

                await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
                
            except Exception as e:
                print(f"Gemini API Error Detail: {e}")
                await message.reply(f"عذراً حبيبي، صار عندي خطأ: `{str(e)[:50]}`")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
