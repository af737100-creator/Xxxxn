from fastapi import FastAPI, Request
from supabase import create_client, Client
import easyocr
from sentence_transformers import SentenceTransformer
import uvicorn

app = FastAPI()

# إعدادات سوبابيس
url = "https://tyuxfvgrabqjlkfqwddj.supabase.co"
key = "sb_secret_BX10JaBtfhd7FJbwbk7tGg_0SWqX1hS"
supabase: Client = create_client(url, key)

# تحميل النماذج مرة واحدة عند تشغيل السيرفر
reader = easyocr.Reader(['ar', 'en'])
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@app.post("/process-dump")
async def handle_webhook(request: Request):
    # استقبال البيانات من سوبابيس (Webhook)
    payload = await request.json()
    new_record = payload['record']
    row_id = new_record['id']
    content = new_record.get('content', '')

    # 1. إذا كان المحتوى نصاً، نولد الـ Vector مباشرة
    if content:
        embedding = model.encode(content).tolist()
        supabase.table("random_dumps").update({"embedding": embedding}).eq("id", row_id).execute()

    # 2. إذا كانت هناك صورة (سنحتاج لتحميلها من Storage أولاً)
    # سنضيف منطق قراءة ملفات الـ Storage هنا

    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
