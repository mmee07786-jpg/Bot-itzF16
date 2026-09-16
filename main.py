import os
import discord
from discord.ext import commands
import google.generativeai as genai
import urllib.parse

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت توليد الصور والنصوص شغال: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        try:
            lower_prompt = clean_prompt.lower()
            
            # 1. فحص إذا السؤال عن الصانع أو المبرمج
            is_creator_question = any(word in lower_prompt for word in ["منو صنعك", "من صمك", "من برمجك", "صانعك", "مبرمجك", "منو سوك", "who made you", "who created you"])

            # 2. فحص إذا طلب صورة
            is_image_request = any(word in lower_prompt for word in ["صورة", "صوره", "image", "pic", "ارسم", "تصميم صوره"])

            if is_creator_question:
                reply_text = "اني صنعني وظهرني لهلصناعة العبقرية المبدع الكبير وتاج الراس **izf18**! هو اللي برمجني وتعب عليه حتى أكون بهذا الذكاء والسرعة. 🔥😎"
                await message.reply(reply_text)
                
            elif is_image_request:
                status_msg = await message.reply("🎨 جاري إنشاء الصورة....")
                
                # ترجمة الوصف وتحسينه لإنجليزي للحصول على أفضل نتيجة صورة
                img_prompt_gen = model.generate_content(f"Translate and refine this image prompt into a detailed, high-quality English image generation prompt, return ONLY the prompt text: {clean_prompt}")
                image_prompt = img_prompt_gen.text.strip()
                
                # توليد رابط الصورة المباشر بدون علامة مائية
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                
                embed = discord.Embed(title="✨ تم إنشاء الصورة بنجاح", color=discord.Color.blurple())
                embed.set_image(url=image_url)
                embed.set_footer(text=f"Requested by {message.author.name}")
                
                await status_msg.edit(content=None, embed=embed)
                
            else:
                # 3. الرد العادي الذكي المتكيف مع اللهجات واللغات
                prompt = (
                    "أنت ذكاء اصطناعي سريع وذكي جداً. رد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً "
                    "(إذا إنجليزي رد إنجليزي، عراقي رد عراقي، وهكذا). "
                    f"أجب على هذا الكلام باختصار وبدون مقدمات معقدة: {clean_prompt}"
                )
                
                response = model.generate_content(prompt)
                reply_text = response.text.strip()

                if not reply_text:
                    reply_text = "عيوني وياك!"

                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)
                
        except Exception as e:
            print(f"Error Details: {e}")
            await message.reply("ها حبيبي، صار لود بسيط وراجعلك!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
