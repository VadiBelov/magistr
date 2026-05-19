import os
import torch
from pyannote.audio import Pipeline
import config

os.environ["HF_TOKEN"] = config.HF_TOKEN

# Фикс для PyTorch 2.6+
import torch.serialization

_original_load = torch.load
torch.load = lambda *args, **kwargs: _original_load(*args, **{**kwargs, "weights_only": False})

pipeline = None


def get_pipeline():
    global pipeline
    if pipeline is None:
        print("⏳ Загрузка pyannote 3.1...")
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=config.HF_TOKEN
        )
        pipeline.to(torch.device("cpu"))
        print("✅ Диаризация готова")
    return pipeline


def diarize_audio(file_path: str):
    pipeline = get_pipeline()
    diarization = pipeline(file_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 1),
            "end": round(turn.end, 1),
            "speaker": speaker
        })

    return segments