import os
import discord
from discord.ext import commands
import google.generativeai as genai
import io

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash") # أو gemini-3.6-flash حسب الموديل المعتمد عندك

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | البوت شغال بسرعة البرق ومتكيف اللغات: {bot.user.name}")

# --- أمر توليد الصور المختصر !ima ---
@bot.command(name="ima")
async def generate_image(ctx, *, prompt: str = None):
    if not prompt:
        await ctx.reply("حبيبي، اكتب وصف الصورة ورا الأمر! مثلاً: `!ima a cyberpunk car`")
        return

    async with ctx.channel.typing():
        try:
            image_model = genai.GenerativeModel('imagen-3.0-generate-002')
            result = image_model.generate_content(prompt)
            
            for part in result.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_bytes = part.inline_data.data
                    file = discord.File(io.BytesIO(image_bytes), filename="generated_image.png")
                    await ctx.reply(content=f"🎨 | أبشر، هاي صورة لـ: **{prompt}**", file=file)
                    return
            
            await ctx.reply("عذراً عيوني، ما قدرت أولد الصورة، جرب وصف ثاني!")
        except Exception as e:
            print(f"Image Error: {e}")
            await ctx.reply(f"عذراً حبيبي، صار عندي خطأ بتوليد الصورة: `{str(e)[:60]}`")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # إذا الرسالة تبدأ بـ ! تعامل وياها كأمر (مثل !ima)
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # التفاعل عند المنشن فقط للنصوص
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟ / Hey there!")
            return

        try:
            prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً. قاعدتك الأساسية: **يجب أن ترد بنفس لغة أو لهجة الشخص الذي يكلمك تماماً** "
                "(إذا تحدث بالإنجليزية رد بالإنجليزية بطلاقة، إذا تحدث باللهجة العراقية رد بعراقي، وإذا باللهجات العربية الأخرى رد بها). "
                "أجب بسرعة وبدون مقدمات معقدة على هذا الكلام: "
                f"{clean_prompt}"
            )
            
            response = model.generate_content(prompt)
            reply_text = response.text.strip()
            
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
            
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("هلا بيك، وياك!")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
