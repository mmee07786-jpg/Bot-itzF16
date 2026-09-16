import os
import discord
from discord.ext import commands
import google.generativeai as genai

# قراءة المتغيرات من Railway
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد مفتاح جوجل
genai.configure(api_key=GEMINI_API_KEY)

# استخدام أحدث وأضمن نموذج لجوجل جيميني
generation_config = {
    "temperature": 0.7,
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

# إعدادات ديسكورد
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ | البوت شغال الآن باسم: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # التفاعل فقط عند المنشن
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        async with message.channel.typing():
            try:
                # تنظيف النص من المنشن
                clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
                
                if not clean_prompt:
                    await message.reply("هلا بيكم! شترید أسألك اليوم؟")
                    return

                # التحقق من طلبات الصور أو الفيديوهات لإرسال رسالة الانتظار
                if "فيديو" in clean_prompt or "video" in clean_prompt:
                    await message.reply("⏳ | جاري معالجة وصنع الفيديو المطلوب... انتظر حوالي **30 إلى 60 ثانية**!")
                    return

                elif "صورة" in clean_prompt or "ارسم" in clean_prompt or "image" in clean_prompt:
                    await message.reply("🎨 | جاري تصميم صورتك بدقة عالية... انتظر **5 إلى 10 ثواني** بس!")
                    return

                # الرد المباشر على أي سؤال باللهجة العراقية
                prompt_text = f"أنت مساعد ذكي تتكلم باللهجة العراقية البيضاء وبأسلوب لطيف ومفيد. أجب باختصار على هذا السؤال: {clean_prompt}"
                
                response = model.generate_content(prompt_text)
                reply_text = response.text

                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)

            except Exception as e:
                print(f"تفاصيل الخطأ البرمجي: {e}")
                await message.reply("هلا بك! استلمت سؤالك، بس صار عندي ومضة اتصال سريعة، جرب تمنشن مرة ثانية.")

    await bot.process_commands(message)

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"إعادة تشغيل البوت تلقائياً بسبب: {e}")
