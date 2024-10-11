from typing import TypedDict, List
from .skills import SkillsModel
from .course import CourseModel

class SoftSkillsState(TypedDict):
    role_input: str
    sector_input: str
    current_resume: dict
    current_skills: SkillsModel
    soft_skills_courses: List[CourseModel]
    missing_soft_skills: List[str]