### Migration Evaluator Vs Application Discovery Agent

| 구분 | **Migration Evaluator** | **Application Discovery Agent (ADS Agent)** |
|---|---|---|
| 목적 | 온프렘 워크로드의 **비용/규모 산정, 권장 사이징, 비즈니스 케이스(Quick Insights/Business Case)** | VM 단위 **세부 인벤토리 + 프로세스/네트워크 플로우 기반 애플리케이션 종속성 맵** 수집 |
| 설치/구성 | **Collector 1대**(온프렘 중앙 수집기) 설치 후 vCenter/Windows/Linux 등에 **원격 수집**(에이전트 불필요) | **각 VM에 경량 에이전트 설치**(Windows/Linux) |
| 수집 데이터 | CPU/메모리/디스크/네트워크 사용량, 실행 소프트웨어/라이선스, 전력/서버 스펙 등 **비용·사이징 메트릭** | OS/하드웨어, 실행 **프로세스/포트**, **IP:Port 연결 관계(네트워크 플로우)**, 리소스 사용률 등 **종속성 텔레메트리** |
| 종속성 시각화 | **불가**(의존성 맵 제공 안 함) | **가능** — Migration Hub 콘솔에서 **서비스/애플리케이션 맵** |
| 결과/리포트 | **Quick Insights** 요약, **Business Case** 상세 비용·TCO 시나리오 | **Migration Hub 대시보드**(애플리케이션 그룹·종속성), CSV/리포트 내보내기 |
| 주 사용 단계 | **사전 평가(Assessment) 초기 단계** — 마이그레이션 대상 규모·비용 가늠 | **이행 계획 수립 단계** — **마이그레이션 웨이브 묶기**, 컷오버/테스트 설계 |
| 운영 오버헤드 | **낮음**(Collector 1대로 중앙 수집) | **중간**(VM 수만큼 에이전트 배포·업데이트 필요) |
| 통합 지점 | 별도 **Migration Evaluator 콘솔** 중심(데이터를 AWS로 업로드) | **AWS Migration Hub**와 **네이티브 통합**(Application Discovery Service 데이터 소스) |
| 비용 | **무상**(서비스 사용료 없음) | **무상**(에이전트/ADS 자체 과금 없음) |
| 네트워크 요구 | Collector → AWS로 **HTTPS(443)** 업링크 | 각 에이전트 → AWS로 **HTTPS(443)** 업링크 |
| 권한/전제 | vCenter/Windows(WMI)/Linux(SSH) 등 **읽기 권한** | 각 OS에 **에이전트 설치 권한** |
| 수집 기간 권장 | **2–4주** 이상 수집 시 정확도 향상 | **수일~수주**(환경 규모에 따라) |
| 잘 쓰이는 시나리오 | “AWS로 옮기면 **얼마 들고 어떤 스펙이 적정인지** 알고 싶다” | “서비스 간 **연결 관계를 시각화**해 **이행 웨이브**를 정하고 싶다” |
