from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type
import pygsheets
import os
from datetime import datetime


class GoogleSheetsToolSchema(BaseModel):
    """Input for GoogleSheetsTool."""
    nombre: str = Field(description="Nombre del lead.")
    apellido: str = Field(description="Apellido del lead.")
    correo: str = Field(description="Correo electrónico del lead.")
    codigo_pais: str = Field(description="Código de país del número de celular.")
    numero_celular: str = Field(description="Número de celular sin el código de país.")
    programas: str = Field(description="Programas de interés del lead, como un solo string.")


class GoogleSheetsTool(BaseTool):
    name: str = "Registrar Lead en Google Sheets"
    description: str = "Registra la información de un nuevo lead en la hoja de cálculo de Google Sheets."
    args_schema: Type[BaseModel] = GoogleSheetsToolSchema

    def _run(self, nombre: str, apellido: str, correo: str, codigo_pais: str, numero_celular: str, programas: str) -> str:
        try:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Interesados")
            service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

            if not service_account_path:
                return "Error: La variable de entorno 'GOOGLE_SERVICE_ACCOUNT_FILE' no está definida en el .env."

            if not os.path.exists(service_account_path):
                return f"Error: El archivo de cuenta de servicio '{service_account_path}' no fue encontrado."

            gc = pygsheets.authorize(service_file=service_account_path)
            sh = gc.open_by_key(sheet_id)
            wks = sh.worksheet_by_title(sheet_name)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [timestamp, nombre, apellido, correo, codigo_pais, numero_celular.replace(codigo_pais, ''), programas]

            wks.append_table(values=new_row, start='A1', end=None, dimension='ROWS', overwrite=False)
            return "Lead registrado exitosamente en Google Sheets."
        except Exception as e:
            return f"Error al registrar en Google Sheets: {e}"
