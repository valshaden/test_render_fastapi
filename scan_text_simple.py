from langchain_gigachat.chat_models import GigaChat
from fastapi import FastAPI, UploadFile, File
import uvicorn
import json
import os
app = FastAPI()


@app.get("/")
def home():
    return {"message": "Text Recognition API"}


# Создаем модель
model = GigaChat(
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    credentials="Nzk2YzZmOWUtZDJkYS00NGY0LThkM2MtYWZhMmVmNWZmOWM3OjUwMDY0MGQwLTU3ODktNDk5MC1hMTY3LWU0ZTYyMTA4ZTllYw=="
)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(contents)
      
    with open(f"temp_{file.filename}", "rb") as f:
        file_uploaded_id = model.upload_file(f).id_

    message = {
        "role": "user",
        "content": "Распознай текст с этого изображения. Найди в нем название компании(name), телефоны(phones), email, адреса и сохрани их в формате JSON: {\"name\": \"\", \"phones\": [], \"email\": \"\", \"address\": \"\", \"description\": \"\"}. Верни только валидный JSON без дополнительного текста.",
        "attachments": [file_uploaded_id]
    }
    

    response = model.invoke([message])
    
    try:
        parsed_data = json.loads(response.content)
        result = parsed_data
    except:
        result = {"text": response.content}
    
    if os.path.exists("ai_response.json"):
        with open("ai_response.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            data = [item for item in data if "text" not in item]
            data.append(result)
        else:
            if "text" not in data:
                data = [data, result]
            else:
                data = result
    else:
        data = result
    
    with open("ai_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return result

# получить все компании из ai_response.json
@app.get("/get-companies")
def get_companies():
    with open("ai_response.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# получить все name из ai_response.json
@app.get("/get-names")
def get_names():
    with open("ai_response.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["name"] for item in data]


# CRUD самостоятельно



if __name__ == "__main__":    
    uvicorn.run("scan_text_simple:app", host="127.0.0.1", port=8000, reload=True)
