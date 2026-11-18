from pathlib import Path
import json,os,sys
repo=Path(__file__).resolve().parents[2]
work=Path(os.environ.get('VJU_SPRINT0_WORKDIR',repo/'work'/'sprint0-tests')).resolve()
if not work.is_relative_to((repo/'work').resolve()):
    raise ValueError('Sprint 0 test outputs must stay inside work/.')
sys.path.insert(0,str(work/'isolated-app'/'webapp'))
from app import app
app.config['TESTING']=True
client=app.test_client()
for line in sys.stdin:
    try:
        request=json.loads(line)
        response=client.open(request['path'],method=request['method'],data=request.get('body') or None,content_type=request.get('contentType') or None)
        result={'id':request['id'],'status':response.status_code,'contentType':response.content_type,'body':response.get_data(as_text=True)}
    except Exception as error:
        result={'id':request.get('id'),'status':500,'contentType':'application/json','body':json.dumps({'error':str(error)})}
    print(json.dumps(result,ensure_ascii=False),flush=True)
