from .skills import SkillsModel
from typing import TypedDict, List
from .course import CourseModel
from .output import OutputModel

class ParentState(TypedDict):
    role_input: str
    sector_input: str
    current_resume: dict

    current_skills: SkillsModel
 
    soft_skills_courses: List[CourseModel]
    hard_skills_courses: List[CourseModel]
    specific_domain_skills_courses: List[CourseModel]

    output: OutputModel