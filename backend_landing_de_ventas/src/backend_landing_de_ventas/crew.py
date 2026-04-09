# ============================================
# CREW DE PROCESAMIENTO DE LEADS
# ============================================
# Este archivo define un sistema multi-agente usando CrewAI para
# automatizar el procesamiento de leads desde una landing page.

# src/backend_fastapi_landingpage/crew.py

import os
from dotenv import load_dotenv

# ============================================
# IMPORTACIONES DE CREWAI
# ============================================
# Agent: Clase base para crear agentes inteligentes
# Crew: Orquestador que coordina múltiples agentes y tareas
# Process: Define cómo se ejecutan las tareas (sequential, hierarchical, etc.)
# Task: Define las tareas que ejecutarán los agentes
from crewai import Agent, Crew, Process, Task

# Decoradores para definir la estructura del Crew de forma declarativa:
# - @CrewBase: Marca la clase como un Crew
# - @agent: Registra un método como definición de agente
# - @crew: Registra el método que ensambla el Crew completo
# - @task: Registra un método como definición de tarea
from crewai.project import CrewBase, agent, crew, task

# LLM (Large Language Model) - El "cerebro" de los agentes
# Usamos la clase LLM de CrewAI que soporta Ollama de forma nativa
from crewai import LLM

# ============================================
# HERRAMIENTAS PRE-CONSTRUIDAS DE CREWAI
# ============================================
# CrewAI incluye herramientas listas para usar:
# - WebsiteSearchTool: Permite buscar información en sitios web
# - DirectorySearchTool: Permite buscar en directorios locales (ej: PDFs, documentos)
#from crewai_tools import DirectorySearchTool #, WebsiteSearchTool

# ============================================
# HERRAMIENTAS PERSONALIZADAS
# ============================================
# Herramientas custom creadas específicamente para este proyecto:
# - EmailTool: Envía emails de bienvenida a los leads
# - WhatsAppTool: Notifica al equipo de ventas por WhatsApp
# - GoogleSheetsTool: Registra leads en Google Sheets para seguimiento
from .tools.email_tool import EmailTool
from .tools.whatsapp_tool import WhatsAppTool
from .tools.google_sheets_tool import GoogleSheetsTool
from .tools.internet_search_tool import InternetSearchTool

# ============================================
# DECORADOR @CrewBase
# ============================================
# Este decorador transforma la clase en un Crew de CrewAI.
# Permite usar los decoradores @agent, @task y @crew dentro de la clase.
@CrewBase
class LeadProcessingCrew():
    """
    CREW DE PROCESAMIENTO DE LEADS
    
    Sistema multi-agente que automatiza el flujo completo de procesamiento
    de nuevos leads desde la landing page:
    
    1. Enriquece el perfil del lead investigando en internet
    2. Envía un email de bienvenida personalizado
    3. Notifica al equipo de ventas y registra en Google Sheets
    """
    
    # ============================================
    # ARCHIVOS DE CONFIGURACIÓN
    # ============================================
    # Separamos la configuración del código para facilitar cambios sin tocar el código
    # agents.yaml: Define rol, objetivo, backstory de cada agente
    # tasks.yaml: Define descripción, resultado esperado de cada tarea
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        """
        INICIALIZACIÓN DEL CREW
        
        Configura el modelo de lenguaje (LLM) y todas las herramientas
        que usarán los agentes para realizar sus tareas.
        """
        # Cargar variables de entorno (.env) con API keys y configuración
        load_dotenv()
        
        # ============================================
        # CONFIGURACIÓN DEL LLM (CEREBRO DE LOS AGENTES)
        # ============================================
        # Todos los agentes usarán Ollama con llama3.1 corriendo localmente
        # - model: ollama/llama3.1 (modelo local de 8B parámetros)
        # - base_url: http://localhost:11434 (servidor local de Ollama)
        # - temperature: 0.7 (balance entre creatividad y consistencia)
        self.llm = LLM(
            model=os.getenv("MODEL", "ollama/llama3.1"),
            base_url=os.getenv("API_BASE", "http://localhost:11434"),
            temperature=0.7
        )
        
        # ============================================
        # INICIALIZACIÓN DE HERRAMIENTAS PRE-CONSTRUIDAS
        # ============================================
        # WebsiteSearchTool: Permite a los agentes buscar información en sitios web
        # Útil para investigar información sobre empresas, personas, industrias, etc.
        self.website_search_tool = InternetSearchTool() #Este es el objeto de DuckDuckGo
        
        # DirectorySearchTool: Permite buscar en documentos locales
        # En este caso, buscará en la carpeta './brochures' (catálogos, PDFs, etc.)
        #self.directory_search_tool = DirectorySearchTool(directory='./brochures')
        
        # ============================================
        # INICIALIZACIÓN DE HERRAMIENTAS PERSONALIZADAS
        # ============================================
        # EmailTool: Herramienta custom para enviar emails via SMTP o servicio de email
        self.email_tool = EmailTool()
        
        # WhatsAppTool: Herramienta custom para enviar mensajes de WhatsApp
        # (usando WhatsApp Business API o servicio como Twilio)
        self.whatsapp_tool = WhatsAppTool()
        
        # GoogleSheetsTool: Herramienta custom para escribir en Google Sheets
        # (usando Google Sheets API para registrar leads)
        self.gsheets_tool = GoogleSheetsTool()

    # ============================================
    # DEFINICIÓN DE AGENTES (AGENTS) EN CREWAI
    # ============================================
    # Los agentes son los "trabajadores" del Crew. Cada uno tiene:
    # - Un ROL específico (ej: comunicador, investigador, coordinador)
    # - HERRAMIENTAS específicas para cumplir su función
    # - Un OBJETIVO y BACKSTORY (definidos en agents.yaml)
    # El decorador @agent registra el método como un agente del Crew.
    
    @agent
    def comunicador_cliente(self) -> Agent:
        """
        AGENTE 1: COMUNICADOR DE CLIENTES
        
        Rol: Responsable de la comunicación directa con los leads
        Función principal: Enviar emails de bienvenida personalizados
        
        Este agente tiene habilidades de:
        - Redacción persuasiva y empática
        - Personalización de mensajes según el perfil del lead
        - Comunicación efectiva para generar confianza inicial
        """
        return Agent(
            # config: Carga la configuración del agente desde agents.yaml
            # (rol, objetivo, backstory, etc.)
            config=self.agents_config['comunicador_cliente'],

            # tools: Herramientas disponibles para este agente
            # Solo tiene acceso a EmailTool (su única función es comunicarse por email)
            tools=[self.email_tool],

            # llm: El modelo de lenguaje que usará este agente para "pensar"
            llm=self.llm,

            # max_iter: Limita las iteraciones del agente para evitar
            # que llame a la herramienta de email múltiples veces
            max_iter=2,

            # verbose: Si es True, imprime los pasos de razonamiento del agente
            # Útil para debugging y entender cómo el agente toma decisiones
            verbose=True
        )

    @agent
    def coordinador_ventas(self) -> Agent:
        """
        AGENTE 2: COORDINADOR DE VENTAS
        
        Rol: Enlace entre los leads nuevos y el equipo de ventas
        Funciones principales:
        - Notificar al equipo de ventas sobre nuevos leads (vía WhatsApp)
        - Registrar leads en Google Sheets para seguimiento y análisis
        
        Este agente tiene habilidades de:
        - Organización y gestión de datos
        - Comunicación interna eficiente
        - Coordinación de procesos de ventas
        """
        return Agent(
            # config: Carga la configuración desde agents.yaml
            config=self.agents_config['coordinador_ventas'],
            
            # tools: Este agente tiene acceso a DOS herramientas:
            # 1. WhatsAppTool: Para notificar al equipo de ventas
            # 2. GoogleSheetsTool: Para registrar los leads en la hoja de cálculo
            # Nota: Puede usar ambas herramientas en la misma tarea
            tools=[self.whatsapp_tool, self.gsheets_tool],
            
            # llm: El cerebro del agente (mismo modelo que los otros agentes)
            llm=self.llm,
            
            # verbose: Activa logs detallados del proceso de razonamiento
            verbose=True
        )
        
    @agent
    def investigador_enriquecimiento(self) -> Agent:
        """
        AGENTE 3: INVESTIGADOR DE ENRIQUECIMIENTO
        
        Rol: Investigador de datos para enriquecer perfiles de leads
        Función principal: Buscar información adicional sobre el lead en internet
        
        Este agente tiene habilidades de:
        - Investigación y recopilación de datos
        - Análisis de información pública (LinkedIn, web corporativa, noticias)
        - Síntesis de datos para crear perfiles completos
        - Identificación de señales de intención de compra
        """
        return Agent(
            # config: Carga la configuración desde agents.yaml
            config=self.agents_config['investigador_enriquecimiento'],
            
            # tools: Solo tiene acceso a WebsiteSearchTool
            # Esta herramienta le permite buscar información en internet
            # (empresa del lead, industria, noticias recientes, presencia digital, etc.)
            tools=[self.website_search_tool],
            
            # llm: El modelo de lenguaje que usará para analizar la información
            llm=self.llm,
            
            # verbose: Muestra el proceso de investigación y razonamiento
            verbose=True
        )

    # ============================================
    # DEFINICIÓN DE TAREAS (TASKS) EN CREWAI
    # ============================================
    # Las tareas son las acciones concretas que ejecutarán los agentes.
    # Cada tarea tiene:
    # - Una DESCRIPCIÓN clara de qué hacer (definida en tasks.yaml)
    # - Un AGENTE asignado para ejecutarla
    # - Opcionalmente, CONTEXTO de otras tareas previas
    # El decorador @task registra el método como una tarea del Crew.
    
    @task
    def enviar_email_bienvenida(self) -> Task:
        """
        TAREA 2: Envío de Email de Bienvenida
        
        Esta tarea se encarga de:
        - Redactar un email personalizado usando el perfil enriquecido del lead
        - Enviar el email de bienvenida al lead
        - Incluir información relevante según el contexto del lead
        
        Nota: Esta tarea se ejecuta DESPUÉS de enriquecer_perfil_lead
        para poder personalizar el mensaje con la información recopilada.
        """
        return Task(
            # config: Carga la descripción de la tarea desde tasks.yaml
            config=self.tasks_config['enviar_email_bienvenida'],
            
            # agent: Asigna esta tarea al "comunicador_cliente"
            # Este agente tiene la herramienta EmailTool para enviar emails
            agent=self.comunicador_cliente(),
            
            # context: Aunque no se especifica explícitamente aquí,
            # esta tarea recibirá implícitamente el output de la tarea anterior
            # (enriquecer_perfil_lead) porque usamos Process.sequential
        )

    @task
    def registrar_lead_en_sheets(self) -> Task:
        """
        TAREA 3: Registro del lead en Google Sheets

        Esta tarea se encarga de:
        - Registrar la información del lead en Google Sheets para seguimiento
        """
        return Task(
            config=self.tasks_config['registrar_lead_en_sheets'],
            agent=self.coordinador_ventas(),
            # tools: Solo Google Sheets para esta tarea, así el agente
            # no puede usar WhatsApp aquí
            tools=[self.gsheets_tool],
            context=[self.enriquecer_perfil_lead()]
        )

    @task
    def notificar_ventas_whatsapp(self) -> Task:
        """
        TAREA 4: Notificación al equipo de ventas por WhatsApp

        Esta tarea se encarga de:
        - Enviar un mensaje de WhatsApp al asesor de ventas con los datos del lead
        """
        return Task(
            config=self.tasks_config['notificar_ventas_whatsapp'],
            agent=self.coordinador_ventas(),
            # tools: Solo WhatsApp para esta tarea
            tools=[self.whatsapp_tool],
            context=[self.enriquecer_perfil_lead()]
        )

    @task
    def enriquecer_perfil_lead(self) -> Task:
        """
        TAREA 1: Enriquecimiento del perfil del lead
        
        Esta tarea investiga información adicional del lead:
        - Busca información en internet sobre la empresa/persona
        - Complementa los datos básicos recibidos del formulario
        - Genera un perfil más completo para personalizar la comunicación
        """
        return Task(
            # config: Carga la configuración desde el archivo YAML
            config=self.tasks_config['enriquecer_perfil_lead'],
            
            # agent: Asigna al "investigador_enriquecimiento"
            # Este agente tiene acceso a WebsiteSearchTool para buscar información
            agent=self.investigador_enriquecimiento(),
            
            # context: No recibe contexto de otras tareas (se ejecuta primero)
            # Es la tarea inicial del flujo
        )

    # ============================================
    # ENSAMBLAJE DEL CREW COMPLETO
    # ============================================
    # El decorador @crew marca este método como el ensamblador final
    # que une todos los agentes y tareas en un Crew funcional.
    
    @crew
    def crew(self) -> Crew:
        """
        CONFIGURACIÓN Y ENSAMBLAJE DEL CREW
        
        Este método crea el Crew completo conectando:
        - Todos los agentes definidos arriba
        - Todas las tareas en el orden correcto
        - El proceso de ejecución (secuencial en este caso)
        
        FLUJO DE EJECUCIÓN:
        1. enriquecer_perfil_lead() → Investiga al lead
        2. enviar_email_bienvenida() → Envía email personalizado
        3. notificar_ventas_y_registrar() → Notifica equipo y registra
        """
        return Crew(
            agents=self.agents,

            tasks=[
                self.enriquecer_perfil_lead(),       # 1º: Investigar y enriquecer
                self.enviar_email_bienvenida(),      # 2º: Enviar email al lead
                self.registrar_lead_en_sheets(),     # 3º: Registrar en Google Sheets
                self.notificar_ventas_whatsapp()     # 4º: Notificar por WhatsApp
            ],

            process=Process.sequential,
            verbose=True
        )