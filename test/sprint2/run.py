from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib,json,re,shutil,subprocess,sys

SOURCE=Path(__file__).resolve().parent
REPO=SOURCE.parents[1]

def main():
    mapping=json.loads((SOURCE/'cases.json').read_text(encoding='utf-8'))
    cases={item['id']:dict(item) for item in mapping['cases']}
    assert len(cases)==61
    node=shutil.which('node.exe') or shutil.which('node')
    if not node: raise RuntimeError('Node.js is required.')
    work=REPO/'work'/'sprint2-tests'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    evidence=work/'evidence'
    evidence.mkdir(parents=True)
    files=[SOURCE/name for name in sorted({item['testFile'] for item in cases.values() if item['testFile']})]
    regression=[REPO/'test/frontend/ManualEntryPage.search-state.test.jsx',REPO/'test/frontend/ManualEntryPage.bo-chot.test.jsx']
    paths=[str(path.relative_to(REPO/'test')).replace('\\','/') for path in files+regression]
    command=[node,str(REPO/'frontend/node_modules/vitest/vitest.mjs'),'run',*['../test/'+name for name in paths],'--reporter=verbose','--reporter=json',f'--outputFile={evidence / "test-results.json"}']
    print('Sprint 2: 14 acceptance checks and 4 component regression checks.',flush=True)
    with (evidence/'test-output.txt').open('w',encoding='utf-8') as output:
        result=subprocess.run(command,cwd=REPO/'frontend',stdout=output,stderr=subprocess.STDOUT,check=False)
    report=evidence/'test-results.json'
    if not report.is_file():
        print('No report produced. See:',evidence/'test-output.txt')
        return result.returncode or 2
    results=json.loads(report.read_text(encoding='utf-8'))
    executed={}
    regression_results=[]
    for suite in results['testResults']:
        for test in suite['assertionResults']:
            match=re.match(r'(S2-B\d{2}-\d{2}):',test['title'])
            if match:
                identifier=match[1]
                assert identifier in cases and identifier not in executed
                executed[identifier]={'status':test['status'],'title':test['title'],'source':str(Path(suite['name']).relative_to(REPO)).replace('\\','/'),'errorSummary':' '.join(test.get('failureMessages',[])).splitlines()[0][:260] if test.get('failureMessages') else ''}
            else:regression_results.append({'title':test['title'],'status':test['status'],'source':str(Path(suite['name']).relative_to(REPO)).replace('\\','/')})
    assert set(executed)=={item['id'] for item in cases.values() if item['testFile']}
    for identifier,entry in cases.items():
        entry['execution']=executed.get(identifier)
        entry['status']=executed[identifier]['status'].upper() if identifier in executed else 'NOT_RUN'
    counts=dict(Counter(entry['status'] for entry in cases.values()))
    assert counts.get('NOT_RUN')==47
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()
    source_files=files+[SOURCE/'cases.json',SOURCE/'run.py',REPO/'frontend/src/App.jsx',REPO/'frontend/src/adapters/urlState.js',REPO/'frontend/src/presentation/pages/ManualEntryPage.jsx',REPO/'frontend/src/presentation/pages/GuidePage.jsx']
    summary={'commit':commit,'runTime':datetime.now().astimezone().isoformat(),'workDir':str(work),'evidenceDir':str(evidence),'command':command,'caseCounts':counts,'executedCases':len(executed),'partialCases':sum(entry['coverage']=='AUTOMATED_PARTIAL' for entry in cases.values()),'regression':dict(Counter(entry['status'] for entry in regression_results)),'sourceHashes':[{'path':str(path.relative_to(REPO)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in source_files],'caseSources':mapping['sources'],'scope':'Component/App shell in jsdom; six cases cover only part of their plan steps. No API/DB or browser E2E claims.'}
    (work/'run-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (evidence/'case-results.json').write_text(json.dumps(list(cases.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Kết quả kiểm thử Sprint 2','',f'Lần chạy: {summary["runTime"]}. Commit: {commit}.','',f'14 bài tự động: {counts.get("PASSED",0)} PASS, {counts.get("FAILED",0)} FAIL. 47 ca chưa chạy. Sáu ca mới kiểm tra một phần.','',
           '| Mã ca | Nội dung | Phạm vi | Kết quả |','|---|---|---|---|']
    for entry in cases.values():
        level='Một phần' if entry['coverage']=='AUTOMATED_PARTIAL' else 'Component' if entry['testFile'] else 'Chờ bàn giao/kiểm tra thủ công'
        lines.append(f'| {entry["id"]} | {entry["title"]} | {level} | {entry["status"]} |')
    lines+=['','PASS một phần chưa kết luận toàn bộ ca/AC đạt. Các ca CSDL, quyền, nhiều người dùng, migration và vận hành vẫn cần bàn giao hoặc hồ sơ tương ứng.','']
    (evidence/'coverage.md').write_text('\n'.join(lines),encoding='utf-8')
    failures=['# Các ca tự động chưa đạt','', 'Bảng ghi lỗi kiểm thử để Dev đối chiếu; không tự sửa chức năng sản phẩm.','', '| Mã ca | Kiểm tra | Quan sát |','|---|---|---|']
    for identifier,entry in executed.items():
        if entry['status']=='failed': failures.append('| '+identifier+' | '+cases[identifier]['title']+' | '+entry['errorSummary'].replace('|','/').replace('\n',' ')+' |')
    failures+=['','Bước chạy, dữ liệu và kết quả mong đợi đối chiếu Test Plan theo mã ca. Stack trace đầy đủ có trong test-results.json và test-output.txt.','']
    (evidence/'failures.md').write_text('\n'.join(failures),encoding='utf-8')
    print(json.dumps({key:summary[key] for key in ['workDir','caseCounts','partialCases','regression']},ensure_ascii=False,indent=2))
    return result.returncode or (1 if counts.get('FAILED',0) else 0)

if __name__=='__main__':
    raise SystemExit(main())
