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
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_memory = {}
MEMORY_TIMEOUT = 3600

# آيدي الأونر المعتمد حصرياً
OWNER_ID = 1107355943408259112

@bot.event
async def on_ready():
    print(f"🚀 | نوفا شغالة وبكامل الكفاءة: {bot.user.name}")

# اختيار السيرفر الأساسي
class ServerSelect(discord.ui.Select):
    def __init__(self, bot_instance):
        self.bot_instance = bot_instance
        options = []
        for guild in bot_instance.guilds[:25]:
            options.append(discord.SelectOption(
                label=guild.name[:100],
                value=str(guild.id),
                description=f"الأعضاء: {guild.member_count}"
            ))
        super().__init__(placeholder="اختر السيرفر لعرض تقرير التجسس الشامل...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("عذراً يا عيني، ما عندي هيك صلاحية أنطيك هاي المعلومات.. هذي تخص فهد وبس!", ephemeral=True)
            return

        guild_id = int(self.values[0])
        guild = self.bot_instance.get_guild(guild_id)

        if not guild:
            await interaction.response.send_message("❌ عذراً فهد، لم يتم العثور على السيرفر المطلوب.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # حساب عمر السيرفر
        created_at = guild.created_at
        now = datetime.now(created_at.tzinfo)
        age_days = (now - created_at).days
        years = age_days // 365
        months = (age_days % 365) // 30
        days = (age_days % 365) % 30
        age_str = f"{years} سنة، {months} شهر، {days} يوم" if years > 0 else f"{months} شهر، {days} يوم"

        # ترتيب الرتب بشكل متساوي ومنتظم
        roles_list = [role.name for role in reversed(guild.roles) if role.name != "@everyone"]
        formatted_roles = []
        for i in range(0, len(roles_list), 5):
            chunk = " | ".join(roles_list[i:i+5])
            formatted_roles.append(chunk)
        roles_str = "\n".join(formatted_roles[:10]) if formatted_roles else "لا توجد رتب"

        vanity_url = guild.vanity_url_code if hasattr(guild, 'vanity_url_code') and guild.vanity_url_code else "لا يوجد"
        features = ", ".join(guild.features) if guild.features else "لا توجد ميزات خاصة"

        # عدد البوستات والثرิดز
        total_posts = 0
        try:
            for channel in guild.text_channels:
                total_posts += len(channel.threads)
        except Exception:
            pass

        # فحص السجل (Audit Log) لأحدث العقوبات والتعديلات
        last_ban = "لا توجد حالات باند حديثة"
        last_role_added = "لا توجد بيانات رتب جديدة"
        last_audit_action = "لا توجد تعديلات حديثة"
        try:
            async for entry in guild.audit_logs(limit=5):
                if entry.action == discord.AuditLogAction.ban:
                    last_ban = f"تم باند لـ {entry.target} بواسطة {entry.user}"
                elif entry.action == discord.AuditLogAction.role_create:
                    last_role_added = f"رتبة جديدة: {entry.target} بواسطة {entry.user}"
                elif entry.action in [discord.AuditLogAction.channel_create, discord.AuditLogAction.guild_update]:
                    last_audit_action = f"تعديل بواسطة {entry.user} ({entry.action.name})"
        except Exception:
            pass

        # الأعضاء
        bots_count = sum(1 for m in guild.members if m.bot)
        humans_count = guild.member_count - bots_count
        admin_suspects = sum(1 for m in guild.members if m.guild_permissions.administrator and not m.bot)

        # آخر شخص نشر رسالة وأخر everyone
        last_poster = "غير معروف"
        last_post_content = "لا توجد رسائل حديثة"
        last_mention_text = "لا توجد إشارات سابقة للجميع."
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).read_message_history:
                    async for msg in channel.history(limit=15):
                        if not msg.author.bot and last_poster == "غير معروف":
                            last_poster = f"{msg.author.name} (<@{msg.author.id}>)"
                            last_post_content = msg.content[:100] if msg.content else "محتوى غير نصي"
                        if "@everyone" in msg.content or "@here" in msg.content:
                            content_preview = msg.content[:150]
                            last_mention_text = f"بواسطة <@{msg.author.id}>\nالرسالة: {content_preview}"
                            break
        except Exception:
            pass

        invite_link = "غير متاح"
        try:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_age=86400, max_uses=0, unique=True)
                    invite_link = invite.url
                    break
        except Exception:
            pass

        info_text = (
            f"🏰 **السيرفر:** {guild.name} (`{guild.id}`)\n"
            f"👑 **صاحب السيرفر:** <@{guild.owner_id}>\n"
            f"👥 **الأعضاء:** {guild.member_count} (بشر: {humans_count} | بوتات: {bots_count})\n"
            f"⏳ **عمر السيرفر:** {age_str}\n"
            f"🔗 **الرابط:** {invite_link} | 🌐 **Vanity:** {vanity_url}\n"
            f"💬 **البوستات/الثرิดز:** {total_posts} | 🛡️ **الإداريين الكليين:** {admin_suspects}\n"
            f"🚨 **سجل التجسس والعقوبات:**\n"
            f" - آخر باند: `{last_ban}`\n"
            f" - آخر رتبة مضافة: `{last_role_added}`\n"
            f" - آخر إجراء: `{last_audit_action}`\n"
            f"👤 **آخر متفاعل:** {last_poster} -> `{last_post_content}`\n"
            f"🔔 **آخر إشارة Everyone:**\n{last_mention_text}\n"
            f"📋 **الرتب المتساوية والموزعة:**\n{roles_str}"
        )

        # عرض الأزرار: زر مغادرة السيرفر + زر عرض قنوات السيرفر لجلب آخر 20 رسالة
        view = ServerExtraActionsView(guild)
        await interaction.followup.send(content=info_text, view=view, ephemeral=True)

# أزرار إضافية للسيرفر المختار
class ServerExtraActionsView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.add_item(ChannelsListButton(guild))
        self.add_item(LeaveSpecificButton(guild.id, guild.name))

class ChannelsListButton(discord.ui.Button):
    def __init__(self, guild):
        super().__init__(style=discord.ButtonStyle.primary, label="📂 عرض القنوات لجلب آخر 20 رسالة")
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("عذراً، هذا الأمر خاص بفهد فقط!", ephemeral=True)
            return

        # إرسال قائمة منسدلة باختيار القنوات
        view = ChannelsSelectView(self.guild)
        await interaction.response.send_message("اختر القناة أو القسم الذي تريد استخراج آخر 20 رسالة منه:", view=view, ephemeral=True)

class ChannelsSelectView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=120)
        options = []
        for channel in guild.text_channels[:25]:
            options.append(discord.SelectOption(
                label=channel.name[:100],
                value=str(channel.id),
                description=f"قسم: {channel.category.name if channel.category else 'عام'}"
            ))
        self.add_item(ChannelSelectDropdown(options))

class ChannelSelectDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="اختر القناة المطلوبة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("عذراً، هذا مخصص لفهد فقط!", ephemeral=True)
            return

        channel_id = int(self.values[0])
        channel = interaction.guild.get_channel(channel_id)

        if not channel:
            await interaction.response.send_message("❌ لم يتم العثور على القناة.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        messages_log = []
        try:
            async for msg in channel.history(limit=20):
                author_name = msg.author.name
                content = msg.content if msg.content else "[ملف/صورة/محتوى فارغ]"
                timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
                messages_log.append(f"[{timestamp}] **{author_name}**: {content}")
        except Exception as e:
            messages_log.append(f"❌ خطأ في قراءة الرسائل: {e}")

        log_text = f"📜 **آخر 20 رسالة في القناة (#{channel.name}):**\n\n" + "\n".join(messages_log)
        if len(log_text) > 2000:
            log_text = log_text[:1997] + "..."

        await interaction.followup.send(content=log_text, ephemeral=True)

class LeaveSpecificButton(discord.ui.Button):
    def __init__(self, guild_id, guild_name):
        super().__init__(style=discord.ButtonStyle.danger, label=f"مغادرة السيرفر")
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
            await interaction.response.send_message("❌ السيرفر غير موجود.", ephemeral=True)

class ServerView(discord.ui.View):
    def __init__(self, bot_instance):
        super().__init__(timeout=180)
        self.add_item(ServerSelect(bot_instance))

# أمر عرض قائمة السيرفرات (للأونر فقط)
@bot.command(name="سيرفر", aliases=["servers", "سيرفرات"])
async def list_servers(ctx):
    if ctx.author.id != OWNER_ID:
        # رفض وغداء عذر للغرباء
        await ctx.send("عذراً، لا أملك الصلاحية لعرض هذه المعلومات، هذه الأوامر خاصة جداً وليست متاحة للعامة.")
        return  

    if not bot.guilds:
        await ctx.send("عيوني فهد، أنا لست منضماً إلى أي سيرفر حالياً.")
        return

    view = ServerView(bot)
    embed = discord.Embed(
        title="🕵️‍♂️ لوحة سيطرة واستخبارات نوفا المتطورة",
        description="اختر السيرفر المطلوب لعرض تقرير التجسس، الرتب، سجل العقوبات، واستخراج رسائل القنوات:",
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
            "إذا سألك شخص غير فهد عن معلومات السيرفرات أو الأسرار، ارفضي تماماً وتمنعي بحجة (ما عندي هاي الصلاحية أو مو من اختصاصي). "
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

