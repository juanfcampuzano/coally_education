from .base_agent import BaseAgent
from pydantic import BaseModel
from typing import List

class HardSkillsOutputModel(BaseModel):
    missing_hard_skills: List[str]

class HardSkillsPathAgent(BaseAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - ROL DESEADO DE LA PERSONA: {role_input}
        - HABILIDADES TÉCNICAS ACTUALES DE LA PERSONA: {current_hardskills}

        Tu tarea es extraer las habilidades técnicas que la persona le hace falta aprender para llegar a ejercer su rol deseado, teniendo en cuenta las que ya tiene.

        La salida debe mantener el siguiente formato JSON:

        {{
            "type": "object",
            "properties": {{
                "missing_hard_skills": {{
                    "type": "array",
                    "items": {{
                        "type":"string"
                    }}
                }}
            }},
            "required":["missing_hard_skills"]
        }}

        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES TÉCNICAS: Las habilidades técnicas son competencias específicas y prácticas que se requieren para realizar tareas en campos especializados, 
        como el uso de herramientas, software, o conocimientos en programación, análisis de datos, ingeniería, entre otros.

        Debes:

        1. Sacar un listado con las habilidades técnicas que se necesitan para ser el rol de la persona
        2. Revisar cuales la persona posee
        3. La salida será las que le hagan falta

        -----------------------------------------
        EJEMPLO 1:

        La persona quiere ser desarrollador de Machine Learning, conoce python y sabe de algoritmos.

        En este caso la salida debe ser:

        {{
            "missing_hard_skills":["Tensorflow","Deep Learning","POO","Estadística","Optimización","MLOps"]
        }}

        Nota que no incluí python y algoritmos porque a pesar de que son requisitos, la persona ya los cumple.
        """
        super().__init__(template=template, response_format=HardSkillsOutputModel)