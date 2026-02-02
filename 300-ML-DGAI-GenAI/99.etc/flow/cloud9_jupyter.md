## Cloud9에서 Jupyter Notebook 사용

1. Cloud9 환경 생성

    - EC2 기반 Amazon Linux 2 선택

2. Notebook 설치

```bash
sudo yum update -y
# pip3 설치 (없을 경우)
sudo yum install -y python3-pip
pip3 install notebook jupyterlab
```

3. Jupyter Notebook 실행

```bash
jupyter lab --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token=''
```

4. Cloud9에서 포트 미리보기

    - Cloud9 IDE 상단 메뉴 --> Preview --> Preview Running Application

5. (선택) Jupyter Notebook 기본 런처 등록

    - .bashrc에 alias 추가

    ```bash
    echo "alias jn='jupyter lab --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token=''" >> ~/.bashrc
    source ~/.bashrc
    ```
