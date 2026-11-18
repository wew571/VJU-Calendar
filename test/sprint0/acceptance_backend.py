from pathlib import Path
import copy, json, os, shutil, sys

REPO=Path(__file__).resolve().parents[2]
WORK=Path(os.environ.get('VJU_SPRINT0_WORKDIR',REPO/'work'/'sprint0-tests')).resolve()
if not WORK.is_relative_to((REPO/'work').resolve()):
    raise ValueError('Sprint 0 test outputs must stay inside the repository work/ folder.')
APP=WORK/'isolated-app'
EVIDENCE=WORK/'evidence'
EVIDENCE.mkdir(parents=True,exist_ok=True)
if not APP.exists():
    shutil.copytree(REPO/'webapp',APP/'webapp',ignore=shutil.ignore_patterns('__pycache__','*.json','*.xlsx','*.log'))
    (APP/'config').mkdir(exist_ok=True)
    shutil.copy2(REPO/'config/backend-example.json',APP/'config/backend.json')
sys.path.insert(0,str(APP/'webapp'))
from app import app
from state import STATE
from snapshot import save_snapshot
app.config['TESTING']=True
client=app.test_client()
results=[]
def save(name,obj):
    (EVIDENCE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def record(identifier,scope,passed,details):
    results.append({'id':identifier,'scope':scope,'status':'PASS' if passed else 'FAIL','details':details})
def post(url,body):
    response=client.post(url,json=body)
    assert response.status_code==200,(url,response.status_code,response.get_json())
    return response.get_json()
post('/api/manual/init',{})
good=post('/api/manual/course',{'code':'TEST101','name':'Kiểm thử phần mềm','credits':3})
course=next(c for c in good['courses'] if c['code']=='TEST101')
again=client.get('/api/data').get_json()
record('TC-11','API',any(c['name']=='Kiểm thử phần mềm' and c['credits']==3 for c in again['courses']),{'created':course,'readBack':again['courses']})
before=copy.deepcopy(STATE['data'])
invalid=[]
for value in ['abc','@@@','3abc']:
    response=client.post('/api/manual/course',json={'code':'BAD','name':'Không được lưu','credits':value})
    invalid.append({'value':value,'http':response.status_code,'body':response.get_json(),'unchanged':STATE['data']==before})
record('TC-12','API',all(x['http']==400 and x['unchanged'] and x['body'].get('error') for x in invalid),invalid)
response=client.patch(f'/api/manual/course/{course["id"]}',json={'credits':'abc'})
record('TC-14','API',response.status_code==400 and STATE['data']==before,{'http':response.status_code,'error':response.get_json(),'dataUnchanged':STATE['data']==before,'readBack':client.get('/api/data').get_json()['courses']})
special=[]
for value in ['@@@','<test>','   ']:
    response=client.post('/api/manual/course',json={'code':value,'name':value,'credits':3})
    special.append({'value':value,'http':response.status_code,'error':response.get_json().get('error')})
save('special-characters-observation.json',special)
# Reset to a dedicated browser fixture; no user data was imported.
post('/api/manual/init',{})
for name,kind in [('Nguyễn Văn A','GUEST'),('GV cơ hữu QA','RESIDENT'),('GV không có lớp QA','GUEST')]:
    post('/api/manual/teacher',{'name':name,'teacherType':kind,'availability':[]})
for index,code in enumerate(['TEST101','TEST102']):
    post('/api/manual/course',{'code':code,'name':'Kiểm thử phần mềm' if index==0 else 'Môn cơ hữu QA','credits':3})
    post('/api/manual/section',{'teacherIds':[index],'courseId':index,'duration':3,'classCode':code+'-1','program':'CSE','cohort':'K2025','autoSchedule':True})
save('seed-incomplete.json',client.get('/api/data').get_json())
response=client.post('/api/solve-guest',json={})
record('TC-08','API',response.status_code==400,{'http':response.status_code,'body':response.get_json()})
old_state=copy.deepcopy(STATE)
generated=post('/api/manual/teachers/generate-availability',{})
observed=[{'id':t['id'],'name':t['name'],'type':t['type'],'slots':t.get('availabilitySlots',[])} for t in generated['teachers'] if not t.get('isPlaceholder')]
record('TC-15','API_PARTIAL',generated.get('generatedTeacherCount')==3 and all(t['slots'] for t in observed),{'generatedTeacherCount':generated.get('generatedTeacherCount'),'teachers':observed,'limit':'Theo config mẫu của bản TEST; chưa thay thế điều kiện Tester/khuôn mẫu được PO chốt.'})
old_names={key:{k:v for k,v in item.items() if k not in ['availability']} for key,item in old_state['data']['teachers'].items()}
new_names={key:{k:v for k,v in item.items() if k not in ['availability']} for key,item in STATE['data']['teachers'].items()}
record('TC-17','API_PARTIAL',generated.get('generatedTeacherCount')==3 and old_names==new_names,{'generatedTeacherCount':generated.get('generatedTeacherCount'),'nonAvailabilityTeacherFieldsUnchanged':old_names==new_names,'limit':'Xác nhận trên UI được chạy riêng; khuôn mẫu chưa có phê duyệt PO trong hồ sơ.'})
STATE.clear(); STATE.update(old_state)
save_snapshot()
save('backend-results.json',results)
save('backend-environment.json',{'isolation':str(APP),'python':sys.executable,'productHead':os.environ.get('VJU_TEST_COMMIT','not recorded; use test/sprint0/run.py'),'configuration':'config/backend-example.json copied into isolated config/backend.json'})
for result in results: print(result['id'],result['scope'],result['status'])
sys.exit(1 if any(item['status']=='FAIL' for item in results) else 0)
