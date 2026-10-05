# 요구 사항 명세 — Task-2: Retrieve API 기반 Q&A 애플리케이션

- **문서 버전**: 1.0
- **작성일**: 2026-09-02
- **표기법**: EARS (`[조건]이 발생하면 시스템은 [동작]을 수행해야 합니다`)

> 이 문서의 모든 요구 사항은 노트북에 실제로 존재하는 동작에서 도출했다.
> REQ ID는 재사용하지 않는다. 요구 사항이 사라지면 ID를 지우지 말고 폐기(deprecated)로 표시한다.

---

## 1. 개요

Amazon Bedrock Knowledge Base의 **Retrieve API**로 관련 문서 청크를 검색하고,
그 청크를 컨텍스트로 프롬프트를 증강한 뒤 파운데이션 모델을 호출해 답변을 생성하는
**Q&A 애플리케이션**을 구축한다.

대상 데이터는 AnyCompany의 financial 10-K 문서(합성 데이터셋)이며, Knowledge Base는 실습 환경에
사전 프로비저닝되어 있다.

### 1.1 두 개의 파트

노트북은 **같은 워크플로를 두 번** 구현한다. 두 파트 모두 필수다.

| 파트 | 섹션 | 방식 | 학습 목적 |
|---|---|---|---|
| 파트 1 | 태스크 2.1 ~ 2.2 | boto3로 Retrieve API와 모델을 직접 호출 | RAG의 각 단계가 어떤 API를 부르는지 본다 |
| 파트 2 | 태스크 2.3 | LangChain 리트리버 + LCEL 체인 | 프레임워크가 그 단계들을 어떻게 묶는지 본다 |

### 1.2 다이어그램 ↔ 요구 사항 매핑

노트북 셀 7의 `images/retrieveAPI.png`가 보여주는 RAG 워크플로.

| # | 다이어그램 요소 | 담당 | 요구 사항 |
|---|---|---|---|
| 1 | 사용자 쿼리 | 질문 문자열 | REQ-08 |
| 2 | Retrieve API 호출 | `retrieve()` 함수 | REQ-05, REQ-06 |
| 3 | 쿼리 임베딩 생성 / 유사 문서 검색 | Knowledge Base 내부(관리형) | REQ-01 |
| 4 | 검색된 텍스트 청크 | `retrievalResults` | REQ-07 |
| 5 | 컨텍스트 | `get_contexts()` | REQ-09 |
| 6 | 프롬프트 증강 | 프롬프트 조립 | REQ-11, REQ-12 |
| 7 | 대규모 언어 모델 | `invoke_model` | REQ-13 ~ REQ-15 |
| 8 | 답변 | 응답 파싱 및 출력 | REQ-16 |

### 1.3 범위

**포함**
- Knowledge Base ID 조회
- Retrieve API 호출 및 검색 파라미터 지정(`numberOfResults`, `overrideSearchType`)
- 검색 결과 → 컨텍스트 → 증강 프롬프트 → 모델 → 답변의 단일 턴 파이프라인
- 동일 워크플로의 LangChain 구현(`AmazonKnowledgeBasesRetriever` + LCEL)

**제외**
- Knowledge Base 생성 및 데이터 소스 동기화 (실습 환경에 사전 제공)
- 멀티턴 대화 이력 관리
- 가드레일 적용 (태스크 4에서 다룸)
- RAG 품질 평가 (태스크 3에서 다룸)

---

## 2. 전제 조건

| ID | 전제 조건 | 근거 |
|---|---|---|
| PRE-01 | 실습 계정에 Amazon Bedrock Knowledge Base가 1개 이상 사전 생성되어 있고, AnyCompany 10-K 데이터가 동기화되어 있다. | 셀 0 |
| PRE-02 | 실행 역할에 `bedrock:ListKnowledgeBases`, `bedrock:Retrieve`, `bedrock:InvokeModel` 권한이 있다. | 셀 3, 9, 23 |
| PRE-03 | 현재 리전에서 `amazon.nova-lite-v1:0` 모델 액세스가 승인되어 있다. | 셀 6, 23 |
| PRE-04 | `boto3`, `botocore`, `langchain`, `langchain_aws`, `langchain_core`가 설치되어 있다. | 셀 3, 5, 27, 33, 36 |
| PRE-05 | 노트북과 같은 위치에 `images/retrieveAPI.png`가 존재한다. | 셀 7 |

---

## 3. 기능 요구 사항

### 3.1 환경 설정 (태스크 2.1)

**REQ-01** 시스템이 시작되면 `bedrock-agent` 클라이언트의 `list_knowledge_bases(maxResults=1)`를 호출해
첫 번째 Knowledge Base의 ID를 `kb_id` 변수에 할당해야 합니다.
- Given 계정에 KB가 1개 이상 존재할 때 / When 조회를 실행하면 / Then `kb_id`가 비어 있지 않은 문자열로 설정되고 화면에 출력된다.
> 근거: 셀 3. KB ID를 하드코딩하지 않는 것이 이 요구 사항의 목적이다.

**REQ-02** 조회 결과에 Knowledge Base가 하나도 없으면 시스템은 그 사실을 알리는 메시지를 출력해야 합니다.
- Given KB가 없는 계정일 때 / When 조회를 실행하면 / Then `No Knowledge Base summaries found.` 취지의 메시지가 출력된다.
> 근거: 셀 3의 `else` 분기.

**REQ-03** Knowledge Base 조회 중 `botocore.exceptions.ClientError`가 발생하면 시스템은 예외를 포착해
오류 내용을 출력해야 합니다.
- Given 권한이 없는 역할로 실행할 때 / When 조회를 시도하면 / Then 예외 메시지가 `Error: ...` 형태로 출력된다.
> 근거: 셀 3의 `except botocore.exceptions.ClientError`.

**REQ-04** 시스템이 Bedrock 클라이언트를 생성할 때 다음을 만족해야 합니다.
1. 리전은 `boto3.session.Session().region_name`에서 얻는다 (하드코딩 금지)
2. 검색 클라이언트(`bedrock-agent-runtime`)에 `connect_timeout=120`, `read_timeout=120`, `retries={'max_attempts': 0}`을 적용한다
3. 생성 클라이언트(`bedrock-runtime`)를 별도로 만든다
- Given 어떤 리전에서 실행하든 / When 클라이언트를 생성하면 / Then 현재 세션의 리전이 사용된다.
> 근거: 셀 5. 타임아웃 120초는 검색과 임베딩 왕복 시간을 감안한 값이다. `max_attempts: 0`은 실습에서 오류가 즉시 드러나게 하려는 의도적 설정이다.

### 3.2 검색 — Retrieve API (태스크 2.2)

**REQ-05** 시스템은 `retrievalQuery`, `knowledgeBaseId`, `retrievalConfiguration`을 파라미터로
`bedrock-agent-runtime`의 `retrieve`를 호출하는 검색 함수를 제공해야 합니다.
- 시그니처: `retrieve(query, kbId, numberOfResults=5)`
- Given 유효한 질문과 KB ID가 주어졌을 때 / When 함수를 호출하면 / Then 응답에 `retrievalResults` 키가 존재한다.
> 근거: 셀 9.

**REQ-06** 검색 함수가 호출되면 시스템은 `vectorSearchConfiguration`에
`numberOfResults`(기본값 5)와 `overrideSearchType`(`HYBRID`)을 지정해야 합니다.
- Given `overrideSearchType="HYBRID"`일 때 / When 검색하면 / Then 키워드 매칭과 의미 유사도를 함께 사용한 결과가 반환된다.
> 근거: 셀 9, 셀 7. `overrideSearchType`은 선택 파라미터이며, 지정하지 않으면 Bedrock이 전략을 자동 선택한다. `HYBRID` 또는 `SEMANTIC`을 지정할 수 있다.

**REQ-07** Retrieve API가 결과를 반환하면 시스템은 검색 결과 전체를 `pp.pprint`로 출력해
텍스트 청크·소스 위치·관련성 점수를 확인할 수 있게 해야 합니다.
- Given 검색이 성공했을 때 / When 결과를 출력하면 / Then 각 결과의 `content`, `location`, `score`가 화면에 보인다.
> 근거: 셀 13, 셀 11. 노트북은 "반환된 각 텍스트 청크에 대한 점수를 볼 수 있으며, 이 점수는 결과가 얼마나 밀접하게 일치하는지에 대한 상관관계를 보여준다"고 설명한다.

**REQ-08** 시스템은 검색 질의와 최종 프롬프트의 질문에 동일한 문자열을 사용해야 합니다.
- 기준 질문: `What was the total operating lease liabilities and total sublease income of the AnyCompany as of December 31, 2022?`
- Given 질문 문자열이 주어졌을 때 / When 파이프라인을 실행하면 / Then 검색에 쓰인 질의와 프롬프트의 `<question>` 값이 같다.
> 근거: 셀 13, 19. **주의**: 노트북은 셀 13과 셀 30에서 같은 문자열을 각각 할당한다. 질문을 바꾸려면 두 곳을 모두 고쳐야 한다.

### 3.3 컨텍스트 조립 및 프롬프트 증강

**REQ-09** 시스템은 `retrievalResults`에서 각 결과의 `content.text`만 추출해
문자열 리스트로 반환하는 컨텍스트 추출 함수를 제공해야 합니다.
- 시그니처: `get_contexts(retrievalResults)`
- Given 5건의 검색 결과일 때 / When 함수를 호출하면 / Then 길이 5의 문자열 리스트가 반환된다.
> 근거: 셀 15.

**REQ-10** 컨텍스트를 추출하면 시스템은 그 내용을 `pp.pprint`로 출력해 확인할 수 있게 해야 합니다.
- Given 컨텍스트 추출이 끝났을 때 / When 출력하면 / Then 각 청크의 본문이 화면에 보인다.
> 근거: 셀 16.

**REQ-11** 시스템이 프롬프트를 구성할 때 검색된 컨텍스트를 `<context>` 태그로,
사용자 질문을 `<question>` 태그로 감싸 구분해야 합니다.
- 프롬프트는 `Human:` 으로 시작하고 `Assistant:` 로 끝나야 한다.
- Given 컨텍스트와 질문이 주어졌을 때 / When 프롬프트를 생성하면 / Then 두 구획이 서로 다른 태그로 분리되어 있다.
> 근거: 셀 19, 33.

**REQ-12** 프롬프트는 다음 네 지시를 모두 포함해야 합니다.
1. 역할 정의 — 재무 자문 AI 시스템이며 가능한 한 사실과 통계에 기반해 답한다
2. 근거 한정 — 주어진 정보를 사용해 `<question>`에 간결히 답한다
3. 환각 금지 — 답을 모르면 모른다고 말하고 지어내지 않는다
4. 구체성 — 가능한 경우 통계나 수치를 사용해 구체적으로 답한다
- Given 컨텍스트에 없는 사실을 묻는 질문일 때 / When 답변을 생성하면 / Then 수치를 지어내지 않고 모른다고 답한다.
> 근거: 셀 19, 33. 두 프롬프트는 플레이스홀더 이름(`{contexts}`/`{query}` vs `{context}`/`{question}`)만 다르고 문구가 동일하다.

### 3.4 답변 생성 — 파운데이션 모델 (태스크 2.2.4)

**REQ-13** 시스템이 모델을 호출할 때 다음 구조의 페이로드를 사용해야 합니다.
```python
{"schemaVersion": "messages-v1",
 "messages": [{"role": "user", "content": [{"text": prompt}]}],
 "inferenceConfig": {"maxTokens": 512, "temperature": 0.5, "topP": 0.9, "topK": 20}}
```
- Given 프롬프트가 준비되었을 때 / When 페이로드를 구성하면 / Then 네 개의 추론 파라미터가 모두 명시되어 있다.
> 근거: 셀 22. `schemaVersion: "messages-v1"`은 Amazon Nova 계열 전용 스키마다.

**REQ-14** 시스템은 `amazon.nova-lite-v1:0` 모델을 `bedrock-runtime`의 `invoke_model`로 호출해야 하며,
`body`는 JSON 문자열로, `accept`와 `contentType`은 `application/json`으로 지정해야 합니다.
- Given 페이로드가 준비되었을 때 / When 모델을 호출하면 / Then 응답 객체가 반환된다.
> 근거: 셀 23, 셀 6.

**REQ-15** 모델 응답을 파싱할 때 시스템은 키 존재를 확인한 뒤 단계적으로 접근해
`output.message.content[0].text`를 추출해야 합니다.
- Given 정상 응답일 때 / When 파싱하면 / Then 답변 텍스트가 추출된다.
- Given 예상과 다른 구조의 응답일 때 / When 파싱하면 / Then `KeyError` 없이 빈 문자열이 된다.
> 근거: 셀 23. 응답 본문은 스트림이므로 `response.get('body').read()` 후 `json.loads`로 파싱한다.

**REQ-16** 시스템은 추출한 답변 텍스트를 화면에 출력해야 합니다.
- Given 답변이 추출되었을 때 / When 출력하면 / Then 답변 본문이 화면에 보인다.
> 근거: 셀 23.

### 3.5 LangChain 구현 (태스크 2.3)

**REQ-17** 시스템은 `langchain_aws.ChatBedrock`으로 LLM을 구성해야 하며,
파트 1과 동일한 `modelId` 변수와 동일한 `bedrock_client`를 사용해야 합니다.
- Given 파트 1이 실행된 뒤일 때 / When LLM을 생성하면 / Then 두 파트가 같은 모델을 사용한다.
> 근거: 셀 27. **주의**: `modelId`는 셀 23에서 정의되므로 파트 1을 건너뛰면 파트 2가 실패한다.

**REQ-18** 시스템은 `AmazonKnowledgeBasesRetriever`를 다음 설정으로 생성해야 합니다.
- `knowledge_base_id`: 파트 1과 동일한 `kb_id`
- `retrieval_config.vectorSearchConfiguration.numberOfResults`: 4
- `retrieval_config.vectorSearchConfiguration.overrideSearchType`: `SEMANTIC`
- Given 리트리버가 생성되었을 때 / When `invoke(input=query)`를 호출하면 / Then 문서 객체 리스트가 반환된다.
> 근거: 셀 30. **파트 1(5건/HYBRID)과 의도적으로 다른 설정**이다. 두 검색 전략을 모두 보여주기 위한 구성이므로 통일하지 않는다.

**REQ-19** 리트리버가 문서를 반환하면 시스템은 각 문서의 `page_content`를
구분선(`------`)과 함께 출력해야 합니다.
- Given 4건의 문서가 검색되었을 때 / When 출력하면 / Then 4개의 본문이 구분선으로 나뉘어 보인다.
> 근거: 셀 30.

**REQ-20** 시스템은 `PromptTemplate`으로 프롬프트를 구성해야 하며,
`input_variables`는 `["context", "question"]`이어야 합니다.
- Given 템플릿이 생성되었을 때 / When 체인에서 사용하면 / Then 두 변수가 채워진다.
> 근거: 셀 33.

**REQ-21** 시스템은 리트리버가 반환한 문서들의 `page_content`를
빈 줄 2개(`"\n\n"`)로 이어 붙이는 문서 병합 함수를 제공해야 합니다.
- 시그니처: `format_docs(docs)`
- Given 4건의 문서일 때 / When 병합하면 / Then 하나의 문자열이 반환된다.
> 근거: 셀 36.

**REQ-22** 시스템은 LCEL로 `리트리버 → 프롬프트 → LLM → 출력 파서`를 연결한 체인을 구성해야 합니다.
```python
chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()}
         | nova_prompt | llm | StrOutputParser())
```
- Given 체인이 구성되었을 때 / When `chain.invoke(query)`를 호출하면 / Then 답변 문자열이 반환되고 출력된다.
> 근거: 셀 36. `RunnablePassthrough`가 입력 질문을 그대로 `question`에 전달한다.

---

## 4. 비기능 요구 사항

| ID | 요구 사항 | 근거 |
|---|---|---|
| NFR-01 | 검색 1회의 응답 시간은 120초 타임아웃 이내여야 한다. | 셀 5 |
| NFR-02 | 자격 증명을 코드에 포함하지 않고 실행 환경의 IAM 역할에서 얻어야 한다. | 셀 3, 5 (명시적 자격 증명 전달 없음) |
| NFR-03 | 각 단계(검색 결과, 컨텍스트, 답변)를 개별적으로 출력해 확인할 수 있어야 한다. | 셀 13, 16, 23, 30, 36 |
| NFR-04 | 노트북의 모든 코드 셀은 앞에 설명 마크다운 셀을 가져야 한다. | 전체 구조 |
| NFR-05 | 셀을 위에서 아래로 **하나씩** 실행했을 때 오류 없이 완료되어야 한다. | 셀 0 경고 |

---

## 5. 제약 사항 및 주의 지점

노트북 자체의 성질에서 오는 제약. 요구 사항이라기보다 **알고 지켜야 할 사실**이다.

| ID | 제약 | 영향 | 근거 |
|---|---|---|---|
| CON-01 | `Run All Cells`를 사용하면 커널 충돌 또는 리소스 제한 오류가 발생할 수 있다. | 반드시 한 셀씩 실행 | 셀 0 |
| CON-02 | `bedrock_client`가 셀 3(`bedrock-agent`)과 셀 5(`bedrock-runtime`)에서 서로 다른 서비스로 재바인딩된다. | 셀 3을 재실행하면 셀 5도 재실행해야 셀 23이 동작한다 | 셀 3, 5 |
| CON-03 | `bedrock_agent_client`라는 이름이 실제로는 `bedrock-agent-runtime` 클라이언트다. | 코드를 읽을 때 서비스 이름을 확인해야 한다 | 셀 5 |
| CON-04 | `modelId`가 셀 23에서 처음 정의되고 셀 27이 이를 사용한다. | 파트 1을 건너뛰고 파트 2만 실행할 수 없다 | 셀 23, 27 |
| CON-05 | `query`가 셀 13과 셀 30에서 각각 할당된다. | 질문을 바꾸려면 두 곳을 모두 고쳐야 한다 | 셀 13, 30 |
| CON-06 | `retries={'max_attempts': 0}`으로 재시도가 꺼져 있다. | 스로틀링 발생 시 즉시 실패한다 (오류를 감추지 않으려는 의도) | 셀 5 |
| CON-07 | `schemaVersion: "messages-v1"` 페이로드는 Amazon Nova 계열 전용이다. | 다른 모델로 바꾸면 셀 22와 셀 23을 함께 고쳐야 한다 | 셀 22 |
| CON-08 | 셀 7이 참조하는 `images/retrieveAPI.png`가 현재 폴더에 없다. | 노트북 배포 시 이미지를 함께 제공해야 한다 | 셀 7 |

---

## 6. 완료 기준

- [ ] `kb_id`가 코드로 조회되어 출력된다 (REQ-01)
- [ ] 클라이언트 생성 시 리전이 하드코딩되지 않고 타임아웃 120초가 적용된다 (REQ-04)
- [ ] `retrieve()` 함수가 `numberOfResults=5`, `overrideSearchType="HYBRID"`로 검색한다 (REQ-05, REQ-06)
- [ ] 검색 결과의 텍스트·위치·점수가 출력으로 확인된다 (REQ-07)
- [ ] `get_contexts()`가 텍스트 청크 리스트를 반환하고 출력된다 (REQ-09, REQ-10)
- [ ] 프롬프트에 `<context>`, `<question>` 태그와 네 지시가 모두 들어 있다 (REQ-11, REQ-12)
- [ ] `amazon.nova-lite-v1:0`을 `invoke_model`로 호출해 답변을 얻는다 (REQ-13 ~ REQ-16)
- [ ] `AmazonKnowledgeBasesRetriever`가 `numberOfResults=4`, `SEMANTIC`으로 문서를 반환한다 (REQ-18, REQ-19)
- [ ] LCEL 체인이 답변을 생성하고 출력한다 (REQ-20 ~ REQ-22)
- [ ] 두 파트가 같은 질문에 대해 근거 있는 답변을 낸다
- [ ] 새 커널에서 셀을 하나씩 순차 실행해 오류가 없다 (NFR-05)
