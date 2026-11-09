from pathlib import Path
import io, re, os
from typing import Any
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

BASE_DIR=Path(__file__).resolve().parent; MODEL_ID='nateraw/vit-age-classifier'; classifier=None; model_error=None
app=FastAPI(title='표지 이용 연령 추정기')
app.mount('/static', StaticFiles(directory=BASE_DIR/'static'), name='static')
@app.get('/')
def index(): return FileResponse(BASE_DIR/'static'/'index.html')
@app.get('/health')
def health(): return {'status':'ok','model':MODEL_ID,'model_version':os.getenv('APP_VERSION','dev'),'model_loaded':classifier is not None,'model_error':model_error}
def load_model():
 global classifier,model_error
 if classifier is not None:return classifier
 try:
  from transformers import pipeline
  classifier=pipeline('image-classification',model=MODEL_ID,device=-1); return classifier
 except Exception as exc:
  model_error=f'모델을 준비하지 못했습니다: {type(exc).__name__}: {exc}'; raise RuntimeError(model_error) from exc
def age_range(label):
 nums=[int(x) for x in re.findall(r'\d+',label.replace('–','-').replace('—','-'))]
 return (nums[0],nums[1] if len(nums)>1 else nums[0]+4) if nums else (18,29)
def rating(start,end,region):
 if region=='kr':
  return ('전체관람가','모든 연령') if end<=6 else ('12세 이상','12세 미만 보호자 지도 권장') if end<=11 else ('15세 이상','15세 미만 보호자 지도 권장') if end<=14 else ('청소년 관람불가','성인 대상')
 return ('G','General audiences') if end<=6 else ('PG','Parental guidance suggested') if end<=11 else ('PG-13','Parents strongly cautioned') if end<=14 else ('R','Restricted') if end<=17 else ('NC-17','Adults only')
@app.post('/api/analyze')
async def analyze(file:UploadFile=File(...),region:str=Form('kr')):
 if region not in {'kr','us'}: return JSONResponse({'error':'기준 국가는 kr 또는 us만 선택할 수 있습니다.'},400)
 if not file.filename:return JSONResponse({'error':'이미지 파일을 선택해 주세요.'},400)
 if file.content_type not in {'image/jpeg','image/png','image/webp'}:return JSONResponse({'error':'JPG, PNG, WEBP 이미지만 업로드할 수 있습니다.'},415)
 data=await file.read()
 if len(data)>10*1024*1024:return JSONResponse({'error':'파일 크기는 10MB 이하만 허용됩니다.'},413)
 try:image=Image.open(io.BytesIO(data)).convert('RGB')
 except (UnidentifiedImageError,OSError):return JSONResponse({'error':'이미지 내용을 읽을 수 없습니다. 파일을 확인해 주세요.'},400)
 try:
  outputs=load_model()(image,top_k=3); best=outputs[0]; start,end=age_range(best['label']); rat,desc=rating(start,end,region)
  return {'filename':file.filename,'region':region,'model_version':os.getenv('APP_VERSION','dev'),'estimated_age_range':f'{start}–{end}세','confidence':round(float(best['score']),4),'rating':rat,'rating_description':desc,'alternatives':[{'label':x['label'],'score':round(float(x['score']),4)} for x in outputs],'notice':'AI가 표지 이미지의 시각적 단서를 바탕으로 추정한 참고 결과이며, 실제 이용 연령이나 공식 등급을 보장하지 않습니다.'}
 except RuntimeError as exc:return JSONResponse({'error':str(exc),'hint':'처음 실행 시 모델 다운로드가 필요합니다. 인터넷 연결 후 다시 시도해 주세요.'},503)
 except Exception as exc:return JSONResponse({'error':f'분석 중 오류가 발생했습니다: {type(exc).__name__}: {exc}'},500)
if __name__=='__main__':
 import uvicorn; uvicorn.run('assignment2:app',host='127.0.0.1',port=8000,reload=False)
