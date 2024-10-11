from .base_rag_agent import BaseRagAgent
from pydantic import BaseModel
from typing import List
from models.course import CourseModel

class HardSkillsRagOutputModel(BaseModel):
    hard_skills_courses: List[CourseModel]

class HardSkillsRagAgent(BaseRagAgent):
    def __init__(self):
        template = """
        Con la siguiente información:
        - HABILIDADES TÉCNICAS QUE LE FALTAN A LA PERSONA: {topics}

        Y haciendo uso de los siguientes cursos:

        {context}

        ---------------------------------------

        Tu tarea es extraer cursos en español online para cada una de estas habilidades técnicas. Solo puedes agregar habilidades que estén dentro
        de la lista de habilidades que la persona necesita. Si un curso no es apropiado, no lo agregues. Intenta elegir 1 curso por habilidad, el más apropiado.
        Usa los de youtube solo si no existe uno apropiado de otra fuente, pero prioriza las de otras fuentes.

        La salida debe mantener el siguiente formato JSON:

        {{
            "type": "object",
            "properties": {{
                "hard_skills_courses": {{
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
            "required":["hard_skills_courses"]
        }}

        -----------------------------------------

        Para darte más contexto te doy las siguientes definiciones:

        HABILIDADES TÉCNICAS: Las habilidades técnicas son competencias específicas y prácticas que se requieren para realizar tareas en campos especializados, 
        como el uso de herramientas, software, o conocimientos en programación, análisis de datos, ingeniería, entre otros.

        Debes:

        1. Buscar habilidad por habilidad un curso en español referente a cada habilidad blanda, que le permita a la persona obtener esta habilidad.
        2. La salida será la lista de cursos en el formato anterior

        -----------------------------------------
        EJEMPLO 1:

        La persona requiere habilidades blandas confianza y paciencia.

        En este caso la salida debe ser:

        {{
            "hard_skills_courses": [
                {{
                    "title": "Introducción a Python para Ciencia de Datos",
                    "description": "Este curso cubre los fundamentos de Python con un enfoque en la ciencia de datos. Aprenderás a manejar estructuras de datos, realizar análisis estadísticos básicos y trabajar con librerías populares como NumPy, pandas y Matplotlib para visualizar datos.",
                    "url": "https://www.coursera.org/learn/python-data-science"
                }},
                {{
                    "title": "Fundamentos de Machine Learning",
                    "description": "En este curso, explorarás los conceptos clave del machine learning, incluyendo algoritmos supervisados y no supervisados, preparación de datos y evaluación de modelos. Utilizarás Python y Scikit-Learn para aplicar estos conocimientos en proyectos prácticos.",
                    "url": "https://www.udemy.com/course/machine-learning-python/"
                }},
                {{
                    "title": "Certificación de Desarrollador Web Full Stack",
                    "description": "Este curso te guiará a través del desarrollo de aplicaciones web desde cero. Aprenderás HTML, CSS, JavaScript, Node.js y React, así como la creación de bases de datos con MongoDB para construir aplicaciones web completas.",
                    "url": "https://www.freecodecamp.org/learn/"
                }}
            ]
        }}

        """
        super().__init__(template=template, response_format=HardSkillsRagOutputModel)