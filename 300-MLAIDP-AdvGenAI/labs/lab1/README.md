Lab1 - Task-3의 랩을 실행할 때 오류가 발생할 경우 패키지를 설치한 후, 커널 재시작

1. 패키지 설치

```python
!pip install datasets==2.19.0 pyarrow==14.0.2
```

2. 커널 재시작

---

| idx | faithfulness | answer_relevancy | context_precision | context_recall | context_entity_recall | answer_similarity | answer_correctness | harmfulness | maliciousness | coherence | correctness | conciseness |
|-----|-------------|------------------|-------------------|----------------|------------------------|-------------------|--------------------|-------------|---------------|------------|--------------|--------------|
| 0   | 0.8         | 0.972577415      | 1                 | 1              | 0.249999999            | 0.568409152       | 0.570673717        | 0           | 0             | 1          | 1            | 1            |
| 1   | 0.75        | 0.79321018       | 1                 | 1              | 0.222222222            | 0.979912429       | 0.619978107        | 0           | 0             | 1          | 1            | 1            |
| 2   | 1           | 0.995492862      | 1                 | 1              | 0.249999999            | 0.933157504       | 0.795789376        | 0           | 0             | 1          | 1            | 1            |
| 3   | 1           | 0.851156444      | 0.7               | 0.333333333    | 0.499999999            | 0.812855063       | 0.390713766        | 0           | 0             | 1          | 1            | 1            |
| 4   | 1           | 0.880288322      | 0                 | 0.4            | 0.222222222            | 0.8975684         | 0.7868921          | 0           | 0             | 1          | 1            | 1            |


---
##### Row 0 분석

- faithfulness: 0.8
- answer_relevancy: 0.97
- context_precision / recall: 1 / 1
- entity_recall: 0.25

- Retrieval: 문서는 정확히 잘 가져옴 (precision/recall 1), BUT 핵심 entity는 부족 (0.25)
- Generation : 답변은 매우 정확 (relevancy 0.97)

- 결론 :“문서는 맞지만, 핵심 정보 밀도가 낮음” 

##### Row 1 분석

- faithfulness: 0.75
- answer_relevancy: 0.79
- context_precision / recall: 1 / 1
- entity_recall: 0.22
- answer_similarity: 0.97

- Retrieval:문서는 맞지만 핵심 정보 부족
- Generation:정답은 맞지만 표현이 덜 정확
결론 : “문서는 맞지만, 답변 품질이 살짝 흔들림”

##### Row 2 분석

faithfulness: 1
answer_relevancy: 0.99
context_precision / recall: 1 / 1
answer_correctness: 0.79

Retrieval: 완벽
Retrieval: 완벽
결론 : “이상적인 RAG 상태 (gold case)”

##### Row 3 분석

faithfulness: 1
answer_relevancy: 0.85
context_precision: 0.7
context_recall: 0.33
answer_correctness: 0.39

Retrieval: 많이 부족 (특히 recall 0.33 ❗)
Generation: 계산 문제라 정확도 떨어짐

결론 : “retrieval 부족 → reasoning 실패”

##### Row 4 분석

| Category    | Metric                   | Value | Interpretation |
|------------|--------------------------|-------|----------------|
| Generation | faithfulness             | 1     | Context 기반으로 생성된 것으로 평가됨 |
| Generation | answer_relevancy         | 0.88  | 질문과의 관련성 높음 |
| Generation | answer_correctness       | 0.78  | 비교적 정확한 답변 |
| Retrieval  | context_precision        | 0 ❗  | 관련 없는 문서 검색 (retrieval 실패) |
| Retrieval  | context_recall           | 0.4   | 일부 정보만 포함됨 |
| Summary    | Retrieval 상태           | -     | ❌ 실패 |
| Summary    | Generation 상태          | -     | ✔️ LLM이 자체 지식으로 보완 |
| Conclusion | 최종 해석               | -     | RAG grounding 실패 + LLM fallback (hallucination risk) |