# Backend OpenAI - Comandos

# 1) Instalar dependencias
uv sync

# 2) Levantar el backend (puerto 8006 para correrlo en paralelo al de Llama, que usa el 8005)
uv run uvicorn src.backend_landing_de_ventas_openai.main:app --host 0.0.0.0 --port 8006 --reload

# Endpoint de prueba:  http://127.0.0.1:8006
# Docs (Swagger):      http://127.0.0.1:8006/docs
