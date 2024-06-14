# 실습 2: AWS Systems Manager 및 Amazon Inspector 사용

### 과제1: Amazon Inspector 에이전트 설치

```bash
aws ssm send-command --targets Key=tag:SecurityScan,Values=true \
--document-name "AmazonInspector-ManageAWSAgent" \
--query Command.CommandId \
--output-s3-bucket-name <LogBucket>
```

Inspector 에이전트가 성공적으로 설치되었는지 확인

```bash
aws ssm list-command-invocations --details \
--query "CommandInvocations[*].[InstanceId,DocumentName,Status]" \
--command-id <CommandId>
```
### 과제2: Amazon Inspector 설정

### 과제3: 스캔 결과 검토

### 과제4: 패치 기준선 생성 및 적용

---

CIS Operating System Security Configuration Benchmarks  The CIS Security Benchmarks program provides well-defined, un-biased and consensus-based industry best practices to help organizations assess and improve their security.

The rules in this package help establish a secure configuration posture for the following operating systems:

  -   Amazon Linux 2 (CIS Benchmark for Amazon Linux 2 Benchmark v1.0.0 Level 1)
  -   Amazon Linux 2 (CIS Benchmark for Amazon Linux 2 Benchmark v1.0.0 Level 2)
  -   Ubuntu Linux 18.04 LTS (CIS Benchmark for Ubuntu Linux 18.04 LTS Benchmark v1.0.0 Level 1 Server)
  -   Ubuntu Linux 18.04 LTS (CIS Benchmark for Ubuntu Linux 18.04 LTS Benchmark v1.0.0 Level 2 Server)
  -   Ubuntu Linux 18.04 LTS (CIS Benchmark for Ubuntu Linux 18.04 LTS Benchmark v1.0.0 Level 1 Workstation)
  -   Ubuntu Linux 18.04 LTS (CIS Benchmark for Ubuntu Linux 18.04 LTS Benchmark v1.0.0 Level 2 Workstation)
  -   Amazon Linux version 2015.03 (CIS benchmark v1.1.0)
  -   Windows Server 2008 R2 (CIS Benchmark for Microsoft Windows 2008 R2, v3.0.0, Level 1 Domain Controller)
  -   Windows Server 2008 R2 (CIS Benchmark for Microsoft Windows 2008 R2, v3.0.0, Level 1 Member Server Profile)
  -   Windows Server 2012 R2 (CIS Benchmark for Microsoft Windows Server 2012 R2, v2.2.0, Level 1 Member Server Profile)
  -   Windows Server 2012 R2 (CIS Benchmark for Microsoft Windows Server 2012 R2, v2.2.0, Level 1 Domain Controller Profile)
  -   Windows Server 2012 (CIS Benchmark for Microsoft Windows Server 2012 non-R2, v2.0.0, Level 1 Member Server Profile)
  -   Windows Server 2012 (CIS Benchmark for Microsoft Windows Server 2012 non-R2, v2.0.0, Level 1 Domain Controller Profile)
  -   Windows Server 2016 (CIS Benchmark for Microsoft Windows Server 2016 RTM (Release 1607), v1.1.0, Level 1 Member Server Profile)
  -   Windows Server 2016 (CIS Benchmark for Microsoft Windows Server 2016 RTM (Release 1607), v1.1.0, Level 2 Member Server Profile)
  -   Windows Server 2016 (CIS Benchmark for Microsoft Windows Server 2016 RTM (Release 1607), v1.1.0, Level 1 Domain Controller Profile)
  -   Windows Server 2016 (CIS Benchmark for Microsoft Windows Server 2016 RTM (Release 1607), v1.1.0, Level 2 Domain Controller Profile)
  -   Windows Server 2016 (CIS Benchmark for Microsoft Windows Server 2016 RTM (Release 1607), v1.1.0, Next Generation Windows SecurityProfile)
  -   Amazon Linux (CIS Benchmark for Amazon Linux Benchmark v2.1.0 Level 1)
  -   Amazon Linux (CIS Benchmark for Amazon Linux Benchmark v2.1.0 Level 2)
  -   CentOS Linux 7 (CIS Benchmark for CentOS Linux 7 Benchmark v2.2.0 Level 1 Server)
  -   CentOS Linux 7 (CIS Benchmark for CentOS Linux 7 Benchmark v2.2.0 Level 2 Server)
  -   CentOS Linux 7 (CIS Benchmark for CentOS Linux 7 Benchmark v2.2.0 Level 1 Workstation)
  -   CentOS Linux 7 (CIS Benchmark for CentOS Linux 7 Benchmark v2.2.0 Level 2 Workstation)
  -   Red Hat Enterprise Linux 7 (CIS Benchmark for Red Hat Enterprise Linux 7 Benchmark v2.1.1 Level 1 Server)
  -   Red Hat Enterprise Linux 7 (CIS Benchmark for Red Hat Enterprise Linux 7 Benchmark v2.1.1 Level 2 Server)
  -   Red Hat Enterprise Linux 7 (CIS Benchmark for Red Hat Enterprise Linux 7 Benchmark v2.1.1 Level 1 Workstation)
  -   Red Hat Enterprise Linux 7 (CIS Benchmark for Red Hat Enterprise Linux 7 Benchmark v2.1.1 Level 2 Workstation)
  -   Ubuntu Linux 16.04 LTS (CIS Benchmark for Ubuntu Linux 16.04 LTS Benchmark v1.1.0 Level 1 Server)
  -   Ubuntu Linux 16.04 LTS (CIS Benchmark for Ubuntu Linux 16.04 LTS Benchmark v1.1.0 Level 2 Server)
  -   Ubuntu Linux 16.04 LTS (CIS Benchmark for Ubuntu Linux 16.04 LTS Benchmark v1.1.0 Level 1 Workstation)
  -   Ubuntu Linux 16.04 LTS (CIS Benchmark for Ubuntu Linux 16.04 LTS Benchmark v1.1.0 Level 2 Workstation)
  -   CentOS Linux 6 (CIS Benchmark for CentOS Linux 6 Benchmark v2.0.2, Level 1 Server)
  -   CentOS Linux 6 (CIS Benchmark for CentOS Linux 6 Benchmark v2.0.2, Level 2 Server)
  -   CentOS Linux 6 (CIS Benchmark for CentOS Linux 6 Benchmark v2.0.2, Level 1 Workstation)
  -   CentOS Linux 6 (CIS Benchmark for CentOS Linux 6 Benchmark v2.0.2, Level 2 Workstation)
  -   Red Hat Enterprise Linux 6 (CIS Benchmark for Red Hat Enterprise Linux 6 Benchmark v2.0.2, Level 1 Server)
  -   Red Hat Enterprise Linux 6 (CIS Benchmark for Red Hat Enterprise Linux 6 Benchmark v2.0.2, Level 2 Server)
  -   Red Hat Enterprise Linux 6 (CIS Benchmark for Red Hat Enterprise Linux 6 Benchmark v2.0.2, Level 1 Workstation)
  -   Red Hat Enterprise Linux 6 (CIS Benchmark for Red Hat Enterprise Linux 6 Benchmark v2.0.2 Level 2 Workstation)
  -   Ubuntu Linux 14.04 LTS (CIS Benchmark for Ubuntu Linux 14.04 LTS Benchmark v2.0.0, Level 1 Server)
  -   Ubuntu Linux 14.04 LTS (CIS Benchmark for Ubuntu Linux 14.04 LTS Benchmark v2.0.0, Level 2 Server)
  -   Ubuntu Linux 14.04 LTS (CIS Benchmark for Ubuntu Linux 14.04 LTS Benchmark v2.0.0, Level 1 Workstation)
  -   Ubuntu Linux 14.04 LTS (CIS Benchmark for Ubuntu Linux 14.04 LTS Benchmark v2.0.0, Level 2 Workstation)

If a particular CIS benchmark appears in a finding produced by an Amazon Inspector assessment run, you can download a detailed PDF description of the benchmark from https://benchmarks.cisecurity.org/ (free registration required). The benchmark document provides detailed information about this CIS benchmark, its severity, and how to mitigate it.


---

Network Reachability    These rules analyze the reachability of your instances over the network. Attacks can exploit your instances over the network by accessing services that are listening on open ports. These rules evaluate the security your host configuration in AWS to determine if it allows access to ports and services over the network. For reachable ports and services, the Amazon Inspector findings identify where they can be reached from, and provide guidance on how to restrict access to these ports.

---

Security Best Practices The rules in this package help determine whether your systems are configured securely.

---

Common Vulnerabilities and Exposures    The rules in this package help verify whether the EC2 instances in your application are exposedto Common Vulnerabilities and Exposures (CVEs). Attacks can exploit unpatched vulnerabilities to compromise the confidentiality, integrity, or availability of your service or data. The CVE system provides a reference for publicly known information security vulnerabilities and exposures. For more information, see [https://cve.mitre.org/](https://cve.mitre.org/). If a particular CVE appears in one of the produced Findings at the end of a completed Inspector assessment, you can search [https://cve.mitre.org/](https://cve.mitre.org/) using the CVE's ID (for example, "CVE-2009-0021") to find detailed information about this CVE, its severity, and how to mitigate it.

