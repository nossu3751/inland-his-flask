import os
from datetime import datetime, timedelta
from docx import Document
import lxml.etree as ET
import html

def format_small_group_note_data(small_group_note):
    return {
            "title": small_group_note.title,
            "date_posted": small_group_note.date_posted.isoformat(),
            "html_template_data": small_group_note.html_template_data,
            "id": small_group_note.id,
            "date_posted": small_group_note.sunday_date.isoformat()
        }

def format_small_group_notes_data(small_group_notes):
    return [format_small_group_note_data(small_group_note) for small_group_note in small_group_notes]

def parse_docx(docx):
    def get_xml(file):
        document = Document(file)
        xml_strings = ""
        for paragraph in document.paragraphs:
            xml_str = ET.tostring(paragraph._element, encoding='unicode')
            xml_strings += xml_str
        return xml_strings
    
    def parse_runs(xml):
        def run_structure(type, run_text, underline, color, line_breaks, font_weight): 
            return {
                "type": type,
                "text": run_text, 
                "underline": underline, 
                "color": color, 
                "line_breaks": line_breaks,
                "font_weight": font_weight
        }
        root = ET.fromstring(xml)
        all_str = []
        
        check_duplicate = set()
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        ns_val = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'
        title=""
        is_first_paragraph = True
        for txbxContent in root.findall('.//w:txbxContent', ns):
            runs = []
            for paragraph in txbxContent.findall('.//w:p', ns):
                runs.append(run_structure('paragraph_start', None, None, None, 0, None))
                
                for run in paragraph.findall('.//w:r', ns):

                    run_texts = run.findall('.//w:t', ns)
                    run_text = ''.join([t.text for t in run_texts])

                    underline = run.find('.//w:rPr/w:u', ns)
                    underline_val = underline.get(ns_val) if underline is not None else None
                    
                    color = run.find(".//w:rPr/w:color", ns)
                    color_val = color.get(ns_val) if color is not None else None
                    
                    font = run.find(".//w:rPr/w:rFonts", ns)
                    font_val = font.get('{%s}eastAsia' % ns['w']) if font is not None else None
                    
                    if not font_val:
                        font_weight = None
                    elif font_val.lower().endswith('b'):
                        font_weight = '700'
                    elif font_val.lower().endswith('m'):
                        font_weight = '500'
                    else:
                        font_weight = None

                    line_breaks = 0
                    run_br = run.findall('.//w:br', ns)
                    for _ in run_br:
                        line_breaks+=1
                    if run_text.isspace() and underline_val != None:
                        runs.append(run_structure("input",None,None,None,0,None))
                        
                    else:
                        runs.append(run_structure("text", run_text, underline_val, color_val, line_breaks, font_weight))
                    
                    if is_first_paragraph:
                        title += run_text
                runs.append(run_structure('paragraph_end', None, None, None, 0, None))
                
                is_first_paragraph = False
            if str(runs) not in check_duplicate:
                check_duplicate.add(str(runs))
                all_str += runs
        title = title if len(title) < 255 else title[:255]
        return all_str, title

    xml = get_xml(docx)
    runs, title = parse_runs(xml)

    html_str = ""
    input_count = 0
    for run in runs:
        if run["type"] == "input":
            input_count += 1
            html_str += " [input] "
        elif run["type"] == "paragraph_start":
            html_str += "<p>"
        elif run["type"] == "paragraph_end":
            html_str += "</p>"
        else:
            underline_val = run["underline"]
            color_val = run["color"]
            font_weight = run["font_weight"]
            line_breaks = run["line_breaks"]
            run_text = run["text"]
            html_str += "<span"
            if underline_val or color_val or font_weight:
                html_str += " style='"
            if underline_val:
                html_str += "text-decoration:underline "
            if color_val:
                html_str += f"color:#{color_val} "
            if font_weight:
                html_str += f"font-weight:{font_weight}"
            if underline_val or color_val or font_weight:
                html_str += "'"
            html_str += f">{run_text}</span>"
            for _ in range(line_breaks):
                html_str += "<br>"
    
    html_structure = {
        "template":runs,
        "inputs":{i:"" for i in range(input_count)},
        "html_string": html_str
    }
    
    date_posted = datetime.utcnow()
    sunday_date = date_posted + timedelta(days=(6 - date_posted.weekday()))
    return {
        "title": title,
        "html_template_data": html_structure,
        "date_posted": date_posted,
        "sunday_date": sunday_date
    }

