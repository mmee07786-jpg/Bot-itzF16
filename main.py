import os
import discord
from discord.ext import commands
import google.generativeai as genai

# قراءة المتغيرات من الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد مفتاح Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# نموذج للدردشة والنصوص
text_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# إعدادات ديسكورد
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ | البوت شغال باسم: {bot.user.name} وجاهز لتوليد الصور والردود!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        async with message.channel.typing():
            try:
                # تنظيف النص من المنشن
                clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
                
                if not clean_prompt:
                    await message.reply("هلا بيكم! شترید أسألك أو أرسملك اليوم؟")
                    return

                # التحقق إذا كان المستخدم يطلب تصميم أو رسم صورة
                if "صورة" in clean_prompt or "ارسم" in clean_prompt or "draw" in clean_prompt or "image" in clean_prompt:
                    # نستخدم نموذج توليد الصور المخصص بدقة عالية جداً وبدون علامة مائية
                    # ملاحظة: يتم إرسال وصف دقيق بالإنجليزية لضمان أعلى جودة خرافية
                    image_model = genai.GenerativeModel(model_name="imagen-3.0-generate-002") # نموذج التوليد المتقدم
                    
                    # نطلب من النموذج تحويل طلب المستخدم إلى وصف احترافي للصورة بدقة 4K
                    prompt_translation = text_model.generate_content(f"Translate and enhance this image prompt into a detailed, high-resolution 4K, photorealistic English prompt without watermarks: {clean_prompt}")
                    enhanced_prompt = prompt_translation.text.strip()

                    result = image_model.generate_images(
                        prompt=enhanced_prompt,
                        number_of_images=1,
                        aspect_ratio="1:1",
                        output_mime_type="image/jpeg"
                    )
                    
                    # إذا تم توليد الصورة بنجاح
                    for generated_image in result.generated_images:
                        image_bytes = generated_image.image.image_bytes
                        file = discord.File(fp=io.BytesIO(image_bytes), filename="high_resolution_image.jpg")
                        await message.reply("🎨 | تفضل صورتك بجودة عالية وبدون علامة مائية:", file=file)
                        return

                # إذا كان طلب عادي (سؤال أو دردشة باللهجة العراقية)
                system_instruction = "أنت مساعد ذكاء اصطناعي ودود في سيرفر ديسكورد، تتكلم وتجيب باللهجة العراقية البيضاء وبأسلوب لطيف ومفيد."
                full_prompt = f"{system_instruction}\nالسؤال: {clean_prompt}"

                response = text_model.generate_content(full_prompt)
                reply_text = response.text

                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)

            except Exception as e:
                print(f"خطأ: {e}")
                # رد احتياطي لو طلب صورة والنموذج تطلب إعدادات خاصة
                await message.reply("عذراً، صار عندي ضغط بالطلبات أو ما قدرت أعالج طلب الصورة حالياً. حاول تطلبها بصيغة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
