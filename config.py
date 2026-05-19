import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent

# Перенаправляем кэш моделей
os.environ["HF_HOME"] = str(BASE_DIR / "models_cache")
os.environ["TORCH_HOME"] = str(BASE_DIR / "models_cache")

# Папка для временных аудио
AUDIO_TEMP_DIR = BASE_DIR / "audio_temp"
AUDIO_TEMP_DIR.mkdir(exist_ok=True)

# База данных
DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/steno_db"

# Redis
REDIS_URL = "redis://localhost:6379/0"

# Hugging Face токен
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Максимальный размер загружаемого файла: 500 МБ
MAX_UPLOAD_SIZE = 500 * 1024 * 1024