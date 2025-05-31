from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO
import datetime
import os
from pathlib import Path
from typing import Union, Optional, Dict

def generate_pdf(
    title: str, 
    data: list[list[str]], 
    filename: str = "report.pdf", 
    logo_path: Optional[str] = None,
    column_renames: Dict[str, str] = None,
    columns_to_remove: list[str] = []
) -> BytesIO:
    """
    Generate a PDF report with customizable column names and optimized layout
    
    Args:
        title: Report title
        data: List of lists representing table data
        filename: Output filename
        logo_path: Path to logo image file
        column_renames: Dictionary mapping original to display column names
        columns_to_remove: List of column names to exclude
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Add logo
    if logo_path:
        try:
            base_dir = Path(__file__).parent
            resolved_logo_path = str(base_dir / logo_path)
            if os.path.exists(resolved_logo_path):
                logo = ImageReader(resolved_logo_path)
                c.drawImage(logo, 40, height-100, width=80, height=60, 
                           preserveAspectRatio=True, mask='auto')
        except Exception as e:
            c.setFont("Helvetica", 8)
            c.drawString(40, height-80, f"[Logo error: {str(e)}]")

    # Title and timestamp
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-50, title)
    c.setFont("Helvetica", 8)
    c.drawString(width-150, height-40, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Process data
    if not data:
        return buffer
        
    # Apply column renames and removals
    headers = data[0]
    if column_renames:
        headers = [column_renames.get(col, col) for col in headers]
    
    if columns_to_remove:
        remove_indices = [i for i, col in enumerate(data[0]) if col in columns_to_remove]
        for row in data:
            for i in sorted(remove_indices, reverse=True):
                if i < len(row):
                    row.pop(i)
        headers = [h for i, h in enumerate(headers) if i not in remove_indices]

    # Create table data with formatted headers
    table_data = [headers] + data[1:]

    # Column width calculation
    num_cols = len(headers)
    col_widths = [60, 80, 40, 60, 60, 60, 40, 40]  # Base widths
    if len(col_widths) > num_cols:
        col_widths = col_widths[:num_cols]
    
    # Adjust total width to fill page
    total_width = sum(col_widths)
    if total_width < width - 60:  # 30px margins
        extra_space = (width - 60) - total_width
        col_widths = [w + extra_space/num_cols for w in col_widths]

    # Create paragraph style for wrapped headers
    header_style = ParagraphStyle(
        name='Header',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=10,
        alignment=0,  # Center aligned
        spaceAfter=2
    )

    # Convert headers to Paragraph objects for wrapping
    wrapped_headers = []
    for header in headers:
        # Replace underscores with spaces and add line breaks
        display_text = header.replace('_', ' ')
        if ' ' in display_text:
            parts = display_text.split(' ')
            display_text = '<br/>'.join(parts)
        wrapped_headers.append(Paragraph(display_text, header_style))

    # Replace first row with wrapped headers
    table_data[0] = wrapped_headers

    # Create table
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4472C4")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
    ]))

    # Draw table
    table.wrapOn(c, width-60, height)
    table.drawOn(c, 30, height-120-table._height)

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(30, 30, "Educational Institution Enrolment Analysis Tool")
    c.drawString(width-50, 30, f"Page {c.getPageNumber()}")
    
    c.save()
    buffer.seek(0)
    return buffer