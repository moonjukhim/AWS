 다른 PC에서 실행하기 위한 준비 사항

  1. AWS 계정 및 자격 증명

  # AWS CLI 설치 후 자격 증명 설정
  aws configure
  - Access Key ID / Secret Access Key 필요
  - Region: us-west-2 (코드에 하드코딩되어 있음)
  - IAM 사용자에 다음 권한 필요:
    - bedrock:InvokeModel (모델 호출)
    - bedrock:CreateGuardrail, bedrock:DeleteGuardrail (Guardrail 생성/삭제)

  2. Bedrock 모델 접근 활성화

  AWS Console > Amazon Bedrock > Model access에서 다음 모델 활성화:
  - Anthropic Claude Haiku 4.5 (global.anthropic.claude-haiku-4-5-20251001-v1:0)

  3. 소프트웨어 설치

  ┌────────────────┬───────────┬─────────────┐
  │      항목      │   버전    │    용도     │
  ├────────────────┼───────────┼─────────────┤
  │ Python         │ 3.10 이상 │ 런타임      │
  ├────────────────┼───────────┼─────────────┤
  │ pip            │ 최신      │ 패키지 관리 │
  ├────────────────┼───────────┼─────────────┤
  │ Git            │ 최신      │ 코드 클론   │
  ├────────────────┼───────────┼─────────────┤
  │ Jupyter (선택) │ 최신      │ 노트북 실행 │
  └────────────────┴───────────┴─────────────┘

  4. 코드 및 패키지 설치

  # 1) 코드 클론
  git clone https://github.com/aws-samples/amazon-bedrock-agentcore-samples.git
  cd amazon-bedrock-agentcore-samples/02-use-cases/finance-personal-assistant

  # 2) 패키지 설치
  pip install -r requirements.txt

  SageMaker 노트북에서 실행할 경우 numpy 호환 문제가 있으므로:
  pip install "numpy<2.0" --quiet
  pip install -r requirements.txt --quiet

  5. Windows PC 추가 사항

  cp949 인코딩 문제로 .py 파일 직접 실행 시 이모지 출력 에러가 발생합니다. 두 가지 해결법 중 택 1:

  방법 A: 환경 변수 설정 (전역 적용, 권장)
  set PYTHONIOENCODING=utf-8

  방법 B: 각 .py 파일 상단에 추가
  import sys, io
  if hasattr(sys.stdout, 'buffer'):
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

  6. 정리 체크리스트

  ┌───────────────────┬───────────────────────────────────────┬─────────────────────────┐
  │       단계        │              확인 명령어              │        기대 결과        │
  ├───────────────────┼───────────────────────────────────────┼─────────────────────────┤
  │ Python 설치       │ python --version                      │ 3.10+                   │
  ├───────────────────┼───────────────────────────────────────┼─────────────────────────┤
  │ AWS CLI 설치      │ aws --version                         │ 2.x                     │
  ├───────────────────┼───────────────────────────────────────┼─────────────────────────┤
  │ AWS 자격 증명     │ aws sts get-caller-identity           │ Account ID 출력         │
  ├───────────────────┼───────────────────────────────────────┼─────────────────────────┤
  │ Bedrock 모델 접근 │ AWS Console에서 확인                  │ Claude Haiku 4.5 활성화 │
  ├───────────────────┼───────────────────────────────────────┼─────────────────────────┤
  │ 패키지 설치       │ python -c "from strands import Agent" │ 에러 없음               │
  └───────────────────┴───────────────────────────────────────┴─────────────────────────┘

  이 6가지만 갖추면 Lab1~Lab3 모두 실행할 수 있습니다