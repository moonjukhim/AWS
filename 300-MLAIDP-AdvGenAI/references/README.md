##

##### 1. Foundation Model Selection

- [Multi-LLM routing strategies for generative AI applications on AWS](https://aws.amazon.com/blogs/machine-learning/multi-llm-routing-strategies-for-generative-ai-applications-on-aws/)
- [Using the circuit breaker pattern with AWS Step Functions and Amazon DynamoDB](https://aws.amazon.com/blogs/compute/using-the-circuit-breaker-pattern-with-aws-step-functions-and-amazon-dynamodb/)
- [circuit-breaker-netcore-blog::github](https://github.com/aws-samples/circuit-breaker-netcore-blog)

##### 2. Data Processing for Foundation Model

- [Effectively use prompt caching on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock/)
- [Reduce costs and latency with Amazon Bedrock Intelligent Prompt Routing and prompt caching (preview)](https://aws.amazon.com/blogs/aws/reduce-costs-and-latency-with-amazon-bedrock-intelligent-prompt-routing-and-prompt-caching-preview/)
- [Guidance for Semantic Caching for GenerativeAI applications using Amazon ElastiCache for Valkey](https://aws.amazon.com/solutions/guidance/semantic-caching-for-generative-ai-applications-using-amazon-elasticache-for-valkey/)


| 슬라이드 구성 | 가장 가까운 공식 레퍼런스 | 보고된 효과 |
|--------------|---|---|
| 프롬프트 캐싱 (Nova Micro/Lite) | Well-Architected GenAI Lens **GENCOST03-BP03** + Bedrock 공식 문서 + ML Blog | 비용 90% / 지연 85% 감소 |
| L1 인메모리 + L2 시맨틱 캐시 | AWS Solutions Library **Guidance for Semantic Caching (ElastiCache for Valkey)** | 비용 86% / 지연 88% 감소 |
| 영속 시맨틱 캐시 (Multi-AZ) | AWS Database Blog **MemoryDB Semantic Cache** + re:Invent 2024 DAT329 | 최대 89.79% 비용 절감, p99 단일 ms |
| 다단계 L1/L2/L3 캐시 전략 종합 | AWS Database Blog **"Optimize LLM response costs and latency with effective caching"** | 캐싱 30% 절감 (슬라이드 ROI와 일치) |
| 운영 플레이북 (캐싱 + 라우팅 + 폴백) | re:Post **Amazon Bedrock Advanced Operations Playbook** | — |

1. Bedrock Prompt Caching (Nova Micro/Lite) : 이건 모델 내부 KV 캐시입니다. 트랜스포머가 attention 계산 시 만드는 Key-Value 텐서를 Bedrock이 GPU 메모리에 보관해두는 방식
2. ElastiCache for Valkey 시맨틱 캐시 (L1/L2) : 이건 모델 외부에 별도로 두는 벡터 캐시. 사용자 질문이 들어오면 먼저 Titan Text Embeddings 같은 임베딩 모델로 벡터화한 뒤, ElastiCache for Valkey의 벡터 인덱스에 코사인 유사도 검색
3. MemoryDB 영속 시맨틱 캐시 (Multi-AZ) : 2번과 동일한 동작 메커니즘
4. 다단계 L1/L2/L3 fallthrough 캐시 : 단일 레이어가 아니라 빠르고 비싼 → 느리고 싼 순으로 조회하는 계층 구조
5. Bedrock Advanced Operations Playbook : 여러 최적화 기법을 한 파이프라인에 직렬 결합한 운영 패턴입니다

##### 3. Vector DB and Augmentation

