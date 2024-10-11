from pydantic import BaseModel
from .course import CourseModel
from typing import List

class SoftSkillsOutputModel(BaseModel):
    soft_skills_courses: List[CourseModel]