from pydantic import BaseModel
from typing import List
from .course import CourseModel

class OutputModel(BaseModel):
    soft_skills_courses: List[CourseModel]
    hard_skills_courses: List[CourseModel]
    specific_domain_skills_courses: List[CourseModel]