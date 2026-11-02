from faster_whisper import WhisperModel


_model = None


def get_model():
    global _model

    if _model is None:
        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    return _model


def transcribe_video(audio_path: str):
    model = get_model()

    segments, info = model.transcribe(
        audio_path,
        language="ru",
        vad_filter=True
    )

    result = []

    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })

    return result
