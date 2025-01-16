import os
import logging
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# Load API key from environment variable for security
API_KEY = os.getenv('GOOGLE_API_KEY')

def initialize_llm() -> ChatGoogleGenerativeAI:
    """
    Initialize and return the Gemini LLM model.
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            api_key=API_KEY,
            temperature=0.7,
            max_tokens=3000,  # Allow for detailed responses
        )
        logger.info("Gemini LLM initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM: {str(e)}")
        raise

def initialize_memory() -> ConversationBufferMemory:
    """
    Initialize and return the conversation memory.
    """
    try:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        logger.info("Conversation memory initialized successfully.")
        return memory
    except Exception as e:
        logger.error(f"Failed to initialize memory: {str(e)}")
        raise

def create_report_chain(llm: ChatGoogleGenerativeAI) -> LLMChain:
    """
    Create and return the LLMChain for report generation.
    """
    try:
        prompt_template = PromptTemplate(
            input_variables=["data"],
            template="""
            Generate a professional cybersecurity report based on the following data:
            {data}

            The report should include:
            1. Executive Summary
            2. Detailed Analysis
            3. Key Findings
            4. Recommendations
            5. Conclusion
            """
        )
        report_chain = LLMChain(llm=llm, prompt=prompt_template)
        logger.info("Report generation chain created successfully.")
        return report_chain
    except Exception as e:
        logger.error(f"Failed to create report chain: {str(e)}")
        raise

def validate_data(data: str) -> bool:
    """
    Validate the input data for report generation.
    """
    if not data or not isinstance(data, str):
        logger.error("Invalid data: Data must be a non-empty string.")
        return False
    return True

def generate_report(data: str) -> str:
    """
    Generate a cybersecurity report using Gemini LLM and LangChain.
    
    Args:
        data (str): The raw file content to generate the report from.
    
    Returns:
        str: The generated report.
    
    Raises:
        Exception: If report generation fails.
    """
    try:
        if not validate_data(data):
            raise ValueError("Invalid input data.")
        
        llm = initialize_llm()
        report_chain = create_report_chain(llm)
        
        # Wrap the data in a dictionary
        input_data = {"data": data}
        
        # Generate the report using the LangChain
        report = report_chain.run(input_data)
        logger.info("Report generated successfully.")
        return report
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise Exception(f"Failed to generate report: {str(e)}")