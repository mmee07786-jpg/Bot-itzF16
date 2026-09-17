import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# إعدادات منع التكرار والجلتش (تخلي الموديل مركز وأكثر استقراراً)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # ثبتناه على الموديل السريع والشغال يمك
    generation_config=generation_config
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بسرعة البرق ومتكيف اللغات: {bot.user.name}")

@bot.event
async def on_message(message):
    # حماية مهمة: منع البوت من الرد على نفسه أو على أي بوت ثاني لتجنب أي Loop أو گلت
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟ / Hey there!")
            return

        try:
            # توجيه ذكي للسرعة والتكيف التام مع أي لغة أو لهجة وبدون تكرار كلام المستخدم
            prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                "أجب بسرعة وبدون مقدمات معقدة وبدون تكرار كلام المستخدم نهائياً على هذا الكلام: "
                f"{clean_prompt}"
            )
            
            # توليد الرد فوراً بدون تأخير
            response = model.generate_content(prompt)
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
            
        except Exception as e:
            print(f"Error: {e}")
            # تم تعديل رد الخطأ ليكون هادئاً ولا يسبب أي إزعاج أو تكرار بالدردشة
            await message.reply("ثواني وراجعلك، صار ضغط بالخدمة!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
