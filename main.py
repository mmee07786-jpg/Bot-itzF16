import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# استخدام إعدادات ذكية تخلي الردود سريعة ومتكيفّة
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="أنت مساعد ذكاء اصطناعي ذكي، ودود، وتتكلم باللهجة العراقية الطبيعية والعفوية تماماً (مثل كلام الشباب بأسلوب ذكي ومرتب). ردودك تكون سريعة، مباشرة، وبدون تكلف أو مقدمات رسمية مملة."
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"البوت اشتغل وصار أونلاين: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيونى وياك، شكو ماكو؟")
            return

        try:
            # إرسال الرسالة مع الحفاظ على سرعة الاستجابة القصوى
            response = model.generate_content(clean_prompt)
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text if reply_text else "هلا بيك حبيبي، وياك!")
            
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("هلا بيك، وياك! تفضل حجي.")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
