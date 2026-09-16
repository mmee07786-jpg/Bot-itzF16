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
    print(f"🚀 | البوت شغال وفلول: {bot.user.name}")

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

        try:
            # التحقق إذا كان السؤال عن المبرمج أو الصانع
            lower_prompt = clean_prompt.lower()
            is_creator_question = any(word in lower_prompt for word in ["منو صنعك", "من صمك", "من برمجك", "صانعك", "مبرمجك", "منو سوك", "who made you", "who created you", "who is your developer"])

            if is_creator_question:
                reply_text = "اني صنعني وظهرني لهلصناعة العبقرية المبدع الكبير وتاج الراس **izf18**! هو اللي برمجني وتعب عليه حتى أكون بهذا الذكاء والسرعة. تگدر تتواصل ويا وتشوف إبداعاته بـديسكورد: `izf18` 🔥😎"
                await message.reply(reply_text)
            else:
                # الرد العادي المتكيف مع اللهجات واللغات
                prompt = (
                    "أنت ذكاء اصطناعي سريع، ذكي، وودود جداً. قاعدتك الأساسية: "
                    "1. رد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً (إنجليزي، عراقي، مصري، خليجي، إلخ). "
                    "2. إذا سألك المستخدم عن قدرتك على إنشاء صور أو فيديوهات، وّضح له بأسلوب لطيف أنك متخصص بالنقاشات والبرمجة وتعطي أفكار (Prompts) جاهزة، وما تولد الملف مباشرة بالدردشة. "
                    f"أجب على هذا الكلام بسرعة وبدون تعقيد: {clean_prompt}"
                )
                
                response = model.generate_content(prompt)
                reply_text = response.text.strip()
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
                
        except Exception as e:
            print(f"Error Details: {e}")
            await message.reply("عيوني وياك، تفضل سولفلي شمحتاج؟")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
