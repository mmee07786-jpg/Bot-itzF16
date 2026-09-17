import os
import discord
from discord.ext import commands
import requests
import json

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # أو حط المفتاح مباشرة هنا إذا تحب

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 | بوت izf18 شغال بالطلب المباشر: {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if not clean_prompt:
            await message.reply("هلا بيك! عيوني وياك، شكو ماكو؟")
            return

        try:
            # توجيه ذكي باللهجة العراقية وبدون تكرار
            full_prompt = (
                "أنت ذكاء اصطناعي سريع وذكي جداً. أجب باللهجة العراقية وبدون تكرار كلام المستخدم نهائياً:\n"
                f"{clean_prompt}"
            )
            
            # الطلب المباشر لـ API جيميناي نفس طريقة الـ cURL
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": GEMINI_API_KEY
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            res_data = response.json()
            
            # استخراج النص من رد الجيسون
            try:
                reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                reply_text = f"صار خطأ بقراءة الرد: {str(res_data)[:100]}"

            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."

            await message.reply(reply_text if reply_text else "هلا بيك حبيبي!")
            
        except Exception as e:
            print(f"Error: {e}")
            await message.reply(f"عذراً فهد، صار خطأ: {str(e)[:60]}")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
