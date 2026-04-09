# Project CrewAI - Landing de Ventas

Sistema multi-agente con **CrewAI** que automatiza el procesamiento de leads desde una landing page de ventas. Cuando un usuario llena el formulario, 3 agentes de IA trabajan en secuencia para enriquecer el perfil, enviar un email de bienvenida y notificar al equipo comercial.

## Arquitectura

```
┌─────────────────────┐       POST /process-lead       ┌─────────────────────────┐
│   Frontend          │ ──────────────────────────────> │   Backend (FastAPI)      │
│   Streamlit         │ <────────────────────────────── │   CrewAI Multi-Agent     │
│   :8501             │       JSON Response             │   :8005                  │
└─────────────────────┘                                 └──────────┬──────────────┘
                                                                   │
                                                    ┌──────────────┼──────────────┐
                                                    │              │              │
                                              ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
                                              │ Agente 1  │ │ Agente 2  │ │ Agente 3  │
                                              │ Investiga │ │ Email     │ │ Ventas    │
                                              │ Perfil    │ │ Bienvenida│ │ Sheets +  │
                                              │           │ │           │ │ WhatsApp  │
                                              └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                                                    │              │              │
                                              DuckDuckGo      Gmail SMTP    Google Sheets
                                                                              WhatsApp API
```

## Flujo de Ejecución (Secuencial)

| Paso | Agente | Tarea | Herramienta |
|------|--------|-------|-------------|
| 1 | Investigador de Enriquecimiento | Busca LinkedIn/empresa del lead | InternetSearchTool (DuckDuckGo) |
| 2 | Comunicador Cliente | Envía email personalizado de bienvenida | EmailTool (Gmail SMTP) |
| 3 | Coordinador de Ventas | Registra lead en Google Sheets | GoogleSheetsTool |
| 4 | Coordinador de Ventas | Notifica al asesor por WhatsApp | WhatsAppTool |

## Estructura del Proyecto

```
.
├── backend_landing_de_ventas/          # Backend con Ollama (llama3.1 - local, gratuito)
│   ├── src/backend_landing_de_ventas/
│   │   ├── config/
│   │   │   ├── agents.yaml             # Definición de agentes (rol, goal, backstory)
│   │   │   └── tasks.yaml              # Definición de tareas
│   │   ├── tools/
│   │   │   ├── email_tool.py           # Envío de emails via Gmail
│   │   │   ├── whatsapp_tool.py        # Notificaciones WhatsApp Business API
│   │   │   ├── google_sheets_tool.py   # Registro en Google Sheets
│   │   │   └── internet_search_tool.py # Búsqueda web con DuckDuckGo
│   │   ├── crew.py                     # Orquestación de agentes y tareas
│   │   └── main.py                     # API FastAPI
│   └── .env                            # Variables de entorno (no incluido en git)
│
├── backend_landing_de_ventas_openai/   # Backend con OpenAI (GPT-4o - cloud, pago)
│   ├── src/backend_landing_de_ventas_openai/
│   │   └── ...                         # Misma estructura que el backend Ollama
│   └── .env
│
├── frontend_landing_de_ventas/         # Frontend Streamlit
│   ├── app.py                          # Formulario de captura de leads
│   └── .env
│
├── requirements.txt
└── README.md
```

## Backends Disponibles

| Backend | LLM | Ventaja | Desventaja |
|---------|-----|---------|------------|
| `backend_landing_de_ventas/` | Ollama / llama3.1 (8B) | Gratuito, local, privado | Modelo pequeño, requiere guardarraíles |
| `backend_landing_de_ventas_openai/` | OpenAI GPT-4o | Superior razonamiento | Requiere API key y tiene costo |

## Requisitos Previos

- Python >= 3.10
- [Ollama](https://ollama.com/) instalado (solo para backend Ollama)
- Cuenta de Gmail con App Password habilitado
- Cuenta de Meta WhatsApp Business API
- Credenciales de Google Cloud (Service Account para Sheets API)
- API Key de OpenAI (solo para backend OpenAI)

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/KevinInoCol/Project-CrewAI-Landing-de-Ventas.git
cd Project-CrewAI-Landing-de-Ventas
```

### 2. Crear entorno virtual e instalar dependencias

```bash
conda create -n CrewAI-Landing-de-Ventas python=3.11 -y
conda activate CrewAI-Landing-de-Ventas
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en cada directorio:

**`backend_landing_de_ventas/.env`** (Ollama):
```env
MODEL=ollama/llama3.1
API_BASE=http://localhost:11434
GOOGLE_SHEET_ID=tu_google_sheet_id
GMAIL_USER=tu_email@gmail.com
GMAIL_APP_PASSWORD=tu_app_password
SENDER_NAME=Tu Nombre
WHATSAPP_API_TOKEN=tu_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
SALES_WHATSAPP_NUMBER=+51999999999
```

**`backend_landing_de_ventas_openai/.env`** (OpenAI):
```env
MODEL=gpt-4o
OPENAI_API_KEY=sk-proj-tu_api_key
GOOGLE_SHEET_ID=tu_google_sheet_id
GMAIL_USER=tu_email@gmail.com
GMAIL_APP_PASSWORD=tu_app_password
SENDER_NAME=Tu Nombre
WHATSAPP_API_TOKEN=tu_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
SALES_WHATSAPP_NUMBER=+51999999999
```

**`frontend_landing_de_ventas/.env`**:
```env
BACKEND_URL=http://127.0.0.1:8005/process-lead
```

### 4. Descargar modelo Ollama (solo backend Ollama)

```bash
ollama pull llama3.1
```

## Ejecucion

### Iniciar Backend (elegir uno)

**Opcion A - Ollama (local, gratuito):**
```bash
cd backend_landing_de_ventas
uvicorn src.backend_landing_de_ventas.main:app --host 0.0.0.0 --port 8005
```

**Opcion B - OpenAI (cloud, pago):**
```bash
cd backend_landing_de_ventas_openai
uvicorn src.backend_landing_de_ventas_openai.main:app --host 0.0.0.0 --port 8005
```

### Iniciar Frontend

```bash
cd frontend_landing_de_ventas
streamlit run app.py
```

El frontend estara disponible en `http://localhost:8501`.

## API

### `POST /process-lead`

```json
{
  "nombre": "Juan",
  "apellido": "Perez",
  "pais": "+51",
  "correo_electronico": "juan@email.com",
  "numero_celular": "+51999888777",
  "programas_interes": ["AI Engineer", "n8n Basico"]
}
```

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "Lead procesado exitosamente.",
  "result": "..."
}
```

### `GET /`

Health check. Retorna `{"status": "API del Procesador de Leads funcionando."}`.

## Programas Disponibles en el Formulario

- AI Engineer
- n8n Basico
- n8n Avanzado
- Make Basico
- Make Avanzado

## Tecnologias

- **CrewAI** 1.14.0 - Framework de agentes multi-IA
- **FastAPI** - Backend API
- **Streamlit** - Frontend
- **Ollama** / **OpenAI** - LLMs
- **DuckDuckGo Search** - Busqueda web
- **heyoo** - WhatsApp Business API
- **pygsheets** - Google Sheets API
- **Gmail SMTP** - Envio de emails
