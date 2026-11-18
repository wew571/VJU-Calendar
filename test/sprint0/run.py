from pathlib import Path
from datetime import datetime
import argparse
import json
import os
import shutil
import subprocess
import sys

SOURCE=Path(__file__).resolve().parent
REPO=SOURCE.parents[1]

def main():
    parser=argparse.ArgumentParser(description='Run Sprint 0 checks against a fresh isolated copy.')
    parser.add_argument('--api-only',action='store_true',help='Run only the six API checks.')
    args=parser.parse_args()
    work=REPO/'work'/'sprint0-tests'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    work.mkdir(parents=True)
    env=os.environ.copy()
    env['VJU_SPRINT0_WORKDIR']=str(work)
    env['VJU_TEST_PYTHON']=sys.executable
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True,check=False)
    env['VJU_TEST_COMMIT']=commit.stdout.strip() or 'unknown'

    def run(label,command,cwd):
        output=work/(label+'.txt')
        print(label,flush=True)
        with output.open('w',encoding='utf-8') as stream:
            result=subprocess.run(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,check=False)
        return result.returncode,output

    code,output=run('backend-output',[sys.executable,'-X','utf8',str(SOURCE/'acceptance_backend.py')],REPO)
    if code:
        print('API execution failed. See:',output)
        return code
    backend=json.loads((work/'evidence/backend-results.json').read_text(encoding='utf-8'))
    browser=[]
    if not args.api_only:
        node=shutil.which('node.exe') or shutil.which('node')
        if not node:
            print('Node.js executable was not found.')
            return 2
        code,output=run('build',[node,str(REPO/'frontend/node_modules/vite/bin/vite.js'),'build','--outDir',str(work/'isolated-app/frontend/dist')],REPO/'frontend')
        if code:
            print('Frontend build failed. See:',output)
            return code
        code,output=run('browser-output',[node,str(SOURCE/'browser-checks.mjs')],REPO)
        results=work/'evidence/browser-results.json'
        if not results.is_file():
            print('Browser execution did not produce results. See:',output)
            return code or 2
        browser=json.loads(results.read_text(encoding='utf-8'))
        if code not in [0,1]:
            print('Browser execution failed. See:',output)
            return code
    summary={
        'commit':env['VJU_TEST_COMMIT'],'workDir':str(work),
        'api':{'passed':sum(item['status']=='PASS' for item in backend),'failed':sum(item['status']=='FAIL' for item in backend)},
        'browser':{'passed':sum(item['status']=='PASS' for item in browser),'failed':sum(item['status']=='FAIL' for item in browser)},
        'scope':'Executed checks only; this does not replace the twenty-case Test Log or its manual/blocked cases.',
    }
    (work/'run-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 1 if summary['api']['failed'] or summary['browser']['failed'] else 0

if __name__=='__main__':
    raise SystemExit(main())
