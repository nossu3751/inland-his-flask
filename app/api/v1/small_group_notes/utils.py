import os
from datetime import datetime, timedelta
from docx import Document
import lxml.etree as ET
import html

def format_small_group_note_data(small_group_note):
    return {
            "title": small_group_note.title,
            "date_posted": small_group_note.date_posted.isoformat(),
            "html_string": small_group_note.html_string,
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
        def run_structure(run_text, run_style, underline, color, line_breaks, font_weight): 
            return {
                "text": run_text, 
                "style": run_style, 
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

        for txbxContent in root.findall('.//w:txbxContent', ns):
            runs = []
            for paragraph in txbxContent.findall('.//w:p', ns):
                runs.append(run_structure('paragraph_start', None, None, None, 0, 300))
                for run in paragraph.findall('.//w:r', ns):

                    run_texts = run.findall('.//w:t', ns)
                    run_text = ''.join([t.text for t in run_texts])

                    run_style = run.find('.//w:rPr/w:rStyle', ns)
                    run_style_val = run_style.get(ns_val) if run_style is not None else None

                    underline = run.find('.//w:rPr/w:u', ns)
                    underline_val = underline.get(ns_val) if underline is not None else None
                    
                    color = run.find(".//w:rPr/w:color", ns)
                    color_val = color.get(ns_val) if color is not None else None
                    
                    font = run.find(".//w:rPr/w:rFonts", ns)
                    font_val = font.get('{%s}eastAsia' % ns['w']) if font is not None else None
                    
                    if not font_val:
                        font_weight = '300'
                    elif font_val.lower().endswith('b'):
                        font_weight = '700'
                    elif font_val.lower().endswith('m'):
                        font_weight = '500'
                    else:
                        font_weight = '300'

                    line_breaks = 0
                    run_br = run.findall('.//w:br', ns)
                    for _ in run_br:
                        line_breaks+=1
                    runs.append(run_structure(run_text, run_style_val, underline_val, color_val, line_breaks, font_weight))
                runs.append(run_structure('paragraph_end', None, None, None, 0, 300))
            if str(runs) not in check_duplicate:
                check_duplicate.add(str(runs))
                all_str += runs
        return all_str

    xml = get_xml(docx)
    runs = parse_runs(xml)

    output_html = ""
    title = ""
    is_first_paragraph = True
    for run in runs:
        if run["text"] == 'paragraph_start':
            output_html += "<p>"
        elif run["text"] == 'paragraph_end':
            output_html += "</p><br>"
            is_first_paragraph = False
        elif run["underline"] != None and str(run["text"]).isspace():
            output_html += "<input/>"
        else:
            if is_first_paragraph:
                title += run['text']
            color = run["color"]
            font_weight = run["font_weight"]
            output_html += f'''
                <span style='color:#{color}; font-weight:{font_weight}'>
                    {html.escape(run['text'])}
                </span>
            '''

    date_posted = datetime.utcnow()
    sunday_date = date_posted + timedelta(days=(6 - date_posted.weekday()))
    return {
        "title": title if len(title) < 255 else title[:255],
        "html": output_html,
        "date_posted": date_posted,
        "sunday_date": sunday_date
    }

