conda activate CrewAI-Landing-de-Ventas

crewai create crew backend_landing_de_ventas

474.1 GB
480.35 GB

uvicorn src.backend_landing_de_ventas.main:app --host 0.0.0.0 --port 8005 --reload

uvicorn src.backend_landing_de_ventas_openai.main:app --host 0.0.0.0 --port 8005


(CrewAI-Landing-de-Ventas) kevininofuente@MacBook-Pro-de-Kevin Proyecto-No-Conversacional-LandingPage-de-Ventas-Ollama % crewai create crew backend_landing_de_ventas
Creating folder backend_landing_de_ventas...
Cache expired or not found. Fetching provider data from the web...
Downloading  [####################################]  1353950/68707
Select a provider to set up:
1. openai
2. anthropic
3. gemini
4. nvidia_nim
5. groq
6. huggingface
7. ollama
8. watson
9. bedrock
10. azure
11. cerebras
12. sambanova
13. other
q. Quit
Enter the number of your choice or 'q' to quit: 7
Select a model to use for Ollama:
1. ollama/llama3.1
2. ollama/mixtral
q. Quit
Enter the number of your choice or 'q' to quit: 1
API keys and model saved to .env file
Selected model: ollama/llama3.1
  - Created backend_landing_de_ventas/.gitignore
  - Created backend_landing_de_ventas/pyproject.toml
  - Created backend_landing_de_ventas/README.md
  - Created backend_landing_de_ventas/knowledge/user_preference.txt
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/__init__.py
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/main.py
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/crew.py
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/tools/custom_tool.py
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/tools/__init__.py
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/config/agents.yaml
  - Created backend_landing_de_ventas/src/backend_landing_de_ventas/config/tasks.yaml
Crew backend_landing_de_ventas created successfully!
