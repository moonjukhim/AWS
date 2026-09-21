1.  의존성 설치

```bash
pip install -r requirements.txt
```

2. AWS 호출 없이 정의 검증 (선택, 권장)

```bash
python deploy_flow.py --dry-run
```

```text
노드 17개 / 연결 33개가 나오고 "검증 통과" 가 뜹니다. flow_definition.json 이 생성돼 DAG 를 눈으로 확인할 수 있습니다.
이미 실행해서 통과 확인했습니다.
```

3. 배포

```bash
python deploy_flow.py --region us-west-2
```

```text
모델은 자동 탐색되며 us.anthropic.claude-opus-5 가 선택.
다른 모델을 쓰려면 --model-id us.anthropic.claude-sonnet-5 처럼 지정
```

4. 호출

```bash
python invoke_flow.py --ticket sample_ticket.json --timing

# --timing 을 붙이면 노드별 타임라인이 나와 1단계 4개 노드가 실제로 동시에 시작하는지 확인할 수 있습니다. python invoke_flow.py --ticket sample_ticket_standard.json --timing
```

5. 정리

```bash
python cleanup.py --with-role
```
