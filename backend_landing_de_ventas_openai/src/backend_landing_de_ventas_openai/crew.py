# ============================================
# CREW DE PROCESAMIENTO DE LEADS (VARIANTE OPENAI)
# ============================================
# Versión "gemela" del backend de Llama, pero usando OpenAI como LLM
# y embeddings de OpenAI para la base de conocimiento. Sirve para comparar
# el mismo flujo multi-agente con dos proveedores distintos.

import os
import glob
from dotenv import load_dotenv

# ============================================
# IMPORTACIONES DE CREWAI
# ============================================
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM

# ============================================
# HERRAMIENTAS PERSONALIZADAS
# ============================================
# - EmailTool: Envía emails de bienvenida a los leads
# - TelegramTool: Notifica al equipo de ventas por Telegram
# - GoogleSheetsTool: Registra leads en Google Sheets para seguimiento
from .tools.email_tool import EmailTool
from .tools.telegram_tool import TelegramTool
from .tools.google_sheets_tool import GoogleSheetsTool
from .tools.internet_search_tool import InternetSearchTool

# ============================================
# FUENTES DE CONOCIMIENTO (KNOWLEDGE / RAG)
# ============================================
# CrewAI puede cargar archivos (txt, pdf, etc.), generar embeddings y guardarlos
# en una base vectorial local (ChromaDB) para que los agentes consulten contexto.
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource


@CrewBase
class LeadProcessingCrew():
    """
    CREW DE PROCESAMIENTO DE LEADS (OpenAI)

    Sistema multi-agente que automatiza el flujo completo de procesamiento
    de nuevos leads desde la landing page:

    1. Enriquece el perfil del lead investigando en internet
    2. Envía un email de bienvenida personalizado
    3. Registra el lead en Google Sheets
    4. Notifica al equipo de ventas por Telegram
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        """Configura el LLM, las herramientas y la base de conocimiento."""
        load_dotenv()

        # ============================================
        # CONFIGURACIÓN DEL LLM (OPENAI)
        # ============================================
        # Modelo de OpenAI (gpt-4.1 por defecto). CrewAI usa OPENAI_API_KEY del .env.
        # temperature=0 → respuestas deterministas y uso fiable de herramientas.
        self.llm = LLM(
            model=os.getenv("MODEL", "gpt-4.1"),
            temperature=0
        )

        # ============================================
        # HERRAMIENTAS
        # ============================================
        self.website_search_tool = InternetSearchTool()  # Búsqueda con DuckDuckGo
        self.email_tool = EmailTool()
        self.telegram_tool = TelegramTool()
        self.gsheets_tool = GoogleSheetsTool()

        # ============================================
        # FUENTES DE CONOCIMIENTO (KNOWLEDGE)
        # ============================================
        # Los archivos se buscan dentro de la carpeta 'knowledge/' del proyecto.
        # CrewAI espera las rutas RELATIVAS a esa carpeta (solo el nombre del archivo).
        self.knowledge_sources = [
            TextFileKnowledgeSource(file_paths=["programas_datapath.txt"]),
        ]

        # Cargamos automáticamente cualquier PDF que coloques en knowledge/
        knowledge_dir = os.path.join(os.getcwd(), "knowledge")
        pdf_files = [
            os.path.basename(p) for p in glob.glob(os.path.join(knowledge_dir, "*.pdf"))
        ]
        if pdf_files:
            self.knowledge_sources.append(PDFKnowledgeSource(file_paths=pdf_files))

        # ============================================
        # EMBEDDER (OPENAI)
        # ============================================
        # Embeddings de OpenAI (text-embedding-3-small). Usa OPENAI_API_KEY del .env.
        # OJO: la clave debe ser 'model_name' (no 'model'); CrewAI valida la config
        # contra un TypedDict y descarta cualquier clave que no reconozca.
        self.embedder = {
            "provider": "openai",
            "config": {
                "model_name": "text-embedding-3-small",
            },
        }

    # ============================================
    # AGENTES
    # ============================================
    @agent
    def comunicador_cliente(self) -> Agent:
        """AGENTE 1: Comunicador de clientes (envía el email de bienvenida)."""
        return Agent(
            config=self.agents_config['comunicador_cliente'],
            tools=[self.email_tool],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def coordinador_ventas(self) -> Agent:
        """AGENTE 2: Coordinador de ventas (Telegram + Google Sheets)."""
        return Agent(
            config=self.agents_config['coordinador_ventas'],
            tools=[self.telegram_tool, self.gsheets_tool],
            llm=self.llm,
            verbose=True
        )

    @agent
    def investigador_enriquecimiento(self) -> Agent:
        """AGENTE 3: Investigador (enriquece el perfil del lead en internet)."""
        return Agent(
            config=self.agents_config['investigador_enriquecimiento'],
            tools=[self.website_search_tool],
            llm=self.llm,
            verbose=True
        )

    # ============================================
    # TAREAS
    # ============================================
    @task
    def enviar_email_bienvenida(self) -> Task:
        """TAREA 2: Envío de email de bienvenida."""
        return Task(
            config=self.tasks_config['enviar_email_bienvenida'],
            agent=self.comunicador_cliente(),
        )

    @task
    def registrar_lead_en_sheets(self) -> Task:
        """TAREA 3: Registro del lead en Google Sheets."""
        return Task(
            config=self.tasks_config['registrar_lead_en_sheets'],
            agent=self.coordinador_ventas(),
            tools=[self.gsheets_tool],
            context=[self.enriquecer_perfil_lead()]
        )

    @task
    def notificar_ventas_telegram(self) -> Task:
        """TAREA 4: Notificación al equipo de ventas por Telegram."""
        return Task(
            config=self.tasks_config['notificar_ventas_telegram'],
            agent=self.coordinador_ventas(),
            tools=[self.telegram_tool],
            context=[self.enriquecer_perfil_lead()]
        )

    @task
    def enriquecer_perfil_lead(self) -> Task:
        """TAREA 1: Enriquecimiento del perfil del lead."""
        return Task(
            config=self.tasks_config['enriquecer_perfil_lead'],
            agent=self.investigador_enriquecimiento(),
        )

    # ============================================
    # ENSAMBLAJE DEL CREW
    # ============================================
    @crew
    def crew(self) -> Crew:
        """
        FLUJO DE EJECUCIÓN:
        1. enriquecer_perfil_lead()    → Investiga al lead
        2. enviar_email_bienvenida()   → Envía email personalizado
        3. registrar_lead_en_sheets()  → Registra en Google Sheets
        4. notificar_ventas_telegram() → Notifica por Telegram
        """
        return Crew(
            agents=self.agents,
            tasks=[
                self.enriquecer_perfil_lead(),
                self.enviar_email_bienvenida(),
                self.registrar_lead_en_sheets(),
                self.notificar_ventas_telegram(),
            ],
            process=Process.sequential,
            verbose=True,

            # knowledge_sources: archivos que los agentes pueden consultar (RAG)
            knowledge_sources=self.knowledge_sources,

            # embedder: modelo de embeddings de OpenAI para la base vectorial
            embedder=self.embedder,
        )
