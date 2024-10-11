from .base_agent import BaseAgent
from pydantic import BaseModel
from typing import List

class SpecificDomainSkillsOutputModel(BaseModel):
    missing_specific_domain_skills: List[str]

class SpecificDomainPathAgent(BaseAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - ROL DESEADO DE LA PERSONA: {role_input}
        - SECTOR / DOMINIO DESEADO DE LA PERSONA: {sector_input}
        - HABILIDADES DE DOMINIO ESPECÍFICO ACTUALES DE LA PERSONA: {current_specificdomain_skills}

        Tu tarea es extraer las habilidades de dominio específico (sector que la persona quiere ejercer) que la persona le hace falta aprender para llegar a ejercer su rol deseado, teniendo en cuenta las que ya tiene.

        La salida debe mantener el siguiente formato JSON:

        {{
            "type": "object",
            "properties": {{
                "missing_specific_domain_skills": {{
                    "type": "array",
                    "items": {{
                        "type":"string"
                    }}
                }}
            }},
            "required":["missing_specific_domain_skills"]
        }}

        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES DEL DOMINIO ESPECÍFICO: Las habilidades de dominio específico son conocimientos y competencias especializadas en un campo o sector particular, 
        como finanzas, salud, o tecnología, que son esenciales para desempeñarse eficazmente en roles dentro de esa área.

        Debes:

        1. Sacar un listado con las habilidades de dominio que se necesitan para ser el rol de la persona en el sector particular.
        2. Revisar cuales habilidades la persona posee
        3. La salida será las que le hagan falta

        -----------------------------------------
        EJEMPLO 1:

        La persona quiere ser desarrollador de Machine Learning en el sector de recursos humanos, conoce el funcionamiento de plataformas de reclutamiento.

        En este caso la salida debe ser:

        {{
        "missing_domain_skills": ["Analítica de datos en recursos humanos", "Sistemas de gestión del talento", "Predicción de rotación de personal", "Análisis de desempeño", "Compensaciones y beneficios", "Evaluaciones de clima laboral"]
        }}

        Nota que no incluí el funcionamiento de plataformas de reclutamiento porque a pesar de que son requisitos, la persona ya los cumple.
        """
        super().__init__(template=template, response_format=SpecificDomainSkillsOutputModel)