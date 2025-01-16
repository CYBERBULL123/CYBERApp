from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_file(file):
    """
    Extract text from a file based on its extension.
    Supported file types: .txt, .log, .pdf, .doc, .docx, .html, .xml
    """
    filename = file.filename
    file_extension = filename.split('.')[-1].lower()

    try:
        if file_extension in ['txt', 'log']:
            # Read text directly from .txt or .log files
            return file.read().decode('utf-8')

        elif file_extension == 'pdf':
            # Extract text from PDF files
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text

        elif file_extension in ['doc', 'docx']:
            # Extract text from Word documents
            doc = Document(file)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text

        elif file_extension in ['html', 'xml']:
            # Extract text from HTML/XML files using BeautifulSoup
            soup = BeautifulSoup(file.read(), 'html.parser')
            return soup.get_text()

        else:
            logger.error(f"Unsupported file type: {file_extension}")
            return None

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        return None