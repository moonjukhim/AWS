# 프로젝트 스티어링 — Task-2 Retrieve API 기반 Q&A 애플리케이션

- **문서 버전**: 1.0
- **작성일**: 2026-09-02

---

## 1. 제품 컨텍스트

| 항목 | 내용 | 노트북 근거 |
|---|---|---|
| 무엇 | AnyCompany 재무 10-K 문서에 대한 근거 기반 Q&A 애플리케이션 | 셀 0 시나리오 |
| 데이터 | AnyCompany financial 10k 합성 데이터셋의 텍스트 임베딩 | 셀 0 |
| 누가 | AWS 기반 AI 개발 과정 수강생 (실습 환경에서 직접 실행) | 셀 0 |
| 어디서 | 사전 프로비저닝된 Amazon Bedrock Knowledge Base | 셀 0 |
| 왜 이 구조 | `Retrieve` API로 검색하고, 그 결과를 컨텍스트로 프롬프트를 증강해 FM에 전달 | 셀 0, 셀 7 |
| 성공 기준 | 검색된 청크를 근거로 수치를 포함한 구체적 답변을 생성한다 | 셀 19, 셀 33 |

---

## 2. 절대 규칙

노트북이 명시적으로 요구하거나 코드로 강제하는 것들. 어기면 실습이 깨진다.

1. **셀을 한 번에 하나씩 실행한다.** `Run` 메뉴의 `Run All Cells`를 쓰지 않는다. 셀 0이 직접 경고한다 — 모든 셀을 한꺼번에 실행하면 커널 충돌 또는 리소스 제한으로 예기치 않은 오류가 발생한다.
2. **Knowledge Base를 코드에서 생성하지 않는다.** KB는 실습 환경에 사전 생성되어 있고, 노트북은 **조회만** 한다(셀 3).
3. **KB ID를 하드코딩하지 않는다.** `list_knowledge_bases`로 조회해 `kb_id`에 할당한다(셀 3).
4. **리전을 하드코딩하지 않는다.** `boto3.session.Session().region_name`을 쓴다(셀 5).
5. **모델은 `amazon.nova-lite-v1:0`을 쓴다.** 셀 6이 명시하고, 파트 1(셀 23)과 파트 2(셀 27)가 같은 `modelId` 변수를 공유한다.
6. **프롬프트의 네 지시를 삭제하지 않는다**(§6). 답변 품질이 이 지시에 의존한다.

---

## 3. 기술 스택

노트북이 실제로 임포트하고 호출하는 것만 적는다. 여기 없는 라이브러리를 새로 들이지 않는다.

| 계층 | 채택 | 노트북 근거 |
|---|---|---|
| 언어 | Python (Jupyter Notebook) | 전체 |
| AWS SDK | `boto3`, `botocore` (`botocore.client.Config`) | 셀 3, 5 |
| KB 조회 | `bedrock-agent` · `list_knowledge_bases` | 셀 3 |
| 검색 | `bedrock-agent-runtime` · `retrieve` | 셀 5, 9 |
| 생성 | `bedrock-runtime` · `invoke_model` | 셀 5, 23 |
| 프레임워크 | `langchain`, `langchain_aws`, `langchain_core` | 셀 27, 33, 36 |
| 출력 | `pprint.PrettyPrinter(indent=2)` | 셀 5 |
| 직렬화 | `json` | 셀 5, 23 |

**클라이언트 생성 규칙** (셀 5 원문)

```python
session = boto3.session.Session()
region = session.region_name

bedrock_config = Config(connect_timeout=120, read_timeout=120,
                        retries={'max_attempts': 0})
bedrock_client = boto3.client('bedrock-runtime', region_name=region)
bedrock_agent_client = boto3.client("bedrock-agent-runtime",
                                    config=bedrock_config, region_name=region)
```

- 타임아웃 120초는 **검색 + 임베딩 왕복**을 감안한 값이다. 줄이지 않는다.
- `retries={'max_attempts': 0}`는 **의도적으로 재시도를 끈 설정**이다. 실습에서 오류가 조용히 감춰지지 않고 즉시 드러나게 한다. 바꾸려면 §9 절차를 따른다.
- `bedrock_config`는 검색 클라이언트에만 적용된다. 생성 클라이언트(`bedrock-runtime`)에는 붙지 않는다.

---

## 4. 실행 순서 의존성

노트북은 **위에서 아래로 순차 실행**을 전제로 한다. 이 전제가 깨지면 조용히 잘못된 결과가 나온다.

### 4.1 변수 이름 재바인딩 — 가장 중요한 주의점

`bedrock_client`라는 **하나의 이름**에 서로 다른 서비스 클라이언트가 차례로 바인딩된다.

| 셀 | 바인딩 | 이후 용도 |
|---|---|---|
| 3 | `session.client('bedrock-agent')` | KB 목록 조회 (셀 3에서만 사용) |
| 5 | `boto3.client('bedrock-runtime')` | 모델 호출 (셀 23), LangChain LLM (셀 27) |

- **셀 3을 셀 5보다 먼저 실행해야 한다.** 순서가 뒤바뀌면 셀 3이 `bedrock-runtime` 클라이언트로 `list_knowledge_bases`를 호출해 실패한다.
- 셀 5를 재실행한 뒤 셀 3을 다시 실행하면 `bedrock_client`가 다시 `bedrock-agent`로 바뀌어 **셀 23이 깨진다**. 셀 3을 재실행했으면 셀 5도 재실행한다.
- `bedrock_agent_client`(셀 5)는 이름과 달리 `bedrock-agent`가 아니라 **`bedrock-agent-runtime`**이다. 헷갈리기 쉬운 지점이므로 코드를 읽을 때 서비스 이름을 확인한다.

---

## 5. 검색 파라미터 규칙

두 경로가 **서로 다른 설정**을 쓴다. 이것은 오류가 아니라 두 옵션을 모두 보여주려는 구성이다.

| | 파트 1 (셀 9·13) | 파트 2 (셀 30) |
|---|---|---|
| `numberOfResults` | 5 | 4 |
| `overrideSearchType` | `HYBRID` | `SEMANTIC` |

- `overrideSearchType`은 **선택 파라미터**다(셀 9 주석 `# optional`). 지정하지 않으면 Bedrock이 가장 적합한 전략을 자동 선택한다(셀 7).
- `HYBRID`는 키워드 매칭과 의미 유사도를 함께 쓰고, `SEMANTIC`은 의미 유사도만 쓴다(셀 7).
- **두 값 중 하나를 다른 쪽에 맞춰 통일하지 않는다.** 차이를 관찰하는 것이 학습 내용이다. 통일하려면 §9 절차를 따르고 마크다운 설명도 함께 고친다.
- 검색 결과 개수를 바꾸면 컨텍스트 길이가 바뀌고 답변도 바뀐다. 값을 바꿔볼 때는 답변 변화를 함께 관찰한다.

---

## 6. 프롬프트 작성 규칙

파트 1(셀 19)과 파트 2(셀 33)의 프롬프트는 **플레이스홀더 이름만 다르고 문구가 동일**하다.

| | 파트 1 | 파트 2 |
|---|---|---|
| 컨텍스트 | `{contexts}` (f-string) | `{context}` (PromptTemplate) |
| 질문 | `{query}` (f-string) | `{question}` (PromptTemplate) |

**구조를 고정한다.**

```
Human: <역할 정의>
<지시문>
<context>
...
</context>

<question>
...
</question>

<출력 지시>

Assistant:
```

**삭제하지 않는 네 지시** (셀 19·33 원문)
1. 역할 — `You are a financial advisor AI system` (사실과 통계에 기반해 답한다)
2. 근거 한정 — `Use the following pieces of information to provide a concise answer`
3. 환각 금지 — `If you don't know the answer, just say that you don't know, don't try to make up an answer`
4. 구체성 — `The response should be specific and use statistics or numbers when possible`

**형식 규칙**
- `Human:` 으로 시작하고 `Assistant:` 로 끝낸다. 두 접두사를 빼지 않는다.
- 컨텍스트는 `<context>`, 질문은 `<question>` 태그로 감싼다. 태그 이름을 바꾸지 않는다.
- 두 프롬프트의 문구를 한쪽만 고치지 않는다. **한쪽을 고치면 다른 쪽도 고친다** — 두 경로의 답변을 비교할 수 없게 된다.

---

## 7. 코드 스타일

노트북에서 관찰된 관례를 따른다.

### 7.1 명명

| 대상 | 관례 | 예 |
|---|---|---|
| 함수 | `snake_case` | `retrieve`, `get_contexts`, `format_docs` |
| 지역 변수 | `snake_case` | `kb_id`, `contexts`, `response_body` |
| 함수 인자 | AWS API 키를 따라 camelCase 혼용 | `kbId`, `numberOfResults` |
| AWS API 응답 키 | API가 정한 camelCase 그대로 | `retrievalResults`, `knowledgeBaseSummaries` |
| 모델 관련 | `modelId`, `nova_payload`, `nova_prompt` | |

- 노트북은 함수 인자에 `kbId`처럼 camelCase를 쓴다(셀 9). AWS API 파라미터와 이름을 맞추려는 의도다. 새 함수를 추가할 때 이 관례를 따를지는 §9로 결정한다.

### 7.2 출력

- 구조화된 값은 `pp.pprint(...)`로 출력한다 — 검색 결과(셀 13), 컨텍스트(셀 16).
- 단순 문자열은 `print(...)`로 출력한다 — 답변(셀 23, 36), 문서 본문(셀 30).
- 문서 목록을 출력할 때는 항목 사이에 `print("------")` 구분선을 넣는다(셀 30).
- **모든 코드 셀은 눈에 보이는 결과를 남긴다.** 아무것도 출력하지 않는 셀은 정의 셀(함수·상수·페이로드)뿐이다.

### 7.3 함수 분리

노트북은 재사용되는 것만 함수로 만든다.

| 함수 | 셀 | 책임 |
|---|---|---|
| `retrieve(query, kbId, numberOfResults=5)` | 9 | Retrieve API 호출 |
| `get_contexts(retrievalResults)` | 15 | 텍스트 청크 추출 |
| `format_docs(docs)` | 36 | LangChain 문서 본문 병합 |

- 함수는 **값을 반환**하고, 출력은 호출부 셀에서 한다. 세 함수 모두 `print`를 포함하지 않는다.
- 한 번만 쓰이는 코드는 함수로 감싸지 않고 셀에 그대로 둔다(프롬프트 조립, 모델 호출). 교육 자료에서 추상화는 학습을 방해한다.

---

## 8. 모델 호출 규칙

### 8.1 페이로드 (셀 22)

```python
nova_payload = {
    "schemaVersion": "messages-v1",
    "messages": [{"role": "user", "content": [{"text": prompt}]}],
    "inferenceConfig": {"maxTokens": 512, "temperature": 0.5,
                        "topP": 0.9, "topK": 20},
}
```

- `schemaVersion: "messages-v1"`은 **Amazon Nova 계열 전용 스키마**다. 다른 모델로 바꾸면 이 페이로드가 그대로 통하지 않는다. 모델 교체는 §9 절차를 거친다.
- 네 개의 추론 파라미터를 모두 명시한다. 생략하지 않는다.
- 페이로드 정의(셀 22)와 호출(셀 23)을 **다른 셀로 나눈다**. 페이로드 내용을 먼저 확인시키려는 구성이다.

### 8.2 호출과 응답 파싱 (셀 23)

```python
response = bedrock_client.invoke_model(
    body=json.dumps(nova_payload), modelId=modelId,
    accept='application/json', contentType='application/json')
response_body = json.loads(response.get('body').read())
```

- `body`는 **JSON 문자열**이어야 한다. dict를 그대로 넘기지 않는다.
- 응답 본문은 스트림이다. `response.get('body').read()` 후 `json.loads`로 파싱한다.
- 텍스트 추출 시 **키 존재를 확인한 뒤 접근한다**(셀 23 원문 방식).
  ```python
  if 'output' in response_body and 'message' in response_body['output']:
      message_content = response_body['output']['message']['content']
      if message_content and isinstance(message_content, list):
          response_text = message_content[0].get('text', '')
  ```
  `response_body['output']['message']['content'][0]['text']`로 한 줄에 꺼내지 않는다. 응답 구조가 다를 때 어디서 어긋났는지 알 수 없게 된다.

---

## 9. 문서 동기화 규칙

- 구현이 `requirements.md`와 어긋나면 **요구 사항 문서를 먼저 갱신**하고 나서 코드를 고친다. 코드만 고치면 다음 세션에서 되돌아간다.
- 갱신 순서는 항상 **규칙 → 요구 사항 → 설계 → 작업 → 코드**다.
- 새 동작을 추가하면 REQ ID를 새로 부여한다. 기존 ID의 의미를 바꾸지 않는다.
- 다음 변경은 **파급 범위가 넓다.** 고치기 전에 영향 범위를 먼저 적는다.

| 변경 | 함께 고쳐야 하는 것 |
|---|---|
| 모델 교체 | 셀 22 페이로드 스키마, 셀 23 응답 파싱, 셀 27 LLM, 셀 6·20 설명, §2-5·§8 |
| 질문 변경 | 셀 13과 셀 30 **두 곳** |
| 프롬프트 문구 변경 | 셀 19와 셀 33 **두 곳**, §6 |
| 검색 파라미터 변경 | 해당 셀, 셀 7·28 설명, §5 |
| 재시도 설정 변경 | 셀 5, §3 |

- 요구 사항 ↔ 코드 대응은 마크다운 셀 또는 주석에 REQ ID로 남긴다.

---

## 10. 노트북 작성 규칙

- **코드 셀 앞에는 반드시 마크다운 셀을 둔다.** 노트북 전체가 이 패턴을 지킨다(예외 없음).
- 실행을 지시하는 마크다운 셀은 **번호로 시작한다** — `1.` ~ `11.`까지 순차. 코드 셀을 추가하면 번호를 다시 매긴다.
- 섹션 번호 체계를 지킨다: `## 태스크 2.x` → `#### 태스크 2.x.y`. 파트 구분은 `## 파트 N`.
- 안내 문구는 노트북의 아이콘 관례를 따른다.

| 용도 | 마크업 |
|---|---|
| 자세히 알아보기 | `<i class="fas fa-info-circle" style="color:#007FAA"></i>` |
| 주의 | `<i class="fas fa-exclamation-circle" style="color:#7C5AED"></i>` |
| 참고 | `<i class="fas fa-sticky-note" style="color:#563377"></i>` |
| 태스크 완료 | `<i class="far fa-thumbs-up" style="color:#008296"></i>` |

- 이미지는 `images/` 상대 경로로 참조한다(셀 7의 `images/retrieveAPI.png`). **현재 이 폴더에 `images/` 디렉터리가 없다** — 노트북을 배포할 때 함께 제공해야 한다.
- 노트북 마지막 셀은 **다음 단계 안내**로 끝낸다(셀 37: 탭을 닫고 실습 지침으로 돌아가 태스크 3을 계속).

---

## 11. 검토 체크리스트

작업을 완료로 보고하기 전에 이 목록을 통과시킨다.

- [ ] 절대 규칙 6개(§2) 위반이 없다
- [ ] 새 커널에서 셀을 **하나씩 순서대로** 실행해 오류가 없다
- [ ] `kb_id`가 코드로 조회되고 하드코딩되어 있지 않다
- [ ] 리전이 하드코딩되어 있지 않다
- [ ] 셀 3 → 셀 5 순서 의존(§4.1)이 마크다운으로 설명되어 있다
- [ ] 파트 1의 검색 설정(5/HYBRID)과 파트 2(4/SEMANTIC)가 각각 유지되어 있다
- [ ] 두 프롬프트의 문구가 동일하다(플레이스홀더 이름 제외)
- [ ] 프롬프트의 네 지시(§6)가 모두 남아 있다
- [ ] 모든 코드 셀 앞에 설명 마크다운 셀이 있고, 실행 지시 번호가 순차적이다
- [ ] 두 경로가 같은 질문에 대해 근거 있는 답변을 낸다
