import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# إعدادات الاستقرار ومنع التكرار
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
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
    # حماية لمنع البوت من الرد على نفسه ودخوله بحلقة تكرار
    if message.author.bot:
        return

    # التفاعل عند المنشن فقط
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟ / Hey there!")
            return

        try:
            prompt = (
                "أنت ذكاء اصطناعي سريع. قاعدتك الأساسية: رد باللهجة العراقية فقط وبدون تكرار كلام المستخدم نهائياً:\n"
                f"{clean_prompt}"
            )
            
            # إرسال الطلب وانتظار الرد الحقيقي للاستجابة
            response = model.generate_content(prompt)
            
            if response and response.text:
                reply_text = response.text.strip()
            else:
                reply_text = "عيوني وياك، بس الرد اجى فارغ، جرب مرة ثانية!"
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)
            
        except Exception as e:
            # طباعة الخطأ الحقيقي بالكونسول للمتابعة وإرسال رد هادئ غير مزعج
            print(f"Full Error Details: {e}")
            await message.reply("صار ضغط أو تأخير بالاستجابة، بس البوت وياك ما عافك! جرب مرة ثانية.")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
