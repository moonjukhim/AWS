### Agentless Vs Application Discovery Agent

| 항목                 | AWS Agentless Discovery Connector  | AWS Application Discovery Agent |
|--------------------|-----------------------------------|----------------------------------|
| **설치 위치**       | VMware 환경의 vCenter에 배포 (OVA)  | 각 물리/가상 서버에 직접 설치 |
| **지원 플랫폼**      | VMware vCenter만                     | Windows, Linux (물리/가상 무관) |
| **수집 방식**        | vCenter API를 통한 메타데이터 수집 (간접) | OS 레벨에서 직접 수집 (에이전트 기반) |
| **수집 정보**       | - 호스트 이름  <br> - IP 주소  <br> - MAC 주소  <br> - OS 정보  <br> - VM 성능(CPU, RAM, 디스크)  <br> - VM inventory  <br> *(제한적)* | - 위 항목 +  <br> - 실행 중인 프로세스  <br> - 포트/네트워크 연결  <br> - 설치된 소프트웨어  <br> - 디스크 상세  <br> - 메모리 사용률  <br> *(심층적)*       |
| **네트워크 연결**    | vCenter → 인터넷(443)               | 각 서버 → 인터넷(443)           |
| **데이터 저장**      | AWS Migration Hub (S3) | AWS Migration Hub (S3) |
| **설치/운영 난이도**  | 간단 (vCenter만 있으면 됨) | 대규모 환경에선 설치 자동화 필요 |
| **성능 분석**        | CPU/RAM만 간단히 | 상세하고 정확한 측정 가능 |
| **적합한 경우**      | - 빠른 인벤토리 파악  <br> - 서버에 접근이 불가한 경우 | - 정밀 분석 필요  <br> - 마이그레이션 계획 수립 단계 |
