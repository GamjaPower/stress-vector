#!/usr/bin/env python3
"""
UTM 로그 대량 전송 스크립트
192.168.203:514 포트로 UTM 로그를 대량으로 전송합니다.
"""

import socket
import time
import random
import json
from datetime import datetime, timedelta
import threading
from typing import List, Dict, Any
import argparse
import sys
import os
from pathlib import Path

# .env 파일 로드를 위한 dotenv import
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv가 없어도 .env 파일을 직접 읽을 수 있도록 구현
    def load_dotenv():
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    try:
        load_dotenv()
    except Exception:
        print("⚠️  .env 파일을 읽을 수 없습니다. 기본 설정을 사용합니다.")

class UTMLogSender:
    def __init__(self, target_host: str = None, target_port: int = None):
        # .env 파일에서 설정 로드
        self.target_host = target_host or os.getenv('TARGET_HOST', '192.168.203')
        self.target_port = target_port or int(os.getenv('TARGET_PORT', '514'))
        self.hostname = os.getenv('HOSTNAME', 'utm-sender')
        self.facility = os.getenv('FACILITY', 'local0')
        self.socket = None
        self.running = False
        
    def connect(self):
        """소켓 연결을 설정합니다."""
        try: 
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 소켓 버퍼 크기 증가 (더 많은 데이터 처리 가능)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # 1MB 송신 버퍼
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024)  # 1MB 수신 버퍼
            
            # UDP는 연결을 설정하지 않고 바로 사용 가능
            print(f"✅ UDP 소켓이 {self.target_host}:{self.target_port}로 설정되었습니다.")
            print(f"📊 소켓 버퍼 크기: 송신 {self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)} bytes, 수신 {self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)} bytes")
            return True
        except Exception as e:
            print(f"❌ UDP 소켓 생성 실패: {e}")
            return False
    
    def disconnect(self):
        """소켓 연결을 종료합니다."""
        if self.socket:
            self.socket.close()
            print("🔌 연결이 종료되었습니다.")
    
    def generate_utm_event(self) -> Dict[str, Any]:
        """UTM 이벤트를 생성합니다."""
        event_types = [
            "firewall_block", "firewall_allow", "ips_alert", "antivirus_scan",
            "web_filter", "email_filter", "vpn_connection", "vpn_disconnection",
            "user_login", "user_logout", "admin_action", "system_alert"
        ]
        
        threat_levels = ["low", "medium", "high", "critical"]
        protocols = ["TCP", "UDP", "HTTP", "HTTPS", "FTP", "SSH", "SMTP"]
        
        # 랜덤 IP 주소 생성
        source_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        dest_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": random.choice(event_types),
            "source_ip": source_ip,
            "destination_ip": dest_ip,
            "source_port": random.randint(1024, 65535),
            "destination_port": random.choice([80, 443, 22, 21, 25, 53, 3389]),
            "protocol": random.choice(protocols),
            "threat_level": random.choice(threat_levels),
            "action": random.choice(["block", "allow", "log", "alert"]),
            "user": f"user_{random.randint(1, 100)}",
            "session_id": f"sess_{random.randint(100000, 999999)}",
            "bytes_sent": random.randint(100, 1000000),
            "bytes_received": random.randint(100, 1000000),
            "message": f"UTM event: {random.choice(event_types)} from {source_ip} to {dest_ip}"
        }
        
        return event
    
    def generate_utm_event_batch(self, batch_size: int = 100) -> List[Dict[str, Any]]:
        """UTM 이벤트를 배치로 생성합니다."""
        events = []
        event_types = [
            "firewall_block", "firewall_allow", "ips_alert", "antivirus_scan",
            "web_filter", "email_filter", "vpn_connection", "vpn_disconnection",
            "user_login", "user_logout", "admin_action", "system_alert"
        ]
        
        threat_levels = ["low", "medium", "high", "critical"]
        protocols = ["TCP", "UDP", "HTTP", "HTTPS", "FTP", "SSH", "SMTP"]
        ports = [80, 443, 22, 21, 25, 53, 3389]
        
        # 현재 시간을 미리 생성 (성능 최적화)
        current_time = datetime.now().isoformat()
        
        for _ in range(batch_size):
            # 랜덤 IP 주소 생성 (최적화된 버전)
            source_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            dest_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            event_type = random.choice(event_types)
            
            event = {
                "timestamp": current_time,
                "event_type": event_type,
                "source_ip": source_ip,
                "destination_ip": dest_ip,
                "source_port": random.randint(1024, 65535),
                "destination_port": random.choice(ports),
                "protocol": random.choice(protocols),
                "threat_level": random.choice(threat_levels),
                "action": random.choice(["block", "allow", "log", "alert"]),
                "user": f"user_{random.randint(1, 100)}",
                "session_id": f"sess_{random.randint(100000, 999999)}",
                "bytes_sent": random.randint(100, 1000000),
                "bytes_received": random.randint(100, 1000000),
                "message": f"UTM event: {event_type} from {source_ip} to {dest_ip}"
            }
            events.append(event)
        
        return events

    def generate_utm_event_generator(self, batch_size: int = 100):
        """UTM 이벤트를 제너레이터로 생성합니다 (메모리 효율적)."""
        event_types = [
            "firewall_block", "firewall_allow", "ips_alert", "antivirus_scan",
            "web_filter", "email_filter", "vpn_connection", "vpn_disconnection",
            "user_login", "user_logout", "admin_action", "system_alert"
        ]
        
        threat_levels = ["low", "medium", "high", "critical"]
        protocols = ["TCP", "UDP", "HTTP", "HTTPS", "FTP", "SSH", "SMTP"]
        ports = [80, 443, 22, 21, 25, 53, 3389]
        
        # 현재 시간을 미리 생성 (성능 최적화)
        current_time = datetime.now().isoformat()
        
        for _ in range(batch_size):
            # 랜덤 IP 주소 생성 (최적화된 버전)
            source_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            dest_ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            event_type = random.choice(event_types)
            
            event = {
                "timestamp": current_time,
                "event_type": event_type,
                "source_ip": source_ip,
                "destination_ip": dest_ip,
                "source_port": random.randint(1024, 65535),
                "destination_port": random.choice(ports),
                "protocol": random.choice(protocols),
                "threat_level": random.choice(threat_levels),
                "action": random.choice(["block", "allow", "log", "alert"]),
                "user": f"user_{random.randint(1, 100)}",
                "session_id": f"sess_{random.randint(100000, 999999)}",
                "bytes_sent": random.randint(100, 1000000),
                "bytes_received": random.randint(100, 1000000),
                "message": f"UTM event: {event_type} from {source_ip} to {dest_ip}"
            }
            yield event

    def send_log(self, log_data: Dict[str, Any]) -> bool:
        """로그를 전송합니다."""
        try:
            # JSON 형식으로 직렬화
            log_message = json.dumps(log_data, ensure_ascii=False)
            
            # RFC3164 형식으로 포맷팅 (Syslog 표준)
            priority = random.randint(0, 191)  # facility * 8 + severity
            timestamp = datetime.now().strftime("%b %d %H:%M:%S")
            syslog_message = f"<{priority}>{timestamp} {self.hostname}: {log_message}\n"
            
            # UDP로 전송
            self.socket.sendto(syslog_message.encode('utf-8'), (self.target_host, self.target_port))
            return True
        except Exception as e:
            print(f"❌ 로그 전송 실패: {e}")
            return False
    
    def send_log_batch(self, log_batch: List[Dict[str, Any]]) -> int:
        """로그 배치를 전송합니다."""
        sent_count = 0
        try:
            # 현재 시간을 미리 생성 (성능 최적화)
            current_time = datetime.now().strftime("%b %d %H:%M:%S")
            
            for log_data in log_batch:
                # JSON 형식으로 직렬화
                log_message = json.dumps(log_data, ensure_ascii=False)
                
                # RFC3164 형식으로 포맷팅 (Syslog 표준)
                priority = random.randint(0, 191)  # facility * 8 + severity
                syslog_message = f"<{priority}>{current_time} {self.hostname}: {log_message}\n"
                
                # UDP로 전송
                self.socket.sendto(syslog_message.encode('utf-8'), (self.target_host, self.target_port))
                sent_count += 1
        except Exception as e:
            print(f"❌ 배치 로그 전송 실패: {e}")
        
        return sent_count
    
    def send_log_batch_generator(self, batch_size: int = 100) -> int:
        """제너레이터를 사용하여 로그 배치를 전송합니다 (메모리 효율적)."""
        sent_count = 0
        try:
            # 현재 시간을 미리 생성 (성능 최적화)
            current_time = datetime.now().strftime("%b %d %H:%M:%S")
            
            for log_data in self.generate_utm_event_generator(batch_size):
                # JSON 형식으로 직렬화
                log_message = json.dumps(log_data, ensure_ascii=False)
                
                # RFC3164 형식으로 포맷팅 (Syslog 표준)
                priority = random.randint(0, 191)  # facility * 8 + severity
                syslog_message = f"<{priority}>{current_time} {self.hostname}: {log_message}\n"
                
                # UDP로 전송
                self.socket.sendto(syslog_message.encode('utf-8'), (self.target_host, self.target_port))
                sent_count += 1
        except Exception as e:
            print(f"❌ 제너레이터 배치 로그 전송 실패: {e}")
        
        return sent_count
    
    def send_bulk_logs(self, count: int, delay: float = 0.1, increase_rate: float = 1.0, max_speed: bool = False):
        """대량의 로그를 전송합니다."""
        if not self.connect():
            return
        
        self.running = True
        sent_count = 0
        failed_count = 0
        
        if max_speed:
            print(f"🚀 {count}개의 UTM 로그를 {self.target_host}:{self.target_port}로 최대 속도로 전송을 시작합니다...")
            print(f"⚡ delay, increase_rate 옵션은 무시됩니다. (최대 속도)")
        else:
            print(f"🚀 {count}개의 UTM 로그를 {self.target_host}:{self.target_port}로 전송을 시작합니다...")
            print(f"⏱️  초기 로그 간격: {delay}초")
            if increase_rate > 1.0:
                print(f"📈 증가율: {increase_rate}배 (시간이 지날수록 전송량 증가)")
        
        start_time = time.time()
        last_log_time = start_time
        current_delay = delay
        
        try:
            if max_speed:
                # 최대 속도 모드: 제너레이터 배치 전송 사용 (메모리 효율적)
                batch_size = 50000  # 5만개로 증가 (기존 5000에서 10배 증가)
                for i in range(0, count, batch_size):
                    if not self.running:
                        break
                    current_batch_size = min(batch_size, count - i)
                    batch_sent = self.send_log_batch_generator(current_batch_size)
                    sent_count += batch_sent
                    failed_count += (current_batch_size - batch_sent)
                    
                    now = time.time()
                    elapsed = now - start_time
                    # 10초마다 로그 출력
                    if now - last_log_time >= 10:
                        speed = sent_count / elapsed if elapsed > 0 else 0
                        print(f"📊 {sent_count}개 로그 전송 완료 (평균 속도: {speed:.1f} 로그/초, 경과시간: {elapsed:.1f}초)")
                        last_log_time = now
            else:
                # 기존 방식: 개별 전송
                for i in range(count):
                    if not self.running:
                        break
                    log_event = self.generate_utm_event()
                    if self.send_log(log_event):
                        sent_count += 1
                        now = time.time()
                        elapsed = now - start_time
                        # 10초마다 로그 출력
                        if now - last_log_time >= 10:
                            speed = sent_count / elapsed if elapsed > 0 else 0
                            print(f"📊 {sent_count}개 로그 전송 완료 (평균 속도: {speed:.1f} 로그/초, 경과시간: {elapsed:.1f}초)")
                            last_log_time = now
                    else:
                        failed_count += 1
                    # 기존 방식: delay 및 increase_rate 적용
                    elapsed_time = time.time() - start_time
                    if increase_rate > 1.0:
                        current_delay = max(0.01, delay / (1 + (increase_rate - 1) * elapsed_time / 60))
                    time.sleep(current_delay)
        except KeyboardInterrupt:
            print("\n⏹️  사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.running = False
            self.disconnect()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📈 전송 완료:")
        print(f"   ✅ 성공: {sent_count}개")
        print(f"   ❌ 실패: {failed_count}개")
        print(f"   ⏱️  소요시간: {duration:.2f}초")
        print(f"   📊 평균 속도: {sent_count/duration:.2f} 로그/초")

    def continuous_sending(self, delay: float = 0.1, increase_rate: float = 1.0, max_speed: bool = False):
        """연속적으로 로그를 전송합니다."""
        if not self.connect():
            return
        
        self.running = True
        sent_count = 0
        
        if max_speed:
            print(f"🔄 {self.target_host}:{self.target_port}로 연속 최대 속도 로그 전송을 시작합니다...")
            print(f"⚡ delay, increase_rate 옵션은 무시됩니다. (최대 속도)")
        else:
            print(f"🔄 {self.target_host}:{self.target_port}로 연속 로그 전송을 시작합니다...")
            print(f"⏱️  초기 로그 간격: {delay}초")
            if increase_rate > 1.0:
                print(f"📈 증가율: {increase_rate}배 (시간이 지날수록 전송량 증가)")
        print("⏹️  중단하려면 Ctrl+C를 누르세요.")
        
        start_time = time.time()
        last_log_time = start_time
        current_delay = delay
        
        try:
            if max_speed:
                # 최대 속도 모드: 제너레이터 배치 전송 사용 (메모리 효율적)
                batch_size = 50000  # 5만개로 증가 (기존 5000에서 10배 증가)
                while self.running:
                    batch_sent = self.send_log_batch_generator(batch_size)
                    sent_count += batch_sent
                    
                    now = time.time()
                    elapsed = now - start_time
                    # 10초마다 로그 출력
                    if now - last_log_time >= 10:
                        speed = sent_count / elapsed if elapsed > 0 else 0
                        print(f"📊 {sent_count}개 로그 전송 완료 (평균 속도: {speed:.1f} 로그/초, 경과시간: {elapsed:.1f}초)")
                        last_log_time = now
            else:
                # 기존 방식: 개별 전송
                while self.running:
                    log_event = self.generate_utm_event()
                    if self.send_log(log_event):
                        sent_count += 1
                        now = time.time()
                        elapsed = now - start_time
                        # 10초마다 로그 출력
                        if now - last_log_time >= 10:
                            speed = sent_count / elapsed if elapsed > 0 else 0
                            print(f"📊 {sent_count}개 로그 전송 완료 (평균 속도: {speed:.1f} 로그/초, 경과시간: {elapsed:.1f}초)")
                            last_log_time = now
                    elapsed_time = time.time() - start_time
                    if increase_rate > 1.0:
                        current_delay = max(0.01, delay / (1 + (increase_rate - 1) * elapsed_time / 60))
                    time.sleep(current_delay)
        except KeyboardInterrupt:
            print("\n⏹️  사용자에 의해 중단되었습니다.")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        finally:
            self.running = False
            self.disconnect()
            print(f"📈 총 {sent_count}개 로그 전송 완료")

    def send_bulk_logs_multi_thread(self, count: int, thread_count: int = 4, max_speed: bool = True):
        """멀티쓰레드를 사용하여 대량의 로그를 전송합니다."""
        if thread_count <= 0:
            thread_count = 1
        
        print(f"🚀 {count}개의 UTM 로그를 {thread_count}개 쓰레드로 {self.target_host}:{self.target_port}에 전송을 시작합니다...")
        print(f"⚡ 최대 속도 모드: {max_speed}")
        
        # 쓰레드당 처리할 로그 개수
        logs_per_thread = count // thread_count
        remaining_logs = count % thread_count
        
        threads = []
        results = []
        
        def thread_worker(thread_id: int, log_count: int):
            """개별 쓰레드에서 실행되는 작업"""
            try:
                # 각 쓰레드마다 새로운 소켓 생성
                thread_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                thread_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
                
                sent_count = 0
                batch_size = 10000  # 쓰레드당 배치 크기
                
                for i in range(0, log_count, batch_size):
                    current_batch_size = min(batch_size, log_count - i)
                    
                    # 제너레이터로 이벤트 생성 및 전송
                    for _ in range(current_batch_size):
                        event = next(self.generate_utm_event_generator(1))
                        log_message = json.dumps(event, ensure_ascii=False)
                        priority = random.randint(0, 191)
                        timestamp = datetime.now().strftime("%b %d %H:%M:%S")
                        syslog_message = f"<{priority}>{timestamp} {self.hostname}-thread{thread_id}: {log_message}\n"
                        
                        thread_socket.sendto(syslog_message.encode('utf-8'), (self.target_host, self.target_port))
                        sent_count += 1
                
                thread_socket.close()
                return sent_count
                
            except Exception as e:
                print(f"❌ 쓰레드 {thread_id} 오류: {e}")
                return 0
        
        start_time = time.time()
        
        # 쓰레드 생성 및 시작
        for i in range(thread_count):
            thread_log_count = logs_per_thread + (1 if i < remaining_logs else 0)
            thread = threading.Thread(target=lambda: results.append(thread_worker(i+1, thread_log_count)))
            threads.append(thread)
            thread.start()
        
        # 모든 쓰레드 완료 대기
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        total_sent = sum(results)
        
        print(f"\n📈 멀티쓰레드 전송 완료:")
        print(f"   ✅ 총 전송: {total_sent}개")
        print(f"   🧵 사용된 쓰레드: {thread_count}개")
        print(f"   ⏱️  소요시간: {duration:.2f}초")
        print(f"   📊 평균 속도: {total_sent/duration:.2f} 로그/초")
        print(f"   📊 쓰레드당 평균: {total_sent/thread_count:.0f} 로그")

def create_env_file():
    """환경변수 설정 파일을 생성합니다."""
    env_content = """# UTM 로그 전송 설정
TARGET_HOST=192.168.203
TARGET_PORT=514

# 전송 설정
DEFAULT_LOG_COUNT=1000
DEFAULT_DELAY=0.1
DEFAULT_INCREASE_RATE=1.0

# 로그 설정
HOSTNAME=utm-sender
FACILITY=local0
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env 파일이 생성되었습니다. 설정을 확인하고 수정하세요.")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="UTM 로그 대량 전송 도구")
    parser.add_argument("--host", help="대상 호스트 IP (.env 파일의 TARGET_HOST보다 우선)")
    parser.add_argument("--port", type=int, help="대상 포트 (.env 파일의 TARGET_PORT보다 우선)")
    parser.add_argument("--count", type=int, help="전송할 로그 개수")
    parser.add_argument("--delay", type=float, help="로그 간격 (초)")
    parser.add_argument("--increase-rate", type=float, default=1.0, help="전송량 증가율 (기본값: 1.0, 증가 없음)")
    parser.add_argument("--continuous", action="store_true", help="연속 전송 모드")
    parser.add_argument("--max-speed", action="store_true", help="최대 속도로 전송 (delay/increase-rate 무시)")
    parser.add_argument("--multi-thread", action="store_true", help="멀티쓰레드 모드 사용")
    parser.add_argument("--threads", type=int, default=4, help="멀티쓰레드 모드에서 사용할 쓰레드 수 (기본값: 4)")
    parser.add_argument("--create-env", action="store_true", help=".env 파일 생성")
    
    args = parser.parse_args()
    
    # .env 파일 생성 옵션
    if args.create_env:
        create_env_file()
        return
    
    # 기본값을 .env 파일에서 가져오기
    default_count = int(os.getenv('DEFAULT_LOG_COUNT', '1000'))
    default_delay = float(os.getenv('DEFAULT_DELAY', '0.1'))
    default_increase_rate = float(os.getenv('DEFAULT_INCREASE_RATE', '1.0'))
    
    # 명령행 인수가 없으면 .env 파일의 기본값 사용
    count = args.count or default_count
    delay = args.delay or default_delay
    increase_rate = args.increase_rate if args.increase_rate != 1.0 else default_increase_rate
    
    sender = UTMLogSender(args.host, args.port)
    
    try:
        if args.multi_thread:
            # 멀티쓰레드 모드
            sender.send_bulk_logs_multi_thread(count, args.threads, args.max_speed)
        elif args.continuous:
            sender.continuous_sending(delay, increase_rate, args.max_speed)
        else:
            sender.send_bulk_logs(count, delay, increase_rate, args.max_speed)
    except KeyboardInterrupt:
        print("\n👋 프로그램을 종료합니다.")
        sys.exit(0)

if __name__ == "__main__":
    main() 