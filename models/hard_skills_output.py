from pydantic import BaseModel
from .course import CourseModel
from typing import List

class HardSkillsOutputModel(BaseModel):
    hard_skills_courses: List[CourseModel]