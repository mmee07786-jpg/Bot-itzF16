import os
import discord
from discord.ext import commands
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت izf18 شغال وبأفضل حالة: {bot.user.name}")

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

        lower_prompt = clean_prompt.lower()
        
        # تفعيل حالة "يكتب الآن..."
        async with message.channel.typing():
            
            # 1. الرد عند السؤال عن الصانع
            if any(word in lower_prompt for word in ["منو صنعك", "من صمك", "من برمجك", "صانعك", "مبرمجك", "منو سوك", "who made you", "who created you"]):
                await message.reply("اني صنعني وظهرني لهلصناعة العبقرية المبدع الكبير وتاج الراس **izf18**! هو اللي برمجني وتعب عليه حتى أكون بهذا الذكاء والسرعة. 🔥😎")
                return

            # 2. الرد الذكي المباشر باستخدام موديل gemini-2.0-flash والـ API المباشر
            try:
                # استخدام أحدث موديل ورابط رسمي معتمد
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
                
                headers = {'Content-Type': 'application/json'}
                
                system_instruction = "أنت مساعد ذكي ولطيف. رد باللهجة العراقية الطبيعية وبشكل مباشر وبدون مقدمات معقدة."
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": f"{system_instruction}\n\nالمستخدم: {clean_prompt}"}
                            ]
                        }
                    ]
                }
                
                res = requests.post(url, headers=headers, json=payload, timeout=10)
                res_data = res.json()
                
                if res.status_code == 200:
                    reply_text = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                else:
                    error_msg = res_data.get('error', {}).get('message', 'Unknown Error')
                    print(f"❌ API Error: {error_msg}")
                    reply_text = f"عذراً حبيبي، صار عندي خطأ بالطلب: `{error_msg[:60]}`"
                    
            except Exception as e:
                print(f"❌ Request Exception: {e}")
                reply_text = "عيوني وياك، صار عندي لود ثواني ورجعتلك!"

            if not reply_text:
                reply_text = "عيوني وياك حبيبي!"

            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text)

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
