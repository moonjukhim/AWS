### Threat-composer

1. 웹 버전 (설치 불필요)

- 전체 기능: https://awslabs.github.io/threat-composer?mode=Full
- 위협만 작성하는 모드: https://awslabs.github.io/threat-composer?mode=ThreatsOnly

모든 처리가 브라우저 안에서만 이루어지고, 데이터는 브라우저 로컬 저장소에 남습니다. 작업한 내용은 .tc.json 파일로 내보내거나 불러옵니다.

2. 내 PC에서 소스로 실행

사전 준비:
- Node.js 24 (20.19, 22.13 이상도 동작)
- pnpm 10 (yarn이나 npm이 아닙니다)
- uv (Python 패키지 관리 도구)

```bash
npm install -g pnpm@10
git clone https://github.com/awslabs/threat-composer.git
cd threat-composer
pnpm install --frozen-lockfile
pnpm build
pnpm dev          # 웹 앱 → http://localhost:3000
```
- 화면 구성요소(UI) 개발용 Storybook: pnpm storybook → http://localhost:6006
- 배포용 빌드: pnpm nx run @aws/threat-composer-app:compile (결과는 packages/threat-composer-app/build/)

3. 내 AWS 계정에 배포 (CDK)

CloudFront, S3, WAF로 구성된 정적 웹사이트로 배포됩니다.

cdk bootstrap aws://<계정ID>/<리전> --cloudformation-execution-policies "arn:aws:iam::aws:policy/IAMFullAccess,arn:aws:iam::aws:policy/AWSLambda_FullAccess,arn:aws:iam::aws:policy/AmazonS3FullAccess,arn:aws:iam::aws:policy/CloudFrontFullAccess,arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
./scripts/deployDev.sh    # 완료되면 CloudFront 도메인을 출력
- 접속 허용 IP를 먼저 바꿔야 합니다: packages/threat-composer-infra/cdk.context.json의 cidrRangesDev 기본값(192.168.0.0/24)으로는 외부에서 접속할 수 없습니다. 수강생이 접속할 IP 대역으로 바꾸세요.
- 기본 설정에는 로그인 같은 인증이 없고, 이 IP 제한만으로 접근을 막습니다. 인증이 필요하면 문서에서 Lambda@Edge를 추가하는 방법을 안내합니다.
- CodePipeline을 이용한 개발·운영 자동 배포가 필요하면 ./scripts/deployAll.sh를 씁니다.

4. 그 밖의 실행 방법

- VS Code: 별도 확장이 아니라 AWS Toolkit 안에 포함되어 있습니다. code --install-extension AmazonWebServices.aws-toolkit-vscode로 설치한 뒤 .tc.json 파일을 열면 Threat Composer 편집기가 열립니다.
- 브라우저 확장: 아직 스토어에 올라와 있지 않습니다.
  - 빌드: ./scripts/build.sh
  - Chrome: chrome://extensions에서 "압축해제된 확장 프로그램을 로드"로 .output/chrome-mv3 폴더를 선택
  - 설치하면 GitHub 등에 올라온 .tc.json 파일 옆에 "View in Threat Composer" 버튼이 생깁니다.
- AI CLI와 MCP 서버 (실험 기능): 코드베이스를 분석해 위협 모델을 자동으로 만들어 줍니다.
  - Amazon Bedrock을 사용하며, 한 번 실행에 50만~150만 토큰 이상이 들어 비용이 발생합니다.
  - Graphviz가 설치되어 있어야 합니다.
uvx --from "git+https://github.com/awslabs/threat-composer.git#subdirectory=packages/threat-composer-ai" threat-composer-ai-cli /path/to/codebase
  - MCP 서버로 쓰려면 MCP 클라이언트 설정에 "command": "threat-composer-ai-mcp"를 등록합니다.

Windows에서 실행할 때

배포·빌드 스크립트(./scripts/*.sh)는 bash 스크립트라서 PowerShell에서는 그대로 실행되지 않을 가능성이 큽니다. Git Bash나 WSL에서 실행하시는 것이 안전합니다. 