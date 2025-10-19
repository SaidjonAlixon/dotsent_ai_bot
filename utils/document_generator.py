from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def create_word_document(sections, user_data, file_path):
    doc = Document()
    
    section = doc.sections[0]
    section.page_height = Inches(11.69)
    section.page_width = Inches(8.27)
    section.left_margin = Inches(1.18)
    section.right_margin = Inches(0.59)
    section.top_margin = Inches(0.79)
    section.bottom_margin = Inches(0.79)
    
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    run = footer_para.add_run()
    
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.5
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    for section_data in sections:
        section_type = section_data['type']
        
        if section_type == 'title_page':
            content = section_data['content']
            lines = content.split('\n')
            for line in lines:
                p = doc.add_paragraph(line)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if line.strip():
                    p.runs[0].font.size = Pt(14)
                    p.runs[0].font.name = 'Times New Roman'
                    if 'RESPUBLIKASI' in line or 'VAZIRLIGI' in line or user_data['university'].upper() in line:
                        p.runs[0].font.bold = True
            doc.add_page_break()
        
        elif section_type == 'plan':
            p = doc.add_paragraph('REJA')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    p = doc.add_paragraph(line)
                    if line.startswith('I ') or line.startswith('II ') or line.startswith('III ') or line.isupper():
                        p.runs[0].font.bold = True
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            doc.add_page_break()
        
        elif section_type == 'intro':
            p = doc.add_paragraph('KIRISH')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            p = doc.add_paragraph(content)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            doc.add_page_break()
        
        elif section_type in ['chapter1', 'chapter2', 'chapter3']:
            title = section_data.get('title', 'BOB')
            # Bob sarlavhasini katta harflar bilan yozish
            p = doc.add_paragraph(title.upper())
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            p.runs[0].font.name = 'Times New Roman'
            
            doc.add_paragraph()
            
            subsections = section_data.get('subsections', [])
            for subsection in subsections:
                subsection_title = f"{subsection['number']}. {subsection['title']}"
                p = doc.add_paragraph(subsection_title)
                p.runs[0].font.bold = True
                p.runs[0].font.size = Pt(14)
                p.runs[0].font.name = 'Times New Roman'
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(12)
                
                subsection_content = subsection['content']
                p = doc.add_paragraph(subsection_content)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
                doc.add_paragraph()
            
            doc.add_page_break()
        
        elif section_type == 'conclusion':
            p = doc.add_paragraph('XULOSA')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            p = doc.add_paragraph(content)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            doc.add_page_break()
        
        elif section_type == 'references':
            p = doc.add_paragraph('FOYDALANILGAN ADABIYOTLAR RO\'YXATI')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    p = doc.add_paragraph(line)
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            doc.add_page_break()
        
        elif section_type == 'appendix':
            p = doc.add_paragraph('ILOVALAR')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    p = doc.add_paragraph(line)
                    if line.endswith('ILOVA'):
                        p.runs[0].font.bold = True
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            doc.add_page_break()
        
        elif section_type == 'toc':
            p = doc.add_paragraph('MUNDARIJA')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.bold = True
            p.runs[0].font.size = Pt(14)
            
            content = section_data['content']
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    p = doc.add_paragraph(line)
                    if line.startswith('I ') or line.startswith('II ') or line.startswith('III ') or line.isupper():
                        p.runs[0].font.bold = True
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    doc.save(file_path)
    return file_path

def create_pdf_document(sections, user_data, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    
    left_margin = 30 * mm
    right_margin = width - 15 * mm
    top_margin = height - 20 * mm
    bottom_margin = 20 * mm
    
    y_position = top_margin
    font_size = 14
    line_height = font_size * 1.5
    
    page_number = 1
    
    def add_page_number():
        nonlocal page_number
        c.setFont("Times-Roman", 10)
        c.drawString(width / 2, bottom_margin - 10, str(page_number))
        page_number += 1
    
    def check_new_page():
        nonlocal y_position
        if y_position < bottom_margin + 50:
            add_page_number()
            c.showPage()
            y_position = top_margin
            return True
        return False
    
    for section_data in sections:
        section_type = section_data['type']
        
        if section_type == 'title_page':
            content = section_data['content']
            c.setFont("Times-Bold", 14)
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    text_width = c.stringWidth(line, "Times-Bold", 14)
                    x_position = (width - text_width) / 2
                    c.drawString(x_position, y_position, line)
                    y_position -= line_height
            add_page_number()
            c.showPage()
            y_position = top_margin
        
        elif section_type in ['plan', 'intro', 'conclusion']:
            if section_type == 'plan':
                title = 'REJA'
            elif section_type == 'intro':
                title = 'KIRISH'
            else:
                title = 'XULOSA'
            
            c.setFont("Times-Bold", 14)
            text_width = c.stringWidth(title, "Times-Bold", 14)
            x_position = (width - text_width) / 2
            c.drawString(x_position, y_position, title)
            y_position -= line_height * 2
            
            content = section_data['content']
            c.setFont("Times-Roman", 14)
            
            words = content.split()
            line = ""
            max_width = right_margin - left_margin
            
            for word in words:
                test_line = line + word + " "
                if c.stringWidth(test_line, "Times-Roman", 14) < max_width:
                    line = test_line
                else:
                    c.drawString(left_margin, y_position, line)
                    y_position -= line_height
                    check_new_page()
                    line = word + " "
            
            if line:
                c.drawString(left_margin, y_position, line)
                y_position -= line_height
            
            check_new_page()
            add_page_number()
            c.showPage()
            y_position = top_margin
        
        elif section_type in ['chapter1', 'chapter2', 'chapter3']:
            title = section_data.get('title', 'BOB')
            
            c.setFont("Times-Bold", 14)
            text_width = c.stringWidth(title, "Times-Bold", 14)
            x_position = (width - text_width) / 2
            c.drawString(x_position, y_position, title)
            y_position -= line_height * 2
            
            subsections = section_data.get('subsections', [])
            for subsection in subsections:
                subsection_title = f"{subsection['number']} {subsection['title']}"
                
                c.setFont("Times-Bold", 14)
                c.drawString(left_margin, y_position, subsection_title)
                y_position -= line_height * 1.5
                check_new_page()
                
                subsection_content = subsection['content']
                c.setFont("Times-Roman", 14)
                
                words = subsection_content.split()
                line = ""
                max_width = right_margin - left_margin
                
                for word in words:
                    test_line = line + word + " "
                    if c.stringWidth(test_line, "Times-Roman", 14) < max_width:
                        line = test_line
                    else:
                        c.drawString(left_margin, y_position, line)
                        y_position -= line_height
                        check_new_page()
                        line = word + " "
                
                if line:
                    c.drawString(left_margin, y_position, line)
                    y_position -= line_height * 2
                    check_new_page()
            
            add_page_number()
            c.showPage()
            y_position = top_margin
        
        elif section_type in ['references', 'appendix', 'toc']:
            if section_type == 'references':
                title = 'FOYDALANILGAN ADABIYOTLAR RO\'YXATI'
            elif section_type == 'appendix':
                title = 'ILOVALAR'
            else:
                title = 'MUNDARIJA'
            
            c.setFont("Times-Bold", 14)
            text_width = c.stringWidth(title, "Times-Bold", 14)
            x_position = (width - text_width) / 2
            c.drawString(x_position, y_position, title)
            y_position -= line_height * 2
            
            content = section_data['content']
            c.setFont("Times-Roman", 14)
            
            words = content.split()
            line = ""
            max_width = right_margin - left_margin
            
            for word in words:
                test_line = line + word + " "
                if c.stringWidth(test_line, "Times-Roman", 14) < max_width:
                    line = test_line
                else:
                    c.drawString(left_margin, y_position, line)
                    y_position -= line_height
                    check_new_page()
                    line = word + " "
            
            if line:
                c.drawString(left_margin, y_position, line)
                y_position -= line_height
            
            check_new_page()
            add_page_number()
            c.showPage()
            y_position = top_margin
    
    if page_number > 1:
        add_page_number()
    
    c.save()
    return file_path
