import os
import google.generativeai as genai

# إعداد مفتاح جوجل
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# استخدام نموذج ذكي ومتكيف
text_model = genai.GenerativeModel("gemini-1.5-flash")

async def get_ai_response(user_message: str) -> str:
    """إرجاع رد عراقي ذكي، عفوي، ومتكيف حرفياً مع سياق الكلام"""
    try:
        # توجيه النظام ليكون الذكاء الاصطناعي متكيف ويسولف بطريقة طبيعية وبدون تكلف
        system_instruction = (
            "أنت شخص عراقي ذكي وودود جداً، تتكلم بالعفوية تامة وبطريقة متكيفّة مع كلام الشخص الذي يكلمك "
            "(تستخدم تعبيرات عراقية طبيعية مثل: هلا بيك، عاشت ايدك، تدلل عיוني، شكو ماكو، صار، إلخ). "
            "اجعل ردودك مباشرة، ذكية، وبدون أي مقدمات رسمية أو جافة."
        )
        
        full_prompt = f"{system_instruction}\n\nالشخص يكلك: {user_message}\nردك:"
        
        response = text_model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"AI Text Error: {e}")
        return "هلا بيك حبيبي، صار عندي التماس بالشبكة ثواني وراجعلكم!"

async def handle_image_request(user_message: str) -> str:
    """معالجة قسم الصور (مفصول حتى تطوره لاحقاً براحتك)"""
    return "🎨 | جاري تصميم صورتك بدقة عالية جداً وبدون أي علامة مائية... انتظر ثواني وراح تجهز!"

