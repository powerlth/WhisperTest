import os
import whisper
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import ffmpeg

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 환경에서는 특정 출처만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model('turbo')
app.mount("/static", StaticFiles(directory="static"), name="static")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path: str, output_path: str):
    try:
        ffmpeg.input(input_path).output(output_path, ac=1, ar='16000').overwrite_output().run()
        return True
    except ffmpeg.Error as e:
        print("❌ ffmpeg 변환 오류:", e)
        return False


@app.post('/stt')
async def transcript(file: UploadFile = File(...)):
    print(f"📥 파일 수신: {file.filename}, 타입: {file.content_type}")

    # 오디오 타입 확인 로직 개선
    if not (file.content_type.startswith("audio") or file.content_type == "application/octet-stream"):
        return JSONResponse(
            content={"error": f"올바르지 않은 파일 형식입니다: {file.content_type}"},
            status_code=400
        )

    raw_input_path = None
    wav_path = None

    try:
        # 업로드 파일 저장
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            return JSONResponse(content={"error": "빈 파일이 업로드되었습니다."}, status_code=400)

        filename = file.filename or f"uploaded_audio_{os.urandom(4).hex()}.webm"
        raw_input_path = os.path.join(UPLOAD_DIR, filename)

        with open(raw_input_path, "wb") as f:
            f.write(file_bytes)
        print(f"🎙 저장된 원본 파일: {raw_input_path} (크기: {len(file_bytes)} bytes)")

        # .wav 경로 설정
        wav_path = f"{os.path.splitext(raw_input_path)[0]}.wav"

        # ffmpeg로 변환
        if not convert_to_wav(raw_input_path, wav_path):
            return JSONResponse(content={"error": "오디오 변환 실패"}, status_code=500)

        print(f"🔄 변환된 wav 파일: {wav_path}")

        # 변환된 파일이 존재하는지 확인
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
            return JSONResponse(content={"error": "변환된 파일이 없거나 비어 있습니다."}, status_code=500)

        # whisper 처리
        stt_result = model.transcribe(wav_path, language='ko')
        return JSONResponse(content={"text": stt_result["text"]}, status_code=200)

    except Exception as e:
        print(f"❌ 오류: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # 파일 정리
        try:
            if raw_input_path and os.path.exists(raw_input_path):
                os.remove(raw_input_path)
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
        except Exception as e:
            print(f"파일 정리 중 오류: {e}")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)