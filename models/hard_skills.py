from typing import TypedDict, List
from .skills import SkillsModel
from .course import CourseModel

class HardSkillsState(TypedDict):
    role_input: str
    sector_input: str
    current_resume: dict
    current_skills: SkillsModel
    hard_skills_courses: List[CourseModel]
    missing_hard_skills: List[str]
