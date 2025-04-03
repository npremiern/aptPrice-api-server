# API 키 생성기 사용 설명서

## 소개
이 프로그램은 API 서버에서 사용할 수 있는 다양한 종류의 안전한 키를 생성하는 파이썬 도구입니다.

## 설치 방법

1. 파이썬이 설치되어 있는지 확인하세요 (3.6 이상 권장).
2. `api_key_generator.py` 파일을 다운로드하세요.

## 사용 방법

### 기본 사용법
```bash
python api_key_generator.py
```
이 명령은 32자리 랜덤 문자열 키를 생성합니다.

### 키 유형 선택
프로그램은 네 가지 유형의 키를 생성할 수 있습니다:

```bash
# UUID 형식 키 생성
python api_key_generator.py --type uuid

# 타임스탬프 포함 키 생성
python api_key_generator.py --type timestamp

# Base64 인코딩된 키 생성
python api_key_generator.py --type base64

# 랜덤 문자열 키 생성 (기본값)
python api_key_generator.py --type random
```

### 키 길이 조정
랜덤 및 base64 유형의 키 길이를 조정할 수 있습니다:

```bash
# 64자 길이의 랜덤 키 생성
python api_key_generator.py --length 64

# 16자 길이의 base64 키 생성
python api_key_generator.py --type base64 --length 16
```

### 여러 개의 키 생성
한 번에 여러 개의 키를 생성할 수 있습니다:

```bash
# 5개의 키 생성
python api_key_generator.py --count 5

# 10개의 UUID 키 생성
python api_key_generator.py --type uuid --count 10
```

### 타임스탬프 키 접두사 설정
타임스탬프 유형 키의 접두사를 설정할 수 있습니다:

```bash
# 'api_' 접두사로 타임스탬프 키 생성
python api_key_generator.py --type timestamp --prefix api_
```

### 키 파일로 저장
생성된 키를 파일에 저장할 수 있습니다:

```bash
# 키를 기본 파일명(api_key.txt)으로 저장
python api_key_generator.py --save

# 키를 지정된 파일명으로 저장
python api_key_generator.py --save --file my_secret_key.txt

# 여러 키를 각각 다른 파일에 저장
python api_key_generator.py --count 3 --save --file key.txt
# 위 명령은 key_1.txt, key_2.txt, key_3.txt 파일을 생성합니다
```

## 모든 옵션 종합 사용 예시

```bash
# 5개의 48자리 base64 키를 생성하고 파일에 저장
python api_key_generator.py --type base64 --length 48 --count 5 --save --file api_keys.txt
```

## 프로그램 도움말 보기
```bash
python api_key_generator.py --help
```

## 주요 키 유형 설명

1. **random**: 알파벳 대소문자와 숫자로 구성된 랜덤 문자열
2. **uuid**: 범용 고유 식별자(UUID) 형식의 키 (예: 550e8400-e29b-41d4-a716-446655440000)
3. **timestamp**: 현재 날짜/시간과 랜덤 부분이 결합된 키 (예: key_20240404123045_a1b2c3d4)
4. **base64**: Base64로 인코딩된 랜덤 바이트 문자열

## 보안 참고 사항
- 생성된 키는 안전한 방법으로 저장하고 관리해야 합니다.
- 소스 코드 저장소에 키를 직접 포함시키지 마세요.
- 프로덕션 환경에서는 환경 변수나 안전한 키 관리 서비스를 통해 키를 관리하는 것을 권장합니다.
