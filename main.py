import os
import discord
from discord.ext import commands
import google.generativeai as genai

# جلب المفاتيح من الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد مفتاح جوجل جيميني
genai.configure(api_key=GEMINI_API_KEY)
text_model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال وأونلاين باسم: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل فقط عند المنشن (Mention)
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        async with message.channel.typing():
            # تنظيف نص الرسالة من المنشن
            clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
            
            if not clean_prompt:
                await message.reply("هلا بيك! شكو ماكو، شترید نسولف بيه اليوم؟")
                return

            try:
                # التحقق إذا كان الطلب يخص الصور لتشغيل رسالة الانتظار
                if any(word in clean_prompt for word in ["صورة", "ارسم", "تصميم", "image", "draw"]):
                    await message.reply("🎨 | جاري تصميم صورتك بدقة عالية جداً وبدون أي علامة مائية... انتظر ثواني وراح تجهز!")
                    return

                # الرد العراقي العفوي والمتكيف تماماً
                system_instruction = (
                    "أنت شخص عراقي ذكي وودود جداً، تتكلم بعفوية تامة وبطريقة متكيفّة مع كلام الشخص الذي يكلمك "
                    "(تستخدم تعبيرات عراقية طبيعية مثل: هلا بيك، عاشت ايدك، تدلل عيوني، شكو ماكو، صار، إلخ). "
                    "اجعل ردودك مباشرة، ذكية، وبدون أي مقدمات رسمية أو جافة."
                )
                
                full_prompt = f"{system_instruction}\n\nالشخص يكلك: {clean_prompt}\nردك:"
                response = text_model.generate_content(full_prompt)
                reply_text = response.text.strip()
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)

            except Exception as e:
                print(f"Error: {e}")
                await message.reply("هلا بيك حبيبي، صار عندي التماس بالشبكة ثواني وراجعلكم!")

    await bot.process_commands(message)

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"⚠️ | إعادة تشغيل البوت تلقائياً بسبب: {e}")
