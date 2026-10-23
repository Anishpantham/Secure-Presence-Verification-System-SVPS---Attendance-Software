"""Build only the new final deliverables; preserve the prior release artifacts."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile
from pypdf import PdfReader
import package_submission as render

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'release/final'
DOCS=ROOT/'docs'


def source_files():
    excluded={'.git','.venv','node_modules','.pytest_cache','__pycache__','.expo','.runtime','dist','artifacts','release','work','test-results','playwright-report','build','.gradle','.cxx','.kotlin'}
    files=[]
    for directory,dirs,names in os.walk(ROOT):
        relative=Path(directory).relative_to(ROOT)
        dirs[:]=[d for d in dirs if d not in excluded and not (relative==Path('mobile') and d in ('android','ios'))]
        for name in names:
            path=Path(directory)/name
            if name=='.env' or name.startswith('.env.') and name!='.env.example':continue
            if name.endswith(('.pyc','.log','.db','.tsbuildinfo','.keystore','.jks')) or name=='work-baseline.xml':continue
            if path.is_symlink():continue
            files.append(path)
    return sorted(files)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sheet=render.styles()
    reports=['PROJECT_REPORT.md','CROSS_PLATFORM_IMPLEMENTATION.md','SYSTEM_ARCHITECTURE.md','DATABASE_DESIGN.md','API_DOCUMENTATION.md','BIOMETRIC_DESIGN.md','SECURITY_ARCHITECTURE.md','THREAT_MODEL.md','TEST_RESULTS.md','REQUIREMENTS_TRACEABILITY.md','KNOWN_LIMITATIONS.md','FINAL_COMPLETION_REPORT.md','REFERENCES.md']
    render.render_pdf(OUT/'SPVS_FINAL_PROJECT_REPORT.pdf',[DOCS/name for name in reports],sheet)
    render.render_pdf(OUT/'SPVS_FINAL_SETUP_AND_DEMO_GUIDE.pdf',[DOCS/name for name in ['SETUP_AND_DEMO_GUIDE.md','DEPLOYMENT_GUIDE.md','USER_MANUAL.md','DEMO_SCRIPT.md','TEST_RESULTS.md']],sheet)
    for name in ['SPVS_FINAL_VERIFICATION_REPORT.md','SPVS_FINAL_DELIVERY_README.md']:
        shutil.copy2(ROOT/name,OUT/name)
    manifest=DOCS/'FINAL_FILE_MANIFEST.txt'
    files=source_files()
    manifest.write_text('\n'.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}' for p in files if p!=manifest)+'\n')
    archive=OUT/'SPVS_FINAL_COMPLETE_PROJECT.zip'
    files=source_files()
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files:z.write(path,'spvs-root/'+str(path.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        required=['backend/app/main.py','backend/app/services/app_attest.py','backend/alembic/versions/5c9d2a1e8b70_cross_platform_security.py','dashboard/src/App.tsx','mobile/App.tsx','mobile/modules/spvs-security/ios/SpvsSecurityModule.swift','mobile/modules/spvs-security/android/src/main/java/edu/spvs/security/SpvsSecurityModule.kt','mobile/modules/spvs-wifi/ios/SpvsWifiModule.swift','mobile/package-lock.json','docs/CROSS_PLATFORM_IMPLEMENTATION.md','docs/FINAL_COMPLETION_REPORT.md','models/face_landmarker.task','models/face_recognition_sface_2021dec.onnx']
        assert all('spvs-root/'+name in z.namelist() for name in required)
        assert not any('/node_modules/' in name or '/.venv/' in name or '/.runtime/' in name or name.endswith(('/.env','.keystore','.jks')) for name in z.namelist())
    checks={'zip_crc':'passed','archive_members':len(files),'required_source_files':'passed','pdfs':{}}
    for path in OUT.glob('SPVS_FINAL_*.pdf'):
        pdf=PdfReader(path);text='\n'.join(page.extract_text() or '' for page in pdf.pages)
        assert len(pdf.pages)>=5 and 'SPVS' in text and len(text)>4000
        checks['pdfs'][path.name]={'pages':len(pdf.pages),'extractable_characters':len(text),'readable':True}
    checks['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.glob('SPVS_*') if p.is_file()}
    (OUT/'artifact-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
