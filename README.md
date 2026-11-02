# 표지 이용 연령 추정기

표지 이미지를 업로드하면 CPU에서 실행되는 사전학습 이미지 분류 모델이 이용 연령대를 추정하는 로컬 웹앱입니다. 한국 또는 미국 기준을 선택할 수 있으며, 결과는 공식 등급 판정이 아닌 참고용 AI 추정치입니다.

## 설치

Python 3.10 이상을 권장합니다. 가상환경 없이도 실행할 수 있습니다.

PowerShell에서 `upload` 폴더로 이동한 뒤 실행합니다.

```powershell
cd "C:\경로\과제2\upload"
python -m pip install -r requirements.txt
```

## 모델 준비

앱은 Hugging Face의 `nateraw/vit-age-classifier`를 사용합니다. 별도의 모델 파일을 저장소에 포함하지 않으며, 첫 분석 요청 시 자동으로 다운로드합니다.

- 인터넷 연결이 필요합니다.
- 모델은 CPU 모드(`device=-1`)로 실행됩니다.
- 회사/학교 네트워크에서 Hugging Face가 차단된 경우 모델 다운로드가 실패할 수 있습니다.
- 이 경우 앱은 분석 결과 대신 다운로드 실패 원인과 재시도 안내를 표시합니다.

## 실행

```powershell
python assignment2.py
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다.

종료하려면 서버가 실행 중인 PowerShell 창에서 `Ctrl+C`를 누릅니다.

## 사용 방법

1. JPG, PNG 또는 WEBP 표지 이미지를 선택하거나 끌어 놓습니다.
2. 선택한 이미지의 미리보기를 확인합니다.
3. 한국 또는 미국 이용 연령 기준을 선택합니다.
4. `이미지 분석하기`를 누릅니다.
5. 추정 연령대, 기준별 등급, 모델 신뢰도 표시, 상위 후보를 확인합니다.

결과는 이미지의 시각적 단서를 바탕으로 한 추정이며 실제 이용 연령이나 공식 등급을 보장하지 않습니다. 최종 판단은 해당 기관의 공식 기준을 확인하세요.

## 파일 구성

```text
upload/
├─ assignment2.py
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ static/
   ├─ index.html
   ├─ style.css
   └─ app.js
```
