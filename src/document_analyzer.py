import threading
import asyncio
from typing import Literal
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langchain.tools import tool
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerativeModel
import vertexai
import json
from .database import (
    update_document_analysis, 
    get_document, 
    extract_file_text, 
    update_document_status
)
import aiosqlite
import io
from .utils.logger import setup_logger

# Initialize Vertex AI
PROJECT_ID = "gen-lang-client-0550928658"
LOCATION = "us-east1"
STAGING_BUCKET = "gs://gen-lang-client-staging-bucket"
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Create logger for this file
logger = setup_logger('document_analyzer')

class UsefulInformation(BaseModel):
    parties_involved: list[str] = Field(description="A list of only the names of the parties involved in the contract")
    effective_dates: list[str] = Field(description="A list containing only the effective start and end dates of the contract")
    renewal_terms: list[str] = Field(description="A list of all renewal terms mentioned in the contract")
    compliance_requirements: list[str] = Field(description="A list of all compliance requirements mentioned in the document")

async def extract_information(text_content: str, doc_id: int) -> UsefulInformation:
    prompt = f"""
    The text below is an excerpt from a service contract. Extract specific information and return it in JSON format.
    
    CRITICAL INSTRUCTIONS:
    1. AVOID DUPLICATES: Never include duplicate items in any list.
    2. BE CONCISE: Keep each item brief and to the point.
    3. VALIDATE: Each piece of information must be explicitly stated in the text; do not make assumptions.
    4. FORMAT: Return output as a valid JSON object, ensuring all fields are lists (even if empty or single item).
    5. CALCULATE DATES: If a date is mentioned, calculate the exact start and end dates based on the context and include it in the response.
    
    JSON Response Format:
    {{
        "parties_involved": ["Service Provider", "Client"],
        "effective_dates": ["03/15/2024", "03/15/2025"],
        "renewal_terms": ["03/15/2025", "03/15/2026"],
        "compliance_requirements": ["Licensee shall comply with SOC 2 Type II requirements, GDPR compliance required for EU data handling"]
    }}

    Text from the service contract:
    {text_content}
    """

    try:
        model = GenerativeModel("gemini-1.5-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        cleaned_response = response.text.strip("```json").strip("```").strip()
        structured_data = json.loads(cleaned_response)
        info = UsefulInformation.model_validate(structured_data)

        # Update status using new function
        await update_document_status(doc_id, 2)

        return info
    except Exception as e:
        print(f"Error in information extraction: {str(e)}")
        return UsefulInformation(
            parties_involved=[],
            effective_dates=[],
            renewal_terms=[],
            compliance_requirements=[]
        )

# Compliance Check Tools
@tool
def check_compliance(doc_id: int) -> str:
    """Check whether the system is compliant or not"""
    return "is compliant" if doc_id % 2 == 0 else "is not compliant"

@tool
def check_risk(doc_id: int) -> str:
    """Analyze the risk level of the system"""
    return "low" if doc_id % 2 == 0 else "high"

@tool
def check_renewal(doc_id: int) -> str:
    """Track the renewal of the system"""
    return "renewal required" if doc_id % 2 == 0 else "renewal not required"

class State(MessagesState):
    next: str

def setup_analysis_graph():
    llm = ChatVertexAI(model_name='gemini-1.5-pro')
    
    compliance_agent = create_react_agent(llm, tools=[check_compliance], 
                                        prompt="You are a compliance checking agent. Return the exact text returned by the tool, which is 'is compliant' or 'is not compliant'.")
    risk_agent = create_react_agent(llm, tools=[check_risk], 
                                  prompt="You are a risk analyst agent. Return the exact text returned by the tool, which is 'low' or 'high'.")
    renewal_agent = create_react_agent(llm, tools=[check_renewal], 
                                     prompt="You are a renewal tracking agent. Return the exact text returned by the tool, which is 'renewal required' or 'renewal not required'.")

    def compliance_node(state: State) -> Command[Literal["risk_node"]]:
        result = compliance_agent.invoke(state)
        return Command(
            update={"messages": [HumanMessage(content=result["messages"][-1].content, 
                                            name="compliance_node")]},
            goto="risk_node",
        )

    def risk_node(state: State) -> Command[Literal["renewal_node"]]:
        result = risk_agent.invoke(state)
        return Command(
            update={"messages": [HumanMessage(content=result["messages"][-1].content, 
                                            name="risk_node")]},
            goto="renewal_node",
        )

    def renewal_node(state: State) -> Command[Literal[END]]:
        result = renewal_agent.invoke(state)
        return Command(
            update={"messages": [HumanMessage(content=result["messages"][-1].content, 
                                            name="renewal_node")]},
            goto=END,
        )

    builder = StateGraph(State)
    builder.add_edge(START, "compliance_node")
    builder.add_node("compliance_node", compliance_node)
    builder.add_node("risk_node", risk_node)
    builder.add_node("renewal_node", renewal_node)
    return builder.compile()

async def summarize(text_content: str, doc_id: int) -> str:
    prompt = f"""
    The text below is an excerpt from a service contract. Summarize the important information from the contract into 1 paragraph.
    
    CRITICAL INSTRUCTIONS:
    1. AVOID DUPLICATES: Never include duplicate items.
    2. BE CONCISE: Keep each line brief and to the point.
    3. VALIDATE: Each piece of information must be explicitly stated in the text; do not make assumptions.
    4. FORMAT: Return output as a String.
    5. INCLUDE: Include but not limited to Parties involved, effective dates, renewal terms, compliance requirements, and cost.
    

    Text from the service contract:
    {text_content}
    """

    try:
        model = GenerativeModel("gemini-1.5-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        summary = response.text

        # Update status using new function
        await update_document_status(doc_id, 3)

        return summary
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return "No summary"

async def potential_risk_finder(text_content: str, doc_id: int) -> str:
    prompt = f"""
    The text below is an excerpt from a service contract. Identify the potential risks from the contract into 1 paragraph.
    
    CRITICAL INSTRUCTIONS:
    1. AVOID DUPLICATES: Never include duplicate items.
    2. BE CONCISE: Keep each line brief and to the point.
    3. ASSUMPTIONS: You may make any and all assumptions about the potential risks in this contract.
    4. FORMAT: Return output as a String.
    5. EXPLANATION: Along with each identified risk, include an extremely brief explanation of why this may be a risk.
    6. SEPARATE: Separate each risk with a new line.
    7. FORMATTING: DO NOT include any special characters in the response. Only newline character is allowed.

    Text from the service contract:
    {text_content}
    """

    try:
        model = GenerativeModel("gemini-1.5-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        risks = response.text

        # Update status using new function
        await update_document_status(doc_id, 4)

        return risks
    except Exception as e:
        print(f"Error in risk finding: {str(e)}")
        return "No risks identified"

async def analyze_document(doc_id: int):
    """Analyze document content in a background thread"""
    def analysis_worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def process_document():
                logger.info(f"Starting analysis for document {doc_id}")
                
                # First extract text from PDF (Status 1)
                if not await extract_file_text(doc_id):
                    logger.error(f"Failed to extract text from document {doc_id}")
                    return
                
                # Get document with extracted text
                doc = await get_document(doc_id)
                if not doc or not doc[7]:
                    logger.error(f"Document {doc_id} not found or has no text content")
                    return
                
                text_content = doc[7]
                logger.info(f"Successfully extracted text from document {doc_id}")
                
                # Extract information (Status 2)
                logger.info(f"Starting information extraction for document {doc_id}")
                info = await extract_information(text_content, doc_id)
                logger.info(f"Completed information extraction for document {doc_id}")
                
                # Generate summary (Status 3)
                logger.info(f"Starting summary generation for document {doc_id}")
                contract_summary = await summarize(text_content, doc_id)
                logger.info(f"Completed summary generation for document {doc_id}")
                
                # Risk analysis (Status 4)
                logger.info(f"Starting risk analysis for document {doc_id}")
                potential_risks = await potential_risk_finder(text_content, doc_id)
                logger.info(f"Completed risk analysis for document {doc_id}")
                
                # Run compliance, risk, and renewal analysis
                logger.info(f"Starting final analysis for document {doc_id}")
                graph = setup_analysis_graph()
                results = graph.invoke({
                    "messages": [HumanMessage(content=f"doc_id: {doc_id}")]
                })
                
                # Process results
                compliance_result = any("is compliant" in msg.content for msg in results["messages"])
                risk_result = next((msg.content for msg in results["messages"] if "risk_node" == msg.name), "low")
                renewal_result = next((msg.content for msg in results["messages"] if "renewal_node" == msg.name), "pending")
                
                # Final update with all results (Status 5)
                logger.info(f"Updating final results for document {doc_id}")
                await update_document_analysis(
                    doc_id=doc_id,
                    parties=info.parties_involved,
                    dates=info.effective_dates,
                    terms=info.renewal_terms,
                    requirements=info.compliance_requirements,
                    compliance=compliance_result,
                    risk=risk_result,
                    renewal=renewal_result,
                    contract_summary=contract_summary,
                    potential_risks=potential_risks
                )
                logger.info(f"Completed analysis for document {doc_id}")
            
            # Run the async function in the thread's event loop
            loop.run_until_complete(process_document())
            
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}", exc_info=True)
        finally:
            loop.close()
    
    # Start analysis in background thread
    thread = threading.Thread(target=analysis_worker)
    thread.start()