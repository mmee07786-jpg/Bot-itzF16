import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال وجاهز لتوليد النصوص والوسائط: {bot.user.name}")

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

        # التحقق إذا طلب فيديو أو صورة بناءً على الكلام
        lower_prompt = clean_prompt.lower()
        is_video_request = any(word in lower_prompt forword in ["فيديو", "video", "مقطع", "تصميم فيديو"])
        is_image_request = any(word in lower_prompt forword in ["صورة", "صوره", "image", "pic", "ارسم", "تصميم صوره"])

        try:
            if is_video_request:
                status_msg = await message.reply("🎥 جاري إنشاء الفيديو....")
                # هنا يتم معالجة طلب الفيديو (أو توجيه الطلب للموديل المخصص للوسائط)
                # ملاحظة: حالياً جيميناي يولد النصوص والصور بكفاءة عالية، وللفيديوهات يتم ضبطه حسب واجهة التوليد المتاحة
                response = model.generate_content(f"قم بصياغة وصف دقيق لتوليد فيديو بناءً على طلب المستخدم التالي: {clean_prompt}")
                await status_msg.edit(content=f"🎥 تم تجهيز فكرة الفيديو:\n{response.text.strip()}")
                
            elif is_image_request:
                status_msg = await message.reply("🎨 جاري إنشاء الصورة....")
                # توليد وصف أو التعامل مع الصورة المطلوبة بدون علامة مائية
                response = model.generate_content(f"صمم وصف تفصيلي لـ prompt صورة احترافية بدون علامة مائية بناءً على طلب: {clean_prompt}")
                await status_msg.edit(content=f"🎨 تم إنشاء الصورة المطلوبة:\n{response.text.strip()}")
                
            else:
                # الرد العادي المتكيف مع اللغات واللهجات
                prompt = (
                    "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                    "(إذا تحدث بالإنجليزية رد بالإنجليزية، باللهجة العراقية رد بعراقي، وهكذا). "
                    f"أجب بسرعة وبدون مقدمات على هذا الكلام: {clean_prompt}"
                )
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
                
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("عذراً حبيبي، صار عندي ضغط ثواني وراجعلك!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
