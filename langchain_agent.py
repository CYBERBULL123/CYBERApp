import os
import logging
import re
import requests
from typing import Dict, Any, List
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
        **Role**: You are an advanced cybersecurity AI agent with expertise in vulnerability assessment, penetration testing, and incident response. Your task is to analyze the input data, apply reasoning, and generate a highly detailed and actionable security report.

        **Capabilities**:
        - Perform **multi-modal reasoning** using Chain-of-Thought (CoT), Tree-of-Thought (ToT), and RPA (Robust Problem Analysis) techniques to solve complex challenges.
        - Evaluate the context critically and explore various hypotheses to derive insightful conclusions.
        - Synthesize data from multiple sources, correlate findings, and provide accurate and justified security recommendations.

        **Input Data**:
        - Raw Data: {data}
        - Search Results: {search_results}
        - Extracted Keywords: {keywords}
        - Extracted Numeric Values: {numeric_values}

        **Report Structure**:
        1. **Strategic Overview**:
            - Contextualize the findings in the organization's cybersecurity landscape.
            - Identify high-level risks and potential attack vectors based on the provided data.

        2. **Multi-Layered Analysis**:
            - **Layer 1 (CoT)**: Sequentially analyze each vulnerability or risk to identify root causes and potential impacts.
            - **Layer 2 (ToT)**: Explore alternative scenarios or threat vectors that could exploit the vulnerabilities.
            - **Layer 3 (RPA)**: Combine reasoning approaches to identify overlooked risks or mitigation strategies.

        3. **Detailed Key Findings**:
            - Present detailed descriptions of identified vulnerabilities, their severity, and their impact.
            - Provide correlation with relevant data (e.g., IP addresses, logs, system configurations).
            - Include tables or visualizations for clarity.

        4. **Actionable Recommendations**:
            - Short-term measures: Patches, configuration adjustments, immediate containment strategies.
            - Long-term measures: Policy changes, incident response improvements, and advanced monitoring solutions.
            - Prioritize recommendations based on risk levels and potential impact.

        5. **Advanced Insights**:
            - Highlight emerging threats and trends derived from search results and external knowledge.
            - Correlate findings with industry benchmarks or standards like NIST, ISO 27001, or OWASP.

        6. **Summary and Roadmap**:
            - Summarize the organization’s current security posture.
            - Provide a roadmap for implementing recommendations and achieving a robust security framework.

        **Guidelines**:
        - Use precise, technical language and maintain professionalism.
        - Justify all findings with reasoning and evidence.
        - Ensure the report is concise but comprehensive, with no redundant information.
        - Include hyperlinks to tools, standards, and additional resources.

        **Objective**:
        Generate a detailed and actionable report that helps organizations improve their security posture, mitigate risks, and enhance resilience against cyber threats.
        """
        )
        report_chain = LLMChain(llm=llm, prompt=prompt_template)
        logger.info("Report generation chain created successfully.")
        return report_chain
    except Exception as e:
        logger.error(f"Failed to create report chain: {str(e)}")
        raise

def validate_data(data: Any) -> bool:
    """
    Validate the input data for report generation.
    """
    if not data or (isinstance(data, str) and not data.strip()):
        logger.error("Invalid data: Data must be a non-empty string or dictionary.")
        return False
    return True

def generate_report(data: Any) -> str:
    """
    Generate a cybersecurity report using Gemini LLM and LangChain.
    
    Args:
        data (Any): The raw file content or form data to generate the report from.
    
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
        if isinstance(data, str):
            keywords, numeric_values = extract_keywords_and_numeric_values(data)
        elif isinstance(data, dict):
            # For advanced form inputs, extract keywords and numeric values from the findings
            findings = data.get("findings", "")
            keywords, numeric_values = extract_keywords_and_numeric_values(findings)
        else:
            raise ValueError("Unsupported data type. Expected str or dict.")
        
        logger.info(f"Extracted keywords: {keywords}")
        logger.info(f"Extracted numeric values: {numeric_values}")
        
        # Gather additional information from the web using scraping
        search_query = f"Cybersecurity trends and insights related to: {', '.join(keywords)}"
        search_results = scrape_google_search(search_query)
        
        # Wrap the data, search results, keywords, and numeric values in a dictionary
        input_data = {
            "data": data if isinstance(data, str) else str(data),  # Convert dict to string if necessary
            "search_results": search_results,
            "keywords": keywords,
            "numeric_values": numeric_values,
        }
        
        # Generate the report using the LangChain
        report = report_chain.run(input_data)
        logger.info("Report generated successfully.")
        return report
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise Exception(f"Failed to generate report: {str(e)}")