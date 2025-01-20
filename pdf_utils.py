from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import markdown
from bs4 import BeautifulSoup

def generate_pdf(report_title, report_content, created_at):
    """
    Generate a PDF from the given report data.

    Args:
        report_title (str): The title of the report.
        report_content (str): The content of the report in Markdown format.
        created_at (str): The timestamp when the report was created.

    Returns:
        BytesIO: A buffer containing the generated PDF.
    """
    # Convert Markdown to HTML
    html_content = markdown.markdown(report_content)

    # Convert HTML to plain text with proper formatting
    soup = BeautifulSoup(html_content, 'html.parser')
    plain_text = soup.get_text(separator='\n')  # Use newlines to separate paragraphs

    # Create a PDF buffer
    buffer = BytesIO()

    # Create a PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Define custom styles (only if they don't already exist)
    # Modify existing styles
    styles['Title'].fontSize = 24
    styles['Title'].textColor = '#2c3e50'
    styles['Title'].spaceAfter = 12
    styles['Title'].alignment = 1  # Center alignment

    styles['Heading1'].fontSize = 18
    styles['Heading1'].textColor = '#2c3e50'
    styles['Heading1'].spaceAfter = 6
    styles['Heading1'].spaceBefore = 12

    styles['Heading2'].fontSize = 16
    styles['Heading2'].textColor = '#34495e'
    styles['Heading2'].spaceAfter = 6
    styles['Heading2'].spaceBefore = 12

    styles['BodyText'].fontSize = 12
    styles['BodyText'].textColor = '#333'
    styles['BodyText'].spaceAfter = 6
    styles['BodyText'].leading = 14

    # Prepare the content for the PDF
    content = []

    # Add the report title
    title = Paragraph(report_title, styles['Title'])
    content.append(title)

    # Add the report generation date
    date_text = f"Generated on: {created_at}"
    date_paragraph = Paragraph(date_text, styles['BodyText'])
    content.append(date_paragraph)
    content.append(Spacer(1, 0.5 * inch))  # Add some space

    # Add the report content
    for line in plain_text.split('\n'):
        if line.strip():  # Skip empty lines
            # Apply custom styles for bold and italic text
            line = line.replace('**', '<b>').replace('**', '</b>')  # Markdown bold
            line = line.replace('*', '<i>').replace('*', '</i>')  # Markdown italic
            paragraph = Paragraph(line, styles['BodyText'])
            content.append(paragraph)
            content.append(Spacer(1, 0.2 * inch))  # Add some space between paragraphs

    # Build the PDF
    pdf.build(content)

    # Prepare the buffer for download
    buffer.seek(0)
    return buffer