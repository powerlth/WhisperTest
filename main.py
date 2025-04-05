import os
import whisper
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
model = whisper.load_model('turbo')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post('/stt')
async def transcript(file: UploadFile = File(...)):
    if file.content_type.startswith("audio") is False:
        return PlainTextResponse("올바르지 않은 파일 형식입니다.", status_code=400)

    file_name = None

    with NamedTemporaryFile(delete=False) as temp:
        temp.write(await file.read())
        temp.seek(0)
        file_name = temp.name
    try:
        stt_result = model.transcribe(file_name)
        return JSONResponse(content={"text": stt_result["text"]}, status_code=200)
    except Exception as e:
        print(e)
    finally:
        os.remove(file_name)

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    os.makedirs(temp_dir, exist_ok=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)