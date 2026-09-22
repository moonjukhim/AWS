# 구현 작업 목록 — Task-2: Retrieve API 기반 Q&A 애플리케이션

- **문서 버전**: 1.0
- **작성일**: 2026-09-02
- **대상 산출물**: `project/Task-2.ipynb`
- **근거 문서**: `requirements.md`(REQ/CON) · `design.md`(§·O) · `proj-steering.md`(규칙)

> 각 작업은 **REQ ID와 셀 번호**를 함께 인용한다. 근거 없는 작업은 넣지 않았다.

**진행 규칙**
1. 위에서 아래로 순서대로 진행한다. 각 작업은 앞 작업의 산출물에 의존한다.
2. 코드 셀을 만들 때는 **반드시 앞에 설명 마크다운 셀을 함께 만든다**(NFR-04).
3. 셀을 추가하면 실행 지시 번호(`1.` ~ `11.`)를 다시 매긴다.
4. 각 작업의 "완료 확인"을 실제로 실행해 보고 체크한다. 실행하지 않고 체크하지 않는다.
5. **셀은 한 번에 하나씩 실행한다.** `Run All Cells`를 쓰지 않는다(CON-01).
6. 구현이 `requirements.md`와 어긋나면 요구 사항 문서를 먼저 고친다(`proj-steering.md` §9).

---

## 단계 0. 준비

- [ ] **0.1 전제 조건 확인**
  - 실습 계정에 Knowledge Base가 1개 이상 존재하고 AnyCompany 10-K 데이터가 동기화되었는지 확인
  - 실행 역할에 `bedrock:ListKnowledgeBases`, `bedrock:Retrieve`, `bedrock:InvokeModel` 권한 확인
  - 현재 리전에서 `amazon.nova-lite-v1:0` 모델 액세스가 승인되었는지 Bedrock 콘솔에서 확인
  - _근거: PRE-01 ~ PRE-03_
  - _완료 확인: 세 항목 모두 확인됨_

- [ ] **0.2 패키지 확인**
  - `boto3`, `botocore`, `langchain`, `langchain_aws`, `langchain_core` 설치 확인
  - _근거: PRE-04_
  - _완료 확인: `from langchain_aws import ChatBedrock, AmazonKnowledgeBasesRetriever`가 오류 없이 실행됨_

- [ ] **0.3 이미지 자산 확인**
  - 노트북과 같은 위치에 `images/retrieveAPI.png`가 있는지 확인. **현재 이 폴더에는 없다**
  - 없으면 실습 배포 패키지에서 가져오거나, 셀 7의 이미지 참조를 조정한다
  - _근거: PRE-05, CON-08_
  - _완료 확인: 셀 7의 다이어그램이 렌더링된다_

---

## 단계 1. 노트북 뼈대 (셀 0)

- [ ] **1.1 제목 및 개요 마크다운 셀 작성**
  - 태스크 제목: `태스크 2: Retrieve API와 함께 Amazon Bedrock Knowledge Base를 사용하여 Q&A 애플리케이션 구축`
  - 시나리오 설명: AnyCompany financial 10-K 합성 데이터셋, 사전 프로비저닝된 KB
  - 이 노트북에서 수행할 세 가지 항목을 목록으로 제시
  - `<i class="fas fa-info-circle" style="color:#007FAA"></i>` 아이콘으로 Knowledge Base 문서 링크 안내
  - **`<i class="fas fa-exclamation-circle" style="color:#7C5AED"></i>` 아이콘으로 `Run All Cells` 경고를 반드시 포함**
  - _근거: 셀 0, CON-01, `proj-steering.md` §2-1·§10_
  - _완료 확인: 한 셀씩 실행하라는 경고가 문서 최상단에 보인다_

---

## 단계 2. 환경 설정 (태스크 2.1 / 셀 1~5)

- [ ] **2.1 태스크 2.1 안내 마크다운 셀 작성**
  - `### 태스크 2.1: 환경 설정` — 지식 기반 ID 확인, 라이브러리 임포트, 클라이언트 생성을 예고
  - _근거: 셀 1_

- [ ] **2.2 KB ID 조회 셀 작성** (지시 `1.`)
  - 앞에 `#### 태스크 2.1.1: 지식 기반 ID 확인` 마크다운 셀
  - `boto3`, `botocore` 임포트, `session.client('bedrock-agent')` 생성
  - `list_knowledge_bases(maxResults=1)` 호출 후 `knowledgeBaseSummaries[0]['knowledgeBaseId']`를 `kb_id`에 할당하고 출력
  - KB가 없으면 `No Knowledge Base summaries found.` 출력
  - `try/except botocore.exceptions.ClientError`로 감싸 `Error: {e}` 출력
  - **KB ID를 하드코딩하지 않는다**
  - _근거: REQ-01, REQ-02, REQ-03, 셀 3, `proj-steering.md` §2-3_
  - _완료 확인: `Knowledge Base ID: ...`가 출력된다_

- [ ] **2.3 클라이언트 생성 셀 작성** (지시 `2.`)
  - 앞에 `#### 태스크 2.1.2: Amazon Bedrock 클라이언트 생성` 마크다운 셀
  - `boto3`, `Config`, `pprint`, `json` 임포트, `pp = pprint.PrettyPrinter(indent=2)`
  - `region = boto3.session.Session().region_name` — **리전 하드코딩 금지**
  - `bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})`
  - `bedrock_client = boto3.client('bedrock-runtime', region_name=region)`
  - `bedrock_agent_client = boto3.client("bedrock-agent-runtime", config=bedrock_config, region_name=region)`
  - _근거: REQ-04, 셀 5, `proj-steering.md` §2-4·§3_
  - _완료 확인: 오류 없이 실행되고, 이후 셀에서 세 객체를 사용할 수 있다_

- [ ] **2.4 실행 순서 의존성 문서화**
  - `bedrock_client`가 셀 3(`bedrock-agent`)과 셀 5(`bedrock-runtime`)에서 재바인딩된다는 사실을
    마크다운 셀 또는 주석으로 남긴다
  - 셀 3을 재실행하면 셀 5도 재실행해야 한다는 점을 명시한다
  - `bedrock_agent_client`가 실제로는 `bedrock-agent-runtime`이라는 점을 명시한다
  - _근거: CON-02, CON-03, 설계 §3.1, O-3_
  - _완료 확인: 두 주의사항이 노트북에 적혀 있다_

---

## 단계 3. Retrieve API 검색 (태스크 2.2 / 셀 6~13)

- [ ] **3.1 파트 1 도입 마크다운 셀 작성**
  - `## 파트 1: Amazon Bedrock의 파운데이션 모델과 함께 Retrieve API 사용`
  - `<i class="fas fa-sticky-note" style="color:#563377"></i>` 아이콘으로 `amazon.nova-lite-v1:0` 사용을 명시
  - _근거: 셀 6, REQ-14_

- [ ] **3.2 Retrieve API 설명 마크다운 셀 작성**
  - `### 태스크 2.2` 제목
  - Retrieve API 응답에 **검색된 텍스트 청크**, **소스 문서의 위치 정보와 URI**, **관련성 점수**가 포함됨을 설명
  - `retrievalConfiguration`의 `overrideSearchType` 옵션(`HYBRID` / `SEMANTIC`)과,
    지정하지 않으면 Bedrock이 자동 선택한다는 점을 설명
  - `<img src="images/retrieveAPI.png" width=50% height=20% />`로 다이어그램 삽입
  - _근거: 셀 7, REQ-06, PRE-05_

- [ ] **3.3 `retrieve()` 함수 셀 작성** (지시 `3.`)
  - 시그니처: `retrieve(query, kbId, numberOfResults=5)`
  - `retrievalQuery={'text': query}`, `knowledgeBaseId=kbId`
  - `retrievalConfiguration.vectorSearchConfiguration`에 `numberOfResults`와
    `overrideSearchType: "HYBRID"` 지정 (`# optional` 주석 포함)
  - 원시 API 응답을 그대로 반환한다 — 파싱하지 않는다
  - _근거: REQ-05, REQ-06, 셀 9, 설계 §3.2_
  - _완료 확인: 함수가 정의되고 오류 없이 실행된다_

- [ ] **3.4 검색 실행 셀 작성** (지시 `4.`)
  - 앞에 `#### 태스크 2.2.1` 마크다운 셀 2개 — 지식 기반 ID·결과 수·쿼리를 파라미터로 전달한다는 설명과,
    `<i class="fas fa-sticky-note"></i>` 아이콘으로 "각 텍스트 청크의 점수가 결과가 얼마나 밀접하게 일치하는지 보여준다"는 참고
  - `query = "What was the total operating lease liabilities and total sublease income of the AnyCompany as of December 31, 2022?"`
  - `response = retrieve(query, kb_id, 5)` / `retrievalResults = response['retrievalResults']`
  - `pp.pprint(retrievalResults)`로 결과 전체 출력
  - _근거: REQ-07, REQ-08, 셀 13_
  - _완료 확인: 검색 결과의 `content`·`location`·`score`가 화면에 보인다_

---

## 단계 4. 컨텍스트 조립과 프롬프트 (태스크 2.2.2~2.2.3 / 셀 14~19)

- [ ] **4.1 `get_contexts()` 함수 셀 작성** (지시 `5.` 전반)
  - 앞에 `#### 태스크 2.2.2: Retrieve API 응답에서 텍스트 청크 추출` 마크다운 셀
    (지시문에 "다음 코드 셀 2개를 실행"이라고 적는다)
  - `retrievalResults`를 순회하며 `retrievedResult['content']['text']`를 리스트에 담아 반환
  - `# fetch context from the response` 주석 포함
  - _근거: REQ-09, 셀 15, 설계 §3.3_
  - _완료 확인: 함수가 정의된다_

- [ ] **4.2 컨텍스트 추출·출력 셀 작성** (지시 `5.` 후반)
  - `contexts = get_contexts(retrievalResults)` / `pp.pprint(contexts)`
  - _근거: REQ-10, 셀 16_
  - _완료 확인: 검색 결과 5건에 대해 길이 5의 문자열 리스트가 출력된다_

- [ ] **4.3 프롬프트 조립 셀 작성** (지시 `6.`)
  - 앞에 `#### 태스크 2.2.3` 마크다운 셀 2개 — 재무 자문 AI 시스템 역할 설명과,
    `{contexts}`가 이전 태스크의 Retrieve API 응답으로 치환된다는 안내
  - f-string으로 `prompt` 조립. **구조를 지킨다**:
    `Human:` → 역할 → 지시 → `<context>{contexts}</context>` → `<question>{query}</question>` → 출력 지시 → `Assistant:`
  - **네 지시를 모두 포함한다**: 역할 정의 / 근거 한정 / 환각 금지 / 수치 구체성
  - _근거: REQ-11, REQ-12, 셀 19, `proj-steering.md` §6_
  - _완료 확인: `prompt` 변수에 `<context>`와 `<question>` 태그가 모두 들어 있다_

---

## 단계 5. 모델 호출 (태스크 2.2.4 / 셀 20~23)

- [ ] **5.1 페이로드 구성 셀 작성** (지시 `7.` 전반)
  - 앞에 `#### 태스크 2.2.4: Amazon Bedrock에서 파운데이션 모델 간접 호출` 마크다운 셀 2개
    (지시문에 "다음 2개의 코드 셀을 실행"이라고 적는다)
  - `messages = [{"role": "user", "content": [{"text": prompt}]}]`
  - `nova_payload`에 `schemaVersion: "messages-v1"`, `messages`,
    `inferenceConfig: {maxTokens: 512, temperature: 0.5, topP: 0.9, topK: 20}`
  - **네 개의 추론 파라미터를 모두 명시한다**
  - 이 셀은 정의만 하고 출력하지 않는다
  - _근거: REQ-13, 셀 22, 설계 §3.5_
  - _완료 확인: 페이로드 dict가 구성된다_

- [ ] **5.2 모델 호출·파싱·출력 셀 작성** (지시 `7.` 후반)
  - `modelId = 'amazon.nova-lite-v1:0'` — 주석으로 다른 버전 사용 가능함을 안내
  - `accept = 'application/json'`, `contentType = 'application/json'`
  - `bedrock_client.invoke_model(body=json.dumps(nova_payload), modelId=modelId, accept=accept, contentType=contentType)`
  - `response_body = json.loads(response.get('body').read())`
  - **단계적 파싱**: `'output' in response_body and 'message' in ...` → `content`가 리스트인지 확인 →
    `message_content[0].get('text', '')`. 한 줄로 꺼내지 않는다
  - `print(response_text)`
  - _근거: REQ-14, REQ-15, REQ-16, 셀 23, `proj-steering.md` §8.2_
  - _완료 확인: 검색된 근거를 바탕으로 수치를 포함한 답변이 출력된다_

- [ ] **5.3 파트 간 의존성 확인**
  - `modelId`가 이 셀에서 처음 정의되고 파트 2(셀 27)가 이를 사용한다는 점을 인지한다
  - **파트 1을 건너뛰고 파트 2만 실행할 수 없다**
  - _근거: CON-04, 설계 §4.3_
  - _완료 확인: 의존 관계를 이해했고, 필요하면 마크다운으로 명시했다_

---

## 단계 6. LangChain 통합 (태스크 2.3 / 셀 24~36)

- [ ] **6.1 파트 2 도입 마크다운 셀 작성**
  - `## 파트 2: LangChain 통합` + `### 태스크 2.3: LangChain 통합`
  - `AmazonKnowledgeBasesRetriever` 클래스로 Q&A 애플리케이션을 구축하고,
    검색된 청크를 LangChain 체인으로 LLM에 전달함을 설명
  - _근거: 셀 24_

- [ ] **6.2 LangChain 환경 설정 셀 작성** (지시 `8.`)
  - 앞에 `#### 태스크 2.3.1: 환경 설정` 마크다운 셀
  - `import langchain`, `from langchain_aws import ChatBedrock, AmazonKnowledgeBasesRetriever`
  - `llm = ChatBedrock(model_id=modelId, client=bedrock_client)`
  - **`modelId`와 `bedrock_client`를 새로 만들지 않고 재사용한다**
  - _근거: REQ-17, 셀 27_
  - _완료 확인: 두 파트가 같은 모델과 같은 클라이언트를 사용한다_

- [ ] **6.3 리트리버 생성·검색 셀 작성** (지시 `9.`)
  - 앞에 `#### 태스크 2.3.2` 마크다운 셀 2개 — 리트리버가 Retrieve API를 호출한다는 설명
  - `query`를 파트 1과 동일한 문자열로 다시 할당
  - `AmazonKnowledgeBasesRetriever(knowledge_base_id=kb_id, retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4, 'overrideSearchType': "SEMANTIC"}})`
  - **파트 1(5건/HYBRID)과 다른 설정을 그대로 유지한다** — 통일하지 않는다
  - 주석 처리된 선택 파라미터(`endpoint_url`, `region_name`, `credentials_profile_name`)를 남겨 둔다
  - `docs = retriever.invoke(input=query)` 후 각 `doc.page_content`를 `print`하고 사이에 `print("------")`
  - _근거: REQ-18, REQ-19, 셀 30, `proj-steering.md` §5, O-1_
  - _완료 확인: 4건의 문서 본문이 구분선으로 나뉘어 출력된다_

- [ ] **6.4 PromptTemplate 셀 작성** (지시 `10.`)
  - 앞에 `#### 태스크 2.3.3` 마크다운 셀 2개
  - `from langchain_core.prompts import PromptTemplate`
  - `PROMPT_TEMPLATE`을 **파트 1(셀 19)과 동일한 문구**로 작성. 플레이스홀더만
    `{context}`, `{question}`으로 바꾼다
  - `nova_prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])`
  - _근거: REQ-20, 셀 33, `proj-steering.md` §6_
  - _완료 확인: 두 프롬프트의 문구가 플레이스홀더 이름을 제외하고 동일하다_

- [ ] **6.5 LCEL 체인 구성·실행 셀 작성** (지시 `11.`)
  - 앞에 `#### 태스크 2.3.4` 마크다운 셀 2개 — LCEL로 리트리버와 LLM을 통합한다는 설명
  - `from langchain_core.output_parsers import StrOutputParser`
  - `from langchain_core.runnables import RunnablePassthrough`
  - `format_docs(docs)`: `"\n\n".join(doc.page_content for doc in docs)` — 주석으로 역할 설명
  - `chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | nova_prompt | llm | StrOutputParser())`
  - 딕셔너리 키가 `PromptTemplate`의 `input_variables`와 일치해야 한다
  - `response = chain.invoke(query)` / `print(response)`
  - _근거: REQ-21, REQ-22, 셀 36, 설계 §3.6_
  - _완료 확인: 체인이 답변을 생성해 출력한다_

---

## 단계 7. 마무리 (셀 37)

- [ ] **7.1 태스크 완료 마크다운 셀 작성**
  - `<i class="far fa-thumbs-up" style="color:#008296"></i>` 아이콘으로 태스크 완료 표시
  - 다음 안내를 포함: 노트북 탭을 닫고, 실습 지침으로 돌아가 태스크 3을 계속한다
  - _근거: 셀 37, `proj-steering.md` §10_
  - _완료 확인: 다음 단계 안내가 마지막 셀에 있다_

---

## 단계 8. 검증

- [ ] **8.1 순차 실행 검증**
  - 커널을 재시작하고 **셀을 하나씩** 위에서 아래로 실행한다. `Run All Cells`를 쓰지 않는다
  - _근거: NFR-05, CON-01_
  - _완료 확인: 오류 0건_

- [ ] **8.2 하드코딩 점검**
  - KB ID가 코드에 하드코딩되어 있지 않다 (REQ-01)
  - 리전이 하드코딩되어 있지 않다 (REQ-04)
  - 자격 증명이 코드에 없다 (NFR-02)
  - _완료 확인: 세 항목 모두 통과_

- [ ] **8.3 프롬프트 일치 확인**
  - 셀 19와 셀 33의 프롬프트 문구가 플레이스홀더 이름을 제외하고 동일한지 대조한다
  - 네 지시(역할 / 근거 한정 / 환각 금지 / 수치 구체성)가 양쪽에 모두 있는지 확인한다
  - _근거: REQ-12, `proj-steering.md` §6_
  - _완료 확인: 두 프롬프트가 일치한다_

- [ ] **8.4 검색 설정 확인**
  - 파트 1이 `numberOfResults=5`, `overrideSearchType="HYBRID"`인지 확인
  - 파트 2가 `numberOfResults=4`, `overrideSearchType="SEMANTIC"`인지 확인
  - **두 설정이 다른 것이 정상이다.** 같아졌다면 되돌린다
  - _근거: REQ-06, REQ-18, O-1_
  - _완료 확인: 두 설정이 각각 유지되어 있다_

- [ ] **8.5 답변 품질 확인**
  - 두 파트가 같은 질문에 대해 검색된 근거를 바탕으로 수치를 포함한 답변을 내는지 확인
  - 답변 문장은 서로 다를 수 있다 (`temperature=0.5`). **수치가 일치하는지**를 본다
  - _근거: REQ-12, REQ-16, REQ-22_
  - _완료 확인: 두 답변이 같은 근거에서 같은 수치를 말한다_

- [ ] **8.6 노트북 구조 점검**
  - 모든 코드 셀 앞에 설명 마크다운 셀이 있는지 확인 (NFR-04)
  - 실행 지시 번호가 `1.` ~ `11.`로 빠짐없이 순차적인지 확인
  - 섹션 번호(`## 태스크 2.x` → `#### 태스크 2.x.y`)가 일관되는지 확인
  - _근거: `proj-steering.md` §10_
  - _완료 확인: 세 항목 모두 통과_

- [ ] **8.7 스티어링 검토 체크리스트 통과**
  - `proj-steering.md` §11의 10개 항목을 하나씩 확인한다
  - _완료 확인: 10개 항목 전부 체크됨_

- [ ] **8.8 요구 사항 완료 기준 대조**
  - `requirements.md` §6의 11개 완료 기준을 대조한다
  - _완료 확인: 11개 항목 전부 체크됨_

---

## 단계 9. 문서 동기화

- [ ] **9.1 변경분 반영**
  - 구현 중 설계와 달라진 부분이 있으면 `design.md`를 갱신한다. 코드만 고치고 넘어가지 않는다
  - 새 동작이 생겼으면 `requirements.md`에 새 REQ ID를 부여한다. 기존 ID의 의미를 바꾸지 않는다
  - _근거: `proj-steering.md` §9_

- [ ] **9.2 파급 범위가 큰 변경 확인**
  - 다음 변경을 했다면 연관 셀을 모두 고쳤는지 확인한다

  | 변경 | 확인할 곳 |
  |---|---|
  | 질문 변경 | 셀 13과 셀 30 **두 곳** (CON-05) |
  | 프롬프트 변경 | 셀 19와 셀 33 **두 곳** |
  | 모델 교체 | 셀 22 페이로드, 셀 23 파싱, 셀 6·20 설명 (CON-07) |
  | 검색 파라미터 변경 | 해당 셀 + 셀 7·28 설명 |
  | 재시도 설정 변경 | 셀 5 (CON-06) |

  - _근거: `proj-steering.md` §9_

- [ ] **9.3 후속 태스크 연결 확인**
  - 태스크 3(RAGAS 평가)이 파트 2의 `retriever`와 `llm` 구성을 그대로 이어받을 수 있는지 확인한다
  - _근거: 설계 §8_

---

## 부록 A. 작업 ↔ 요구 사항 추적표

| REQ | 작업 |
|---|---|
| REQ-01 | 2.2, 8.2 |
| REQ-02 | 2.2 |
| REQ-03 | 2.2 |
| REQ-04 | 2.3, 8.2 |
| REQ-05 | 3.3 |
| REQ-06 | 3.2, 3.3, 8.4 |
| REQ-07 | 3.4 |
| REQ-08 | 3.4 |
| REQ-09 | 4.1 |
| REQ-10 | 4.2 |
| REQ-11 | 4.3 |
| REQ-12 | 4.3, 8.3, 8.5 |
| REQ-13 | 5.1 |
| REQ-14 | 3.1, 5.2 |
| REQ-15 | 5.2 |
| REQ-16 | 5.2, 8.5 |
| REQ-17 | 6.2 |
| REQ-18 | 6.3, 8.4 |
| REQ-19 | 6.3 |
| REQ-20 | 6.4 |
| REQ-21 | 6.5 |
| REQ-22 | 6.5, 8.5 |
| NFR-01 | 2.3 |
| NFR-02 | 8.2 |
| NFR-03 | 3.4, 4.2, 5.2, 6.3, 6.5 |
| NFR-04 | 8.6 |
| NFR-05 | 8.1 |

## 부록 B. 작업 ↔ 제약 사항 추적표

| CON | 작업 |
|---|---|
| CON-01 | 1.1, 8.1 |
| CON-02 | 2.4 |
| CON-03 | 2.4 |
| CON-04 | 5.3 |
| CON-05 | 6.3, 9.2 |
| CON-06 | 2.3, 9.2 |
| CON-07 | 5.1, 9.2 |
| CON-08 | 0.3, 3.2 |
