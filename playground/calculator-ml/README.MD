# NeuroCalc: 손글씨 인식 AI 계산기

> **Deep Learning 기반의 손글씨 숫자 인식 기능을 탑재한 인터랙티브 웹 계산기입니다.** > 사용자가 캔버스에 숫자를 그리면 AI가 실시간으로 인식하고, 동적으로 수식을 구성하여 계산 결과를 보여줍니다.

![Project Preview](https://via.placeholder.com/800x400?text=Project+Screenshot+Here)
*(여기에 실제 구동 화면 스크린샷이나 GIF를 넣어주세요)*

## 주요 기능 (Key Features)

- ** 실시간 손글씨 인식**: 캔버스에 숫자를 그리면 백엔드 딥러닝 모델이 숫자를 예측하여 변환합니다.
- ** 동적 블록 시스템**: 숫자, 연산자, 특수기호 등을 블록처럼 자유롭게 추가하고 삭제할 수 있습니다.
- ** 다양한 연산 지원**:
  - 사칙연산 (`+`, `-`, `×`, `÷`)
  - 고급 수학 기능: 제곱(`^`), 루트(`√`), 괄호(`(`, `)`)
- ** 자릿수 자동 병합**: 연속으로 숫자 블록을 추가하면 자동으로 자릿수를 인식하여 병합합니다 (예: `1`, `2` → `12`).
- ** 직관적인 UI/UX**: 점선 노트 스타일의 캔버스, 사이드바 네비게이션, 반응형 레이아웃.

##  기술 스택 (Tech Stack)

### Frontend
- **Framework**: React (TypeScript)
- **Styling**: CSS Modules, Flexbox Layout
- **Routing**: React Router DOM
- **State Management**: React Hooks (useState, useRef)

### Backend
- **Framework**: Python (FastAPI or Flask) *[사용하신 프레임워크로 수정]*
- **AI Model**: PyTorch / TensorFlow / Keras *[사용하신 라이브러리로 수정]*
- **Image Processing**: OpenCV, PIL

---

## 설치 및 실행 방법 (Getting Started)

이 프로젝트는 Frontend와 Backend 서버를 각각 실행해야 합니다.

### 1. Backend (Python Server)

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화 (선택 사항)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (Port: 8000)
uvicorn main:app --reload 
# 또는 python app.py 등 본인의 실행 명령어
