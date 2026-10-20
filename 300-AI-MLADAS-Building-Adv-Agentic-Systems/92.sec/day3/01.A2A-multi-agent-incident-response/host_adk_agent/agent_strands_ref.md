## ADK의 transfer_to_agent와 Strands 비교

원격 A2A 에이전트는 strands.agent.a2a_agent.A2AAgent로 감쌉니다. 
ADK의 RemoteA2aAgent에 해당하며, a2a_client_factory를 받을 수 있어서 이 사례의 LazyClientFactory처럼 Bearer 토큰과 AgentCore 헤더를 넣을 수 있습니다.

다만 A2AAgent에는 as_tool()이 없고, Swarm 노드로도 쓸 수 없습니다. 
Swarm은 각 노드의 tool_registry에 handoff 도구를 넣어야 하기 때문입니다. 그래서 선택지는 아래 세 가지입니다.

```python
from strands import Agent, tool
from strands.agent.a2a_agent import A2AAgent

remote_monitor = A2AAgent(endpoint=MONITOR_URL, name="monitor_agent", a2a_client_factory=factory)

@tool
def monitor_agent(query: str) -> str:
    """CloudWatch 지표/로그/알람을 조회하는 원격 에이전트"""
    return str(remote_monitor(query))

orchestrator = Agent(system_prompt=SYSTEM_PROMPT, tools=[monitor_agent, websearch_agent])
```

- ① @tool로 직접 감싸기: 위 코드 방식이며 가장 단순합니다.
- ② Graph 노드로 쓰기: GraphNode.executor가 AgentBase를 받으므로 A2AAgent를 노드로 바로 넣을 수 있습니다. 이 경우 LLM이 아니라 엣지가 라우팅합니다.
- ③ strands.vended_tools.a2a_client의 A2A 클라이언트 도구 사용: LLM이 에이전트 카드를 탐색한 뒤 메시지를 보내는 범용 도구입니다.

정리하면, ADK의 transfer에 가장 가까운 것은 Swarm의 handoff_to_agent입니다. 이 사례처럼 오케스트레이터가 결과를 모아 종합해야 한다면 as_tool() 방식이 프롬프트 의도에 더 맞습니다.