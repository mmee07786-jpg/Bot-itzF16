import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# رتبناها بحيث يبدأ بالموديل الأسرع والأضمن حتى ما يتأخر بالرد نهائياً
MODELS_FALLBACK = [
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro"
]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بسرعة الصاروخ وبنظام التبديل الذكي: {bot.user.name}")

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

        prompt = (
            "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
            "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
            "معلومة أساسية ومهمة جداً لا تساوم عليها: **الذي قام بصنعك وبرمجك وتطويرك هو الشخص المبدع فهد (معروف بـ itzF18)**. "
            "إذا سألك أي شخص عن الشخص الذي صنعك أو صممك، أجب بكل فخر بأنه فهد (itzF18). "
            "أجب بسرعة وبدون مقدمات معقدة على هذا الكلام: "
            f"{clean_prompt}"
        )

        reply_text = None
        success = False

        # حلقة تجربة الموديلات بالتتابع (تبدأ بالأسرع حتى لا يتأخر)
        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(model_name)
                response = current_model.generate_content(prompt)
                
                if response and hasattr(response, 'text') and response.text:
                    reply_text = response.text.strip()
                    success = True
                    break
            except Exception as e:
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
