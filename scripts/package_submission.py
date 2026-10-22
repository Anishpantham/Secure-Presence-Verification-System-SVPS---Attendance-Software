"""Render the actual project documentation and package verified source artifacts.

This packages existing files; it does not generate the application or fabricate tests.
Run with: bash scripts/backend.sh python ../scripts/package_submission.py
"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import html
import json
import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET

from pypdf import PdfReader
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
                               Preformatted, Image, KeepTogether)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
DOCS = ROOT / "docs"
TEAL = colors.HexColor("#17695b")
INK = colors.HexColor("#19372e")
MUTED = colors.HexColor("#658172")
PALE = colors.HexColor("#edf4ef")
STAMP = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST")


def test_counts(path):
    if not path.exists():
        return None
    cases = ET.parse(path).findall(".//testcase")
    failed = sum(c.find("failure") is not None or c.find("error") is not None for c in cases)
    skipped = sum(c.find("skipped") is not None for c in cases)
    return len(cases) - failed - skipped, failed, skipped


def evidence_docs():
    suites = [
        ("Backend / PostgreSQL (includes real-model tests)", "backend-tests.xml", "bash scripts/backend.sh pytest --junitxml=../artifacts/backend-tests.xml"),
        ("Dashboard interactions", "dashboard-tests.xml", "cd dashboard && npm test -- --run --reporter=junit --outputFile=../artifacts/dashboard-tests.xml"),
        ("Mobile protocol and UI logic", "mobile-tests.xml", "cd mobile && npm test -- --run --reporter=junit --outputFile=../artifacts/mobile-tests.xml"),
        ("Chromium against running containers", "browser-tests.xml", "cd dashboard && npx playwright test"),
    ]
    rows = []
    commands = []
    totals = [0, 0, 0]
    for label, name, command in suites:
        counts = test_counts(OUT / name)
        if counts is None:
            rows.append(f"| {label} | UNRUN | — | — | Linux x86_64 |")
        else:
            rows.append(f"| {label} | {counts[0]} | {counts[1]} | {counts[2]} | Linux x86_64 |")
            totals = [a+b for a, b in zip(totals, counts)]
        commands.append(f"- `{command}`")
    table = "| Suite | Passed | Failed/errors | Skipped | Execution platform |\n|---|---:|---:|---:|---|\n" + "\n".join(rows)
    status_path = OUT / "build-status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    build_table = "| Capability | Observed outcome |\n|---|---|\n" + "\n".join(
        f"| {name} | {value} |" for name, value in status.items())
    audits = []
    for name in ("backend", "dashboard", "mobile"):
        path = OUT / f"{name}-audit.json"
        if not path.exists():
            audits.append(f"- {name}: audit not run.")
            continue
        data = json.loads(path.read_text())
        if name == "backend":
            count = sum(bool(d.get("vulns")) for d in data.get("dependencies", []))
            audits.append(f"- Backend: {count} runtime packages with reported vulnerabilities in the locked-requirements audit.")
        else:
            info = data.get("metadata", {}).get("vulnerabilities", {})
            audits.append(f"- {name.title()}: {info.get('total', 'unknown')} affected package entries ({info.get('critical', 0)} critical, {info.get('high', 0)} high, {info.get('moderate', 0)} moderate, {info.get('low', 0)} low).")
    notes = (
        "The backend's four real-model smoke cases are included in its total, not counted twice. "
        "Its API transaction happy paths explicitly substitute vision inside pytest fixtures; they do not prove live human capture. "
        "Real-model smoke tests execute the current YuNet, SFace and MediaPipe Tasks pipeline. "
        "No physical phone, iOS device, macOS ARM64 run, provider-backed attestation or population biometric evaluation was performed.\n\n"
        "The mobile audit's affected entries propagate two root advisories through the Expo/Metro tree: "
        "GHSA-vfj7-8cjw-p6xm (`braces`) and GHSA-86w9-cpqp-85rv (`node-forge`). "
        "The registry reported no fixed version. See `KNOWN_LIMITATIONS.md`; do not interpret build success as security certification."
    )
    results = f"""# Test and build results

Generated from actual result files at **{STAMP}**. JUnit timestamps reflect the Linux runner clock.

{table}

Unique suite totals: **{totals[0]} passed, {totals[1]} failed/errors, {totals[2]} skipped**.

## Commands executed

{chr(10).join(commands)}

## Build and runtime validation

{build_table}

## Dependency audits

{chr(10).join(audits)}

Audit commands: `npm audit --json` in each client; `pip-audit -r .runtime/backend-requirements.txt --format json` using requirements exported from `backend/uv.lock`. Raw reports are in `docs/evidence`.

## Interpretation and unverified behavior

{notes}

No manual sensor or live-biometric success is claimed. Intermediate failures included a missing graphics runtime, cloud CA trust configuration, older dependency advisories and test locator/assertion errors; these were diagnosed before the recorded final successful checks. Any still-blocked native capability appears in the build table.
"""
    (DOCS / "TEST_RESULTS.md").write_text(results)
    verification = f"""# SPVS engineering verification report

Generated **{STAMP}** from the actual workspace and test outputs.

## Delivery status

Actual application source, PostgreSQL migration, clients, tests, model-download configuration, documentation and packaging tools exist. This is a production-inspired college project. Hardware validation and configured platform attestation remain outstanding; the mobile dependency advisories below remain unresolved. Read those limits before treating this as a deployable institutional system.

## Tests

{table}

Total: **{totals[0]} passed, {totals[1]} failed/errors, {totals[2]} skipped**.

{chr(10).join(commands)}

## Builds and startup

{build_table}

## What was verified

- Real PostgreSQL migration and schema constraints, authentication and backend role scope.
- Course/enrollment/classroom workflows, session creation/closure and actual dashboard-to-API integration.
- Refresh-token rotation/reuse, evidence HMAC verification, device reset/revocation, replay, idempotency and concurrent duplicate protection.
- Server-side geofence, accuracy/freshness, Wi-Fi fallback, explainable anomalies, disputes and correction auditing.
- Real model-generated 128-dimensional embeddings, same-person variation, different-person rejection and no/multiple-face rejection on public test portraits.
- Server temporal-liveness sequence/timing rules on unit inputs; no client-supplied successful liveness verdict is trusted.
- Dashboard forms and role navigation, actual browser session lifecycle/CSV export, mobile TypeScript/signing logic and Android JavaScript bundle.

## Verification boundaries

{notes}

## Dependency audits

{chr(10).join(audits)}

## Files and artifacts

The source ZIP is `SPVS_COMPLETE_PROJECT.zip`. PDF outputs are `SPVS_PROJECT_REPORT.pdf` and `SPVS_SETUP_AND_DEMO_GUIDE.pdf`. The archive contains source, locks, migrations, documentation, audit/test evidence and the verified pretrained model assets. It excludes secrets, node_modules, Python virtual environments, camera samples, native generated folders and database contents. `docs/FILE_MANIFEST.txt` lists packaged source files with SHA-256 values (excluding the manifest itself). PDF readability, ZIP CRCs and required members are checked by `scripts/package_submission.py`; `artifacts/artifact-checks.json` records those checks.

## Remaining work

1. Run and document the real-device matrix in `docs/TESTING_STRATEGY.md`, including live enrollment/attendance, spoof attempts, direction/blink timing and actual Android Wi-Fi measurements.
2. Configure Google/Apple provider verification only with real developer-account settings; current verdicts remain unverified.
3. Calibrate face/liveness thresholds on consented local evaluation data and establish accessible review alternatives.
4. Resolve upstream Expo tooling advisories when patches become available; complete production TLS, secrets, backups, retention and operational hardening before real institutional use.
5. Fill the academic title-page placeholders and add only measurements actually collected.
"""
    (ROOT / "SPVS_VERIFICATION_REPORT.md").write_text(verification)
    (ROOT / "SPVS_DELIVERY_README.md").write_text("""# SPVS delivery

Start with `README.md` inside the ZIP or the setup/demo PDF.

- `SPVS_COMPLETE_PROJECT.zip` — actual backend, dashboard, mobile source, migration, tests, lockfiles, documentation, verified models and recorded evidence.
- `SPVS_PROJECT_REPORT.pdf` — editable-source college report with diagrams, implementation details and measured test evidence.
- `SPVS_SETUP_AND_DEMO_GUIDE.pdf` — installation, configuration, demonstration and troubleshooting instructions.
- `SPVS_VERIFICATION_REPORT.md` — exact validation results and remaining limits.
- `SPVS_DELIVERY_README.md` — this delivery map.

Unpack `spvs-root`, then run `make setup`, `make db`, `make migrate`, and `make seed`. Start the API and dashboard using separate `make api` and `make dashboard` terminals, or follow the Docker instructions. Local secrets and demo passwords are generated into `.env`; none are included here.

The project includes real face-model inference and server-side gates. Physical-phone verification, Apple Silicon runtime testing and external attestation are not claimed as completed. The current Expo dependency tree has two unpatched upstream advisories. Read the verification report before deployment or evaluation.

If an Android debug APK accompanies this delivery, it is a development build requiring Metro and a suitable API endpoint, not a production-signed release or evidence of physical-device testing.
""")
    evidence = DOCS / "evidence"
    evidence.mkdir(exist_ok=True)
    for pattern in ("*-tests.xml", "*-audit.json", "build-status.json"):
        for path in OUT.glob(pattern):
            shutil.copy2(path, evidence / path.name)


def arrow(drawing, x1, y1, x2, y2, label=None):
    import math
    drawing.add(Line(x1, y1, x2, y2, strokeColor=MUTED, strokeWidth=1))
    theta = math.atan2(y2-y1, x2-x1)
    length, width = 6, 3
    drawing.add(Polygon([x2, y2, x2-length*math.cos(theta)+width*math.sin(theta), y2-length*math.sin(theta)-width*math.cos(theta),
                         x2-length*math.cos(theta)-width*math.sin(theta), y2-length*math.sin(theta)+width*math.cos(theta)], fillColor=MUTED, strokeColor=MUTED))
    if label:
        drawing.add(String((x1+x2)/2, (y1+y2)/2+5, label, fontName="Body", fontSize=7, fillColor=MUTED, textAnchor="middle"))


def box(d, x, y, w, h, text, dark=False):
    d.add(Rect(x, y, w, h, rx=5, ry=5, fillColor=INK if dark else PALE, strokeColor=TEAL, strokeWidth=.6))
    lines = text.split("\n")
    for i, line in enumerate(lines):
        d.add(String(x+w/2, y+h/2+(len(lines)-1)*5-i*10-3, line, fontName="Body-Bold" if dark else "Body",
                     fontSize=8, fillColor=colors.white if dark else INK, textAnchor="middle"))


def diagram(kind):
    if kind == "architecture":
        d = Drawing(480, 270)
        box(d, 0, 220, 140, 40, "Student mobile\nCamera / location / secure key")
        box(d, 340, 220, 140, 40, "Faculty / admin dashboard\nAcademic workflows")
        box(d, 165, 145, 150, 50, "FastAPI /api/v1\nAuthentication + scope", True)
        arrow(d, 70, 220, 165, 175); arrow(d, 410, 220, 315, 175)
        box(d, 0, 65, 190, 50, "Layer 1: identity\nYuNet + SFace + MediaPipe\nSigned device evidence")
        box(d, 290, 65, 190, 50, "Layer 2: physical presence\nGPS uncertainty + geofence\nWi-Fi + explainable rules")
        arrow(d, 195, 145, 95, 115); arrow(d, 285, 145, 385, 115)
        box(d, 145, 0, 190, 40, "PostgreSQL\nAttempts / records / audit", True)
        arrow(d, 95, 65, 170, 40); arrow(d, 385, 65, 310, 40)
    elif kind == "sequence":
        d = Drawing(480, 330)
        cols = [35, 175, 315, 445]
        for x, label in zip(cols, ["Student app", "FastAPI", "Vision", "PostgreSQL"]):
            d.add(String(x, 316, label, fontName="Body-Bold", fontSize=8, fillColor=INK, textAnchor="middle"))
            d.add(Line(x, 304, x, 8, strokeColor=colors.HexColor("#c7d6cc"), strokeDashArray=[3, 3]))
        for y, a, b, label in [(287,0,1,"Request bound challenge"),(260,1,3,"Check eligibility"),(233,1,0,"Actions + expiry + clock"),(206,0,1,"Signed frames and signals"),(179,1,3,"Lock / replay checks"),(152,1,2,"Embed and analyze sequence"),(125,2,1,"Match / liveness result"),(98,1,3,"Consume challenge + attempt"),(71,1,3,"Unique record if PRESENT"),(37,1,0,"Decision + reasons")]:
            arrow(d, cols[a], y, cols[b], y, label)
    elif kind == "decision":
        d = Drawing(480, 330)
        for y, label in [(280,"Authenticate and validate signature"),(215,"Session / enrollment / challenge / device"),(150,"Face matching and temporal liveness"),(85,"Fresh GPS and geofence evidence"),(20,"Wi-Fi / uncertainty / policy evaluation")]:
            box(d, 0, y, 255, 35, label)
            if y>20:arrow(d,127,y,127,y-30)
        box(d,320,210,155,45,"REJECTED / EXPIRED\nNo present record",True)
        arrow(d,255,232,320,232,'invalid')
        arrow(d,255,167,320,219,'failed')
        box(d,320,100,155,45,"REQUIRES_RETRY\nRecover evidence",True)
        arrow(d,255,102,320,123,'poor GPS')
        box(d,320,30,155,45,"PRESENT or REVIEW\nOnly PRESENT creates record",True)
        arrow(d,255,37,320,50)
    else:
        d = Drawing(480, 350)
        nodes = {'users':(0,300),'faculty':(170,300),'courses':(340,300),'students':(0,220),'enrollments':(170,220),
                 'sessions':(340,220),'devices':(0,140),'challenges':(170,140),'classrooms':(340,140),
                 'biometrics':(0,60),'attempts':(170,60),'records':(340,60)}
        for name,(x,y) in nodes.items():box(d,x,y,135,35,name)
        for a,b in [('users','faculty'),('faculty','courses'),('users','students'),('students','enrollments'),('courses','sessions'),('students','devices'),('devices','challenges'),('sessions','classrooms'),('challenges','attempts'),('attempts','records'),('students','biometrics')]:
            x,y=nodes[a];u,v=nodes[b]
            if (a,b)==('students','biometrics'):
                d.add(Line(x,y+17,-8,y+17,strokeColor=MUTED))
                d.add(Line(-8,y+17,-8,v+17,strokeColor=MUTED))
                arrow(d,-8,v+17,u,v+17)
            elif x==u:arrow(d,x+67,y,u+67,v+35)
            else:arrow(d,x+135,y+17,u,v+17)
        d.add(String(240,15,"Core foreign-key relationships; full schema and remaining tables listed in the database chapter.",fontName="Body",fontSize=7,fillColor=MUTED,textAnchor="middle"))
    return d


def inline(text):
    value = html.escape(text)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font face="Mono" size="8">\1</font>', value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    return value


def styles():
    candidates = [Path("/usr/share/fonts/truetype/dejavu"),Path("/Library/Fonts")]
    fontdir = next((p for p in candidates if (p/"DejaVuSans.ttf").exists()),None)
    if fontdir:
        for name, filename in [("Body","DejaVuSans.ttf"),("Body-Bold","DejaVuSans-Bold.ttf"),("Mono","DejaVuSansMono.ttf")]:
            pdfmetrics.registerFont(TTFont(name,str(fontdir/filename)))
        pdfmetrics.registerFontFamily("Body",normal="Body",bold="Body-Bold",italic="Body",boldItalic="Body-Bold")
    else:
        pdfmetrics.registerFont(pdfmetrics.Font("Body","Helvetica","WinAnsiEncoding"))
        pdfmetrics.registerFont(pdfmetrics.Font("Body-Bold","Helvetica-Bold","WinAnsiEncoding"))
        pdfmetrics.registerFont(pdfmetrics.Font("Mono","Courier","WinAnsiEncoding"))
        pdfmetrics.registerFontFamily("Body",normal="Body",bold="Body-Bold",italic="Body",boldItalic="Body-Bold")
    sheet=getSampleStyleSheet()
    sheet.add(ParagraphStyle(name="P",fontName="Body",fontSize=9,leading=14,textColor=INK,spaceAfter=8))
    sheet.add(ParagraphStyle(name="H1",fontName="Body-Bold",fontSize=22,leading=29,textColor=INK,spaceBefore=8,spaceAfter=18,keepWithNext=True))
    sheet.add(ParagraphStyle(name="H2",fontName="Body-Bold",fontSize=13,leading=19,textColor=TEAL,spaceBefore=15,spaceAfter=8,keepWithNext=True))
    sheet.add(ParagraphStyle(name="H3",fontName="Body-Bold",fontSize=10,leading=15,textColor=INK,spaceBefore=10,spaceAfter=6,keepWithNext=True))
    sheet.add(ParagraphStyle(name="Cell",fontName="Body",fontSize=7,leading=10,textColor=INK,spaceAfter=0))
    sheet.add(ParagraphStyle(name="CodeBlock",fontName="Mono",fontSize=7,leading=10,textColor=INK,backColor=PALE,borderPadding=8,spaceAfter=12))
    return sheet


def markdown_flow(path,sheet):
    lines=path.read_text().splitlines();flow=[];paragraph=[];index=0
    def flush():
        if paragraph:
            flow.append(Paragraph(inline(" ".join(paragraph)),sheet['P']));paragraph.clear()
    while index<len(lines):
        line=lines[index]
        if line.startswith('```'):
            flush();language=line[3:];block=[];index+=1
            while index<len(lines) and not lines[index].startswith('```'):
                block.append(lines[index]);index+=1
            if language=='mermaid':
                source='\n'.join(block)
                kind='sequence' if 'sequenceDiagram' in source else 'er' if 'erDiagram' in source else 'decision' if 'flowchart TD' in source else 'architecture'
                flow.extend([diagram(kind),Spacer(1,12)])
            else:
                for start in range(0,len(block),24):
                    flow.append(Preformatted('\n'.join(block[start:start+24]),sheet['CodeBlock'],maxLineLength=88))
        elif line.startswith('|'):
            flush();rows=[]
            while index<len(lines) and lines[index].startswith('|'):
                cells=[x.strip() for x in lines[index].strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',x) for x in cells):rows.append([Paragraph(inline(x),sheet['Cell']) for x in cells])
                index+=1
            index-=1
            if rows:
                columns=max(map(len,rows));rows=[row+[Paragraph('',sheet['Cell'])]*(columns-len(row)) for row in rows]
                table=Table(rows,colWidths=[480/columns]*columns,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfece3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8f6')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),.6,TEAL)]))
                flow.extend([table,Spacer(1,12)])
        elif line.startswith('#'):
            flush()
            if path.name == 'PROJECT_REPORT.md' and line == '## Abstract':
                flow.append(PageBreak())
            level=len(line)-len(line.lstrip('#'));flow.append(Paragraph(inline(line.lstrip('#').strip()),sheet[f'H{min(level,3)}']))
        elif not line.strip():flush()
        elif re.match(r'^(- |\d+\. )',line):
            flush();flow.append(Paragraph(inline(line),sheet['P']))
        else:paragraph.append(line)
        index+=1
    flush();return flow


def footer(canvas,doc):
    canvas.saveState();width,height=A4
    canvas.setStrokeColor(colors.HexColor('#d5e2d8'));canvas.line(48,43,width-48,43)
    canvas.setFont('Body',8);canvas.setFillColor(MUTED)
    canvas.drawString(48,29,'SPVS · Secure Presence Verification System')
    canvas.drawRightString(width-48,29,str(doc.page));canvas.restoreState()


def render_pdf(target,files,sheet):
    doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=60,title=files[0].stem.replace('_',' '),author='SPVS project')
    flow=[]
    for index,path in enumerate(files):
        if index:flow.append(PageBreak())
        flow.extend(markdown_flow(path,sheet))
        if path.name=='PROJECT_REPORT.md' and (OUT/'dashboard-overview.png').exists():
            flow.append(PageBreak());flow.append(Paragraph('Application evidence · actual dashboard',sheet['H1']))
            image=Image(str(OUT/'dashboard-overview.png'));image.drawHeight=480*image.imageHeight/image.imageWidth;image.drawWidth=480
            flow.extend([image,Spacer(1,10),Paragraph('Actual browser screenshot from the evaluated workspace. Counts reflect real demo activity; no attendance was fabricated.',sheet['P'])])
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)


def source_files():
    excluded={'.git','.venv','node_modules','.pytest_cache','__pycache__','.expo','.runtime','dist','artifacts','test-results','playwright-report','build','.gradle'}
    files=[]
    for directory,dirs,names in os.walk(ROOT):
        relative=Path(directory).relative_to(ROOT)
        dirs[:]=[d for d in dirs if d not in excluded and not (relative==Path('mobile') and d in ('android','ios'))]
        for name in names:
            path=Path(directory)/name
            if name=='.env' or name.startswith('.env.') and name!='.env.example' or name.endswith(('.pyc','.log','.db','.tsbuildinfo')):
                continue
            if path.is_symlink():continue
            files.append(path)
    return sorted(files)


def main():
    OUT.mkdir(exist_ok=True);evidence_docs();sheet=styles()
    diagrams=DOCS/'diagrams';diagrams.mkdir(exist_ok=True)
    for kind in ['architecture','sequence','decision','er']:
        renderSVG.drawToFile(diagram(kind),str(diagrams/(kind+'.svg')))
    report_files=['PROJECT_REPORT.md','SYSTEM_ARCHITECTURE.md','DATABASE_DESIGN.md','API_DOCUMENTATION.md','BIOMETRIC_DESIGN.md','SECURITY_ARCHITECTURE.md','THREAT_MODEL.md','TEST_RESULTS.md','REQUIREMENTS_TRACEABILITY.md','KNOWN_LIMITATIONS.md','REFERENCES.md']
    render_pdf(OUT/'SPVS_PROJECT_REPORT.pdf',[DOCS/name for name in report_files],sheet)
    render_pdf(OUT/'SPVS_SETUP_AND_DEMO_GUIDE.pdf',[DOCS/name for name in ['SETUP_AND_DEMO_GUIDE.md','DEPLOYMENT_GUIDE.md','USER_MANUAL.md','DEMO_SCRIPT.md','TEST_RESULTS.md']],sheet)
    for name in ['SPVS_VERIFICATION_REPORT.md','SPVS_DELIVERY_README.md']:
        shutil.copy2(ROOT/name,OUT/name)
    files=source_files()
    manifest=DOCS/'FILE_MANIFEST.txt'
    manifest.write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}' for p in files if p!=manifest)+'\n')
    files=source_files()
    archive=OUT/'SPVS_COMPLETE_PROJECT.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipped:
        for path in files:zipped.write(path,'spvs-root/'+str(path.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None,'Archive CRC failure'
        required=['README.md','backend/app/main.py','backend/uv.lock','dashboard/src/App.tsx','dashboard/package-lock.json','mobile/App.tsx','mobile/package-lock.json','docs/PROJECT_REPORT.md','docs/openapi.json','SPVS_VERIFICATION_REPORT.md','models/face_recognition_sface_2021dec.onnx','models/face_landmarker.task']
        assert all('spvs-root/'+p in zipped.namelist() for p in required),'Required archive content missing'
        assert not any(p.endswith('/.env') or '/node_modules/' in p or '/.venv/' in p for p in zipped.namelist())
    checks={'created_at':STAMP,'zip_crc':'passed','archive_members':len(files),'pdfs':{}}
    for path in OUT.glob('SPVS_*.pdf'):
        pdf=PdfReader(path);text='\n'.join(page.extract_text() or '' for page in pdf.pages)
        assert len(pdf.pages)>=5 and 'SPVS' in text and len(text)>3000,'PDF is not readable'
        checks['pdfs'][path.name]={'pages':len(pdf.pages),'extractable_characters':len(text),'readable':True}
    checks['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.glob('SPVS_*') if p.is_file()}
    (OUT/'artifact-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
