from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type
from duckduckgo_search import DDGS


class InternetSearchToolInput(BaseModel):
    """Define qué parámetros recibe la herramienta."""
    query: str = Field(..., description="La consulta de búsqueda para encontrar información en internet.")


class InternetSearchTool(BaseTool):
    name: str = "Búsqueda en Internet"
    description: str = (
        "Herramienta para buscar información actualizada en internet sobre destinos turísticos, "
        "restaurantes, atracciones, vuelos, alojamiento y cualquier otro dato relacionado con viajes. "
        "Proporciona resultados actualizados y relevantes."
    )
    args_schema: Type[BaseModel] = InternetSearchToolInput

    def _run(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

                if not results:
                    return f"No se encontraron resultados para: {query}"

                formatted_results = []
                for idx, result in enumerate(results, 1):
                    title = result.get('title', 'Sin título')
                    body = result.get('body', 'Sin descripción')
                    href = result.get('href', '')

                    formatted_results.append(
                        f"{idx}. {title}\n"
                        f"   {body}\n"
                        f"   Fuente: {href}\n"
                    )

                return "\n".join(formatted_results)

        except Exception as e:
            return f"Error al realizar la búsqueda: {str(e)}"
