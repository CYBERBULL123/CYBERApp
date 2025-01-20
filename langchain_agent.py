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
            **Role**: You are a senior cybersecurity analyst with expertise in vulnerability assessment, penetration testing, and incident response. Your task is to generate a comprehensive and professional cybersecurity report based on the provided data.

            **Instructions**:
            1. Use a **zero-shot learning approach** to analyze the data and generate insights without prior examples.
            2. Apply **Chain-of-Thought (CoT)** and **Tree-of-Thought (ToT)** techniques to break down complex problems, explore multiple reasoning paths, and arrive at well-justified conclusions.
            3. Structure the report in a professional format with clear sections and actionable recommendations.
            4. Use technical terminology and provide in-depth analysis.

            **Input Data**:
            - Raw Data: {data}
            - Search Results: {search_results}
            - Extracted Keywords: {keywords}
            - Extracted Numeric Values: {numeric_values}

            **Report Structure**:
            1. **Executive Summary**:
            - Provide a high-level overview of the findings, risks, and recommendations.
            - Highlight the most critical issues and their potential impact on the organization.

            2. **Detailed Analysis**:
            - Analyze the data thoroughly, including technical details such as IP addresses, software versions, and configurations.
            - Use CoT and ToT to explore multiple angles of the findings (e.g., root causes, attack vectors, potential exploits).
            - Include tables, bullet points, or diagrams if necessary to present technical details clearly.

            3. **Key Findings**:
            - List and describe the key vulnerabilities, threats, and risks identified in the data.
            - For each finding, provide:
                - A detailed description of the issue.
                - The potential impact on the organization.
                - Evidence or reasoning supporting the finding (use CoT and ToT).

            4. **Recommendations**:
            - Provide specific, actionable, and prioritized recommendations to mitigate the identified risks.
            - Include:
                - Short-term fixes (e.g., patches, configuration changes).
                - Long-term strategies (e.g., security policies, employee training).
                - Tools or technologies that can help address the issues.

            5. **Conclusion**:
            - Summarize the overall security posture of the organization based on the findings.
            - Highlight the importance of implementing the recommendations to prevent future incidents.

            6. **References**:
            - Include links to official documentation, tools, or resources mentioned in the report.
            - Ensure all references are credible and relevant.

            **Additional Guidelines**:
            - Use a formal and professional tone.
            - Avoid jargon unless it is clearly defined.
            - Ensure the report is concise yet comprehensive.
            - Proofread the report for grammar, spelling, and clarity.

            **Output**:
            Generate a well-structured, detailed, and actionable cybersecurity report based on the above instructions.
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