# CloudFormation 헬퍼 스크립트 데모 (cfn-init / cfn-signal / cfn-hup)

`cfn-helper-demo.yaml` 한 개의 템플릿으로 세 헬퍼 스크립트가 **어떻게 함께 동작하는지**를 보여줍니다.
Amazon Linux 2023 EC2 인스턴스 한 대를 띄워 Apache 웹 서버를 구성하고, 스택 업데이트만으로
웹 페이지가 자동 갱신되는 모습을 확인합니다.

## 세 스크립트의 역할

| 스크립트 | 트리거 | 하는 일 | 템플릿 위치 |
|----------|--------|---------|-------------|
| **cfn-init** | UserData에서 부팅 시 1회 실행 | `AWS::CloudFormation::Init` 메타데이터를 읽어 패키지 설치·파일 생성·서비스 시작 | `Metadata` 블록 + UserData |
| **cfn-signal** | cfn-init 직후 실행 | cfn-init 종료 코드를 `CreationPolicy`로 전송 → 성공해야 스택이 CREATE_COMPLETE | UserData + `CreationPolicy` |
| **cfn-hup** | 데몬으로 상주하며 메타데이터를 폴링 | 스택 업데이트로 메타데이터가 바뀌면 훅에 정의된 cfn-init을 자동 재실행 | `cfn-hup.conf` + `hooks.d/cfn-auto-reloader.conf` |

## 동작 흐름

```
부팅
 └─ UserData
      ├─ dnf install aws-cfn-bootstrap   (헬퍼 스크립트 설치)
      ├─ cfn-init   --configsets default → httpd 설치, 파일 생성, cfn-hup 데몬 기동
      └─ cfn-signal -e $?                → CreationPolicy(Count:1)에 완료 신호
                                            신호 없으면 10분 후(PT10M) 생성 실패·롤백

스택 업데이트(SiteVersion 변경)
 └─ cfn-hup(상주 데몬)이 메타데이터 변경 감지
      └─ hooks.d 훅 발동 → cfn-init --configsets update → index.html 다시 렌더링
```

## 사전 준비
- AWS CLI 설치 및 자격 증명 구성 (`aws configure`)
- 템플릿을 배포할 리전의 **기본 VPC** (보안 그룹이 기본 VPC를 사용)

## 1. 배포 (스택 생성)

```bash
aws cloudformation create-stack \
  --stack-name cfn-helper-demo \
  --template-body file://cfn-helper-demo.yaml \
  --parameters ParameterKey=SiteVersion,ParameterValue=v1 \
  --capabilities CAPABILITY_IAM

# 완료 대기 (cfn-signal 신호를 받아야 COMPLETE)
aws cloudformation wait stack-create-complete --stack-name cfn-helper-demo
```

생성된 웹 URL 확인:
```bash
aws cloudformation describe-stacks --stack-name cfn-helper-demo \
  --query "Stacks[0].Outputs" --output table
```
출력된 `WebsiteURL`을 브라우저로 열면 **현재 버전: v1** 페이지가 보입니다.
→ 여기까지가 **cfn-init**(콘텐츠 구성)과 **cfn-signal**(생성 완료 신호)의 결과입니다.

## 2. cfn-hup 동작 확인 (핵심)

웹 콘텐츠를 직접 SSH로 바꾸지 않고 **스택 파라미터만** 변경합니다.

```bash
aws cloudformation update-stack \
  --stack-name cfn-helper-demo \
  --use-previous-template \
  --parameters ParameterKey=SiteVersion,ParameterValue=v2 \
  --capabilities CAPABILITY_IAM

aws cloudformation wait stack-update-complete --stack-name cfn-helper-demo
```

업데이트 후 잠시(폴링 간격 `interval=1`분) 기다렸다가 같은 URL을 새로고침하면
**현재 버전: v2** 로 바뀝니다. SSH 접속이나 수동 배포 없이 cfn-hup이 자동으로
cfn-init을 다시 돌린 결과입니다.

### 인스턴스에서 직접 로그로 확인 (선택)
SSH 접속 후:
```bash
# cfn-hup 데몬 상태
sudo systemctl status cfn-hup

# 헬퍼 스크립트 실행 로그
sudo tail -n 50 /var/log/cfn-hup.log        # cfn-hup이 변경 감지·훅 실행한 기록
sudo tail -n 50 /var/log/cfn-init.log       # cfn-init 실행 상세
sudo tail -n 50 /var/log/cfn-init-cmd.log   # commands 블록 실행 결과
```

## 3. 정리 (과금 방지)

```bash
aws cloudformation delete-stack --stack-name cfn-helper-demo
aws cloudformation wait stack-delete-complete --stack-name cfn-helper-demo
```

## 자주 막히는 부분
- **스택이 CREATE_COMPLETE까지 10분 넘게 걸리다 실패** → cfn-signal이 신호를 못 보낸 경우.
  인스턴스의 `/var/log/cloud-init-output.log`에서 cfn-init 오류를 확인하세요.
- **SSH가 안 됨** → `SSHLocation` 기본값은 `0.0.0.0/0`(전체 허용)입니다. 실제로는 `내IP/32`로 좁히세요.
- **cfn-hup이 안 도는 것 같음** → `interval`은 분 단위입니다. 1~2분 기다린 뒤 새로고침하세요.
- **packages에 dnf 키 사용 시 오류** → cfn-init의 `packages`는 `yum` 키를 씁니다(AL2023도 내부적으로 dnf 처리).
