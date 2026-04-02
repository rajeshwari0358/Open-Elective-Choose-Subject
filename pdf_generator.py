from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

def draw_page_border(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(2)
    margin = 0.4 * inch
    canvas.rect(margin, margin, A4[0] - 2*margin, A4[1] - 2*margin)
    canvas.setLineWidth(0.5)
    canvas.rect(margin + 3, margin + 3, A4[0] - 2*margin - 6, A4[1] - 2*margin - 6)
    canvas.restoreState()

def add_page_number(canvas, doc):
    draw_page_border(canvas, doc)
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(A4[0]/2, 0.6*inch, text)
    canvas.restoreState()

def generate_student_list_pdf(branch_name, students, selected_branch_code=None):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.6*inch,
        bottomMargin=0.85*inch
    )
    
    styles = getSampleStyleSheet()
    
    vtu_title_style = ParagraphStyle(
        'VTUTitle',
        parent=styles['Heading1'],
        fontSize=12,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    college_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        leading=12
    )
    
    branch_title_style = ParagraphStyle(
        'BranchTitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    year_style = ParagraphStyle(
        'YearStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=4,
        alignment=TA_CENTER,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    list_title_style = ParagraphStyle(
        'ListTitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    vtu_logo_path = os.path.join('static', 'images', 'vtu_logo.jpg')
    if os.path.exists(vtu_logo_path):
        try:
            vtu_logo = Image(vtu_logo_path, width=1.2*inch, height=1.2*inch)
            vtu_logo.hAlign = 'CENTER'
            elements.append(vtu_logo)
            elements.append(Spacer(1, 0.08*inch))
        except:
            pass
    
    vtu_title = Paragraph("VISVESVARAYA TECHNOLOGICAL UNIVERSITY, BELAGAVI", vtu_title_style)
    elements.append(vtu_title)
    
    elements.append(Spacer(1, 0.15*inch))
    
    blde_logo_path = os.path.join('static', 'images', 'blde_logo.png')
    if os.path.exists(blde_logo_path):
        try:
            blde_logo = Image(blde_logo_path, width=1.0*inch, height=0.8*inch)
            blde_logo.hAlign = 'CENTER'
            elements.append(blde_logo)
            elements.append(Spacer(1, 0.08*inch))
        except:
            pass
    
    college_title = Paragraph(
        "B.L.D.E.A's V.P.DR.P.G. HALAKATTI COLLEGE OF ENGINEERING AND<br/>TECHNOLOGY, VIJAYAPUR-586103",
        college_style
    )
    elements.append(college_title)
    
    elements.append(Spacer(1, 0.15*inch))
    
    if selected_branch_code:
        branch_title = Paragraph(f"{branch_name} ({selected_branch_code})", branch_title_style)
        elements.append(branch_title)
    
    elements.append(Spacer(1, 0.1*inch))
    
    year_title = Paragraph("2025-2026", year_style)
    elements.append(year_title)
    
    elements.append(Spacer(1, 0.1*inch))
    
    list_title = Paragraph("Open Elective-Student Lists", list_title_style)
    elements.append(list_title)
    
    elements.append(Spacer(1, 0.15*inch))
    
    if students:
        table_data = [['Sl.No', 'USN', 'Student Name', 'Branch', 'Subject Code', 'Subject Name']]
        
        for i, student in enumerate(students, 1):
            table_data.append([
                str(i),
                student['usn'],
                student['name'],
                student.get('branch', ''),
                student['subject_code'],
                student['subject_name']
            ])
        
        col_widths = [0.5*inch, 1.2*inch, 1.8*inch, 0.8*inch, 0.9*inch, 1.8*inch]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        table_style = TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
    else:
        no_data_style = ParagraphStyle(
            'NoDataStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=30
        )
        no_data = Paragraph("No students from this branch have confirmed their subject yet.", no_data_style)
        elements.append(no_data)
    
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    buffer.seek(0)
    return buffer

