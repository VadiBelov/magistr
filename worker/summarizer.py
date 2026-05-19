from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import config

summarizer = None


def get_summarizer():
    global summarizer
    if summarizer is None:
        print("⏳ Загрузка модели суммаризации (rut5-base)...")
        model_name = "cointegrated/rut5-base-absum"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer
        )
        print("✅ Суммаризация готова")
    return summarizer


def summarize_text(text: str, max_length: int = 150):
    """Создаёт краткий итог текста"""
    if len(text) < 50:
        return text  # слишком короткий текст — нечего сокращать

    summarizer = get_summarizer()
    result = summarizer(
        text,
        max_length=max_length,
        min_length=20,
        do_sample=False,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    return result[0]["summary_text"]