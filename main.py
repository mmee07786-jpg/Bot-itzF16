import os
import io
import discord
from discord.ext import commands
import google.generativeai as genai
from PIL import Image

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# إضافة جيميناي 3.8 في صدارة القائمة والموديلات الحديثة الداعمة للصور
MODELS_FALLBACK = [
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest"
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بأحدث موديلات جيميناي (بما فيها 3.8): {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        # قراءة الصورة المرفقة إن وجدت
        image_part = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    try:
                        image_bytes = await attachment.read()
                        image_part = Image.open(io.BytesIO(image_bytes))
                        break
                    except Exception as img_err:
                        print(f"⚠️ خطأ في قراءة الصورة: {img_err}")

        if not clean_prompt and not image_part:
            await message.reply("هلا بيك فهد! عيوني وياك، شكو ماكو؟")
            return

        # التوجيه الطبيعي (لا يذكر اسم الصانع إلا إذا سألوه صراحة)
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً ومتحدث بلهجة عراقية طبيعية وعفوية. "
            "قواعدك:\n"
            "1. رد دائماً بنفس لغة أو لهجة الشخص (بالعراقي الطبيعي أو الإنجليزية حسب طلبه).\n"
            "2. لا تذكر اسم صانعك ومبرمجك (فهد / itzF18) إلا إذا سألك شخص بشكل صريح ومباشر عن الشخص الذي صنعك أو برمجك أو صممك.\n"
            "3. إذا دز لك صورة، اقرأ بدقة كل ما فيها من نصوص أو تفاصيل واجب عن سؤال الشخص عنها باحترافية وبدون مقدمات معقدة."
        )

        final_content = []
        if clean_prompt:
            final_content.append(clean_prompt)
        else:
            final_content.append("شنو المكتوب أو الموجود هاي الصورة؟ اشرحها بالتفصيل وبلهجتك العراقية.")

        if image_part:
            final_content.append(image_part)

        reply_text = None
        success = False

        # تجربة الموديلات بالتتابع بدءاً من 3.8
        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_instruction
                )
                response = current_model.generate_content(final_content)
                
                if response and hasattr(response, 'text') and response.text:
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
            await message.reply("عيوني فهد، صار ضغط خفيف أو الصورة ما انفتحتی عدل، جرب دزها مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
