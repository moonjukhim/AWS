# 구현 작업 목록 (Tasks)

`requirements.md`와 `design.md`를 기준으로 한 구현 작업 체크리스트.
각 작업은 요구사항(R#) / 설계 절(D#)에 매핑된다.

---

## 1. 환경 준비
- [ ] 1.1 의존성 설치: `boto3`, `langchain`, `langchain-aws` (R: 기술스택 / D9)
- [ ] 1.2 AWS 자격 증명 및 리전 설정 확인 (Bedrock 지원 리전) (D9)
- [ ] 1.3 amazon.nova-lite-v1:0 모델 액세스 활성화 확인 (R5, R6 / D9)

## 2. Knowledge Base ID 조회
- [ ] 2.1 `bedrock-agent` 클라이언트 생성 (R1 / D5.1)
- [ ] 2.2 `list_knowledge_bases()`로 기존 KB 목록 조회 (R1 / D4)
- [ ] 2.3 KB ID 확보, 없으면 명확한 오류 후 종료 (KB 생성 금지) (R1, R7 / D10)

## 3. boto3 Retrieve 방식
- [ ] 3.1 `bedrock-agent-runtime` 클라이언트 생성 (R2 / D5.1)
- [ ] 3.2 Retrieve 호출: `overrideSearchType=HYBRID`, `numberOfResults=5` (R2 / D5.2)
- [ ] 3.3 `content.text` 추출 후 context 문자열로 결합 (R3 / D5.3)
- [ ] 3.4 환각 방지 프롬프트 구성 (context + question) (R4 / D5.4)
- [ ] 3.5 `bedrock-runtime.invoke_model`로 amazon.nova-lite-v1:0 호출 (R5 / D5.5)
- [ ] 3.6 Nova 응답 파싱하여 답변 텍스트 추출 (R5 / D5.5)

## 4. LangChain LCEL 방식
- [ ] 4.1 `AmazonKnowledgeBasesRetriever` 구성: `SEMANTIC`, `numberOfResults=4` (R6 / D6.1)
- [ ] 4.2 `PromptTemplate`로 환각 방지 프롬프트 재사용 (R4, R6 / D6.2)
- [ ] 4.3 `ChatBedrock`(amazon.nova-lite-v1:0) 구성 (R6 / D6.2)
- [ ] 4.4 LCEL 파이프라인 연결: retriever → prompt → LLM → `StrOutputParser` (R6 / D6.2)

## 5. 실행 및 검증
- [ ] 5.1 검증 질문으로 boto3 방식 실행, 정상 응답 확인 (검증 / D11)
- [ ] 5.2 검증 질문으로 LangChain 방식 실행, 정상 응답 확인 (검증 / D11)
- [ ] 5.3 두 방식 결과 비교 출력 (D7)

## 6. 품질/제약 검증
- [ ] 6.1 멱등성 확인: 반복 실행 시 리소스/설정 중복 생성 없음 (R8 / D8)
- [ ] 6.2 불필요한 파일/코드 미생성 확인 (R9 / D8)
- [ ] 6.3 기존 구현이 요구사항 충족 시 변경하지 않음 (R7 / D8)

---

## 검증 질문
```
What was the total operating lease liabilities and total sublease income of the AnyCompany as of December 31, 2022?
```

## 완료 조건
- [ ] boto3 Retrieve API 방식이 정상 응답한다.
- [ ] LangChain LCEL 방식이 정상 응답한다.
- [ ] 불필요한 파일이나 코드는 생성하지 않는다.
