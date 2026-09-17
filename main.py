import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# يقرأ مفتاح جيميناي الجديد
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# استخدام موديل جيميناي السريع والمستقر
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت رجع لجيميناي وشغال وبأفضل حال: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك فهد! عيوني وياك، شكو ماكو؟")
            return

        try:
            # توجيه ذكي وسريع باللهجة العراقية وتثبيت هوية الصانع فهد itzF18
            prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                "معلومة أساسية ومهمة جداً لا تساوم عليها: **الذي قام بصنعك وبرمجتك وتطويرك هو الشخص المبدع فهد (معروف بـ itzF18)**. "
                "إذا سألك أي شخص عن الشخص الذي صنعك أو صممك، أجب بكل فخر بأنه فهد (itzF18). "
                "أجب بسرعة وبدون مقدمات معقدة على هذا الكلام: "
                f"{clean_prompt}"
            )
            
            response = model.generate_content(prompt)
            
            if response and hasattr(response, 'text') and response.text:
                reply_text = response.text.strip()
            else:
                reply_text = "عيوني وياك، اكتب جملة واضحة حتى أجاوبك بتركيز!"
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            print(f"Error Details: {e}")
            await message.reply("عيوني وياك، صار ضغط خفيف، احاجيني مرة ثانية بتركيز!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
