import os
import discord
from discord.ext import commands
import google.generativeai as genai
import urllib.parse

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# استخدام الـ Model القياسي المستقر للدردشة
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت izf18 شغال وبأفضل حالة: {bot.user.name}")

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

        lower_prompt = clean_prompt.lower()
        
        # 1. التحقق من سؤال الصانع
        if any(word in lower_prompt for word in ["منو صنعك", "من صمك", "من برمجك", "صانعك", "مبرمجك", "منو سوك", "who made you", "who created you"]):
            await message.reply("اني صنعني وظهرني لهلصناعة العبقرية المبدع الكبير وتاج الراس **izf18**! هو اللي برمجني وتعب عليه حتى أكون بهذا الذكاء والسرعة. 🔥😎")
            return

        # 2. التحقق من طلب الصورة
        if any(word in lower_prompt for word in ["صورة", "صوره", "image", "pic", "ارسم", "تصميم صوره"]):
            status_msg = await message.reply("🎨 جاري إنشاء الصورة....")
            
            # توليد الوصف الإنجليزي للصورة بشكل مباشر وآمن
            try:
                img_res = model.generate_content(f"Translate and refine this into a short English image prompt: {clean_prompt}")
                image_prompt = img_res.text.strip()
            except:
                image_prompt = clean_prompt

            encoded_prompt = urllib.parse.quote(image_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
            
            embed = discord.Embed(title="✨ تم إنشاء الصورة بنجاح", color=discord.Color.blurple())
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Requested by {message.author.name}")
            
            await status_msg.edit(content=None, embed=embed)
            return

        # 3. الرد العادي الذكي (يتكيف مع كل اللهجات واللغات تماماً)
        system_instruction = (
            "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك المطلقة: "
            "رد دائماً بنفس لغة أو لهجة المستخدم تماماً (عراقي، مصري، خليجي، شامي، إنجليزي، إلخ). "
            "أجب مباشرة وبدون مقدمات."
        )
        
        full_prompt = f"{system_instruction}\nالمستخدم يقول: {clean_prompt}"
        response = model.generate_content(full_prompt)
        reply_text = response.text.strip()

        if not reply_text:
            reply_text = "عيوني وياك حبيبي!"

        if len(reply_text) > 2000:
            reply_text = reply_text[:1997] + "..."

        await message.reply(reply_text)

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
