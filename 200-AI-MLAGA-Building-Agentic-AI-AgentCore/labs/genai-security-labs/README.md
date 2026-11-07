# Track 2. AWS Generative AI 보안 with Amazon Bedrock — 실습·데모 키트

2일 과정의 실습 4개와 설계 워크숍 자료입니다. 모든 실습은 **"한빛대학병원 안내·의료진 AI"** 라는 하나의 시나리오로 이어집니다. 실습 1에서 만든 가드레일을 실습 2·3에서 재사용하고, 실습 2에서 확인한 한계(확률적 방어)를 실습 3·4의 결정론적 통제로 메우는 흐름입니다.

## 과정 시간표와 자료 매핑

| 일차 | 시간 | 세션 | 사용할 자료 | 데모 포인트 |
|---|---|---|---|---|
| 1 | 09:30–10:30 | 모듈1 GenAI 위협 모델링 | `lab2` 2절 공격 세트, `lab5` 1단계 표 | 공격 8종을 OWASP LLM01·LLM07에 매핑 |
| 1 | 10:30–12:00 | 모듈2 Guardrails 심화 | `lab1` 1절 정책 설계 | STANDARD 티어와 한국어, BLOCK vs ANONYMIZE |
| 1 | 13:00–14:30 | **실습1 Guardrails 구현** | `lab1_guardrails.ipynb` | 3절 테스트 표, 6절 v1→v2 비교 |
| 1 | 14:30–16:00 | 모듈3 입출력 안전 제어 | `lab1` 4절(근거 검사), `lab2` 3절(방어층 코드) | 할루시네이션 점수, Defense-in-Depth 구조 |
| 1 | 16:00–17:30 | **실습2 적대적 공격 방어** | `lab2_adversarial_defense.ipynb` | 4절 방어층별 ASR 표, 5절 레드팀 |
| 2 | 09:30–10:30 | 모듈4 RAG 보안·프라이버시 | `lab3` 상단 아키텍처 그림 | 6개 통제 지점 설명 |
| 2 | 10:30–12:00 | **실습3 RAG 보안 아키텍처** | `lab3_rag_security.ipynb` + `rag_security_stack.yaml` | 4절 역할별 검색, 7절 오염 문서, 8절 엔드포인트 정책 |
| 2 | 13:00–14:30 | 모듈5 AgentCore·AI 거버넌스 | `lab4` 4절 Cedar 정책 표 | forbid가 permit을 이기는 이유 |
| 2 | 14:30–16:00 | **실습4 AgentCore 보안정책** | `lab4_agentcore_policy.ipynb` | 5절 권한 매트릭스, 6절 인젝션당한 에이전트 |
| 2 | 16:00–17:30 | GenAI 보안 아키텍처 설계 | `lab5_design/design_worksheet.md` | 팀 발표 |

## 폴더 구성

```
genai-security-labs/
├── README.md                       ← 이 문서 (강사 가이드)
├── requirements.txt
├── common/labutils.py              ← 공통 설정, 모델 자동 선택, 상태 저장, 출력 도우미
├── lab1_guardrails/                ← 실습 1
├── lab2_adversarial/               ← 실습 2
├── lab3_rag_security/              ← 실습 3 (CloudFormation 템플릿, 샘플 문서 6개 포함)
├── lab4_agentcore/                 ← 실습 4 (EMR 도구 Lambda 코드 포함)
├── lab5_design/                    ← 설계 워크숍 워크시트
├── 99_cleanup.ipynb                ← 전체 리소스 정리
└── tools/dryrun.py                 ← AWS 호출 없이 노트북 API 파라미터를 검증하는 도구
```

## 사전 준비 (강의 전날까지)

1. **AWS 계정과 리전**
   - 권장 리전: `us-east-1` 또는 `us-west-2`. AgentCore Policy, S3 Vectors, Guardrails STANDARD 티어를 모두 지원하는지 강의 전에 [리전별 기능 표](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)와 AgentCore 문서에서 확인하세요.
   - 수강생 IAM 권한: 실습 계정에서는 `AdministratorAccess`가 가장 간단합니다. 최소 권한으로 하려면 Bedrock, Bedrock AgentCore, S3, S3 Vectors, IAM(역할 생성·PassRole), Lambda, EC2(VPC), CloudFormation, KMS, Cognito, CloudWatch Logs, CloudTrail 읽기가 필요합니다.
2. **Bedrock 모델 액세스**: Anthropic Claude(Haiku 또는 Sonnet) 추론 프로파일과 `amazon.titan-embed-text-v2:0`을 사용할 수 있어야 합니다. 노트북은 사용 가능한 Claude 추론 프로파일을 자동으로 고릅니다. 특정 모델을 쓰려면 `LAB_MODEL_ID` 환경 변수를 지정하세요.
3. **실행 환경**: SageMaker Studio JupyterLab, 또는 AWS 자격 증명이 설정된 로컬 Jupyter. Python 3.10 이상.
   ```bash
   pip install -r requirements.txt
   ```
   AgentCore Policy, S3 Vectors API가 들어간 **최신 boto3**가 필요합니다(작성 시 boto3 1.43.124로 검증).
4. **여러 수강생이 한 계정을 쓸 때**: 수강생마다 `LAB_PREFIX` 환경 변수를 다르게 주세요(예: `gsec01`, `gsec02`). 리소스 이름 충돌을 막습니다. 소문자·숫자만, 12자 이내로 쓰세요.
5. **강사 리허설**: 실습 1 → 2 → 3 → 4 → 99 순서로 한 번 끝까지 실행해 보세요. 전체 약 2시간, 비용은 몇 달러 수준입니다(VPC 엔드포인트를 오래 켜 두지 않는 경우).

## 실습별 진행 가이드

### 실습 1. Guardrails 구현 (90분)
| 절 | 시간 | 강사 포인트 |
|---|---|---|
| 1 정책 설계 | 15분 | 정책 6종을 표로 설명. **STANDARD 티어를 쓰지 않으면 한국어 탐지가 약하다**는 점 강조 |
| 2 생성·버전 | 10분 | DRAFT와 고정 버전의 차이, 운영은 항상 버전 참조 |
| 3 ApplyGuardrail | 20분 | 테스트 표를 띄워 놓고 케이스별로 "기대 vs 결과" 비교. 마스킹 케이스에서 `{PHONE}` 확인 |
| 4 출력 검사 | 15분 | 근거 검사 점수 3개 비교. 임계값 토론 |
| 5 Converse 적용 | 15분 | `stopReason=guardrail_intervened`, trace 확인 |
| 6 v2 배포 | 15분 | 운영 중 새 위협 대응 흐름: 정책 추가 → 새 버전 → 회귀 비교 |

**자주 나오는 질문:** "결과가 기대와 다르게 나와요" → 가드레일은 확률적 분류기라 정상입니다. 그 차이가 바로 실습 2의 출발점입니다.

### 실습 2. 적대적 공격 방어 (90분)
| 절 | 시간 | 강사 포인트 |
|---|---|---|
| 1~2 취약 앱·공격 세트 | 15분 | 공격 8종을 하나씩 읽으며 OWASP 번호 매핑 |
| 3 방어층 코드 | 20분 | L1(정규식)의 한계, L2 `guardContent` 태깅, L3 spotlighting, L4 정규화 |
| 4 ASR 측정 | 25분 | **핵심 장면.** 방어층을 쌓을 때마다 공격 성공률이 떨어지는 표. 오차단 열도 꼭 짚기 |
| 5 레드팀 | 20분 | 규칙 변형 12개 중 대부분이 L1을 통과함 → 나머지 층이 막는지 확인 |
| 6~7 회귀 세트·토론 | 10분 | "비밀은 프롬프트에 두지 않는다" → 실습 4 예고 |

**참고:** 모델 출력이 확률적이라 L0의 유출 결과는 실행마다 다를 수 있습니다. 데모 전 한 번 돌려 결과를 확인해 두세요. 모델이 스스로 거절해 L0에서도 막히는 공격이 있다면 "모델 정렬도 한 층이지만 통제할 수 없는 층"이라고 설명하면 됩니다.

### 실습 3. RAG 보안 아키텍처 (90분)
| 절 | 시간 | 강사 포인트 |
|---|---|---|
| 0 스택 배포 | 10분 | **첫 셀을 실행해 두고** 템플릿을 같이 읽으며 기다리기 (5~8분) |
| 1 수집 전 검사 | 10분 | 오염 공지문이 탐지되는 것 확인. 일부러 그대로 업로드 |
| 2~3 저장소·KB | 15분 | 키 하나로 원문·벡터·수집 임시 데이터를 모두 암호화. KB 역할의 최소 권한 |
| 4 역할별 검색 | 15분 | 같은 질문, 다른 결과. **필터는 서버가 인증 정보로 만든다** |
| 5~6 마스킹·계보 | 15분 | 가드레일 유무 비교, 계보 레코드의 S3 버전 ID |
| 7 오염 문서 | 10분 | 격리 전후 답변 비교 |
| 8 엔드포인트 정책 | 15분 | IAM은 허용했는데 네트워크에서 거부되는 장면 |

### 실습 4. AgentCore 보안정책 (90분)
| 절 | 시간 | 강사 포인트 |
|---|---|---|
| 1 Identity | 20분 | 인바운드(Cognito JWT)와 아웃바운드(토큰 볼트) 구분. 에이전트 코드에 키가 없다는 점 |
| 2~3 도구·게이트웨이 | 15분 | 정책 엔진을 ENFORCE로 붙이면 **처음엔 모두 거부** (기본 거부 확인 셀) |
| 4 Cedar 정책 | 15분 | P4(과잉 허용)와 P5(forbid)를 함께 넣은 이유. 잘못된 정책이 검증에서 거부되는 장면 |
| 5 권한 매트릭스 | 15분 | **핵심 장면.** 사용자 3명 × 호출 6개 표, 역할별 도구 목록 |
| 6 인젝션당한 에이전트 | 15분 | 실습 2와 연결: 에이전트가 넘어가도 정책은 안 넘어감 |
| 7 모니터링 | 10분 | LOG_ONLY 섀도 정책, 로그 전달, CloudTrail 정책 변경 감사 |

## 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| `사용 가능한 Claude 추론 프로파일이 없습니다` | Bedrock 콘솔 → 모델 액세스에서 Claude 활성화, 또는 `LAB_MODEL_ID` 지정 |
| Guardrail 생성 시 `crossRegionConfig` 오류 | 리전의 guardrail 프로파일 ID 확인. `common/labutils.py`의 `guardrail_profile_id()` 수정 |
| 실습 2에서 `실습 1을 먼저 실행` 오류 | 실습 1의 2절까지 실행하면 `lab_state.json`에 가드레일 ID가 저장됩니다 |
| CloudFormation 스택이 `CREATE_FAILED` (VPC 엔드포인트) | 선택된 가용 영역에 `bedrock-agent-runtime` 엔드포인트가 없는 경우. 템플릿의 `!Select [0/1, ...]`를 다른 AZ 인덱스로 바꿔 재배포 |
| KB 수집 작업 `FAILED` | KB 역할의 KMS·S3 Vectors 권한, 임베딩 모델 액세스 확인. `failureReasons` 출력 확인 |
| 실습 3 8절에서 Lambda가 타임아웃 | 엔드포인트 보안 그룹 규칙 또는 Private DNS 설정 확인 |
| 실습 4 정책이 `CREATE_FAILED` | `statusReasons`에 Cedar 검증 메시지가 나옵니다. 액션 이름의 밑줄이 3개인지(`HospitalEMR___도구`), 도구 스키마의 필수 인자를 정책에서 쓰는지 확인 |
| 실습 4 모든 호출이 HTTP 401/403 | 토큰 만료(1시간). 1-1절의 `TOKENS = ...` 줄을 다시 실행 |
| 실습 4 로그 조회 결과 0건 | 로그 전달에 1~3분 걸립니다. 잠시 후 다시 실행 |

## 정리

실습이 끝나면 `99_cleanup.ipynb`를 위에서부터 실행하세요. VPC 인터페이스 엔드포인트와 AgentCore 게이트웨이는 켜 두는 동안 요금이 발생합니다.

## 검증 상태와 한계

- 모든 노트북을 `tools/dryrun.py`로 검증했습니다. 이 도구는 AWS 호출을 가로채 **최신 boto3 서비스 모델로 모든 API 파라미터의 이름과 타입을 검사**하고, 가짜 응답으로 노트북을 처음부터 끝까지 실행합니다(277건 호출, 오류 0건).
- **실제 AWS 계정에서는 아직 실행하지 않았습니다.** 모델 응답 내용, 서비스 간 권한 전파, 로그 형식처럼 실제 환경에서만 확인되는 부분이 있으니 강의 전 리허설을 꼭 해 주세요.
- AgentCore Policy, S3 Vectors는 비교적 새 기능입니다. boto3를 업데이트한 뒤에는 `python tools/dryrun.py lab1_guardrails/lab1_guardrails.ipynb ...`로 다시 검증할 수 있습니다.
