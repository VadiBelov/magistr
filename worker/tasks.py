import os
from backend.ws_manager import manager
import asyncio
from worker.celery_app import celery_app
from faster_whisper import WhisperModel
from worker.diarization import diarize_audio
from worker.summarizer import summarize_text


model = None


def get_model():
    global model
    if model is None:
        print("⏳ Загрузка Whisper small...")
        model = WhisperModel("small", device="cpu", compute_type="int8")
        print("✅ Whisper готов")
    return model


@celery_app.task(bind=True, name="transcribe_audio")
def transcribe_audio(self, file_path: str, file_id: str, filename: str):
    print(f"⏳ Распознавание: {filename}")

    # Шаг 1: Распознавание речи
    model = get_model()
    segments, info = model.transcribe(file_path, beam_size=1, language="ru")

    asr_segments = []
    full_text = ""
    for seg in segments:
        asr_segments.append({
            "start": round(seg.start, 1),
            "end": round(seg.end, 1),
            "text": seg.text.strip()
        })
        full_text += seg.text.strip() + " "

    full_text = full_text.strip()

    # Шаг 2: Диаризация (пробуем, но не критично)
    speaker_segments = []
    try:
        print("⏳ Диаризация...")
        speaker_segments = diarize_audio(file_path)
    except Exception as e:
        print(f"⚠️ Диаризация недоступна: {e}")

    result_segments = []
    for asr in asr_segments:
        mid = (asr["start"] + asr["end"]) / 2
        speaker = "Speaker_0"
        for spk in speaker_segments:
            if spk["start"] <= mid <= spk["end"]:
                speaker = spk["speaker"]
                break
        result_segments.append({
            "start": asr["start"],
            "end": asr["end"],
            "speaker": speaker,
            "text": asr["text"]
        })

    # Шаг 3: Суммаризация
    summary = ""
    try:
        print("⏳ Суммаризация...")
        summary = summarize_text(full_text)
    except Exception as e:
        print(f"⚠️ Суммаризация недоступна: {e}")

    if os.path.exists(file_path):
        os.remove(file_path)

    return {
        "file_id": file_id,
        "filename": filename,
        "language": info.language,
        "full_text": full_text,
        "summary": summary,
        "segments": result_segments
    }


@celery_app.task(bind=True, name="transcribe_chunk")
def transcribe_chunk(self, file_path: str, room_id: str, user_id: str):
    """Быстрое распознавание короткого чанка"""
    try:
        model = get_model()
        segments, info = model.transcribe(file_path, beam_size=1, language="ru")

        text = " ".join([seg.text.strip() for seg in segments])

        # Отправляем результат через менеджер комнат (вызывается из основного процесса)
        return {
            "room_id": room_id,
            "speaker": user_id,
            "text": text,
            "language": info.language
        }
    except Exception as e:
        return {"error": str(e)}