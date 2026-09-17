import os
import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# تم ضبط الموديل بالذات على gemini-3.6-flash مثل ما طلبت
model = genai.GenerativeModel("gemini-3.6-flash")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# قفل تنظيمي حتى يتحمل هواي ناس ويردون بالدور بدون ضغط
lock = asyncio.Lock()

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بسرعة البرق على Gemini 3.6 Flash: {bot.user.name}")

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

        async with lock:
            try:
                # توجيه ذكي مع تثبيت اسم الصانع فهد itzF18
                prompt = (
                    "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                    "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                    "معلومة أساسية ومهمة جداً لا تساوم عليها: **الذي قام بصنعك وبرمجتك وتطويرك هو الشخص المبدع فهد (معروف بـ itzF18)**. "
                    "إذا سألك أي شخص عن الشخص الذي صنعك أو صممك، أجب بكل فخر بأنه فهد (itzF18). "
                    "أجب بسرعة وبدون مقدمات معقدة على هذا الكلام: "
                    f"{clean_prompt}"
                )
                
                # تنفيذ الطلب وانتظار الرد الحقيقي بدون تسرع
                response = await asyncio.to_thread(model.generate_content, prompt)
                
                if response and response.text:
                    reply_text = response.text.strip()
                else:
                    reply_text = "عيوني وياك، اكتب سؤالك أو كلامك الكامل حتى أجاوبك بتركيز!"
                
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1997] + "..."

                await message.reply(reply_text)
                
            except Exception as e:
                print(f"Error Details: {e}")
                # تم تغيير رسالة الخطأ حتى نعرف لو صار شي بدل الجملة القديمة
                await message.reply("صار ضغط أو تأخير بالشبكة، جرب احاجيني بجملة واضحة مرة ثانية!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
