import os
import discord
from discord.ext import commands
import google.generativeai as genai
from PIL import Image
import io
import time
from datetime import datetime

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

# قائمة اختيار السيرفرات (Dropdown)
class ServerSelect(discord.ui.Select):
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance
        options = []
        for guild in bot_instance.guilds[:25]: # ديسكورد يسمح بحد أقصى 25 خيار بالقائمة
            options.append(discord.SelectOption(
                label=guild.name[:100],
                value=str(guild.id),
                description=f"الأعضاء: {guild.member_count}"
            ))
        super().__init__(placeholder="اختر السيرفر لعرض معلوماته الشاملة وتجسسه...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("عذراً، هذه القائمة مخصصة للأونر فقط!", ephemeral=True)
            return

        guild_id = int(self.values[0])
        guild = self.bot_instance.get_guild(guild_id)

        if not guild:
            await interaction.response.send_message("❌ لم يتم العثور على السيرفر المطلوب.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # 1. حساب عمر السيرفر
        created_at = guild.created_at
        now = datetime.now(created_at.tzinfo)
        age_days = (now - created_at).days
        years = age_days // 365
        months = (age_days % 365) // 30
        days = (age_days % 365) % 30
        age_str = f"{years} سنة، {months} شهر، {days} يوم" if years > 0 else f"{months} شهر، {days} يوم"

        # 2. الرتب
        roles_list = [role.name for role in reversed(guild.roles) if role.name != "@everyone"]
        roles_str = ", ".join(roles_list[:40]) if roles_list else "لا توجد رتب"
        if len(roles_list) > 40:
            roles_str += f" ... (والمزيد من إجمالي {len(roles_list)} رتبة)"

        # 3. التاج / رابط التفاخر (Vanity URL)
        vanity_url = guild.vanity_url_code if hasattr(guild, 'vanity_url_code') and guild.vanity_url_code else "لا يوجد"
        features = ", ".join(guild.features) if guild.features else "لا توجد ميزات خاصة"

        # 4. عدد البوستات والثرิดز النشطة
        total_posts = 0
        try:
            for channel in guild.text_channels:
                threads = channel.threads
                total_posts += len(threads)
        except Exception:
            pass

        # 5. معلومات التجسس (البوتات، الأعضاء الإداريين، الأمان)
        bots_count = sum(1 for m in guild.members if m.bot)
        humans_count = guild.member_count - bots_count
        admin_suspects = sum(1 for m in guild.members if m.guild_permissions.administrator and not m.bot)

        # 6. آخر شخص تفاعل / نشر بوست أو رسالة
        last_poster = "غير معروف"
        last_post_content = "لا توجد رسائل حديثة"
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_message_history:
                    async for msg in channel.history(limit=10):
                        if not msg.author.bot:
                            last_poster = f"{msg.author.name} (<@{msg.author.id}>)"
                            last_post_content = msg.content[:100] if msg.content else "محتوى غير نصي (صورة/ملف)"
                            break
                    if last_poster != "غير معروف":
                        break
        except Exception:
            pass

        # 7. آخر Everyone أو Here
        last_mention_text = "لا توجد إشارات سابقة للجميع."
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_message_history:
                    async for msg in channel.history(limit=50):
                        if "@everyone" in msg.content or "@here" in msg.content:
                            content_preview = msg.content[:150]
                            last_mention_text = f"بواسطة <@{msg.author.id}>\nالرسالة: {content_preview}"
                            break
                    if last_mention_text != "لا توجد إشارات سابقة للجميع.":
                        break
        except Exception:
            pass

        # رابط الدعوة
        invite_link = "غير متاح"
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_age=86400, max_uses=0, unique=True)
                    invite_link = invite.url
                    break
        except Exception:
            pass

        # بناء النص الشامل
        info_text = (
            f"🏰 **اسم السيرفر:** {guild.name}\n"
            f"🆔 **آيدي السيرفر:** `{guild.id}`\n"
            f"👑 **صاحب السيرفر:** <@{guild.owner_id}>\n"
            f"👥 **الأعضاء:** {guild.member_count} (بشر: {humans_count} | بوتات: {bots_count})\n"
            f"⏳ **عمر السيرفر:** {age_str}\n"
            f"🔗 **رابط الدعوة:** {invite_link}\n"
            f"🌐 **رابط التفاخر (Vanity):** {vanity_url}\n"
            f"🏷️ **ميزات السيرفر (Features):** `{features}`\n"
            f"💬 **عدد الثرิดز/المنشورات النشطة:** {total_posts}\n"
            f"🛡️ **معلومات التجسس والأمان:**\n"
            f" - عدد الإداريين بصلاحيات كاملة: {admin_suspects}\n"
            f" - مستوى الحماية (Verification): {guild.verification_level}\n"
            f"👤 **آخر شخص نشر رسالة:** {last_poster}\n"
            f"   └ المحتوى: `{last_post_content}`\n"
            f"🔔 **آخر إشارة Everyone/Here:**\n{last_mention_text}\n"
            f"📋 **الرتب الموجودة ({len(roles_list)}):**\n`{roles_str}`"
        )

        # إرسال المعلومات مع زر مغادرة السيرفر المختار
        view = ServerManageView(guild)
        await interaction.followup.send(content=info_text, view=view, ephemeral=True)

class ServerView(discord.ui.View):
    def __init__(self, bot_instance):
        super().__init__(timeout=180)
        self.add_item(ServerSelect(bot_instance))

class ServerManageView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        # زر المغادرة لهذا السيرفر بالذات
        self.add_item(LeaveSpecificButton(guild.id, guild.name))

class LeaveSpecificButton(discord.ui.Button):
    def __init__(self, guild_id, guild_name):
        super().__init__(style=discord.ButtonStyle.danger, label=f"مغادرة سيرفر: {guild_name[:15]}")
        self.target_guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("عذراً، هذا الزر مخصص للأونر فقط!", ephemeral=True)
            return

        guild = interaction.client.get_guild(self.target_guild_id)
        if guild:
            name = guild.name
            try:
                await guild.leave()
                await interaction.response.send_message(f"✅ تم مغادرة السيرفر (**{name}**) بنجاح.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ حدث خطأ أثناء المغادرة: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ السيرفر غير موجود أو تم مغادرته مسبقاً.", ephemeral=True)


# أمر عرض قائمة السيرفرات (مخصص للأونر فقط)
@bot.command(name="سيرفر", aliases=["servers", "سيرفرات"])
async def list_servers(ctx):
    if ctx.author.id != OWNER_ID:
        return  

    if not bot.guilds:
        await ctx.send("عيوني فهد، أنا لست منضماً إلى أي سيرفر حالياً.")
        return

    view = ServerView(bot)
    embed = discord.Embed(
        title="🕵️‍♂️ لوحة تحكم ومراقبة سيرفرات نوفا",
        description="اختر السيرفر الذي تريد فحصه ومعرفة كل تفاصيله والرتب والبوستات ومعلومات التجسس الخاصة به من القائمة أدناه:",
        color=0x2b2d31
    )
    await ctx.send(embed=embed, view=view, delete_after=180)


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

