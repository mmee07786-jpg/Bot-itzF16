import os
import discord
from discord.ext import commands
from ai_handlers import get_ai_response, handle_image_request

# جلب توكن ديسكورد من الاستضافة
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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

            # التحقق إذا كان الطلب يخص الصور
            if any(word in clean_prompt forword in ["صورة", "ارسم", "تصميم", "image", "draw"]):
                image_reply = await handle_image_request(clean_prompt)
                await message.reply(image_reply)
                return

            # الرد العادي المتكيف والعفوي
            reply_text = await get_ai_response(clean_prompt)
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)

    await bot.process_commands(message)

if __name__ == "__main__":
    while True:
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            print(f"⚠️ | إعادة تشغيل البوت تلقائياً بسبب: {e}")
