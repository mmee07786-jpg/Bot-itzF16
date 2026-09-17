import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
import io

class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ima", description="توليد صورة احترافية باستخدام الذكاء الاصطناعي")
    @app_commands.describe(prompt="اكتب وصف الصورة باللغة الإنجليزية أو العربية")
    async def ima(self, interaction: discord.Interaction, prompt: str):
        # تأخير الاستجابة حتى البوت ما ينطي Timeout
        await interaction.response.defer(thinking=True)
        
        try:
            image_model = genai.GenerativeModel('imagen-3.0-generate-002')
            result = image_model.generate_content(prompt)
            
            for part in result.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_bytes = part.inline_data.data
                    file = discord.File(io.BytesIO(image_bytes), filename="ai_image.png")
                    await interaction.followup.send(content=f"🎨 | أبشر يا ملك، صورتك لـ: **{prompt}**", file=file)
                    return
            
            await interaction.followup.send("عذراً عيوني، ما قدرت أولد الصورة، جرب وصف ثاني!")
            
        except Exception as e:
            print(f"Slash Image Error: {e}")
            await interaction.followup.send(f"عذراً حبيبي، صار عندي خطأ بتوليد الصورة: `{str(e)[:50]}`")

async def setup(bot):
    await bot.add_cog(ImageCog(bot))

