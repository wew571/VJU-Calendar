from pathlib import Path
from datetime import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as E

SOURCE=Path(__file__).resolve().parent
REPO=SOURCE.parents[1]

def main():
    work=REPO/'work'/'sprint1-tests'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    isolated=work/'isolated-app'
    evidence=work/'evidence'
    evidence.mkdir(parents=True)
    shutil.copytree(REPO/'webapp',isolated/'webapp',ignore=shutil.ignore_patterns('__pycache__','*.json','*.xlsx','*.log'))
    (isolated/'config').mkdir()
    for kind in ['backend','frontend']:
        source=REPO/'config'/f'{kind}.json'
        if not source.is_file(): source=REPO/'config'/f'{kind}-example.json'
        shutil.copy2(source,isolated/'config'/f'{kind}.json')
    shutil.copy2(REPO/'main.py',isolated/'main.py')
    (isolated/'test').mkdir()
    shutil.copytree(REPO/'test/backend',isolated/'test/backend',ignore=shutil.ignore_patterns('__pycache__'))
    for source in [REPO/'test/conftest.py',REPO/'test/runtests.py']:
        shutil.copy2(source,isolated/'test'/source.name)
    env={**os.environ,'VJU_SPRINT1_WORKDIR':str(work),'PYTHONIOENCODING':'utf-8'}
    node=shutil.which('node.exe') or shutil.which('node')
    if not node: raise RuntimeError('Node.js is required.')
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()
    commands=[]
    def run(label,command,cwd):
        print(label,flush=True)
        output=evidence/(label+'.txt')
        with output.open('w',encoding='utf-8') as stream:
            result=subprocess.run(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,check=False)
        commands.append({'name':label,'command':command,'cwd':str(cwd),'exitCode':result.returncode,'output':output.name})
        return result.returncode,output
    run('acceptance-api',[sys.executable,'-X','utf8',str(SOURCE/'acceptance_backend.py')],REPO)
    run('api-suite',[sys.executable,'-X','utf8','test/runtests.py'],isolated)
    run('pytest',[sys.executable,'-X','utf8','-m','pytest','test','-q','--basetemp=pytest-temp',f'--junitxml={evidence / "pytest-results.xml"}'],isolated)
    # All pre-existing frontend regression tests plus the new S1-23 tests.
    # Sprint 2 acceptance tests are outside the Sprint 1 delivery scope.
    files=sorted(p for p in (REPO/'test').rglob('*.test.*') if 'sprint2-' not in p.name)
    file_args=[os.path.relpath(p,REPO/'frontend').replace('\\','/') for p in files]
    excluded=sorted(str(p.relative_to(REPO)) for p in (REPO/'test').rglob('sprint2-*.test.*'))
    vitest=[node,str(REPO/'frontend/node_modules/vitest/vitest.mjs'),'run']
    run('save-confirm-tests',[*vitest,'../test/sprint1/save-confirm.test.jsx','--reporter=verbose','--reporter=json',f'--outputFile={evidence / "save-confirm-results.json"}'],REPO/'frontend')
    run('frontend-tests',[*vitest,*file_args,'--reporter=verbose','--reporter=json',f'--outputFile={evidence / "frontend-results.json"}'],REPO/'frontend')
    api_text=(evidence/'api-suite.txt').read_text(encoding='utf-8')
    match=re.search(r'KẾT QUẢ TỔNG THỂ:\s*(\d+)/(\d+)',api_text)
    api={'passed':int(match[1]),'total':int(match[2])} if match else {'passed':0,'total':0}
    api['failed']=api['total']-api['passed']
    root=E.parse(evidence/'pytest-results.xml').getroot()
    suites=list(root) if root.tag=='testsuites' else [root]
    pytest={key:sum(int(suite.get(key,'0')) for suite in suites) for key in ['tests','failures','errors','skipped']}
    frontend=json.loads((evidence/'frontend-results.json').read_text(encoding='utf-8'))
    confirm=json.loads((evidence/'save-confirm-results.json').read_text(encoding='utf-8'))
    acceptance=json.loads((evidence/'acceptance-results.json').read_text(encoding='utf-8'))
    summary={'commit':commit,'runTime':datetime.now().astimezone().isoformat(),'workDir':str(work),'evidenceDir':str(evidence),'apiAcceptance':{'passed':sum(item['status']=='PASS' for item in acceptance),'total':len(acceptance)},'REG-01':api,'REG-02':pytest,'REG-03':{'passed':frontend['numPassedTests'],'failed':frontend['numFailedTests'],'total':frontend['numTotalTests'],'files':file_args,'excludedOutsideSprint':excluded},'S1-23':{'passed':confirm['numPassedTests'],'failed':confirm['numFailedTests'],'total':confirm['numTotalTests']},'commands':commands}
    (work/'run-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['commands','REG-03']},ensure_ascii=False,indent=2))
    print('Frontend:',frontend['numPassedTests'],'PASS,',frontend['numFailedTests'],'FAIL')
    return 1 if any(command['exitCode'] for command in commands) or not api['total'] or api['failed'] else 0

if __name__=='__main__':
    raise SystemExit(main())
