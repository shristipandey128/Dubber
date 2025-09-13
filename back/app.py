# backend/app.py
from dotenv import load_dotenv
import os, random, uuid, subprocess, requests
from fastapi import FastAPI
from pydantic import BaseModel
from gtts import gTTS
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # loads variables from .env
LLM_API_KEY = os.getenv("OPENROUTER_API_KEY")
print("LLM_API_KEY:", LLM_API_KEY)  # debug line
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, backend is running!"}
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE, "assets")
OUTPUTS = os.path.join(BASE, "outputs")
os.makedirs(OUTPUTS, exist_ok=True)

def list_files(subdir):
    path = os.path.join(ASSETS_DIR, subdir)
    if not os.path.exists(path): return []
    return [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.')]

IMAGES = list_files("images")
VIDEOS = list_files("videos")

LLM_API_URL = "https://api.openrouter.ai/v1/chat/completions"  # replace if needed
LLM_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class GenReq(BaseModel):
    prompt: str
    length: int = 3

@app.post("/generate")
def generate(req: GenReq):
    prompt_text = f"Write {req.length} short lines suitable for a short video from this prompt: {req.prompt}"
    # call LLM (OpenRouter style) - fallback: simple echo
    try:
        headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
        payload = {"model":"deepseek-chat-v3.1:free","messages":[{"role":"user","content":prompt_text}], "max_tokens":300}
        r = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=30)
        data = r.json()
        script = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception:
        script = "This is a fallback script. Provide a better prompt or set OPENROUTER_API_KEY."

    chosen_images = random.sample(IMAGES, min(3, len(IMAGES)))
    chosen_videos = random.sample(VIDEOS, min(3, len(VIDEOS)))

    # TTS
    audio_name = f"audio_{uuid.uuid4().hex}.mp3"
    audio_path = os.path.join(OUTPUTS, audio_name)
    try:
        tts = gTTS(text=script, lang="en")
        tts.save(audio_path)
    except Exception:
        # empty placeholder silent mp3 generation via ffmpeg (1s)
        audio_path = os.path.join(OUTPUTS, "silent.mp3")
        if not os.path.exists(audio_path):
            subprocess.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t","1", audio_path], check=True)

    return {
        "script": script,
        "images": chosen_images,
        "videos": chosen_videos,
        "audio": f"/outputs/{os.path.basename(audio_path)}"
    }

@app.get("/outputs/{fn}")
def get_output(fn: str):
    return FileResponse(os.path.join(OUTPUTS, fn))

@app.post("/export")
def export(payload: dict):
    images = payload.get("images", [])
    videos = payload.get("videos", [])
    audio_url = payload.get("audio", "")
    outname = f"final_{uuid.uuid4().hex}.mp4"
    tmp_concat = f"/tmp/concat_{uuid.uuid4().hex}.txt"
    temp_vids = []
    with open(tmp_concat, "w") as f:
        for v in videos:
            f.write(f"file '{os.path.abspath(v)}'\n")
        for img in images:
            img_vid = f"/tmp/img_{uuid.uuid4().hex}.mp4"
            # create 2s video from image
            subprocess.run(["ffmpeg","-y","-loop","1","-t","2","-i",img,"-vf","scale=1280:720","-c:v","libx264","-pix_fmt","yuv420p", img_vid], check=True)
            temp_vids.append(img_vid)
            f.write(f"file '{img_vid}'\n")
    merged = f"/tmp/merged_{uuid.uuid4().hex}.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",tmp_concat,"-c","copy", merged], check=True)
    # handle audio (download if http)
    audio_local = audio_url
    if audio_url.startswith("http"):
        r = requests.get(audio_url)
        audio_local = f"/tmp/audio_{uuid.uuid4().hex}.mp3"
        open(audio_local,"wb").write(r.content)
    final_out = os.path.join(OUTPUTS, outname)
    subprocess.run(["ffmpeg","-y","-i",merged,"-i",audio_local,"-c:v","copy","-c:a","aac","-shortest", final_out], check=True)
    # cleanup temp files
    for t in temp_vids: os.remove(t)
    return {"download_url": f"/download/{outname}"}

@app.get("/download/{fn}")
def download(fn: str):
    return FileResponse(os.path.join(OUTPUTS, fn))
