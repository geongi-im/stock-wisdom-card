# Stock Wisdom Card Generator (주식 명언 카드 생성기)

주식 투자 대가들의 명언을 이미지 카드로 자동 생성하는 프로젝트입니다.

## 주요 기능

- 주식 투자 대가들의 명언을 이미지 카드로 자동 생성
- 텍스트 위치 자동 조정 (상단, 중앙, 하단)
- 텍스트 그림자 효과로 가독성 향상
- SQLite 데이터베이스를 통한 명언 관리
- 이미지 전처리 기능 (리사이징, 흑백 변환)
- 자동 폰트 크기 조정

## 지원하는 투자 대가

- 워렌 버핏 (Warren Buffett)
- 안드레 코스톨라니 (Andre Kostolany)
- 피터 린치 (Peter Lynch)
- 켄 피셔 (Ken Fisher)
- 벤자민 그레이엄 (Benjamin Graham)
- 존 템플턴 (John Templeton)
- 세스 클라만 (Seth Klarman)
- 윌리엄 오닐 (William O'Neil)
- 찰리 멍거 (Charlie Munger)

## 설치 방법

1. 저장소 클론

2. 필요한 패키지 설치

3. 폰트 파일 준비
- `fonts` 디렉토리에 다음 폰트 파일을 위치시킵니다:
  - NanumGothicBold.ttf (명언 텍스트용)
  - MaruBuri-Bold.ttf (저자명 텍스트용)

4. 이미지 준비
- `img/source` 디렉토리에 각 투자자의 이미지를 위치시킵니다.
- 파일명 형식: `{이름}_{번호}.jpg` (예: `Warren Buffett_01.jpg`)

## 사용 방법

1. 이미지 전처리

2. 명언 카드 생성

## 프로젝트 구조

- `main.py`: 메인 실행 파일
- `image_processor.py`: 이미지 처리 및 카드 생성 클래스
- `database_manager.py`: SQLite 데이터베이스 관리 클래스
- `preprocessing_img.py`: 이미지 전처리 스크립트
- `wisdom.csv`: 명언 데이터 파일
- `fonts/`: 폰트 파일 디렉토리
- `img/`: 이미지 파일 디렉토리
  - `source/`: 원본 이미지
  - `{투자자명}/`: 처리된 이미지

## 이미지 파일명 규칙

- 상단 텍스트: `{번호}_t.jpg`
- 중앙 텍스트: `{번호}_c.jpg`
- 하단 텍스트: `{번호}_b.jpg`

## 생성된 파일

- 생성된 이미지는 `output` 디렉토리에 저장됩니다
- 파일명 형식: `YYYYMMDD.jpeg` 또는 `YYYYMMDD_1.jpeg`

## 라이선스

MIT License

