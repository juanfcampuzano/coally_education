from pydantic import BaseModel
from typing import List


class SkillsModel(BaseModel):
    hard_skills: List[str]
    soft_skills: List[str]
    specific_domain_skills: List[str]