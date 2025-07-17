# UTM 로그 대량 전송 도구

192.168.203:514 UDP 포트로 UTM 로그를 대량으로 전송하는 Python 스크립트입니다.

## 기능

- 다양한 UTM 이벤트 타입 생성 (방화벽, IPS, 안티바이러스, 웹필터 등)
- Syslog 표준 형식으로 UDP 로그 전송
- 대량 전송 및 연속 전송 모드 지원
- **멀티쓰레드 지원으로 초당 수만 개 로그 전송 가능**
- **메모리 효율적인 제너레이터 패턴 사용**
- **소켓 버퍼 최적화로 네트워크 성능 향상**
- 실시간 전송 상태 모니터링
- 커스터마이징 가능한 전송 속도
- 시간이 지날수록 전송량 증가 기능

## 성능 개선 사항

### v2.0 주요 개선사항:
- **배치 크기 증가**: 5,000개 → 50,000개 (10배 증가)
- **멀티쓰레드 지원**: 최대 16개 쓰레드로 병렬 처리
- **메모리 최적화**: 제너레이터 패턴으로 메모리 사용량 대폭 감소
- **소켓 버퍼 확장**: 1MB 송신/수신 버퍼로 네트워크 처리량 향상
- **쓰레드당 처리량**: 기존 4만개 → 무제한 (메모리 한계까지)

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정 파일 생성
```bash
# .env 파일 생성 (처음 실행 시)
python3 utm_log_sender.py --create-env
```

생성된 `.env` 파일을 편집하여 설정을 변경할 수 있습니다:
```bash
# .env 파일 편집
nano .env
```

### 3. 스크립트 실행 권한 부여
```bash
chmod +x utm_log_sender.py
```

### 4. 기본 사용법
```bash
# .env 파일의 기본 설정으로 1000개 로그 전송
python3 utm_log_sender.py

# 5000개 로그를 0.05초 간격으로 전송
python3 utm_log_sender.py --count 5000 --delay 0.05

# 최대 속도로 10000개 로그 전송 (delay/increase-rate 무시)
python3 utm_log_sender.py --count 10000 --max-speed

# 연속 전송 모드 (최대 속도)
python3 utm_log_sender.py --continuous --max-speed

# 시간이 지날수록 전송량 증가 (2배씩)
python3 utm_log_sender.py --count 1000 --delay 0.1 --increase-rate 2.0

# 연속 전송 모드 (전송량 증가)
python3 utm_log_sender.py --continuous --increase-rate 1.5

# 명령행에서 다른 호스트와 UDP 포트 지정 (우선순위 높음)
python3 utm_log_sender.py --host 192.168.1.100 --port 1514

# 🆕 멀티쓰레드 모드 (4개 쓰레드로 100만개 로그 전송)
python3 utm_log_sender.py --count 1000000 --multi-thread --threads 4

# 🆕 8개 쓰레드로 최대 속도 전송
python3 utm_log_sender.py --count 500000 --multi-thread --threads 8 --max-speed
```

## 명령행 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--host` | 대상 호스트 IP | 192.168.203 |
| `--port` | 대상 포트 | 514 |
| `--count` | 전송할 로그 개수 | 1000 |
| `--delay` | 로그 간격 (초) | 0.1 |
| `--increase-rate` | 전송량 증가율 | 1.0 |
| `--continuous` | 연속 전송 모드 | False |
| `--max-speed` | 최대 속도로 전송 (delay/increase-rate 무시) | False |
| `--multi-thread` | 🆕 멀티쓰레드 모드 사용 | False |
| `--threads` | 🆕 멀티쓰레드 모드에서 사용할 쓰레드 수 | 4 |
| `--create-env` | .env 파일 생성 | False |

## 성능 비교

### 단일 쓰레드 모드
- **기존**: 최대 4만개/쓰레드
- **개선**: 무제한 (메모리 한계까지)
- **배치 크기**: 5,000개 → 50,000개 (10배 증가)

### 멀티쓰레드 모드
- **4개 쓰레드**: 초당 약 40,000-80,000개 로그
- **8개 쓰레드**: 초당 약 80,000-150,000개 로그
- **16개 쓰레드**: 초당 약 150,000-300,000개 로그

### 메모리 사용량
- **기존**: 배치 크기에 비례하여 메모리 사용
- **개선**: 제너레이터 패턴으로 메모리 사용량 90% 감소

## 환경변수 설정 (.env 파일)

`.env` 파일에서 다음 설정을 관리할 수 있습니다:

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `TARGET_HOST` | 대상 호스트 IP | 192.168.203 |
| `TARGET_PORT` | 대상 포트 | 514 |
| `DEFAULT_LOG_COUNT` | 기본 로그 개수 | 1000 |
| `DEFAULT_DELAY` | 기본 로그 간격 (초) | 0.1 |
| `DEFAULT_INCREASE_RATE` | 기본 전송량 증가율 | 1.0 |
| `HOSTNAME` | 로그에 표시될 호스트명 | utm-sender |
| `FACILITY` | Syslog facility | local0 |

### .env 파일 예제
```bash
# UTM 로그 전송 설정
TARGET_HOST=192.168.203
TARGET_PORT=514

# 전송 설정
DEFAULT_LOG_COUNT=1000
DEFAULT_DELAY=0.1
DEFAULT_INCREASE_RATE=1.0

# 로그 설정
HOSTNAME=utm-sender
FACILITY=local0
```

## 생성되는 UTM 이벤트 타입

- **firewall_block/allow**: 방화벽 차단/허용 이벤트
- **ips_alert**: 침입 탐지 시스템 알림
- **antivirus_scan**: 안티바이러스 스캔 결과
- **web_filter**: 웹 필터링 이벤트
- **email_filter**: 이메일 필터링 이벤트
- **vpn_connection/disconnection**: VPN 연결/해제
- **user_login/logout**: 사용자 로그인/로그아웃
- **admin_action**: 관리자 작업
- **system_alert**: 시스템 알림

## 로그 형식

스크립트는 RFC3164 Syslog 표준을 따르는 로그를 생성합니다:

```
<priority>timestamp hostname: {"timestamp": "...", "event_type": "...", ...}
```

멀티쓰레드 모드에서는 호스트명에 쓰레드 번호가 추가됩니다:
```
<priority>timestamp hostname-thread1: {"timestamp": "...", "event_type": "...", ...}
```

## 예제 출력

### 단일 쓰레드 모드
```
✅ UDP 소켓이 192.168.203:514로 설정되었습니다.
📊 소켓 버퍼 크기: 송신 1048576 bytes, 수신 1048576 bytes
🚀 1000개의 UTM 로그를 192.168.203:514로 전송을 시작합니다...
⏱️  초기 로그 간격: 0.1초
📊 100개 로그 전송 완료 (평균 속도: 9.8 로그/초, 경과시간: 10.2초)
...
📈 전송 완료:
   ✅ 성공: 1000개
   ❌ 실패: 0개
   ⏱️  소요시간: 100.23초
   📊 평균 속도: 9.98 로그/초
```

### 멀티쓰레드 모드
```
✅ UDP 소켓이 192.168.203:514로 설정되었습니다.
📊 소켓 버퍼 크기: 송신 1048576 bytes, 수신 1048576 bytes
🚀 1000000개의 UTM 로그를 4개 쓰레드로 192.168.203:514에 전송을 시작합니다...
⚡ 최대 속도 모드: True
📈 멀티쓰레드 전송 완료:
   ✅ 총 전송: 1000000개
   🧵 사용된 쓰레드: 4개
   ⏱️  소요시간: 12.45초
   📊 평균 속도: 80321.28 로그/초
   📊 쓰레드당 평균: 250000 로그
```

## 주의사항

1. **네트워크 연결**: 대상 서버가 실행 중이고 접근 가능한지 확인하세요.
2. **포트 방화벽**: 514 UDP 포트가 열려있는지 확인하세요.
3. **대상 서버**: 로그를 받을 서버가 UDP Syslog 프로토콜을 지원하는지 확인하세요.
4. **네트워크 부하**: 대량 전송 시 네트워크 부하를 고려하여 적절한 간격을 설정하세요.
5. **UDP 특성**: UDP는 신뢰성이 보장되지 않으므로 패킷 손실이 발생할 수 있습니다.
6. **🆕 시스템 리소스**: 멀티쓰레드 모드 사용 시 CPU와 메모리 사용량이 증가합니다.
7. **🆕 쓰레드 수**: 시스템 성능에 따라 적절한 쓰레드 수를 설정하세요 (권장: CPU 코어 수의 2배).

## 문제 해결

### 연결 실패
```bash
# UDP 포트 연결 확인
nc -zu 192.168.203 514

# 또는
nmap -p 514 -sU 192.168.203
```

### 권한 문제
```bash
# 스크립트 실행 권한 확인
ls -la utm_log_sender.py

# 권한 부여
chmod +x utm_log_sender.py
```

### Python 버전 확인
```bash
python3 --version
```

### .env 파일 문제
```bash
# .env 파일이 없는 경우
python3 utm_log_sender.py --create-env

# .env 파일 권한 확인
ls -la .env

# .env 파일 내용 확인
cat .env
```

### python-dotenv 설치 문제
```bash
# 의존성 설치
pip install python-dotenv

# 또는
pip install -r requirements.txt
```

### 🆕 멀티쓰레드 성능 문제
```bash
# 시스템 리소스 확인
top
htop

# 네트워크 대역폭 확인
iftop
nethogs

# 적절한 쓰레드 수 설정 (CPU 코어 수 확인)
nproc
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.