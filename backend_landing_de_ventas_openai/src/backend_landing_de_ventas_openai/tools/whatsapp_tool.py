from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type
from heyoo import WhatsApp
import os


class WhatsAppToolSchema(BaseModel):
    """Input for WhatsAppTool."""
    numero_destinatario: str = Field(description="Número de teléfono del destinatario en formato internacional (ej. +51999888777).")
    mensaje: str = Field(description="El mensaje de texto a enviar.")


class WhatsAppTool(BaseTool):
    name: str = "Enviar Mensaje de WhatsApp"
    description: str = "Envía un mensaje de texto a un número de WhatsApp usando la API de Heyoo."
    args_schema: Type[BaseModel] = WhatsAppToolSchema

    def _run(self, numero_destinatario: str, mensaje: str) -> str:
        try:
            token = os.getenv("WHATSAPP_API_TOKEN")
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            messenger = WhatsApp(token, phone_number_id=phone_number_id)
            messenger.send_message(mensaje, numero_destinatario)
            return f"Mensaje de WhatsApp enviado exitosamente a {numero_destinatario}."
        except Exception as e:
            return f"Error al enviar WhatsApp: {e}"
