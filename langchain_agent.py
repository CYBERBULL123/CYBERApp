import os
import logging
import re
import requests
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from file_processor import extract_keywords_and_numeric_values

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

def scrape_google_search(query: str) -> str:
    """
    Scrape Google search results for a given query without using any frameworks.
    """
    try:
        # Prepare the search URL
        search_url = f"https://www.google.com/search?q={query}"
        
        # Set headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Send a GET request to Google
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Extract search results using regex
        search_results = []
        pattern = r'<h3[^>]*>(.*?)<\/h3>'  # Regex to match search result titles
        matches = re.findall(pattern, response.text)
        
        # Clean up the results
        for match in matches:
            clean_result = re.sub(r'<[^>]+>', '', match)  # Remove HTML tags
            search_results.append(clean_result)
        
        # Return the top 3 results
        return "\n".join(search_results[:3])
    except Exception as e:
        logger.error(f"Failed to scrape Google search results: {str(e)}")
        raise

def create_report_chain(llm: ChatGoogleGenerativeAI) -> LLMChain:
    """
    Create and return the LLMChain for report generation.
    """
    try:
        prompt_template = PromptTemplate(
            input_variables=["data", "search_results", "keywords", "numeric_values"],
            template="""
            You are a cybersecurity expert. Generate a professional and detailed cybersecurity report based on the following data:
            {data}

            Additionally, use the following search results to enhance the report:
            {search_results}

            The following keywords were extracted from the data:
            {keywords}

            The report should include:
            1. Executive Summary
            2. Detailed Analysis (including technical details like IPs, versions, etc.)
            3. Key Findings
            4. Recommendations (specific and actionable)
            5. Conclusion
            6. References (with their official links)

            Ensure the report is well-structured, concise, and actionable. Use technical terms and provide in-depth analysis.
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
        
        # Extract keywords and numeric values from the input data
        keywords, numeric_values = extract_keywords_and_numeric_values(data)
        logger.info(f"Extracted keywords: {keywords}")
        logger.info(f"Extracted numeric values: {numeric_values}")
        
        # Gather additional information from the web using scraping
        search_query = f"Cybersecurity trends and insights related to: {', '.join(keywords)}"
        search_results = scrape_google_search(search_query)
        
        # Wrap the data, search results, keywords, and numeric values in a dictionary
        input_data = {
            "data": data,
            "search_results": search_results,
            "keywords": keywords,
            # "numeric_values": numeric_values,
        }
        
        # Generate the report using the LangChain
        report = report_chain.run(input_data)
        logger.info("Report generated successfully.")
        return report
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise Exception(f"Failed to generate report: {str(e)}")