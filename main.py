from fastapi import FastAPI, Request
from supabase import create_client, Client
import easyocr
from sentence_transformers import SentenceTransformer
import uvicorn
import os

app = FastAPI()

# إعدادات سوبابيس (يفضل استخدام متغيرات البيئة Environment Variables للأمان)
SB_URL = "https://tyuxfvgrabqjlkfqwddj.supabase.co"
SB_KEY = "sb_secret_BX10JaBtfhd7FJbwbk7tGg_0SWqX1hS"
supabase: Client = create_client(SB_URL, SB_KEY)

# تحميل النماذج عند بدء التشغيل
print("⌛ جاري تحميل نماذج الذكاء الاصطناعي على السيرفر...")
reader = easyocr.Reader(['ar', 'en'])
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("✅ السيرفر جاهز لاستقبال الطلبات.")

@app.post("/webhook")
async def handle_supabase_webhook(request: Request):
    try:
        payload = await request.json()
        # سوبابيس ترسل السجل الجديد في حقل 'record'
        record = payload.get('record', {})
        row_id = record.get('id')
        content = record.get('content', '')

        if not row_id:
            return {"status": "no id found"}

        # معالجة النص وتوليد الـ Vector
        if content:
            print(f"🔍 معالجة سجل جديد ID: {row_id}")
            embedding = model.encode(content).tolist()
            
            # تحديث قاعدة البيانات بالـ Embedding
            supabase.table("random_dumps").update({
                "embedding": embedding
            }).eq("id", row_id).execute()
            
            return {"status": "processed", "id": row_id}
            
        return {"status": "empty content"}
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
