import os
import discord
from discord.ext import commands
import google.generativeai as genai

# قراءة المتغيرات من إعدادات الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد مفتاح Google Gemini
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.7,
}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

# إعدادات البوت ودیسکورد
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ | تم تسجيل الدخول بنجاح باسم: {bot.user.name}")
    print("🤖 | بوت الذكاء الاصطناعي جاهز للعمل!")

@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات حتى لا يحدث تكرار
    if message.author.bot:
        return

    # الرد فقط عند منشن البوت
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        async with message.channel.typing():
            try:
                # تنظيف النص من المنشن
                clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
                
                if not clean_prompt:
                    await message.reply("هلا بيكم! شترید أسألك اليوم؟")
                    return

                # توجيه البوت للتحدث باللهجة العراقية
                system_instruction = "أنت مساعد ذكاء اصطناعي ودود في سيرفر ديسكورد، تتكلم وتجيب باللهجة العراقية البيضاء وبأسلوب لطيف ومفيد."
                full_prompt = f"{system_instruction}\nالسؤال: {clean_prompt}"

                # توليد الرد من النموذج
                response = model.generate_content(full_prompt)
                reply_text = response.text

                # التأكد من عدم تجاوز حد الحروف في ديسكورد
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)

            except Exception as e:
                print(f"خطأ في الرد: {e}")
                await message.reply("عذراً، صار عندي خلل بسيط وما قدرت أعالج رسالتك حالياً. حاول مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

