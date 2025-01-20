from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import logging
import re
from typing import Tuple, List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_file(file):
    """
    Extract text from a file based on its extension.
    Supported file types: .txt, .log, .pdf, .doc, .docx, .html, .xml, .csv, .json
    
    Args:
        file: The file object to extract text from.
    
    Returns:
        str: The extracted text, or an empty string if extraction fails.
    """
    filename = file.filename
    file_extension = filename.split('.')[-1].lower()

    try:
        if file_extension in ['txt', 'log', 'csv', 'json']:
            # Read text directly from .txt, .log, .csv, or .json files
            file_content = file.read().decode('utf-8')
            file.seek(0)  # Reset file pointer
            return file_content

        elif file_extension == 'pdf':
            # Extract text from PDF files
            pdf_reader = PyPDF2.PdfReader(file.stream)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            file.seek(0)  # Reset file pointer
            return text

        elif file_extension in ['doc', 'docx']:
            # Extract text from Word documents
            doc = Document(file.stream)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            file.seek(0)  # Reset file pointer
            return text

        elif file_extension in ['html', 'xml']:
            # Extract text from HTML/XML files using BeautifulSoup
            file_content = file.read().decode('utf-8')
            soup = BeautifulSoup(file_content, 'html.parser')
            file.seek(0)  # Reset file pointer
            return soup.get_text()

        else:
            logger.error(f"Unsupported file type: {file_extension}")
            return ""  # Return an empty string for unsupported file types

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        return ""  # Return an empty string if extraction fails

def extract_keywords_and_numeric_values(text: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Extract all keywords and numeric values (e.g., IPs, versions) from the input text using regex.
    
    Args:
        text (str): The input text to extract keywords and numeric values from.
    
    Returns:
        Tuple[List[str], Dict[str, str]]: A tuple containing:
            - List of all keywords.
            - Dictionary of numeric values with their types (e.g., {"ip": "192.168.1.1"}).
    """
    try:
        # Check if the input text is empty or None
        if not text or not isinstance(text, str):
            logger.warning("Input text is empty or invalid. Returning empty results.")
            return [], {}

        # Convert text to lowercase
        text = text.lower()
        
        # Extract keywords using regex (words with 3 or more letters)
        keywords = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Remove duplicates
        keywords = list(set(keywords))
        
        # Extract numeric values (IPs, versions, etc.)
        numeric_values = {}
        
        # Regex to match IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, text)
        if ips:
            numeric_values["ip"] = ips[0]  # Store the first IP found
        
        # Regex to match version numbers (e.g., 2.4.49)
        version_pattern = r'\b(?:\d+\.)+\d+\b'
        versions = re.findall(version_pattern, text)
        if versions:
            numeric_values["version"] = versions[0]  # Store the first version found
        
        # Regex to match other numeric values (e.g., ports, IDs)
        numeric_pattern = r'\b\d+\b'
        numbers = re.findall(numeric_pattern, text)
        if numbers:
            numeric_values["numeric"] = numbers  # Store all numeric values
        
        logger.info(f"Extracted keywords: {keywords}")
        logger.info(f"Extracted numeric values: {numeric_values}")
        return keywords, numeric_values
    except Exception as e:
        logger.error(f"Failed to extract keywords and numeric values: {str(e)}")
        return [], {}  # Return empty results if extraction fails