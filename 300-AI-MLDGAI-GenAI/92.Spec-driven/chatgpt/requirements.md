# 요구사항 명세서 (Requirements)

## 프로젝트 개요

Amazon Bedrock Knowledge Base를 이용한 RAG(Retrieval-Augmented Generation) 기반 Q&A 예제를 구현한다.
사용자의 질문에 대해 Knowledge Base에서 관련 문서를 검색하고, 검색된 컨텍스트를 기반으로
LLM이 답변을 생성한다. 동일한 기능을 **boto3 직접 호출 방식**과 **LangChain LCEL 방식** 두 가지로 구현한다.

---

## 기능 요구사항

### 1. Knowledge Base ID 조회
- **boto3**를 사용하여 기존 Knowledge Base ID를 조회한다.
- 존재하는 Knowledge Base를 리스트에서 찾아 ID를 확보한다.

### 2. boto3 Retrieve 방식 검색
- `bedrock-agent-runtime` 클라이언트의 **Retrieve API**로 Knowledge Base를 검색한다.
- 검색 방식(search type): **HYBRID**
- 기본 검색 결과 개수: **5개**

### 3. Context 추출
- 검색 결과에서 각 항목의 `content.text`를 추출한다.
- 추출한 텍스트들을 하나의 `context` 문자열로 결합한다.

### 4. 프롬프트 구성
- `context`와 사용자 질문(question)을 프롬프트에 포함한다.
- **context에 없는 내용은 추측하지 않는다** (환각 방지 지침을 프롬프트에 명시).

### 5. 답변 생성 (boto3)
- **amazon.nova-lite-v1:0** 모델을 호출하여 답변을 생성한다.
- `bedrock-runtime` 클라이언트를 사용한다.

### 6. LangChain 방식 구현
- **AmazonKnowledgeBasesRetriever**를 사용하여 검색한다.
- 검색 방식(search type): **SEMANTIC**
- 검색 결과 개수: **4개**
- 체인 구성: **PromptTemplate + LCEL + ChatBedrock + StrOutputParser**
- LCEL 파이프라인으로 retriever → prompt → LLM → output parser를 연결한다.

---

## 비기능 요구사항

### 7. 기존 구현 보존
- 기존 구현이 이미 요구사항을 만족하면 **변경하지 않는다**.

### 8. 멱등성 (Idempotency)
- 동일 작업을 반복 실행해도 코드나 설정이 **중복 생성되지 않도록** 보장한다.
- 파일/설정 생성 시 이미 존재하고 요구사항을 만족하면 재생성하지 않는다.

### 9. 불필요한 산출물 금지
- 요구사항에 필요하지 않은 파일이나 코드는 생성하지 않는다.

---

## 기술 스택

| 구분 | 내용 |
|------|------|
| 언어 | Python |
| AWS SDK | boto3 |
| AWS 서비스 | Amazon Bedrock, Bedrock Knowledge Base |
| 검색 API | bedrock-agent-runtime `Retrieve` |
| 생성 모델 | amazon.nova-lite-v1:0 |
| LangChain | AmazonKnowledgeBasesRetriever, PromptTemplate, LCEL, ChatBedrock, StrOutputParser |

---

## 검증 (Verification)

### 검증 질문
```
What was the total operating lease liabilities and total sublease income of the AnyCompany as of December 31, 2022?
```

### 완료 조건
- [ ] boto3 Retrieve API 방식이 정상 응답한다.
- [ ] LangChain LCEL 방식이 정상 응답한다.
- [ ] 불필요한 파일이나 코드는 생성하지 않는다.

---

## 파라미터 요약

| 항목 | boto3 방식 | LangChain 방식 |
|------|-----------|----------------|
| 검색 방식 | HYBRID | SEMANTIC |
| 검색 결과 개수 | 5 | 4 |
| 생성 모델 | amazon.nova-lite-v1:0 | amazon.nova-lite-v1:0 (ChatBedrock) |
| context 소스 | Retrieve 결과의 `content.text` | Retriever 결과 문서 |
