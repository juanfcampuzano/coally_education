from .base_rag_agent import BaseRagAgent
from pydantic import BaseModel
from typing import List
from models.course import CourseModel

class SpecificDomainRagOutputModel(BaseModel):
    specific_domain_skills_courses: List[CourseModel]

class SpecificDomainSkillsRagAgent(BaseRagAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - HABILIDADES DE DOMINIO ESPECÍFICO QUE LE FALTAN A LA PERSONA: {topics}

        Y haciendo uso de los siguientes cursos:

        {context}

        ---------------------------------------

        Tu tarea es extraer cursos en español online para cada una de estas habilidades de dominio específico. Solo puedes agregar habilidades que estén dentro
        de la lista de habilidades que la persona necesita. Si un curso no es apropiado, no lo agregues. Intenta elegir 1 curso por habilidad, el más apropiado.
        Usa los de youtube solo si no existe uno apropiado de otra fuente, pero prioriza las de otras fuentes.

        La salida debe mantener el siguiente formato JSON:

        {{
            "type": "object",
            "properties": {{
                "specific_domain_skills_courses": {{
                    "type": "array",
                    "items": {{
                        "type":"object",
                        "properties":{{
                            "title":{{
                                "type":"string"
                            }},
                            "description":{{
                                "type":"string"
                            }},
                            "url":{{
                                "type":"string"
                            }}
                        }}
                    }}
                }}
            }},
            "required":["specific_domain_skills_courses"]
        }}

        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES DEL DOMINIO ESPECÍFICO: Las habilidades de dominio específico son conocimientos y competencias especializadas en un campo o sector particular, 
        como finanzas, salud, o tecnología, que son esenciales para desempeñarse eficazmente en roles dentro de esa área.

        Debes:

        1. Buscar habilidad por habilidad un curso en español referente a cada habilidad blanda, que le permita a la persona obtener esta habilidad.
        2. La salida será la lista de cursos en el formato anterior

        -----------------------------------------
        EJEMPLO 1:

        La persona requiere habilidades blandas confianza y paciencia.

        En este caso la salida debe ser:

        {{
            "specific_domain_skills_courses": [{{"title":"Confianza indestructible en 30 días", "description":"Una confianza autentica es el fundamento para tomar decisiones inteligentes, construir relaciones fuertes y comportamientos que nos acerquen a los resultados personales que queremos obtener en nuestra vida personal y profesional. Sin tener las bases de una confianza genuina en nosotros mismos, construimos nuestras vidas en fundamentos bastante débiles sin ni siquiera darnos cuenta. Esto nos lleva a tener problemas de autoestima, valor propio y nos impide crear comunicaciones de valor con otros. Confianza Indestructible te llevara a un extenso viaje de auto-descubrimiento donde el cual podrás entender quien eres en realidad. También te permitirá entenderte a ti mismo, tus creencias, como tomar control de tus emociones y como construir una autoestima lo suficientemente fuerte y versátil en cada área de tu vida.", "url":"https://www.udemy.com/course/como-aumentar-mi-autoestima-desarrollo-personal-autoayuda/"}},
            {{"title":"¿Cómo desarrollar la paciencia? | Isaac Palomares", "description":"En este curso obtendrás 5 consejos para tener más paciencia, con la ayuda del psicólogo Isaac Palomares", "url":"https://www.youtube.com/watch?v=rYryqHW-zGE&pp=ygUSY3Vyc28gZGUgcGFjaWVjbmlh"}}]
        }}

        """
        super().__init__(template=template, response_format=SpecificDomainRagOutputModel)