from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type, Optional
import smtplib
from email.message import EmailMessage
import mimetypes
import os


class EmailToolSchema(BaseModel):
    """Input for EmailTool."""
    destinatario_nombre: str = Field(description="Nombre del lead a quien se envía el correo.")
    destinatario_correo: str = Field(description="Correo electrónico del lead.")
    mensaje: str = Field(description="Cuerpo del mensaje a enviar.")
    ruta_adjunto: Optional[str] = Field(description="[Opcional] Ruta local al archivo PDF a adjuntar.", default=None)


class EmailTool(BaseTool):
    name: str = "Enviar Correo Electrónico"
    description: str = "Envía un correo electrónico a un destinatario. Puede incluir un adjunto si se proporciona la ruta."
    args_schema: Type[BaseModel] = EmailToolSchema

    def _run(self, destinatario_nombre: str, destinatario_correo: str, mensaje: str, ruta_adjunto: str = None) -> str:
        try:
            remitente = os.getenv("GMAIL_USER")
            password = os.getenv("GMAIL_APP_PASSWORD")
            nombre_remitente = os.getenv("SENDER_NAME", "El Equipo de Datapath")

            email = EmailMessage()
            email["From"] = f'"{nombre_remitente}" <{remitente}>'
            email["To"] = destinatario_correo
            email["Subject"] = f"Información sobre tu interés en Datapath, {destinatario_nombre}"

            cuerpo_completo = f"{mensaje}\n\nSaludos cordiales,\n{nombre_remitente}"
            email.set_content(cuerpo_completo)

            if ruta_adjunto and os.path.exists(ruta_adjunto):
                ctype, _ = mimetypes.guess_type(ruta_adjunto)
                if ctype is None: ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                with open(ruta_adjunto, 'rb') as fp:
                    email.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(ruta_adjunto))
                print(f"--- Adjuntando archivo: {ruta_adjunto} ---")
            elif ruta_adjunto:
                print(f"--- Advertencia: No se encontró el archivo para adjuntar en la ruta: {ruta_adjunto} ---")

            smtp = smtplib.SMTP_SSL("smtp.gmail.com")
            smtp.login(remitente, password)
            smtp.send_message(email)
            smtp.quit()

            if ruta_adjunto and not os.path.exists(ruta_adjunto):
                return f"Correo enviado exitosamente a {destinatario_correo}, pero NO se pudo adjuntar el archivo (no encontrado)."
            elif ruta_adjunto:
                return f"Correo enviado exitosamente a {destinatario_correo} con el brochure adjunto."
            else:
                return f"Correo de texto enviado exitosamente a {destinatario_correo}."

        except Exception as e:
            return f"Error al enviar el correo: {e}"
