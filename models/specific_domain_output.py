from pydantic import BaseModel
from .course import CourseModel
from typing import List

class SpecificDomainOutputModel(BaseModel):
    specific_domain_skills_courses: List[CourseModel]