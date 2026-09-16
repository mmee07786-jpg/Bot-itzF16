import os
import discord
from discord.ext import commands
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد العميل بالمكتبة الحديثة
client = genai.Client(api_key=GEMINI_API_KEY)

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
        
        # تفعيل حالة "يكتب الآن..."
        async with message.channel.typing():
            
            # 1. الرد عند السؤال عن الصانع
            if any(word in lower_prompt for word in ["منو صنعك", "من صمك", "من برمجك", "صانعك", "مبرمجك", "منو سوك", "who made you", "who created you"]):
                await message.reply("اني صنعني وظهرني لهلصناعة العبقرية المبدع الكبير وتاج الراس **izf18**! هو اللي برمجني وتعب عليه حتى أكون بهذا الذكاء والسرعة. 🔥😎")
                return

            # 2. الرد الذكي والنصي فقط باستخدام المكتبة الحديثة
            try:
                system_instruction = "أنت مساعد ذكي ولطيف. رد باللهجة العراقية الطبيعية وبشكل مباشر وبدون مقدمات معقدة."
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"{system_instruction}\n\nالمستخدم: {clean_prompt}"
                )
                
                reply_text = response.text.strip() if response.text else "عيوني وياك، بس ما عرفت شجاوبك!"
                    
            except Exception as e:
                print(f"❌ GEMINI API ERROR: {e}")
                reply_text = f"عذراً حبيبي، صار عندي هذا الخطأ التقني: `{str(e)[:80]}`"

            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
