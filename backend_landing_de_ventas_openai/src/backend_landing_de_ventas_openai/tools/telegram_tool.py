from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type, Optional
import requests
import os


class TelegramToolSchema(BaseModel):
    """Input for TelegramTool."""
    mensaje: str = Field(description="El mensaje de texto a enviar por Telegram.")
    chat_id: Optional[str] = Field(
        default=None,
        description="chat_id del destinatario. Si se omite, se usa TELEGRAM_CHAT_ID del .env.",
    )


class TelegramTool(BaseTool):
    name: str = "Enviar Mensaje de Telegram"
    description: str = "Envía un mensaje de texto a un chat de Telegram usando la API de bots de Telegram."
    args_schema: Type[BaseModel] = TelegramToolSchema

    def _run(self, mensaje: str, chat_id: Optional[str] = None) -> str:
        try:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            # Si el agente no pasa un chat_id, usamos el del .env (el asesor de ventas)
            destino = chat_id or os.getenv("TELEGRAM_CHAT_ID")

            if not token:
                return "Error: La variable de entorno 'TELEGRAM_BOT_TOKEN' no está definida en el .env."
            if not destino:
                return "Error: No se proporcionó chat_id ni existe 'TELEGRAM_CHAT_ID' en el .env."

            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": destino,
                "text": mensaje,
                "parse_mode": "HTML",  # permite <b>negritas</b>, <i>cursivas</i>, etc.
            }

            response = requests.post(url, json=payload, timeout=15)

            if response.status_code != 200:
                return f"Error al enviar Telegram (HTTP {response.status_code}): {response.text}"

            return f"Mensaje de Telegram enviado exitosamente al chat {destino}."
        except Exception as e:
            return f"Error al enviar Telegram: {e}"
