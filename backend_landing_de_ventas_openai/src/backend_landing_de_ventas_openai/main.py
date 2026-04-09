from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from starlette.responses import JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware

from .crew import LeadProcessingCrew

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Procesamiento de Leads",
    description="Recibe datos de un formulario y activa un equipo de agentes de IA para procesar el lead.",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://v0-interest-form-clone.vercel.app", #ESTE ES MIO
        "http://localhost:8501",  # Para desarrollo local
        "http://localhost:5173",  # Para Vite en desarrollo
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)


# Modelo de datos para la petición de entrada (debe coincidir con el payload del frontend)
class LeadRequest(BaseModel):
    nombre: str
    apellido: str
    pais: str
    correo_electronico: str
    numero_celular: str
    programas_interes: List[str]

#Endpoint de tipo POST
@app.post("/process-lead")
async def process_lead_endpoint(request: LeadRequest):
    """
    Recibe los datos de un lead, los convierte en un diccionario de inputs
    y activa el Crew de procesamiento.
    """
    try:
        # Convertir la lista de programas a un string para pasarlo a los agentes
        programas_str = ", ".join(request.programas_interes)
        
        inputs = {
            'nombre': request.nombre,
            'apellido': request.apellido,
            'pais': request.pais, # Pasamos el código de país como 'pais'
            'correo_electronico': request.correo_electronico,
            'numero_celular': request.numero_celular,
            'programas_interes': programas_str,
            'numero_asesor_ventas': os.getenv('SALES_WHATSAPP_NUMBER')
        }
        
        print(f"🚀 Procesando nuevo lead con los siguientes datos: {inputs}")
        
        # Instanciar y ejecutar el crew
        lead_crew = LeadProcessingCrew()
        result = lead_crew.crew().kickoff(inputs=inputs)
        
        print(f"✅ Procesamiento de lead finalizado.")
        
        return {"status": "success", "message": "Lead procesado exitosamente.", "result": result}

    except Exception as e:
        print(f"❌ Error durante la ejecución del crew: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error interno al procesar tu solicitud: {e}"
        )

@app.get("/")
def read_root():
    return {"status": "API del Procesador de Leads funcionando."}

# uvicorn src.backend_fastapi_landingpage.main:app --host 0.0.0.0 --port 8005