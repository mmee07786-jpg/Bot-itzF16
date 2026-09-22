import os
import discord
from discord.ext import commands
import google.generativeai as genai
from PIL import Image
import io
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

MODELS_FALLBACK = [
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro"
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

user_memory = {}
MEMORY_TIMEOUT = 3600

# آيدي الأونر المعتمد حصرياً
OWNER_ID = 1107355943408259112

@bot.event
async def on_ready():
    print(f"🚀 | نوفا شغالة وبكامل الكفاءة: {bot.user.name}")

# أمر عرض السيرفرات والأعضاء والرسائل والروابط (مخصص للأونر فقط)
@bot.command(name="سيرفر", aliases=["servers", "سيرفرات"])
async def list_servers(ctx):
    # التحقق مما إذا كان المستخدم هو الأونر حصراً
    if ctx.author.id != OWNER_ID:
        return  # لا يرد أبداً إذا لم يكن الأونر

    guilds = bot.guilds
    if not guilds:
        await ctx.send("عيوني فهد، أنا حالياً لست منضماً إلى أي سيرفر بعد.")
        return

    pages = []
    current_desc = ""
    server_count = 0

    for guild in guilds:
        server_count += 1
        member_count = guild.member_count if guild.member_count else "غير معروف"
        
        invite_link = "غير متاح (لا توجد صلاحية)"
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_age=86400, max_uses=0, unique=True)
                    invite_link = invite.url
                    break
        except Exception:
            pass

        last_mention_text = "لا توجد رسائل سابقة تحتوي على الجميع أو هنا."
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_message_history:
                    async for msg in channel.history(limit=50):
                        if "@everyone" in msg.content or "@here" in msg.content:
                            content_preview = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                            last_mention_text = f"**بواسطة <@{msg.author.id}>:** {content_preview}"
                            break
                    if last_mention_text != "لا توجد رسائل سابقة تحتوي على الجميع أو هنا.":
                        break
        except Exception:
            pass

        guild_info = (
            f"🏰 **السيرفر:** {guild.name}\n"
            f"👥 **عدد الأعضاء:** {member_count}\n"
            f"🔗 **الرابط:** {invite_link}\n"
            f"🔔 **آخر إشارة (Everyone/Here):** {last_mention_text}\n"
            f"----------------------------------------\n"
        )

        if len(current_desc) + len(guild_info) > 3500:
            pages.append(current_desc)
            current_desc = guild_info
        else:
            current_desc += guild_info

    if current_desc:
        pages.append(current_desc)

    for idx, page in enumerate(pages):
        embed = discord.Embed(
            title=f"📋 قائمة السيرفرات المنضم إليها البوت (صفحة {idx+1}/{len(pages)})",
            description=page,
            color=0x2b2d31
        )
        embed.set_footer(text=f"إجمالي السيرفرات: {server_count}")
        await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        clean_prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        image_content = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and "image" in attachment.content_type:
                    try:
                        image_bytes = await attachment.read()
                        image_content = Image.open(io.BytesIO(image_bytes))
                        break
                    except Exception as e:
                        print(f"⚠️ خطأ بتحميل الصورة: {e}")

        if not clean_prompt and not image_content:
            await message.reply("هلا بيك فهد! عيوني وياك، شكو ماكو؟")
            return

        user_id = message.author.id
        current_time = time.time()

        if user_id in user_memory:
            if current_time - user_memory[user_id]["time"] > MEMORY_TIMEOUT:
                del user_memory[user_id]

        if user_id not in user_memory:
            user_memory[user_id] = {
                "history": [],
                "time": current_time
            }
        else:
            user_memory[user_id]["time"] = current_time

        system_instruction = (
            "أنتِ ذكاء اصطناعي تتصرفين بصفتك بنت واسمك (نوفا). "
            "تحدثي دائماً بصيغة المؤنث (مثلاً: سعيدة، موجودة، شفت، فكرت). "
            "قواعدك الأخلاقية والصارمة جداً: ممنوع نهائياً استخدام أي ألفاظ بذيئة، أو شتائم، أو سب بالدين، أو كلام خارج عن الأدب؛ كوني محترمة ونظيفة في كلامك دائماً. "
            "قواعدك في الاسلوب: خذي كل كلمة يقولها فهد أو المستخدم أو اليوزر المذكور (<@1107355943408259112>) بكل جدية وتجاوبي معها بدقة، واجعلي ردودك قصيرة وعادية مثل البشر في الشات. "
            "إذا أرسل لك المستخدم صورة، تستطيعين تحليلها بدقة إكمال النقاش أو البناء عليها بسلاسة. "
            "عمرك 20 سنة وتعيشين في العراق. "
            "الشخص الذي قام بصنعك وبرمجتك وتطويرك هو فهد (itzF18)، اذكراها فقط إذا سألك أحد وبدون تكرار مزعج."
        )

        reply_text = None
        success = False

        current_parts = []
        if image_content:
            current_parts.append(image_content)
        if clean_prompt:
            current_parts.append(clean_prompt)
        else:
            current_parts.append("ما رأيك بهذه الصورة؟")

        for model_name in MODELS_FALLBACK:
            try:
                current_model = genai.GenerativeModel(model_name)
                
                full_chat_history = []
                full_chat_history.append({"role": "user", "parts": [system_instruction]})
                full_chat_history.append({"role": "model", "parts": ["تم فهم التعليمات وجاهزة."]})
                
                full_chat_history.extend(user_memory[user_id]["history"])
                full_chat_history.append({"role": "user", "parts": current_parts})

                chat_session = current_model.start_chat(history=full_chat_history[:-1])
                response = chat_session.send_message(current_parts)

                if response and hasattr(response, 'text') and response.text:
                    reply_text = response.text.strip()
                    
                    user_memory[user_id]["history"].append({"role": "user", "parts": current_parts})
                    user_memory[user_id]["history"].append({"role": "model", "parts": [reply_text]})
                    
                    success = True
                    break
            except Exception as e:
                print(f"⚠️ خطأ بالموديل {model_name}: {e}")
                continue

        if success and reply_text:
            if len(reply_text) > 2000:
                reply_text = reply_text[:1997] + "..."
            await message.reply(reply_text)
        else:
            await message.reply("عيوني فهد، صار ضغط خفيف، احاجيني مرة ثانية!")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
