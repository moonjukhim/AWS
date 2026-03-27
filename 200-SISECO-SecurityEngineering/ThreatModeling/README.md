# 1. Introduction to Threat Modeling

### 2. Threat Modeling at AWS

Exercises

- What are we working on?
- What can go wrong?
- What are we going to do about it?
- Did we do a good enough job?

---

##### References

- [위협 모델링에 접근하는 방법](https://aws.amazon.com/ko/blogs/security/how-to-approach-threat-modeling/)
- [SAFECode 전술적 위협 모델링 백서](https://safecode.org/wp-content/uploads/2017/05/SAFECode_TM_Whitepaper.pdf)
- [OWASP(Open Web Application Security Project) 위협 모델링 치트 시트](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [Threat Modeling for Builders Workshop]()

---

##### threat-composer

- https://github.com/awslabs/threat-composer
- https://awslabs.github.io/threat-composer/workspaces/default/dashboard

---

###

- User + Amazon Cognito
- Host Orchestrator Agent (A2A Client 포함)
- AgentCore Runtime (각 Agent)
- AgentCore Gateway
- External Tools (Smithy / Tavily 등)
- LLM (Amazon Bedrock / GPT-4o / Gemini)
- Agent Memory / Observability

1. User + Cognito

| STRIDE | 위협                   | 설명                                         | 대응 방안                                   |
| ------ | ---------------------- | -------------------------------------------- | ------------------------------------------- |
| S      | Spoofing               | JWT 탈취, 세션 하이재킹, OAuth redirect 공격 | PKCE, Short-lived token, Secure cookie, MFA |
| T      | Tampering              | JWT payload 변조, session_id 조작            | JWT signature 검증, 서버측 session 관리     |
| R      | Repudiation            | 사용자 요청 부인                             | CloudTrail, audit log, user_id 추적         |
| I      | Information Disclosure | 토큰 노출, 사용자 데이터 유출                | TLS 강제, PII masking                       |
| D      | DoS                    | 로그인 brute force, token endpoint abuse     | Rate limit, WAF                             |
| E      | Elevation of Privilege | 권한 상승 공격                               | Least privilege IAM, scope 제한             |

2. Host Orchestrator Agent

| STRIDE | 위협                   | 설명                                 | 대응 방안                            |
| ------ | ---------------------- | ------------------------------------ | ------------------------------------ |
| S      | Spoofing               | agent impersonation, fake agent-card | Agent signing, mTLS                  |
| T      | Tampering              | payload 조작, tool invocation 변조   | Input validation, policy enforcement |
| R      | Repudiation            | agent action 추적 불가               | Structured logging, trace ID         |
| I      | Information Disclosure | agent 간 데이터 leakage              | Agent isolation, context scoping     |
| D      | DoS                    | recursive agent loop                 | Max depth, timeout, circuit breaker  |
| E      | Elevation of Privilege | tool misuse, 권한 상승               | IAM role 분리, policy sandbox        |

3. AgentCore Runtime

| STRIDE | 위협                   | 설명              | 대응 방안                           |
| ------ | ---------------------- | ----------------- | ----------------------------------- |
| S      | Spoofing               | runtime 위장      | Signed runtime, identity validation |
| T      | Tampering              | agent-card 변조   | Checksum, signature                 |
| I      | Information Disclosure | memory leakage    | Encryption, context boundary        |
| D      | DoS                    | agent overload    | Autoscaling, rate limit             |
| E      | Elevation of Privilege | runtime 권한 탈취 | Container isolation, sandbox        |

4. AgentCore Gateway

| STRIDE | 위협                   | 설명                     | 대응 방안                  |
| ------ | ---------------------- | ------------------------ | -------------------------- |
| S      | Spoofing               | API key spoofing         | IAM auth, JWT validation   |
| T      | Tampering              | request 변조             | TLS, request signing       |
| I      | Information Disclosure | stream data 노출         | Encryption, redaction      |
| D      | DoS                    | API flooding             | Throttling                 |
| E      | Elevation of Privilege | unauthorized tool access | Fine-grained authorization |

5. External Tools (Smithy / Tavily)

| STRIDE | 위협                   | 설명              | 대응 방안            |
| ------ | ---------------------- | ----------------- | -------------------- |
| S      | Spoofing               | fake external API | Endpoint allowlist   |
| T      | Tampering              | 응답 데이터 변조  | Response validation  |
| I      | Information Disclosure | 데이터 외부 유출  | Outbound policy, DLP |
| D      | DoS                    | API 장애          | Fallback 전략        |
| E      | Elevation of Privilege | API 권한 남용     | 최소 권한 API key    |

6. LLM (Bedrock / GPT / Gemini)

| STRIDE | 위협                   | 설명                | 대응 방안                           |
| ------ | ---------------------- | ------------------- | ----------------------------------- |
| S      | Spoofing               | fake model endpoint | 공식 endpoint 사용                  |
| T      | Tampering              | Prompt Injection    | Input filtering, system prompt 보호 |
| I      | Information Disclosure | 데이터 leakage      | 민감정보 제거, guardrails           |
| D      | DoS                    | 모델 호출 폭주      | Rate limit, caching                 |
| E      | Elevation of Privilege | tool chain exploit  | Tool execution control              |

7. Agent Memory / Observability

| STRIDE | 위협                   | 설명             | 대응 방안                 |
| ------ | ---------------------- | ---------------- | ------------------------- |
| S      | Spoofing               | memory 접근 위장 | Access control            |
| T      | Tampering              | 로그 변조        | Immutable logging         |
| R      | Repudiation            | 로그 부인        | Signed logs               |
| I      | Information Disclosure | 민감 정보 저장   | Encryption, anonymization |
| D      | DoS                    | logging overload | Sampling                  |
| E      | Elevation of Privilege | memory 권한 상승 | RBAC                      |

---

##### Top 5 Risk

| 순위 | 위협                         | 설명                         |
| ---- | ---------------------------- | ---------------------------- |
| 1    | Prompt Injection → Tool 실행 | LLM 기반 공격의 핵심         |
| 2    | Agent 간 데이터 Leakage      | Multi-agent 구조 취약점      |
| 3    | Tool 권한 남용               | CloudWatch 등 실제 사고 다수 |
| 4    | Token 탈취                   | 계정 takeover                |
| 5    | External API 데이터 유출     | 검색 API 통한 exfiltration   |
