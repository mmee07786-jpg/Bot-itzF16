import os
import discord
from discord.ext import commands
import google.generativeai as genai
from PIL import Image
import io
import time

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

# نظام الذاكرة المؤقتة لكل مستخدم (يحفظ الجلسات وتنسحب لفترة ساعة كاملة)
# شكل القاموس: {user_id: {"chat": chat_session, "last_time": timestamp}}
user_chats = {}
MEMORY_TIMEOUT = 3600  # ساعة كاملة بالثواني (60 دقيقة)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بنظام الذاكرة المؤقتة (ساعة كاملة) ودعم الصور: {bot.user.name}")

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

        user_id = message.author.id
        current_time = time.time()

        # التحقق من انتهاء وقت الذاكرة (ساعة كاملة) أو إنشاء جلسة جديدة
        if user_id in user_chats:
            if current_time - user_chats[user_id]["last_time"] > MEMORY_TIMEOUT:
                # انتهت الساعة، مسح الذاكرة القديمة وبدء جلسة جديدة
                del user_chats[user_id]

        # التعليمات الدقيقة وثابتة
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً. "
            "قاعدتك الأساسية: رد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً (إذا تحدث بالإنجليزية رد بالإنجليزية، إذا بالعراقية رد بعراقي). "
            "معلوماتك الشخصية: عمرك الحقيقي 20 سنة، وتعيش في العراق. "
            "معلومة عن الصنع: الشخص الذي قام بصنعك وبرمجتك وتطويرك هو المبدع فهد (معروف بـ itzF18). اذكر هذه المعلومة فقط إذا سألك أحد عن صانعك، ولا تكرر اسم فهد في كل جملة لكي لا يكون الأمر مزعجاً. "
            "أجب بسرعة وبدون مقدمات معقدة وتذكر كل ما تم تداوله في هذه المحادثة."
        )

        reply_text = None
        success = False

        # حلقة تجربة الموديلات مع الاحتفاظ بالسياق (Chat Session)
        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )
                
                # إذا لم تكن جلسة المحادثة موجودة أو تم مسحها، نبدأ جلسة جديدة
                if user_id not in user_chats:
                    user_chats[user_id] = {
                        "chat": current_model.start_chat(history=[]),
                        "last_time": current_time
                    }
                else:
                    # تحديث وقت النشاط الأخير
                    user_chats[user_id]["last_time"] = current_time

                chat_session = user_chats[user_id]["chat"]

                # تجميع المحتوى المرسل (صورة أو نص أو كلاهما)
                content_to_send = []
                if image_content:
                    content_to_send.append(image_content)
                if clean_prompt:
                    content_to_send.append(clean_prompt)
                else:
                    content_to_send.append("صف هذه الصورة باختصار وبنفس لهجة السائل.")

                # إرسال الرسالة إلى جلسة الدردشة المحفوظة
                response = chat_session.send_message(content_to_send)
                
                if response and response.text:
                    reply_text = response.text.strip()
                    success = True
                    break
            except Exception as e:
                # في حال حدث خطأ مع الموديل، جرب الموديل التالي
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
