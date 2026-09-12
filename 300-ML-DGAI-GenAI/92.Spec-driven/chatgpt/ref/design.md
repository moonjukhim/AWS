# 설계 명세서 (Design)

## 1. 개요

`requirements.md`와 `retrieveAPI.png`(사용자 지정 RAG 워크플로)를 기준으로 설계한다.
Amazon Bedrock Knowledge Base의 **Retrieve API**를 사용해 관련 문서를 검색하고,
검색된 컨텍스트로 프롬프트를 증강한 뒤 LLM(amazon.nova-lite-v1:0)이 답변을 생성하는
**Custom RAG Workflow**를 구현한다. 동일 기능을 **boto3 방식**과 **LangChain LCEL 방식** 두 가지로 제공한다.

---

## 2. 아키텍처 (retrieveAPI.png 매핑)

`retrieveAPI.png`의 "사용자 지정 RAG 워크플로" 구조를 그대로 반영한다.

```
                              ┌────────────────────────────────────────────┐
                              │           프롬프트 증강                      │
             사용자 입력      │  (context + question 을 프롬프트에 결합)     │
  ┌────────┐ ───────────────────────────────▲──────────────┐               │
  │ 사용자 │                                 │ context      │               │
  └───┬────┘                                 │              │               │
      │ 사용자 입력(query)                    │              ▼               │
      ▼                                       │        ┌───────────┐         │
  ┌─────────────┐   사용자 쿼리         ┌──────┴─────┐ │ 대규모      │  ┌──────┐
  │ Retrieve API│ ───────────────────► │  컨텍스트   │►│ 언어 모델   │─►│ 답변 │
  └──────┬──────┘   검색된 문서         └────────────┘ │ (LLM)      │  └──────┘
         │  ▲                                          └───────────┘
         ▼  │ 검색된 문서
  ┌─────────────────────────────────────────────┐
  │ Knowledge Base (지식 기반)                    │
  │  1) 쿼리 임베딩 생성 (Query Embedding)         │
  │  2) 유사 문서 검색 (Similarity Search)         │
  └───────────────────────────────────────────────┘
```

| 다이어그램 요소 | 구현 매핑 |
|-----------------|-----------|
| 사용자 (User) | 검증 질문을 입력하는 실행 진입점 |
| 사용자 입력 (query) | question 문자열 |
| Retrieve API | `bedrock-agent-runtime.retrieve()` / `AmazonKnowledgeBasesRetriever` |
| 쿼리 임베딩 생성 + 유사 문서 검색 | Knowledge Base 내부 처리(임베딩·벡터 검색) |
| 검색된 문서 | Retrieve 응답의 `retrievalResults[]` |
| 컨텍스트 (context) | 각 결과의 `content.text`를 결합한 문자열 |
| 프롬프트 증강 | context + question 을 프롬프트 템플릿에 삽입 |
| LLM | amazon.nova-lite-v1:0 (boto3 InvokeModel / ChatBedrock) |
| 답변 | 모델이 생성한 최종 응답 텍스트 |

---

## 3. 처리 흐름 (End-to-End)

1. **KB ID 조회**: boto3 `bedrock-agent` 클라이언트의 `list_knowledge_bases()`로 기존 Knowledge Base ID 확보.
2. **Retrieve (검색)**: 사용자 쿼리를 Retrieve API에 전달 → KB가 임베딩 생성 및 유사 문서 검색 → 검색된 문서 반환.
3. **Context 추출**: 검색 결과에서 `content.text`를 추출하여 하나의 context 문자열로 결합.
4. **프롬프트 증강**: context + question 을 프롬프트에 삽입, "context에 없는 내용은 추측하지 않는다" 지침 포함.
5. **답변 생성**: 증강된 프롬프트를 LLM에 전달하여 답변 생성.

---

## 4. 모듈 구성

멱등성(요구사항 8)과 불필요한 산출물 금지(요구사항 9)를 위해 단일 스크립트로 구성하고,
공통 로직은 함수로 재사용한다.

| 모듈/함수 | 책임 | 요구사항 |
|-----------|------|----------|
| `get_knowledge_base_id()` | 기존 KB ID 조회 (없으면 명확한 오류) | 1 |
| `retrieve_boto3(kb_id, query)` | Retrieve API 호출 (HYBRID, 5개) | 2 |
| `build_context(results)` | `content.text` 추출·결합 | 3 |
| `build_prompt(context, question)` | 프롬프트 증강 (환각 방지 지침 포함) | 4 |
| `generate_answer_boto3(prompt)` | nova-lite-v1:0 InvokeModel 호출 | 5 |
| `build_langchain_chain(kb_id)` | LCEL 체인 구성 (SEMANTIC, 4개) | 6 |
| `main()` | 두 방식 실행 및 결과 출력 | 검증 |

---

## 5. boto3 방식 설계

### 5.1 클라이언트
- `bedrock-agent`: KB 목록 조회 (`list_knowledge_bases`)
- `bedrock-agent-runtime`: 문서 검색 (`retrieve`)
- `bedrock-runtime`: 답변 생성 (`invoke_model`)

### 5.2 Retrieve 요청 파라미터
```python
retrievalConfiguration = {
    "vectorSearchConfiguration": {
        "numberOfResults": 5,
        "overrideSearchType": "HYBRID"
    }
}
```

### 5.3 Context 추출
```python
context = "\n\n".join(
    r["content"]["text"] for r in response["retrievalResults"]
)
```

### 5.4 프롬프트 (환각 방지)
```
당신은 제공된 컨텍스트만을 근거로 답변하는 어시스턴트입니다.
컨텍스트에 없는 내용은 추측하지 말고 "정보를 찾을 수 없습니다"라고 답하세요.

<context>
{context}
</context>

질문: {question}
```

### 5.5 답변 생성
- 모델 ID: `amazon.nova-lite-v1:0`
- Nova 메시지 스키마(`messages`, `content[].text`)로 요청, 응답의 `output.message.content[0].text` 추출.

---

## 6. LangChain LCEL 방식 설계

### 6.1 Retriever
```python
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id=kb_id,
    retrieval_config={
        "vectorSearchConfiguration": {
            "numberOfResults": 4,
            "overrideSearchType": "SEMANTIC"
        }
    },
)
```

### 6.2 LCEL 체인
```
{ "context": retriever | format_docs, "question": RunnablePassthrough() }
    | PromptTemplate
    | ChatBedrock(model_id="amazon.nova-lite-v1:0")
    | StrOutputParser()
```

- `PromptTemplate`: 5.4와 동일한 환각 방지 프롬프트를 재사용.
- `format_docs`: 검색 문서의 `page_content`를 결합.
- `StrOutputParser`: 최종 문자열 출력.

---

## 7. 두 방식 파라미터 비교

| 항목 | boto3 방식 | LangChain 방식 |
|------|-----------|----------------|
| 검색 API | `bedrock-agent-runtime.retrieve` | `AmazonKnowledgeBasesRetriever` |
| 검색 방식 | HYBRID | SEMANTIC |
| 검색 결과 개수 | 5 | 4 |
| 프롬프트 증강 | 문자열 포맷 | PromptTemplate |
| LLM 호출 | `bedrock-runtime.invoke_model` | ChatBedrock |
| 출력 처리 | JSON 파싱 | StrOutputParser |
| 생성 모델 | amazon.nova-lite-v1:0 | amazon.nova-lite-v1:0 |

---

## 8. 멱등성 및 산출물 관리 (요구사항 7·8·9)

- **KB 생성 없음**: 기존 KB를 조회만 하며 새로 만들지 않는다.
- **파일 중복 방지**: 구현 파일이 이미 존재하고 요구사항을 만족하면 재생성/덮어쓰기 하지 않는다.
- **설정 중복 방지**: 반복 실행 시 리소스나 설정을 추가 생성하지 않는다(조회·검색·생성만 수행).
- **최소 산출물**: 구현 파일과 (필요 시) 의존성 목록만 생성한다.

---

## 9. 설정 항목

| 항목 | 값 | 비고 |
|------|-----|------|
| AWS Region | 환경변수/기본 프로파일 | Bedrock 지원 리전 |
| Model ID | `amazon.nova-lite-v1:0` | 공통 |
| boto3 numberOfResults | 5 | HYBRID |
| LangChain numberOfResults | 4 | SEMANTIC |

---

## 10. 오류 처리

- KB가 하나도 없으면 명확한 메시지와 함께 종료(추측/자동 생성 금지).
- Retrieve 결과가 비면 context 없이 진행하되, 프롬프트 지침에 따라 LLM이 "정보를 찾을 수 없습니다"로 응답하도록 유도.
- AWS 자격 증명/권한 오류는 원인이 드러나도록 예외를 그대로 표면화.

---

## 11. 검증 (Verification)

- 검증 질문:
  `What was the total operating lease liabilities and total sublease income of the AnyCompany as of December 31, 2022?`
- 완료 조건:
  - boto3 Retrieve API 방식이 정상 응답한다.
  - LangChain LCEL 방식이 정상 응답한다.
  - 불필요한 파일/코드가 생성되지 않는다.
