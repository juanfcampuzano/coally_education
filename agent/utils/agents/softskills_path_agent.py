from .base_agent import BaseAgent
from pydantic import BaseModel
from typing import List

class SoftSkillsOutputModel(BaseModel):
    missing_soft_skills: List[str]

class SoftSkillsPathAgent(BaseAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - ROL DESEADO DE LA PERSONA: {role_input}
        - HABILIDADES BLANDAS ACTUALES DE LA PERSONA: {current_softskills}

        Tu tarea es extraer las habilidades blandas que la persona le hace falta aprender para llegar a ejercer su rol deseado, teniendo en cuenta las que ya tiene.

        La salida debe mantener el siguiente formato JSON:

        {{
            "type": "object",
            "properties": {{
                "missing_soft_skills": {{
                    "type": "array",
                    "items": {{
                        "type":"string"
                    }}
                }}
            }},
            "required":["missing_soft_skills"]
        }}

        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES BLANDAS: Las habilidades blandas son capacidades interpersonales y sociales que facilitan la interacción efectiva con los demás,
        como la comunicación, el trabajo en equipo, la empatía y la resolución de conflictos.

        Debes:

        1. Sacar un listado con las habilidades blandas que se necesitan para ser el rol de la persona
        2. Revisar cuales la persona posee
        3. La salida será las que le hagan falta

        -----------------------------------------
        EJEMPLO 1:

        La persona quiere ser profesor de escuela y tiene habilidades blandas comunicación y paciencia.

        En este caso la salida debe ser:

        {{
            "missing_soft_skills": ["Empatía", "Resolución de conflictos", "Creatividad", "Adaptabilidad", "Gestión del tiempo", "Trabajo en equipo"]
        }}
        Nota que no incluí comunicación y paciencia porque a pesar de que son requisitos, la persona ya los cumple.
        """
        super().__init__(template=template, response_format=SoftSkillsOutputModel)