"""
Script to create the reference DOCX template with custom styling.

This script should be run once to generate the reference.docx template
used by Pandoc for styling converted documents.

Requirements:
    pip install python-docx

Usage:
    python create_reference_template.py
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os


def create_reference_template():
    """Create a DOCX template with custom styles matching the TipTap editor."""
    doc = Document()

    # Set document margins (1 inch all sides)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Configure Normal style - matches editor prose styling
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Arial'
    normal_font.size = Pt(11)
    normal_font.color.rgb = RGBColor(0, 0, 0)  # Black text
    normal_paragraph = normal_style.paragraph_format
    normal_paragraph.line_spacing = 1.6  # Match editor line height
    normal_paragraph.space_after = Pt(8)  # Add spacing between paragraphs

    # Configure Heading 1 - large, bold, black
    heading1_style = doc.styles['Heading 1']
    heading1_font = heading1_style.font
    heading1_font.name = 'Arial'
    heading1_font.size = Pt(28)  # Larger to match editor prominence
    heading1_font.bold = True
    heading1_font.color.rgb = RGBColor(0, 0, 0)  # Black
    heading1_paragraph = heading1_style.paragraph_format
    heading1_paragraph.space_before = Pt(12)
    heading1_paragraph.space_after = Pt(12)
    heading1_paragraph.line_spacing = 1.2

    # Configure Heading 2 - medium, bold, black
    heading2_style = doc.styles['Heading 2']
    heading2_font = heading2_style.font
    heading2_font.name = 'Arial'
    heading2_font.size = Pt(20)  # Adjusted for hierarchy
    heading2_font.bold = True
    heading2_font.color.rgb = RGBColor(0, 0, 0)  # Black
    heading2_paragraph = heading2_style.paragraph_format
    heading2_paragraph.space_before = Pt(10)
    heading2_paragraph.space_after = Pt(10)
    heading2_paragraph.line_spacing = 1.2

    # Configure Heading 3 - smaller, bold, black
    heading3_style = doc.styles['Heading 3']
    heading3_font = heading3_style.font
    heading3_font.name = 'Arial'
    heading3_font.size = Pt(16)  # Adjusted for hierarchy
    heading3_font.bold = True
    heading3_font.color.rgb = RGBColor(0, 0, 0)  # Black
    heading3_paragraph = heading3_style.paragraph_format
    heading3_paragraph.space_before = Pt(8)
    heading3_paragraph.space_after = Pt(8)
    heading3_paragraph.line_spacing = 1.2

    # Add sample content to establish styles
    doc.add_heading('Sample Heading 1', level=1)
    doc.add_paragraph('This is normal text in Arial 11pt with 1.6 line spacing.')

    doc.add_heading('Sample Heading 2', level=2)
    doc.add_paragraph('Another paragraph of normal text.')

    doc.add_heading('Sample Heading 3', level=3)
    doc.add_paragraph('More sample text.')

    # Add a sample table with default styling
    table = doc.add_table(rows=3, cols=4)

    # Add simple header row
    for i, cell in enumerate(table.rows[0].cells):
        cell.text = f'Header {i+1}'

    # Add simple data rows
    for row_idx in range(1, 3):
        for col_idx, cell in enumerate(table.rows[row_idx].cells):
            cell.text = f'Data {row_idx}-{col_idx+1}'

    # Save the template
    output_path = os.path.join(os.path.dirname(__file__), 'templates', 'reference.docx')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)

    print(f"Reference template created successfully: {output_path}")


if __name__ == "__main__":
    create_reference_template()
