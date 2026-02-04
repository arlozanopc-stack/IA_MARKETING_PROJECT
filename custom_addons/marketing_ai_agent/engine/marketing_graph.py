from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
project_root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(project_root_env)

# Definimos el estado del grafo
class AgentState(TypedDict):
    question: str
    context: str
    answer: str

# Configuración de la DB Vectorial
persist_directory = os.path.expanduser("~/IA_Marketing_Project/chroma_db")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_db = Chroma(
    persist_directory=persist_directory, 
    embedding_function=embeddings,
    collection_name="marketing_strategies"
)

# NODO 1: Recuperación
def retrieve_knowledge(state: AgentState):
    query = state["question"]
    docs = vector_db.similarity_search(query, k=2)
    context = "\n".join([d.page_content for d in docs])
    return {"context": context}

# NODO 2: Generación
def generate_response(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = f"""Basado en la siguiente estrategia de marketing:
    {state['context']}
    Responde a la pregunta: {state['question']}"""
    
    response = llm.invoke(prompt)
    return {"answer": response.content}

# Construcción del Grafo
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_knowledge)
workflow.add_node("generate", generate_response)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

marketing_ai = workflow.compile()