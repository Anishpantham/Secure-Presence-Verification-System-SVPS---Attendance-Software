"""Export the dated audit academic report without overwriting historical releases.

Run: backend/.venv/bin/python scripts/export_academic_report.py
Uses the project reportlab/pypdf dependencies; DOCX uses standard OOXML.
"""
from pathlib import Path
import re
import json
import hashlib
import html
import sys
import zipfile
from xml.sax.saxutils import escape
from xml.etree import ElementTree as ET
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from pypdf import PdfReader

root=Path(__file__).resolve().parents[1]
source=root/'docs/PROJECT_REPORT.md'
dest=root/'docs/reports'
dest.mkdir(exist_ok=True)
base=dest/'SPVS_PROJECT_REPORT_2026-10-28'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyTextAudit',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=9))
styles.add(ParagraphStyle(name='CellAudit',fontSize=8,leading=11))
def inline(text):
 text=escape(text).replace('—',' - ').replace('–','-').replace('→',' to ')
 text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',text)
 return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text).replace('`','')
def architecture():
 drawing=Drawing(490,230)
 boxes=[(5,165,145,45,['Faculty/admin dashboard']),(5,65,145,45,['Android / iOS client']),(180,115,140,45,['FastAPI roles / protocol']),(345,165,140,45,['Identity / device checks']),(345,65,140,45,['QR / audio / GPS policy']),(180,0,140,45,['Decision / PostgreSQL'])]
 for x,y,w,h,labels in boxes:
  drawing.add(Rect(x,y,w,h,fillColor=colors.HexColor('#edf4ef'),strokeColor=colors.HexColor('#17695b')))
  drawing.add(String(x+w/2,y+h/2,labels[0],textAnchor='middle',fontName='Helvetica',fontSize=9))
 for x1,y1,x2,y2 in [(150,187,180,147),(150,87,180,127),(320,147,345,187),(320,127,345,87),(250,115,250,45),(415,65,320,20)]:
  drawing.add(Line(x1,y1,x2,y2,strokeColor=colors.HexColor('#17695b')))
 drawing.add(String(10,140,'QR display and audible signal',fontSize=8))
 drawing.add(Line(75,165,75,110,strokeColor=colors.HexColor('#17695b')))
 return drawing
flow=[];paragraph=[];docparas=[];code=False;mermaid=False
def flush():
 if paragraph:
  text=' '.join(paragraph);flow.append(Paragraph(inline(text),styles['BodyTextAudit']));docparas.append(('Normal',text));paragraph.clear()
for line in source.read_text().splitlines():
 if line.startswith('```'):
  flush()
  if not code:code=True;mermaid='mermaid' in line
  else:
   code=False
   if mermaid:
    flow.append(architecture());flow.append(Spacer(1,12))
    docparas.append(('Normal','Architecture: faculty dashboard and native student client communicate with FastAPI. Faculty supplies QR/audio to the client. FastAPI evaluates identity/device and QR/audio/GPS/platform policy before the decision is persisted in PostgreSQL. The full Mermaid diagram is in the Markdown source.'))
  continue
 if code:continue
 if line.startswith('#'):
  flush();level=min(len(line)-len(line.lstrip('#')),3);text=line.lstrip('#').strip()
  if line.startswith('## 2. Abstract'):flow.append(PageBreak())
  flow.append(Paragraph(inline(text),styles['Title' if level==1 else 'Heading'+str(level-1)]));docparas.append(('Title' if level==1 else 'Heading1',text))
 elif not line.strip():flush()
 elif re.match(r'^(?:- |\d+\. )',line):flush();flow.append(Paragraph(inline(line),styles['BodyTextAudit']));docparas.append(('Normal',line))
 else:paragraph.append(line)
flush()
def footer(canvas,doc):
 canvas.setFillColor(colors.white);canvas.rect(0,0,A4[0],A4[1],fill=1,stroke=0);canvas.setFillColor(colors.black)
 canvas.setFont('Helvetica',8);canvas.drawString(45,27,'SPVS | Audit checkpoint 28 October 2026');canvas.drawRightString(A4[0]-45,27,str(doc.page))
SimpleDocTemplate(str(base.with_suffix('.pdf')),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=42,bottomMargin=48,title='SPVS Academic Project Report',author='SPVS project').build(flow,onFirstPage=footer,onLaterPages=footer)

# Standards-based minimal editable Word document; no external conversion dependency.
ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
paras=[]
for style,text in docparas:
 text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',text).replace('**','').replace('`','')
 paras.append(f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')
document=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{ns}"><w:body>'+''.join(paras)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850"/></w:sectPr></w:body></w:document>'
styles_xml=f'''<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="{ns}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="280" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="40"/><w:color w:val="17695B"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="160"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="17695B"/></w:rPr></w:style></w:styles>'''
with zipfile.ZipFile(base.with_suffix('.docx'),'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','''<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>''')
 z.writestr('_rels/.rels','''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>''')
 z.writestr('word/_rels/document.xml.rels','''<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''')
 z.writestr('word/document.xml',document);z.writestr('word/styles.xml',styles_xml)
checks={}
pdf=PdfReader(base.with_suffix('.pdf'));text='\n'.join(p.extract_text() or '' for p in pdf.pages)
assert '26. Appendices' in text and '234' in text and '146' in text
for suffix in ['.pdf','.docx']:
 p=base.with_suffix(suffix);checks[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
checks[base.with_suffix('.pdf').name].update(pages=len(pdf.pages),extractable_characters=len(text),diagram='vector architecture')
with zipfile.ZipFile(base.with_suffix('.docx')) as z:
 assert z.testzip() is None
 for n in z.namelist():ET.fromstring(z.read(n))
 assert '26. Appendices' in z.read('word/document.xml').decode()
checks[base.with_suffix('.docx').name].update(zip_crc='passed',xml_parts='parsed',diagram='editable textual architecture; Mermaid remains in Markdown')
(root/'docs/evidence/final-audit-20261028/report-exports.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks))
