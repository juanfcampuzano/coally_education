from typing import TypedDict, List
from .skills import SkillsModel
from .course import CourseModel

class SpecificDomainSkillsState(TypedDict):
    role_input: str
    sector_input: str
    current_resume: dict
    current_skills: SkillsModel
    specific_domain_skills_courses: List[CourseModel]
    missing_specific_domain_skills: List[str]