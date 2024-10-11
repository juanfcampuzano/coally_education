import json
from .agents.current_skills_agent import CurrentSkillsAgent
from .agents.hardskills_path_agent import HardSkillsPathAgent
from .agents.hardskills_rag_agent import HardSkillsRagAgent
from .agents.softskills_path_agent import SoftSkillsPathAgent
from .agents.softskills_rag_agent import SoftSkillsRagAgent
from .agents.specific_domain_skills_agent import SpecificDomainPathAgent
from .agents.specific_domain_skills_rag_agent import SpecificDomainSkillsRagAgent

def current_skills_node(state):
    current_skills_generator = CurrentSkillsAgent()

    inputs = {
        "current_resume":state.get("current_resume")
    }

    result = current_skills_generator.run(inputs)

    return json.loads(result)

def softskills_path_node(state):
    softskills_path_creator = SoftSkillsPathAgent()

    inputs = {
        "role_input":state.get("role_input"),
        "current_softskills": state.get("current_skills", {}).get("soft_skills", [])
    }

    result = softskills_path_creator.run(inputs)

    return json.loads(result)

def hardskills_path_node(state):
    hardskills_path_creator = HardSkillsPathAgent()

    inputs = {
        "role_input":state.get("role_input"),
        "current_hardskills": state.get("current_skills", {}).get("hard_skills", [])
    }

    result = hardskills_path_creator.run(inputs)

    return json.loads(result)

def specific_domain_path_node(state):
    specific_domain_path_creator = SpecificDomainPathAgent()

    inputs = {
        "role_input":state.get("role_input"),
        "current_specificdomain_skills": state.get("current_skills", {}).get("specific_domain_skills", []),
        "sector_input":state.get("sector_input")
    }

    result = specific_domain_path_creator.run(inputs)

    return json.loads(result)

def softskills_rag_node(state):
    soft_skills_rag_creator = SoftSkillsRagAgent()

    inputs = {
        "topics":state.get("missing_soft_skills")
    }

    result = soft_skills_rag_creator.run(inputs)

    return json.loads(result)

def hardskills_rag_node(state):
    hard_skills_rag_creator = HardSkillsRagAgent()

    inputs = {
        "topics":state.get("missing_hard_skills")
    }

    result = hard_skills_rag_creator.run(inputs)

    return json.loads(result)

def specific_domain_rag_node(state):
    domain_skills_rag_creator = SpecificDomainSkillsRagAgent()

    inputs = {
        "topics":state.get("missing_specific_domain_skills")
    }

    result = domain_skills_rag_creator.run(inputs)

    return json.loads(result)

def output_formatter_node(state):
    return { "output":{

                "soft_skills_courses":state.get("soft_skills_courses"),
                "hard_skills_courses":state.get("hard_skills_courses"),
                "specific_domain_skills_courses":state.get("specific_domain_skills_courses")
            }
    }