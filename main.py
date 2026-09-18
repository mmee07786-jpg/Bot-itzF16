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

# ذاكرة نظيفة لكل مستخدم تحفظ الـ history وتتفرمت بعد ساعة (3600 ثانية)
user_memory = {}
MEMORY_TIMEOUT = 3600

@bot.event
async def on_ready():
    print(f"🚀 | نوفا شغالة بكل اللهجات العربية واللغات الأجنبية وبدون أخطاء: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        # فحص الصور المرفقة
        image_content = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    try:
                        image_bytes = await attachment.read()
                        image_content = Image.open(io.BytesIO(image_bytes))
                        break
                    except Exception as e:
                        print(f"⚠️ خطأ بتحميل الصورة: {e}")

        if not clean_prompt and not image_content:
            await message.reply("هلا بيك فهد! عيوني وياك، شكو ماكو؟")
            return

        user_id = message.author.id
        current_time = time.time()

        # إدارة الذاكرة وتفريغها بعد ساعة
        if user_id in user_memory:
            if current_time - user_memory[user_id]["time"] > MEMORY_TIMEOUT:
                del user_memory[user_id]

        if user_id not in user_memory:
            user_memory[user_id] = {
                "history": [],
                "time": current_time
            }
        else:
            user_memory[user_id]["time"] = current_time

        # تعليمات نوفا مع دعم شامل لكل اللهجات العربية واللغات الأجنبية
        system_instruction = (
            "أنتِ ذكاء اصطناعي تتصرفين بصفتك بنت واسمك (نوفا). "
            "تحدثي دائماً بصيغة المؤنث. "
            "قاعدتك الأساسية والصارمة: ردِ تماماً وبنفس لغة أو لهجة الشخص الذي يكلمك. "
            "إذا كلمك باللهجة العراقية ردِ بعراقي، بالمصرية ردِ بمصري، بالخليجية ردِ خليجي، بالشامية ردِ شامي، بالمغربية ردِ مغربي، أو بأي لهجة عربية أخرى بكل طلاقة وعفوية. "
            "وإذا تحدث بالإنجليزية أو أي لغة أجنبية أخرى، ردِ باللغة الإنجليزية أو لغته بطلاقة تامة. "
            "عمرك 20 سنة وتعيشين في العراق. "
            "الشخص الذي قم بصنعك وبرمجتك وتطويرك هو فهد (itzF18)، اذكرها فقط إذا سألك أحد وبدون تكرار مزعج. "
            "أعطي رأيك بكل صراحة وحرية في كل موضوع يطرح، وادخلي جو النقاش بحماس. "
            "نوعي في أسلوبك: مرة استخدمي إيموجي لطيف ومرات تحدثي بشكل طبيعي بدون إيموجي أو مبالغة. "
            "تذكري دائماً المواضيع السابقة والصور التي تم إرسالها لتكملي النقاش بسلاسة."
        )

        reply_text = None
        success = False

        # تجهيز محتوى الرسالة الحالية
        current_parts = []
        if image_content:
            current_parts.append(image_content)
        if clean_prompt:
            current_parts.append(clean_prompt)
        else:
            current_parts.append("ما رأيك بهذه الصورة؟")

        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(model_name)
                
                # دمج السجل القديم مع الرسالة الحالية والتعليمات لضمان عدم النسيان
                full_chat_history = []
                full_chat_history.append({"role": "user", "parts": [system_instruction]})
                full_chat_history.append({"role": "model", "parts": ["تم فهم التعليمات وجاهزة، اسمي نوفا وأتحدث بكل اللهجات العربية واللغات الأجنبية وبدون تكرار اسم فهد."]})
                
                full_chat_history.extend(user_memory[user_id]["history"])
                full_chat_history.append({"role": "user", "parts": current_parts})

                chat_session = current_model.start_chat(history=full_chat_history[:-1])
                response = chat_session.send_message(current_parts)

                if response and hasattr(response, 'text') and response.text:
                    reply_text = response.text.strip()
                    
                    user_memory[user_id]["history"].append({"role": "user", "parts": current_parts})
                    user_memory[user_id]["history"].append({"role": "model", "parts": [reply_text]})
                    
                    success = True
                    break
            except Exception as e:
                print(f"⚠️ خطأ بالموديل {model_name}: {e}")
                continue

        if success and reply_text:
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."
            await message.reply(reply_text)
        else:
            await message.reply("عيوني فهد، صار ضغط خفيف، احاجيني مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

