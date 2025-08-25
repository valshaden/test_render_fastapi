from fastapi import FastAPI, File, UploadFile
from langchain_gigachat.chat_models import GigaChat

app = FastAPI()

model = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    credentials="=="
)

@app.get("/")
def home():
    return {"message": "Text Recognition API"}

@app.post("/recognize")
async def recognize_text(file: UploadFile = File(...)):
    contents = await file.read()
    
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(contents)
    
    with open(f"temp_{file.filename}", "rb") as f:
        file_uploaded_id = model.upload_file(f).id_
    
    message = {
        "role": "user",
        "content": "Распознай текст с этого изображения и выведи его полностью.",
        "attachments": [file_uploaded_id]
    }
    
    response = model.invoke([message])
    return {"text": response.content}

@app.post("/extract")
async def extract_company_info(file: UploadFile = File(...)):
    contents = await file.read()
    
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(contents)
    
    with open(f"temp_{file.filename}", "rb") as f:
        file_uploaded_id = model.upload_file(f).id_
    
    message = {
        "role": "user",
        "content": "Распознай текст с этого изображения. Найди в нем название компании(name), телефоны(phones), email, адреса и сохрани их в формате JSON: {\"name\": \"\", \"phones\": [], \"email\": \"\", \"address\": \"\", \"description\": \"\"}. Верни только JSON без дополнительного текста.",
        "attachments": [file_uploaded_id]
    }
    
    response = model.invoke([message])
    return {"extracted_data": response.content}
