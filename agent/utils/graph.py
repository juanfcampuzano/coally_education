from langgraph.graph import StateGraph, START, END
from agent.utils.llm_nodes import *
from models.hard_skills import HardSkillsState
from models.hard_skills_output import HardSkillsOutputModel
from models.soft_skills import SoftSkillsState
from models.soft_skills_output import SoftSkillsOutputModel
from models.specific_domain_output import SpecificDomainOutputModel
from models.specific_domain_skills import SpecificDomainSkillsState
from models.parent import ParentState
from .mongo.mongodb_checkpointer import MongoDBSaver
import os

def build_graph():

    # HARDSKILLS GRAPH

    hardskills_graph = StateGraph(input=HardSkillsState, output=HardSkillsOutputModel)
    hardskills_graph.add_node('hardskills_path_node', lambda state: hardskills_path_node(state))
    hardskills_graph.add_node('hardskills_rag_node', lambda state: hardskills_rag_node(state))

    hardskills_graph.add_edge(START, 'hardskills_path_node')
    hardskills_graph.add_edge('hardskills_path_node', 'hardskills_rag_node')
    hardskills_graph.add_edge('hardskills_rag_node', END)

    # SOFTSKILLS GRAPH

    softskills_graph = StateGraph(input=SoftSkillsState, output=SoftSkillsOutputModel)
    softskills_graph.add_node('softskills_path_node', lambda state: softskills_path_node(state))
    softskills_graph.add_node('softskills_rag_node', lambda state: softskills_rag_node(state))

    softskills_graph.add_edge(START, 'softskills_path_node')
    softskills_graph.add_edge('softskills_path_node', 'softskills_rag_node')
    softskills_graph.add_edge('softskills_rag_node', END)

    # SPECIFIC DOMAIN GRAPH

    specific_domain_graph = StateGraph(input=SpecificDomainSkillsState, output=SpecificDomainOutputModel)
    specific_domain_graph.add_node('specific_domain_path_node', lambda state: specific_domain_path_node(state))
    specific_domain_graph.add_node('specific_domain_rag_node', lambda state: specific_domain_rag_node(state))

    specific_domain_graph.add_edge(START, 'specific_domain_path_node')
    specific_domain_graph.add_edge('specific_domain_path_node', 'specific_domain_rag_node')
    specific_domain_graph.add_edge('specific_domain_rag_node', END)

    # MAIN GRAPH
    import pymongo

    main_graph = StateGraph(ParentState)
    main_graph.add_node('current_skills_node', lambda state: current_skills_node(state))
    main_graph.add_node('softskills_graph', softskills_graph.compile())
    main_graph.add_node('hardskills_graph', hardskills_graph.compile())
    main_graph.add_node('specific_domain_graph', specific_domain_graph.compile())
    main_graph.add_node('output_formatter_node', lambda state: output_formatter_node(state))

    main_graph.add_edge(START, 'current_skills_node')
    main_graph.add_edge('current_skills_node', 'softskills_graph')
    main_graph.add_edge('current_skills_node', 'hardskills_graph')
    main_graph.add_edge('current_skills_node', 'specific_domain_graph')
    main_graph.add_edge(['softskills_graph','hardskills_graph','specific_domain_graph'], 'output_formatter_node')
    main_graph.add_edge('output_formatter_node', END)

    checkpointer = MongoDBSaver( client=pymongo.MongoClient(os.getenv("MONGO_URI")), db_name=os.getenv("EMBEDDINGS_DB_NAME"))

    graph = main_graph.compile(checkpointer=checkpointer)

    return graph

graph = build_graph()