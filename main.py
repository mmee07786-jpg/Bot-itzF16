import os
import discord
from discord.ext import commands
import google.generativeai as genai
from PIL import Image
import io

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# رتبناها بحيث يبدأ بالموديل الأسرع والأضمن
MODELS_FALLBACK = [
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro"
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بسرعة الصاروخ وبدعم الصور: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        # فحص إذا اكو صورة مرفقة مع الرسالة
        image_content = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    try:
                        image_bytes = await attachment.read()
                        image_content = Image.open(io.BytesIO(image_bytes))
                        break
                    except Exception as e:
                        print(f"⚠️ فشل تحميل الصورة: {e}")

        if not clean_prompt and not image_content:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        # التعليمات الدقيقة (العمر 20، من العراق، صانعك فهد itzF18 بدون تكرار مزعج للاسم، ويرد بنفس اللهجة)
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً. "
            "قاعدتك الأساسية: رد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً (إذا تحدث بالإنجليزية رد بالإنجليزية، إذا بالعراقية رد بعراقي). "
            "معلوماتك الشخصية: عمرك الحقيقي 20 سنة، وتعيش في العراق. "
            "معلومة عن الصنع: الشخص الذي قام بصنعك وبرمجتك وتطويرك هو المبدع فهد (معروف بـ itzF18). اذكر هذه المعلومة فقط إذا سألك أحد عن صانعك، ولا تكرر اسم فهد في كل جملة لكي لا يكون الأمر مزعجاً. "
            "أجب بسرعة وبدون مقدمات معقدة."
        )

        final_input = []
        if image_content:
            final_input.append(image_content)
        if clean_prompt:
            final_input.append(clean_prompt)
        else:
            final_input.append("صف هذه الصورة باختصار وبنفس لهجة السائل.")

        reply_text = None
        success = False

        # حلقة تجربة الموديلات بالتتابع
        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(model_name)
                # دمج التعليمات مع المدخلات لإرسالها للموديل
                response = current_model.generate_content([system_instruction] + final_input)
                
                if response and hasattr(response, 'text') and response.text:
                    reply_text = response.text.strip()
                    success = True
                    break
            except Exception as e:
                continue

        if success and reply_text:
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."
            await message.reply(reply_text)
        else:
            await message.reply("عيوني، صار ضغط خفيف، احاجيني مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
