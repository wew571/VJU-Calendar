from pathlib import Path
import io
import json
import os
import sys

REPO=Path(__file__).resolve().parents[2]
WORK=Path(os.environ['VJU_SPRINT1_WORKDIR']).resolve()
if not WORK.is_relative_to((REPO/'work').resolve()):
    raise ValueError('Sprint 1 must run inside work/. Use test/sprint1/run.py.')
APP=WORK/'isolated-app'
OUT=WORK/'evidence'
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(APP/'webapp'))
from app import app
app.config['TESTING']=True
client=app.test_client()
results=[]

def call(path,data=None):
    return client.get(path) if data is None else client.post(path,json=data)

def check(identifier,title,expected,actual,passed):
    results.append({'id':identifier,'title':title,'expected':expected,'actual':actual,'status':'PASS' if passed else 'FAIL'})

def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def setup(prefix):
    assert call('/api/manual/init',{}).status_code==200
    for name,kind in [(prefix+' Guest','GUEST'),(prefix+' Resident','RESIDENT')]:
        response=call('/api/manual/teacher',{'name':name,'teacherType':kind,'availability':list(range(65))})
        assert response.status_code==200,response.get_json()
    for index in range(2):
        response=call('/api/manual/course',{'code':prefix+str(index),'name':prefix+' Course '+str(index),'credits':3})
        assert response.status_code==200,response.get_json()
        response=call('/api/manual/section',{'teacherIds':[index],'courseId':index,'duration':3,'classCode':prefix+str(index)+'-1','program':['CSE','BCE'][index],'cohort':['K2025',''][index],'autoSchedule':True,'coordinatorOverride':'QA Coordinator '+str(index)})
        assert response.status_code==200,response.get_json()

setup('IMP')
response=call('/api/manual/export')
assert response.status_code==200
fixture=response.data
(OUT/'import-fixture.xlsx').write_bytes(fixture)
setup('QA')

def preview():
    return client.post('/api/manual/import/preview',data={'file':(io.BytesIO(fixture),'import-fixture.xlsx')},content_type='multipart/form-data')

response=preview()
data=call('/api/data').get_json()
check('S1-01','Xem trước file Excel','HTTP 200, dữ liệu QA chưa bị thay thế',f'HTTP {response.status_code}; classes={len(data["classes"])}',response.status_code==200 and any(c['code']=='QA0' for c in data['courses']))
response=call('/api/manual/import/commit',{'mode':'merge'})
codes=[c['code'] for c in call('/api/data').get_json()['courses']]
check('S1-02','Gộp dữ liệu Excel','Giữ QA0/QA1 và thêm IMP0/IMP1',str(codes),response.status_code==200 and {'QA0','QA1','IMP0','IMP1'}<=set(codes))
assert preview().status_code==200
response=call('/api/manual/import/commit',{'mode':'replace'})
codes=[c['code'] for c in call('/api/data').get_json()['courses']]
check('S1-03','Thay thế dữ liệu Excel','Chỉ còn IMP0/IMP1',str(codes),response.status_code==200 and set(codes)=={'IMP0','IMP1'})
setup('QA')
data=call('/api/data').get_json()
save('seed-data.json',data)
names=[teacher['nameRaw'] for teacher in data['teachers']]
types={teacher['nameRaw']:teacher['type'] for teacher in data['teachers']}
check('S1-04','Thêm giảng viên qua API','Có QA Guest và QA Resident',str(types),set(names)=={'QA Guest','QA Resident'} and types=={'QA Guest':'GUEST','QA Resident':'RESIDENT'})
codes=[course['code'] for course in data['courses']]
check('S1-05','Thêm học phần qua API','Có QA0 và QA1',str(codes),set(codes)=={'QA0','QA1'})
classes=[(item['classCode'],item['programLabel']) for item in data['classes']]
check('S1-06','Thêm lớp qua API','Có 2 lớp thuộc CSE/BCE',str(classes),set(classes)=={('QA0-1','CSE'),('QA1-1','BCE')})
response=call('/api/solve-resident',{})
check('S1-07','Chặn cơ hữu trước thỉnh giảng','HTTP 400',response.get_data(as_text=True),response.status_code==400)
response=call('/api/solve-guest',{})
guest=response.get_json()
check('S1-08','Giải thỉnh giảng','HTTP 200 và 1 lớp được xếp',f'HTTP {response.status_code}; status={guest.get("status")}; placedCount={guest.get("placedCount")}; lessons='+str([(item.get('id'),item.get('day'),item.get('period'),item.get('duration')) for item in guest.get('lessons',[])]),response.status_code==200 and guest.get('placedCount')==1)
response=call('/api/solve-resident',{})
resident=response.get_json()
check('S1-09','Giải cơ hữu sau thỉnh giảng','HTTP 200 và 1 lớp được xếp',f'HTTP {response.status_code}; status={resident.get("status")}; placedCount={resident.get("placedCount")}; lessons='+str([(item.get('id'),item.get('day'),item.get('period'),item.get('duration')) for item in resident.get('lessons',[])]),response.status_code==200 and resident.get('placedCount')==1)
save('solve-results.json',call('/api/results').get_json())
response=call('/api/manual/save-schedule',{})
saved_data=call('/api/data').get_json()
saved=saved_data['classes']
save('saved-data.json',saved_data)
hours_ok=len(saved)==2 and all(item.get('day') is not None and item.get('periodStart') is not None and item.get('periodEnd') is not None for item in saved)
check('S1-10','Lưu toàn bộ lịch qua API','savedCount=2; cả hai lớp có ngày/tiết',f'HTTP {response.status_code}; savedCount={response.get_json().get("savedCount")}; bothClassesHaveTimes={hours_ok}; classes='+str([(item['classCode'],item['day'],item['periodStart'],item['periodEnd']) for item in saved]),response.status_code==200 and response.get_json().get('savedCount')==2 and hours_ok)
save('acceptance-results.json',results)
for item in results: print(item['id'],item['status'],item['title'])
raise SystemExit(1 if any(item['status']=='FAIL' for item in results) else 0)
