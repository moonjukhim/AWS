# 설계 문서 — Task-2: Retrieve API 기반 Q&A 애플리케이션

- **문서 버전**: 1.0
- **작성일**: 2026-09-02
- **근거**: `project/Task-2.ipynb` (총 38셀 — 마크다운 26, 코드 12)
- **상위 문서**: `requirements.md`(무엇을), `proj-steering.md`(어떻게 — 규칙)
- **하위 문서**: `tasks.md`(어떤 순서로)

> 이 문서는 노트북의 **실제 구조**를 기술한다. 개선안이 아니라 현재 설계의 기록이다.
> 모든 구성 요소는 REQ ID와 셀 번호를 함께 인용한다.

---

## 1. 설계 개요

### 1.1 구조

노트북은 **같은 RAG 워크플로를 두 번** 구현한다. 앞은 API를 직접 부르고, 뒤는 프레임워크에 맡긴다.

```
파트 1 (셀 0~23)                        파트 2 (셀 24~37)
  태스크 2.1 환경 설정                     태스크 2.3 LangChain 통합
    2.1.1 KB ID 확인                        2.3.1 환경 설정
    2.1.2 클라이언트 생성                    2.3.2 리트리버 생성
  태스크 2.2 Retrieve API                    2.3.3 프롬프트 정의
    2.2.1 검색 실행                          2.3.4 LCEL 체인 구성
    2.2.2 텍스트 청크 추출
    2.2.3 프롬프트 증강
    2.2.4 모델 호출
```

- 태스크 2.1(환경 설정)은 **두 파트가 공유**한다. 파트 2는 자체 환경 설정 셀(2.3.1)을 갖지만
  클라이언트와 `kb_id`는 파트 1의 것을 그대로 쓴다.
- 파트 2는 파트 1에 **의존한다**. 독립 실행 가능한 구조가 아니다(§4.2).

### 1.2 두 파트 대비표

| | 파트 1 (boto3) | 파트 2 (LangChain) | 근거 |
|---|---|---|---|
| 검색 | `bedrock_agent_client.retrieve()` | `AmazonKnowledgeBasesRetriever` | 셀 9 / 30 |
| 검색 결과 수 | 5 | 4 | 셀 9 / 30 |
| 검색 전략 | `HYBRID` | `SEMANTIC` | 셀 9 / 30 |
| 반환 형식 | dict (`retrievalResults`) | `Document` 객체 리스트 | 셀 13 / 30 |
| 컨텍스트 조립 | `get_contexts()` → list | `format_docs()` → str | 셀 15 / 36 |
| 프롬프트 | f-string | `PromptTemplate` | 셀 19 / 33 |
| 모델 호출 | `invoke_model` + Nova 페이로드 | `ChatBedrock` | 셀 23 / 27 |
| 응답 파싱 | 수동 (dict 탐색) | `StrOutputParser` | 셀 23 / 36 |
| 조립 방식 | 셀 단위 순차 실행 | LCEL 파이프 연산자 | 셀 13~23 / 36 |

**설계 의도**: 파트 1에서 손으로 한 일곱 단계가 파트 2에서는 파이프 연산자 한 줄로 줄어든다.
이 대비가 태스크의 학습 내용이다.

---

## 2. 셀 구조

### 2.1 전체 셀 목록

| 셀 | 유형 | 섹션 | 내용 | REQ |
|---|---|---|---|---|
| 0 | MD | 제목 | 태스크 개요, 시나리오, `Run All Cells` 경고 | CON-01 |
| 1 | MD | 태스크 2.1 | 환경 설정 안내 | |
| 2 | MD | 2.1.1 | KB ID 확인 안내 + 지시 `1.` | |
| 3 | **코드** | 2.1.1 | KB ID 조회 | REQ-01~03 |
| 4 | MD | 2.1.2 | 클라이언트 생성 안내 + 지시 `2.` | |
| 5 | **코드** | 2.1.2 | 라이브러리 임포트, 클라이언트 3종 | REQ-04 |
| 6 | MD | 파트 1 | Nova Lite 사용 안내 | REQ-14 |
| 7 | MD | 태스크 2.2 | Retrieve API 설명 + 다이어그램 | REQ-06 |
| 8 | MD | | 지시 `3.` | |
| 9 | **코드** | 2.2 | `retrieve()` 함수 정의 | REQ-05, REQ-06 |
| 10~12 | MD | 2.2.1 | 검색 실행 안내 + 지시 `4.` | |
| 13 | **코드** | 2.2.1 | 질문 정의, 검색 실행, 결과 출력 | REQ-07, REQ-08 |
| 14 | MD | 2.2.2 | 청크 추출 안내 + 지시 `5.` | |
| 15 | **코드** | 2.2.2 | `get_contexts()` 함수 정의 | REQ-09 |
| 16 | **코드** | 2.2.2 | 컨텍스트 추출 및 출력 | REQ-10 |
| 17~18 | MD | 2.2.3 | 프롬프트 설명 + 지시 `6.` | |
| 19 | **코드** | 2.2.3 | 프롬프트 조립 (f-string) | REQ-11, REQ-12 |
| 20~21 | MD | 2.2.4 | 모델 호출 안내 + 지시 `7.` | |
| 22 | **코드** | 2.2.4 | Nova 페이로드 구성 | REQ-13 |
| 23 | **코드** | 2.2.4 | `invoke_model` 호출, 응답 파싱, 출력 | REQ-14~16 |
| 24 | MD | 파트 2 / 태스크 2.3 | LangChain 통합 개요 | |
| 25~26 | MD | 2.3.1 | 환경 설정 안내 + 지시 `8.` | |
| 27 | **코드** | 2.3.1 | LangChain 임포트, `ChatBedrock` 생성 | REQ-17 |
| 28~29 | MD | 2.3.2 | 리트리버 설명 + 지시 `9.` | |
| 30 | **코드** | 2.3.2 | 리트리버 생성, 검색, 문서 출력 | REQ-18, REQ-19 |
| 31~32 | MD | 2.3.3 | 프롬프트 설명 + 지시 `10.` | |
| 33 | **코드** | 2.3.3 | `PROMPT_TEMPLATE`, `PromptTemplate` | REQ-20 |
| 34~35 | MD | 2.3.4 | 체인 설명 + 지시 `11.` | |
| 36 | **코드** | 2.3.4 | `format_docs()`, LCEL 체인, 실행 | REQ-21, REQ-22 |
| 37 | MD | 마무리 | 태스크 완료, 다음 단계 안내 | |

### 2.2 셀 패턴

노트북 전체가 예외 없이 지키는 두 패턴.

1. **마크다운 → 코드**: 모든 코드 셀 앞에 그 셀을 설명하는 마크다운 셀이 있다.
2. **번호 지시**: 실행을 요구하는 마크다운 셀은 `1.` ~ `11.`로 번호가 매겨진다. 코드 셀 12개에 지시 11개
   — 셀 15와 16이 하나의 지시(`5.` "다음 코드 셀 2개를 실행")를 공유하고, 셀 22와 23도
   하나의 지시(`7.` "다음 2개의 코드 셀을 실행")를 공유한다.

---

## 3. 구성 요소 설계

### 3.1 클라이언트 (셀 3, 5)

| 변수 | 서비스 | 생성 셀 | 설정 | 용도 |
|---|---|---|---|---|
| `bedrock_client` (1차) | `bedrock-agent` | 3 | 기본 | KB 목록 조회 |
| `bedrock_client` (2차) | `bedrock-runtime` | 5 | `region_name` | 모델 호출 (셀 23, 27) |
| `bedrock_agent_client` | `bedrock-agent-runtime` | 5 | `bedrock_config`, `region_name` | 검색 (셀 9) |

```python
bedrock_config = Config(connect_timeout=120, read_timeout=120,
                        retries={'max_attempts': 0})
```

**설계상 주의 두 가지**

- `bedrock_client`가 **같은 이름에 두 번 바인딩된다**(CON-02). 셀 3의 것은 셀 3에서만 쓰이고,
  셀 5가 덮어쓴 뒤로는 생성용이다. 셀 3을 나중에 재실행하면 셀 23이 깨진다.
- `bedrock_agent_client`는 이름과 달리 `bedrock-agent`가 아니라 **`bedrock-agent-runtime`**이다(CON-03).
  제어 평면(`bedrock-agent`)과 데이터 평면(`bedrock-agent-runtime`)은 다른 서비스다.

### 3.2 `retrieve(query, kbId, numberOfResults=5)` (셀 9 / REQ-05, REQ-06)

```python
return bedrock_agent_client.retrieve(
    retrievalQuery={'text': query},
    knowledgeBaseId=kbId,
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': numberOfResults,
            'overrideSearchType': "HYBRID",   # optional
        }
    })
```

- 반환은 **원시 API 응답**이다. 파싱하지 않는다.
- `overrideSearchType`이 함수 본문에 고정되어 있다 — 파라미터가 아니다.
  전략을 바꾸려면 함수 정의를 고쳐야 한다.
- `numberOfResults`만 인자로 노출된다. 호출부(셀 13)는 `retrieve(query, kb_id, 5)`로
  **위치 인자**를 쓴다.

### 3.3 `get_contexts(retrievalResults)` (셀 15 / REQ-09)

```python
contexts = []
for retrievedResult in retrievalResults:
    contexts.append(retrievedResult['content']['text'])
return contexts
```

- **`content.text`만 보존한다.** `location`(소스 URI)과 `score`(관련성 점수)는 여기서 버려진다.
- 버려진 두 값은 셀 13의 `pp.pprint(retrievalResults)` 출력에서만 확인할 수 있다.
  최종 답변에는 출처가 표기되지 않는다.

### 3.4 프롬프트 (셀 19 / REQ-11, REQ-12)

```python
prompt = f"""
Human: You are a financial advisor AI system, and provides answers to questions by using fact based and statistical information when possible.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{contexts}
</context>

<question>
{query}
</question>

The response should be specific and use statistics or numbers when possible.

Assistant:"""
```

- `{contexts}`는 **리스트**다. f-string이 `str(list)`를 호출하므로 프롬프트에는
  `['청크1', '청크2', ...]` 형태의 파이썬 리터럴이 삽입된다.
  파트 2의 `format_docs()`(빈 줄 2개로 join)와 결과 문자열이 다르다.
- 프롬프트를 출력하는 셀이 없다. 컨텍스트가 어떻게 삽입되었는지는 육안으로 확인되지 않는다.

### 3.5 모델 호출 (셀 22, 23 / REQ-13 ~ REQ-16)

**페이로드 구성과 호출을 두 셀로 나눈다.** 페이로드 내용을 먼저 확인시키려는 구성이다.

```python
# 셀 22 — 정의만, 출력 없음
nova_payload = {
    "schemaVersion": "messages-v1",
    "messages": [{"role": "user", "content": [{"text": prompt}]}],
    "inferenceConfig": {"maxTokens": 512, "temperature": 0.5,
                        "topP": 0.9, "topK": 20},
}

# 셀 23 — 호출, 파싱, 출력
response = bedrock_client.invoke_model(
    body=json.dumps(nova_payload), modelId=modelId,
    accept='application/json', contentType='application/json')
response_body = json.loads(response.get('body').read())
```

**응답 파싱 — 방어적 단계 접근**

```python
response_text = ''
if 'output' in response_body and 'message' in response_body['output']:
    message_content = response_body['output']['message']['content']
    if message_content and isinstance(message_content, list):
        response_text = message_content[0].get('text', '')
```

- 세 단계로 나눠 확인한다: `output`/`message` 키 존재 → `content`가 비지 않은 리스트 →
  첫 원소의 `text`.
- 어느 단계에서 어긋나도 `KeyError` 없이 빈 문자열이 된다.
- `content[0]`만 본다 — 블록이 여러 개면 첫 번째만 취한다.

### 3.6 LangChain 구성 요소 (셀 27, 30, 33, 36)

```python
# 셀 27 — LLM
llm = ChatBedrock(model_id=modelId, client=bedrock_client)

# 셀 30 — 리트리버
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id=kb_id,
    retrieval_config={"vectorSearchConfiguration": {
        "numberOfResults": 4,
        'overrideSearchType': "SEMANTIC",
    }})
docs = retriever.invoke(input=query)

# 셀 33 — 프롬프트
nova_prompt = PromptTemplate(template=PROMPT_TEMPLATE,
                             input_variables=["context", "question"])

# 셀 36 — 체인
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()}
         | nova_prompt | llm | StrOutputParser())
response = chain.invoke(query)
```

- `ChatBedrock`은 `modelId`(셀 23)와 `bedrock_client`(셀 5)를 **재사용**한다. 새로 만들지 않는다.
- 셀 30은 리트리버를 만들고 **즉시 한 번 호출해** 결과를 보여준다. 그리고 셀 36의 체인이
  같은 리트리버를 **다시 호출**한다 — 검색이 총 2회 일어난다. 중간 결과를 보여주기 위한 구성이다.
- `retriever.invoke(input=query)`는 키워드 인자를, `chain.invoke(query)`는 위치 인자를 쓴다.
- LCEL 딕셔너리에서 `retriever | format_docs`가 `context`를, `RunnablePassthrough()`가
  `question`을 채운다. 두 키 이름이 `PromptTemplate`의 `input_variables`와 일치해야 한다.

---

## 4. 데이터 흐름

### 4.1 파트 1

```
질문 (셀 13)
  │
  ▼
retrieve() ──> retrievalResults  [{content:{text}, location, score}, ...]  (셀 13)
  │                    │
  │                    └──> pp.pprint  ← 점수·위치를 볼 수 있는 유일한 지점
  ▼
get_contexts() ──> contexts  ['청크1', '청크2', ...]                       (셀 15,16)
  │                    │                (location·score는 여기서 버려짐)
  │                    └──> pp.pprint
  ▼
f-string ──> prompt  (str(list)로 삽입)                                     (셀 19)
  │
  ▼
nova_payload ──> invoke_model ──> response_body                             (셀 22,23)
  │
  ▼
단계적 파싱 ──> response_text ──> print
```

### 4.2 파트 2

```
질문 (셀 30에서 재할당)
  │
  ├──> retriever.invoke() ──> docs ──> print(page_content) + "------"       (셀 30)
  │                                     ← 중간 결과 확인용, 체인과 무관
  ▼
chain.invoke(query)                                                          (셀 36)
  │
  ├─ {"context": retriever | format_docs,   ← 검색 재실행 + "\n\n" join
  │   "question": RunnablePassthrough()}
  ▼
nova_prompt ──> llm (ChatBedrock) ──> StrOutputParser ──> response ──> print
```

### 4.3 파트 간 의존성

```
셀 3  ──kb_id──────────────────────────> 셀 13, 셀 30
셀 5  ──bedrock_client────────────────> 셀 23, 셀 27
      ──bedrock_agent_client──────────> 셀 9
      ──pp───────────────────────────> 셀 13, 셀 16
셀 23 ──modelId───────────────────────> 셀 27   ★ 파트 1 → 파트 2 의존
```

**★ 표시 지점이 핵심 제약이다**(CON-04). `modelId`가 파트 1의 마지막 코드 셀에서 정의되므로,
파트 2만 따로 실행할 수 없다. 파트 2를 독립 실행 가능하게 하려면 `modelId` 정의를
셀 5(환경 설정)나 셀 27로 옮겨야 하는데, 이는 설계 변경이므로 `proj-steering.md` §9 절차를 따른다.

---

## 5. 오류 처리 설계

노트북은 **한 곳에서만** 예외를 처리한다.

| 위치 | 처리 | 근거 |
|---|---|---|
| 셀 3 | `try/except botocore.exceptions.ClientError` → `print(f"Error: {e}")` | REQ-03 |
| 셀 3 | KB 0건 → `print("No Knowledge Base summaries found.")` | REQ-02 |
| 셀 9, 13, 23, 30, 36 | 처리 없음 — 예외가 그대로 셀을 실패시킨다 | |

**설계 의도와 결과**

- 실습 환경에서는 **예외가 그대로 드러나는 편이 낫다.** 수강생이 오류 메시지를 보고
  권한·모델 액세스·리전 문제를 스스로 확인할 수 있다.
- `retries={'max_attempts': 0}`도 같은 맥락이다(CON-06). 재시도가 실패를 감추지 않는다.
- 다만 셀 3의 두 실패 경로는 **`print` 후 계속 진행**한다. `kb_id`가 할당되지 않은 채
  셀 13에 도달하면 `NameError: kb_id`가 난다 — 실제 원인(KB 없음)에서 두 셀 떨어진 곳에서 증상이 나타난다.
  이 동작을 바꾸려면 REQ-02를 먼저 갱신한다.

---

## 6. 관찰된 설계 특성

노트북에 실제로 존재하는 성질들. **개선 지시가 아니라 사실의 기록**이며, 바꾸려면
`proj-steering.md` §9의 문서 갱신 절차를 따른다.

| # | 특성 | 위치 | 성격 |
|---|---|---|---|
| O-1 | 두 파트의 검색 설정이 다르다 (5/HYBRID vs 4/SEMANTIC) | 셀 9, 30 | **의도적** — 두 전략을 모두 보여준다 |
| O-2 | `query`가 두 곳에서 각각 할당된다 | 셀 13, 30 | 파트별 독립성을 위한 구성. 질문 변경 시 두 곳을 고쳐야 한다 |
| O-3 | `bedrock_client`가 두 서비스로 재바인딩된다 | 셀 3, 5 | 실행 순서 의존을 만든다 |
| O-4 | `modelId`가 파트 1에서 정의되어 파트 2가 의존한다 | 셀 23, 27 | 파트 2 독립 실행 불가 |
| O-5 | 프롬프트에 리스트가 `str(list)`로 삽입된다 | 셀 19 | 파트 2의 `"\n\n".join`과 형식이 다르다 |
| O-6 | 최종 프롬프트를 출력하는 셀이 없다 | 셀 19 | 컨텍스트 삽입 결과를 육안 확인할 수 없다 |
| O-7 | `location`·`score`가 컨텍스트 추출에서 버려진다 | 셀 15 | 답변에 출처가 표기되지 않는다 |
| O-8 | 파트 2에서 검색이 2회 실행된다 | 셀 30, 36 | 중간 결과 확인을 위한 구성 |
| O-9 | `overrideSearchType`이 `retrieve()` 본문에 고정되어 있다 | 셀 9 | 전략 변경 시 함수 정의를 고쳐야 한다 |
| O-10 | 검색 결과 0건에 대한 분기가 없다 | 셀 13~23 | 빈 컨텍스트로도 모델이 호출된다 |

---

## 7. 확장 지점

노트북을 변형·확장할 때 손대는 자리.

| 하고 싶은 것 | 손댈 곳 | 함께 고칠 것 |
|---|---|---|
| 다른 질문으로 실험 | 셀 13, 셀 30의 `query` | 두 곳 모두 (CON-05) |
| 검색 결과 수 변경 | 셀 13의 세 번째 인자, 셀 30의 `numberOfResults` | 답변 변화를 함께 관찰 |
| 검색 전략 비교 | 셀 9의 `overrideSearchType` | 셀 7의 설명 |
| 답변 길이 조정 | 셀 22의 `maxTokens` | |
| 답변 다양성 조정 | 셀 22의 `temperature`, `topP`, `topK` | |
| 프롬프트 실험 | 셀 19와 셀 33 | 두 곳 모두, REQ-12의 네 지시는 유지 |
| 모델 교체 | 셀 23의 `modelId` | 셀 22 페이로드 스키마, 셀 23 파싱, 셀 6·20 설명 (CON-07) |
| 출처 표기 추가 | 셀 15의 `get_contexts()` | `location` 보존, 셀 23 출력 (O-7) |
| 프롬프트 확인 | 셀 19 뒤에 `print(prompt)` 추가 | 지시 번호 재정렬 (O-6) |

---

## 8. 후속 태스크와의 관계

| 태스크 | 관계 | 근거 |
|---|---|---|
| 태스크 1 | `RetrieveAndGenerate` API로 검색·생성을 한 번에 처리. 태스크 2는 이를 두 단계로 분리한 형태다. | 셀 0 |
| 태스크 3 | RAGAS로 RAG 품질을 평가. 태스크 2의 리트리버와 체인 구성을 그대로 이어받는다. | 셀 37 |
| 태스크 4 | 가드레일 적용. 모델 호출 앞뒤에 필터가 들어간다. | |

- 셀 37은 "노트북 탭을 닫고 실습 지침으로 돌아가 태스크 3을 계속하라"고 안내한다.
- 태스크 3이 같은 `AmazonKnowledgeBasesRetriever`와 `ChatBedrock`을 사용하므로,
  파트 2의 구성이 다음 태스크의 출발점이 된다.
