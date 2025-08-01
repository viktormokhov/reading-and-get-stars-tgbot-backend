from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field, SecretStr, BaseModel
from pydantic_settings import BaseSettings

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

WEBAPP_URL = "https://read-q.cloudns.ch:8443"


class ProjectBaseSettings(BaseSettings):
    class Config:
        env_file = ENV_FILE
        case_sensitive = False
        extra = "ignore"


class TextModelConfig(BaseModel):
    model_name: str


class ImageModelConfig(BaseModel):
    model_name: str


class TelegramSettings(ProjectBaseSettings):
    tg_admin_id: int
    tg_bot_token: SecretStr
    tg_webhook_url: str
    tg_webhook_token: SecretStr

    @property
    def bot_token(self) -> str:
        return self.tg_bot_token.get_secret_value()

    @property
    def webhook_token(self) -> str:
        return self.tg_webhook_token.get_secret_value()


class OpenAISettings(ProjectBaseSettings):
    openai_api_key: SecretStr
    text: Optional[TextModelConfig] = TextModelConfig(model_name="gpt-4.1-nano-2025-04-14")
    image: Optional[ImageModelConfig] = ImageModelConfig(model_name="dall-e-3")

    @property
    def api_key(self) -> str:
        return self.openai_api_key.get_secret_value()


class GeminiSettings(ProjectBaseSettings):
    google_gemini_api_key: SecretStr
    google_gemini_proxy_url: str
    text: Optional[TextModelConfig] = TextModelConfig(model_name="gemini-2.0-flash-001:generateContent")
    image: Optional[ImageModelConfig] = None

    @property
    def api_key(self) -> str:
        return self.google_gemini_api_key.get_secret_value()


class CloudflareSettings(ProjectBaseSettings):
    cloudflare_api_key: SecretStr
    cloudflare_account_id: str
    text: Optional[TextModelConfig] = None
    image: Optional[ImageModelConfig] = ImageModelConfig(model_name="bytedance/stable-diffusion-xl-lightning")

    @property
    def cloudflare_worker_image_url(self) -> str:
        return (
            f'https://api.cloudflare.com/client/v4/accounts/'
            f'{self.cloudflare_account_id}/ai/run/@cf/{self.image.model_name}'
        )

    @property
    def api_key(self) -> str:
        return self.cloudflare_api_key.get_secret_value()


class DeepSeekSettings(ProjectBaseSettings):
    openrouter_api_key: SecretStr
    openrouter_url: str = 'https://openrouter.ai/api/v1'
    text: Optional[TextModelConfig] = TextModelConfig(model_name="deepseek/deepseek-r1:free")
    image: Optional[ImageModelConfig] = None

    @property
    def api_key(self) -> str:
        return self.openrouter_api_key.get_secret_value()


class AISettings:
    def __init__(self, **providers):
        for name, provider in providers.items():
            setattr(self, name, provider)

    def get_all_text_models(self) -> dict:
        result = {}
        for k, v in vars(self).items():
            if hasattr(v, "text") and v.text is not None:
                provider_dict = v.model_dump() if hasattr(v, "model_dump") else v.dict()
                # Удаляем ключ 'image', если он есть
                provider_dict.pop('image', None)
                result[k] = provider_dict
        return result

    def get_all_image_models(self) -> dict:
        result = {}
        for k, v in vars(self).items():
            if hasattr(v, "image") and v.image is not None:
                provider_dict = v.model_dump() if hasattr(v, "model_dump") else v.dict()
                # Удаляем ключ 'text', если он есть
                provider_dict.pop('text', None)
                result[k] = provider_dict
        return result


class DBSettings(ProjectBaseSettings):
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str
    postgres_port: int
    postgres_db: str

    @property
    def db_url(self) -> str:
        password = quote_plus(self.postgres_password.get_secret_value())
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def db_url_sync(self) -> str:
        password = quote_plus(self.postgres_password.get_secret_value())
        return (
            f"postgresql://{self.postgres_user}:{password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def secret(self) -> str:
        return self.postgres_password.get_secret_value()

    mongo_initdb_root_username: str
    mongo_initdb_root_password: SecretStr
    mongodb_host: str
    mongodb_port: int
    mongodb_name: str

    @property
    def mongodb_url(self) -> str:
        password = quote_plus(self.mongo_initdb_root_password.get_secret_value())
        return (
            f"mongodb://{self.mongo_initdb_root_username}:{password}@"
            f"{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_name}"
            "?authSource=admin"
        )

    @property
    def mongodb_secret(self) -> str:
        return self.mongo_initdb_root_password.get_secret_value()

    # ---- REDIS SETTINGS ----
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_password: SecretStr

    @property
    def redis_url(self) -> str:
        password = quote_plus(self.redis_password.get_secret_value())
        return (
            f"redis://:{password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        )

    @property
    def redis_secret(self) -> str | None:
        return self.redis_password.get_secret_value()


class ImgBBSettings(ProjectBaseSettings):
    imgbb_api_key: SecretStr


class BackendSettings(ProjectBaseSettings):
    backend_api_key: SecretStr

    @property
    def api_key(self) -> str:
        return self.backend_api_key.get_secret_value()


class MinioSettings(ProjectBaseSettings):
    minio_root_user: str
    minio_root_password: SecretStr
    minio_host: str
    minio_port: int = 9000
    minio_secure: bool = True

    @property
    def endpoint_url(self) -> str:
        return f"{self.minio_host}:{self.minio_port}"

    @property
    def access_key(self) -> str:
        return self.minio_root_user

    @property
    def secret_key(self) -> str:
        return self.minio_root_password.get_secret_value()

# === Инициализация ===
def get_tg_settings():
    return TelegramSettings()


def get_openai_settings():
    return OpenAISettings()


def get_gemini_settings():
    return GeminiSettings()


def get_cloudflare_settings():
    return CloudflareSettings()


def get_deepseek_settings():
    return DeepSeekSettings()


def get_ai_settings():
    return AISettings(
        openai=get_openai_settings(),
        gemini=get_gemini_settings(),
        cloudflare=get_cloudflare_settings(),
        deepseek=get_deepseek_settings(),
    )


def get_db_settings():
    return DBSettings()


def get_imgbb_settings():
    return ImgBBSettings()


def get_backend_settings():
    return BackendSettings()

def get_minio_settings():
    return MinioSettings()

