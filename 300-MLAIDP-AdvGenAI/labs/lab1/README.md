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

- 결론 :
  - 답변은 매우 정확 (relevancy 0.97)

##### 