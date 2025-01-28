from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageTemplate, Frame, PageBreak, ListFlowable, ListItem, Image
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
import markdown
from bs4 import BeautifulSoup

class CyberSecurityReport:
    def __init__(self):
        self.buffer = BytesIO()
        self.pagesize = letter
        self.styles = getSampleStyleSheet()
        self.accent_color = HexColor('#2c3e50')
        self.secondary_color = HexColor('#e74c3c')
        self._define_styles()
        
    def _define_styles(self):
        styles = {
            'CoverTitle': ParagraphStyle(
                name='CoverTitle',
                fontSize=32,
                textColor=self.accent_color,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=15,
                leading=34
            ),
            'SectionHeader': ParagraphStyle(
                name='SectionHeader',
                fontSize=18,
                textColor=self.secondary_color,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceBefore=20,
                spaceAfter=12,
                leftIndent=10
            ),
            'SubsectionHeader': ParagraphStyle(
                name='SubsectionHeader',
                fontSize=14,
                textColor=self.accent_color,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceBefore=15,
                spaceAfter=8,
                leftIndent=20
            ),
            'BodyText': ParagraphStyle(
                name='BodyText',
                fontSize=14,
                textColor=HexColor('#444'),
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                leading=18,
                spaceAfter=12
            ),
            'BulletPoint': ParagraphStyle(
                name='BulletPoint',
                fontSize=12,
                textColor=HexColor('#444'),
                alignment=TA_LEFT,
                fontName='Helvetica',
                leftIndent=25,
                spaceAfter=6
            ),
            'RecommendationHeader': ParagraphStyle(
                name='RecommendationHeader',
                fontSize=13,
                textColor=HexColor('#2c3e50'),
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                spaceBefore=15,
                spaceAfter=8,
                leftIndent=10
            )
        }

        for name, style in styles.items():
            if name not in self.styles.byName:
                self.styles.add(style)

    def _header_footer(self, canvas: Canvas, doc):
        if doc.page == 1:  # Skip header/footer for cover page
            return
        
        canvas.saveState()
        # Header
        canvas.setStrokeColor(self.accent_color)
        canvas.setLineWidth(1)
        canvas.line(50, 750, 550, 750)
        
        # Footer
        canvas.setFont('Helvetica-Oblique', 9)
        canvas.setFillColor(HexColor('#666'))
        canvas.drawString(50, 40, "Confidential - Created by CypherDeck (OxSecure Intelligence)")
        canvas.drawRightString(550, 40, f"Page {doc.page}")
        canvas.restoreState()

    def _create_cover(self, title):
        cover = []
        # Vertical centering with logo
        cover.append(Spacer(1, 1.2*inch))
        
        # Add centered logo
        logo = Image('static/imgs/detective.png', width=3.5*inch, height=3.5*inch)
        logo.hAlign = 'CENTER'
        cover.append(logo)
        cover.append(Spacer(1, 0.4*inch))
        
        # Report title
        title_paragraph = Paragraph(title, self.styles['CoverTitle'])
        cover.append(title_paragraph)
        
        # Decorative line
        cover.append(Spacer(1, 0.3*inch))
        line = Table([[""]], colWidths=[5*inch], rowHeights=[2])
        line.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 2, self.secondary_color),
        ]))
        cover.append(line)
        
        cover.append(Spacer(1, 1.5*inch))
        cover.append(PageBreak())
        return cover

    def _create_threat_indicator(self, level):
        threat_colors = {
            'critical': HexColor('#e74c3c'),
            'high': HexColor('#e67e22'),
            'medium': HexColor('#f1c40f'),
            'low': HexColor('#2ecc71')
        }
        return Table(
            [[level.upper()]],
            style=[
                ('BACKGROUND', (0,0), (0,0), threat_colors[level.lower()]),
                ('TEXTCOLOR', (0,0), (0,0), colors.white),
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('ROUNDEDCORNERS', [5]),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ],
            colWidths=80,
            rowHeights=20
        )

    def _process_content(self, html_content):
        elements = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for element in soup.find_all(True):
            if element.name in ['h1', 'h2', 'h3']:
                style_map = {
                    'h1': 'SectionHeader',
                    'h2': 'SubsectionHeader',
                    'h3': 'RecommendationHeader'
                }
                elements.append(Paragraph(element.get_text(), self.styles[style_map[element.name]]))
                
            elif element.name == 'table':
                table_data = []
                for row in element.find_all('tr'):
                    row_data = []
                    for cell in row.find_all(['td', 'th']):
                        cell_text = cell.get_text(strip=True)
                        if cell_text.lower() in ['high', 'medium', 'low']:
                            row_data.append(self._create_threat_indicator(cell_text.lower()))
                        else:
                            row_data.append(Paragraph(cell_text, self.styles['Normal']))
                    table_data.append(row_data)
                
                threat_table = Table(
                    table_data,
                    colWidths=[150, 200, 100],
                    repeatRows=1
                )
                threat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), HexColor('#f7ead1')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('GRID', (0,0), (-1,-1), 1, HexColor('#ecf0f1')),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#ffffff'), HexColor('#f8f9fa')]),
                    ('BOX', (0,0), (-1,-1), 2, self.accent_color),
                ]))
                elements.append(threat_table)
                elements.append(Spacer(1, 0.5*inch))
                
            elif element.name in ['ul', 'ol']:
                bullet_style = 'bullet' if element.name == 'ul' else '1'
                list_items = []
                for li in element.find_all('li'):
                    list_items.append(ListItem(Paragraph(li.get_text(), self.styles['BulletPoint'])))
                elements.append(ListFlowable(
                    list_items,
                    bulletType=bullet_style,
                    leftIndent=25,
                    bulletColor=self.secondary_color
                ))
                elements.append(Spacer(1, 0.3*inch))
                
            elif element.name == 'p':
                text = element.get_text()
                if text.strip():
                    elements.append(Paragraph(text, self.styles['BodyText']))
                    elements.append(Spacer(1, 0.2*inch))
                    
        return elements

    def generate(self, title, content, created_at):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=50,
            rightMargin=50,
            topMargin=70,
            bottomMargin=50
        )
        
        story = self._create_cover(title)
        story.append(Paragraph(f"<b>Report Generated:</b> {created_at}", self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))
        
        processed_content = self._process_content(markdown.markdown(content, extensions=['tables']))
        story += processed_content
        
        doc.build(
            story,
            onFirstPage=self._header_footer,
            onLaterPages=self._header_footer
        )
        
        self.buffer.seek(0)
        return self.buffer