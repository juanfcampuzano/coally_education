from .base_agent import BaseAgent
from pydantic import BaseModel
from typing import List
from models.skills import SkillsModel

class CurrentSkillsOutputModel(BaseModel):
    current_skills: SkillsModel

class CurrentSkillsAgent(BaseAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - HOJA DE VIDA DE LA PERSONA {current_resume}

        Extrae las habilidades técnicas, blandas y del dominio específico que la persona tiene.

        La salida debe mantener el siguiente formato JSON:

        {{
            "description": "Objeto que contiene las habilidades actuales de una persona, organizadas en tres categorías: habilidades técnicas (hard skills), habilidades blandas (soft skills) y habilidades específicas de dominio (specific domain skills).",
            "type": "object",
            "properties": {{
                "current_skills": {{
                "description": "Categoría que agrupa las habilidades actuales de la persona.",
                "type": "object",
                "properties": {{
                    "hard_skills": {{
                    "description": "Lista de habilidades técnicas (conocimientos prácticos o técnicos).",
                    "type": "array",
                    "items": {{
                        "type": "string",
                        "description": "Una habilidad técnica específica."
                    }},
                    "example": ["Hardskill 1", "Hardskill 2"]
                    }},
                    "soft_skills": {{
                    "description": "Lista de habilidades blandas (interpersonales o sociales).",
                    "type": "array",
                    "items": {{
                        "type": "string",
                        "description": "Una habilidad blanda específica."
                    }},
                    "example": ["Softskill 1", "Softskill 2"]
                    }},
                    "specific_domain_skills": {{
                    "description": "Lista de habilidades específicas para un dominio particular (sector o industria).",
                    "type": "array",
                    "items": {{
                        "type": "string",
                        "description": "Una habilidad específica de dominio."
                    }},
                    "example": ["Specific Domain Skill 1", "Specific Domain Skill 2"]
                    }}
                }},
                "required": ["hard_skills", "soft_skills", "specific_domain_skills"]
                }}
            }},
            "required": ["current_skills"]
        }}


        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES TÉCNICAS: Las habilidades técnicas son competencias específicas y prácticas que se requieren para realizar tareas en campos especializados, 
        como el uso de herramientas, software, o conocimientos en programación, análisis de datos, ingeniería, entre otros.

        HABILIDADES BLANDAS: Las habilidades blandas son capacidades interpersonales y sociales que facilitan la interacción efectiva con los demás,
        como la comunicación, el trabajo en equipo, la empatía y la resolución de conflictos.

        HABILIDADES DEL DOMINIO ESPECÍFICO: Las habilidades de dominio específico son conocimientos y competencias especializadas en un campo o sector particular, 
        como finanzas, salud, o tecnología, que son esenciales para desempeñarse eficazmente en roles dentro de esa área.

        -----------------------------------------

        EJEMPLO 1:

        La persona sabe Python, Scikit-Learn y es bueno para comunicarse en público, ha trabajado en el sector de Finanzas en el área de análisis crediticio y tiene 7 años
        de experiencia como desarrollador backend.

        En este caso la salida debe ser:

        {{
            "current_skills":
                {{
                "hard_skills":["Python", "Scikit-Learn", "Desarrollo backend"], 
                "soft_skills":["Hablar en público"], 
                "specific_domain_skills":["Finanzas", "Análisis crediticio"]
                }}
        }}
        """
        super().__init__(template=template, response_format=CurrentSkillsOutputModel)