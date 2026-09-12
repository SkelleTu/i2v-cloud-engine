import io
import os
from typing import Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image

app = FastAPI(title="I2V Cloud Engine", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"] , allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

MODEL = os.getenv("I2V_MODEL", "Wan-AI/Wan2.2-I2V-A14B-Diffusers")
BACKEND = os.getenv("I2V_BACKEND", "auto").lower()
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "20"))
API_KEY = os.getenv("I2V_API_KEY", "").strip()


def _authorize(x_i2v_api_key: Optional[str]) -> None:
    # If configured, this protects generation endpoints from public abuse.
    if API_KEY and x_i2v_api_key != API_KEY:
        raise HTTPException(401, "I2V API key inválida.")


@app.get("/")
def root():
    return {"service": "I2V Cloud Engine", "status": "online", "model": MODEL, "backend": BACKEND}


@app.get("/health")
def health():
    try:
        import torch
        cuda = bool(torch.cuda.is_available())
        gpu = torch.cuda.get_device_name(0) if cuda else None
    except Exception:
        cuda, gpu = False, None
    return {"ok": True, "cuda": cuda, "gpu": gpu, "model": MODEL, "backend": BACKEND, "api_key_required": bool(API_KEY)}


@app.get("/api/models")
def models():
    return {"default": MODEL, "models": [
        {"id": "Wan-AI/Wan2.2-I2V-A14B-Diffusers", "name": "Wan 2.2 I2V A14B"},
        {"id": "Wan-AI/Wan2.1-I2V-14B-480P", "name": "Wan 2.1 I2V 480P"},
        {"id": "zai-org/CogVideoX-5b-I2V", "name": "CogVideoX 5B I2V"},
        {"id": "Lightricks/LTX-Video", "name": "LTX-Video"},
    ]}


async def _read_image(upload: UploadFile) -> bytes:
    data = await upload.read()
    if not data:
        raise HTTPException(400, "Imagem vazia.")
    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(413, f"Imagem excede o limite de {MAX_FILE_MB} MB.")
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as exc:
        raise HTTPException(400, "Arquivo de imagem inválido.") from exc
    return data


def _generate_hf(image_bytes: bytes, prompt: str, negative_prompt: Optional[str], frames: int, steps: int, guidance: float) -> bytes:
    from huggingface_hub import InferenceClient
    token = os.getenv("HF_TOKEN")
    if not token:
        raise HTTPException(503, "HF_TOKEN não configurado.")
    client = InferenceClient(api_key=token)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    try:
        return client.image_to_video(image=image, model=MODEL, prompt=prompt,
            negative_prompt=negative_prompt or None, num_frames=frames,
            num_inference_steps=steps, guidance_scale=guidance)
    except Exception as exc:
        raise HTTPException(502, f"Falha no provedor Hugging Face: {exc}") from exc


def _generate_diffusers(image_bytes: bytes, prompt: str, negative_prompt: Optional[str], frames: int, steps: int, guidance: float) -> bytes:
    raise HTTPException(501, "Backend Diffusers ainda precisa ser habilitado para a GPU deste deployment.")


@app.post("/api/generate")
async def generate(
    image: UploadFile = File(...), prompt: str = Form(...), negative_prompt: str = Form(""),
    num_frames: int = Form(49), num_inference_steps: int = Form(30), guidance_scale: float = Form(5.0),
    x_i2v_api_key: Optional[str] = Header(default=None),
):
    _authorize(x_i2v_api_key)
    if not prompt.strip():
        raise HTTPException(400, "Prompt obrigatório.")
    if not 1 <= num_frames <= 200:
        raise HTTPException(400, "num_frames deve estar entre 1 e 200.")
    if not 1 <= num_inference_steps <= 100:
        raise HTTPException(400, "num_inference_steps deve estar entre 1 e 100.")
    image_bytes = await _read_image(image)
    use_diffusers = BACKEND == "diffusers"
    if BACKEND == "auto":
        try:
            import torch
            use_diffusers = bool(torch.cuda.is_available())
        except Exception:
            use_diffusers = False
    video = _generate_diffusers(image_bytes, prompt, negative_prompt, num_frames, num_inference_steps, guidance_scale) if use_diffusers else _generate_hf(image_bytes, prompt, negative_prompt, num_frames, num_inference_steps, guidance_scale)
    return Response(content=video, media_type="video/mp4", headers={"Content-Disposition": "inline; filename=i2v-video.mp4"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
