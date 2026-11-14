# Building Agentic AI with Amazon Bedrock AgentCore — 챕터별 연결형 데모

강의 챕터(02~06)마다 하나의 노트북을 실행하면, **하나의 고객지원 에이전트**가 단계적으로 발전해
마지막에는 프로덕션 수준의 에이전트가 완성되는 구조입니다.

## 시나리오: AnyCompany Electronics 고객지원 에이전트

| 챕터 | 강의 자료 | 노트북 | 에이전트에 추가되는 기능 | 런타임 버전 |
|---|---|---|---|---|
| 02 | 02-Runtime | `02_Runtime_Demo.ipynb` | Strands 에이전트 → Runtime 배포, 세션 격리(microVM), 비동기 작업, `PROD` 엔드포인트 | V1 |
| 03 | 03-SecurityAndIdentity | `03_SecurityIdentity_Demo.ipynb` | Cognito JWT 인바운드 인증, 사용자 컨텍스트·감사 로그, API 키 아웃바운드 인증 | V2 |
| 04 | 04-ToolsAndGateway | `04_ToolsGateway_Demo.ipynb` | Code Interpreter, MCP, Gateway(Lambda→MCP, 토큰 전파), Policy(Cedar 환불 한도) | V3 |
| 05 | 05-Memory | `05_Memory_Demo.ipynb` | Memory 단기/장기(선호·사실·요약), 후크, actor = 인증된 고객 | V4 |
| 06 | 06-DeploymentObservablity | `06_Observability_Evaluation_Demo.ipynb` | Transaction Search, 스팬/지표 분석, 온디맨드·온라인 평가, `PROD` 승격 | V4 → PROD |
| — | — | `99_Cleanup.ipynb` | 모든 리소스 삭제 | |

각 챕터의 런타임 코드는 `agent/runtime_chNN.py` 에 있으며, 이전 챕터 코드에 `# [CH03]`, `# [CH04]`, `# [CH05]`
표시로 추가된 부분만 비교하면 챕터별 변화가 보입니다. (노트북의 `%%writefile` 셀이 같은 파일을 다시 생성합니다.)

```
 고객(alice/bob) ─로그인─▶ Cognito ─JWT─▶ AgentCore Runtime (세션별 microVM)
                                           └─ Strands 고객지원 에이전트 (Claude Haiku 4.5 on Bedrock)
                                               ├─ 로컬 도구: 제품정보 · 반품정책 · 판매리포트(비동기)
                                               ├─ track_shipment ──(AgentCore Identity API 키)──▶ 배송 파트너 API (목)
                                               ├─ run_python ──▶ AgentCore Code Interpreter
                                               ├─ MCP ─(같은 JWT)─▶ AgentCore Gateway ─[Policy: Cedar]─▶ Lambda(보증·프로필·환불)
                                               └─ AgentCoreMemorySessionManager ──▶ AgentCore Memory
                                           OpenTelemetry ──▶ CloudWatch GenAI Observability ──▶ AgentCore Evaluations
```

## 폴더 구조

```
demo/
├─ 02_… ~ 06_….ipynb, 99_Cleanup.ipynb
├─ requirements.txt            # 노트북 실행 환경
├─ demo_helpers/
│   ├─ config.py               # 리소스 이름, 모델 ID, 챕터 간 상태 저장(demo_state.json)
│   ├─ tools.py                # 로컬 도구 + 시스템 프롬프트 (런타임 컨테이너에도 포함)
│   ├─ aws_setup.py            # IAM 역할, Cognito, Transaction Search 준비
│   └─ invoke.py               # SigV4 / JWT 로 런타임 호출
├─ agent/
│   ├─ requirements.txt        # 런타임 컨테이너 패키지
│   └─ runtime_ch02.py … runtime_ch05.py
├─ lambda_tools/customer_tools.py   # 04장 Gateway 타깃 Lambda
└─ mcp_server/store_mcp_server.py   # 04장 로컬 MCP 서버 예제
```

## 사전 준비

1. **Python 3.10+**, Jupyter (VS Code / JupyterLab / SageMaker Studio)
2. **AWS 자격 증명** (`aws configure`) — AgentCore 를 지원하는 리전 (예: `us-east-1`, `us-west-2`)
   - AgentCore Policy, Evaluations 는 지원 리전이 더 제한될 수 있으니 강의 전 리전을 확인하세요.
3. **Bedrock 모델 액세스**: 기본 모델은 `global.anthropic.claude-haiku-4-5-20251001-v1:0`
   - 다른 모델을 쓰려면 실행 전 `DEMO_MODEL_ID` 환경 변수를 설정하거나 `demo_helpers/config.py` 의 `MODEL_ID` 를 수정합니다.
     (예: `global.amazon.nova-2-lite-v1:0`)
4. IAM 권한: IAM 역할 생성, Cognito, Lambda, ECR, CodeBuild, S3, CloudWatch/X-Ray, `bedrock-agentcore:*`
5. 로컬 Docker 는 **필요 없습니다** (스타터 툴킷이 AWS CodeBuild 에서 ARM64 이미지를 빌드).

## 실행 방법

- 작업 디렉터리를 `demo/` 로 두고 **02 → 03 → 04 → 05 → 06 순서**로 실행합니다.
  각 노트북은 `demo_state.json` 에서 이전 챕터 결과(런타임 ARN, Cognito, Gateway, Memory ID 등)를 읽어 이어서 진행합니다.
- 노트북의 셀은 여러 번 실행해도 안전하도록(기존 리소스 재사용) 작성되었습니다.
- 강의 당일 시간을 절약하려면 런타임 배포(`launch`, 챕터당 3~5분)와 Memory 생성(2~3분)을 미리 실행해 두세요.

### 소요 시간(대략)
| 노트북 | 실행 시간 | 시간이 걸리는 단계 |
|---|---|---|
| 02 | 10~15분 | 첫 배포(CodeBuild), PROD 엔드포인트 |
| 03 | 7~10분 | 재배포 |
| 04 | 10~15분 | Gateway/정책 엔진 생성, 재배포 |
| 05 | 10~15분 | Memory 생성, 장기 메모리 추출 대기, 재배포 |
| 06 | 10~15분 | 스팬 인덱싱 대기, 평가 실행 |

## 데모 계정 정보

| 항목 | 값 |
|---|---|
| Cognito 사용자 | `alice`, `bob` |
| 비밀번호 | `demo_helpers/config.py` 의 `DEMO_PASSWORD` (데모 전용) |
| 테스트 시리얼 | `SN1000001`(보증 유효), `SN2000002`(만료) |
| 환불 정책 | 500,000원 미만만 허용 (Cedar) |

## 문제 해결

| 증상 | 확인할 것 |
|---|---|
| `AccessDeniedException` (모델 호출) | Bedrock 콘솔의 모델 액세스, `MODEL_ID` 와 리전 |
| 03장 이후 `invoke_with_iam` 실패 | 의도된 동작 — 03장부터 런타임은 JWT 인증만 허용 |
| 401/403 (JWT 호출) | 토큰 만료(1시간) → `get_bearer_token()` 셀 재실행 |
| 04장 `GATEWAY_URL` KeyError | 04장 런타임 배포 셀에서 `env_vars` 가 전달되었는지 |
| 05장 장기 메모리가 비어 있음 | 추출은 비동기 — 1~2분 후 다시 조회 |
| 06장 스팬/평가 결과 없음 | Transaction Search 활성화 후 새 트래픽 생성, 2~5분 대기 |
| 런타임 오류 원인 | CloudWatch 로그 그룹 `/aws/bedrock-agentcore/runtimes/<agent_id>-DEFAULT` |

## 참고 소스

`agentcore-samples-main` 의 다음 예제를 참고해, 강의 챕터 순서(Runtime → Identity → Gateway → Memory → Observability)에 맞게 재구성했습니다.
- `06-workshops/09-AgentCore-E2E/strands-agents` (고객지원 에이전트 E2E 워크숍)
- `01-features/02-host-your-agent` (비동기 작업), `01-features/05-authenticate-and-authorize` (아웃바운드 인증)
- `01-features/03-connect-your-agent-to-anything/01-code-interpreter`, `01-features/07-centralize-and-govern-your-ai-infrastructure/02-policy`
- `06-workshops/07-AgentCore-evaluations`
