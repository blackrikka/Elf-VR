# IMU 리더 (`read_imu.py`)

BNO085 계열 IMU의 방향 쿼터니언을 읽고 실제 출력 주기를 측정하는 스크립트입니다. 하드웨어가 아직 없어도 `--simulate` 모드로 동작을 확인할 수 있습니다. 외부 패키지는 필요하지 않습니다 (Python 3.8 이상, 표준 라이브러리만 사용).

## 백엔드

| 백엔드 | 옵션 | 상태 | 설명 |
|--------|------|------|------|
| `sim` | `--simulate` 또는 `--backend sim` | 동작 | 가짜 쿼터니언을 `--rate` Hz로 생성 |
| `serial` | `--backend serial --port /dev/ttyACM0` | 동작 (인터페이스 기준) | `w,x,y,z` 형식 텍스트 줄을 읽는 장치 (MCU 브리지 등) |
| `bno085` | `--backend bno085` | **미구현** | I2C SHTP 드라이버 자리 표시자, 호출 시 안내 메시지와 함께 종료 코드 2 |

## 사용법

```bash
# 가짜 데이터, 2초 측정 (기본 목표 500Hz)
python3 firmware/imu/read_imu.py --simulate --seconds 2

# 목표 주기 변경 및 주기 기준 검사 (미달 시 종료 코드 1)
python3 firmware/imu/read_imu.py --simulate --rate 500 --seconds 10 --expect-hz 500

# 시리얼 브리지에서 읽기
stty -F /dev/ttyACM0 115200 raw -echo
python3 firmware/imu/read_imu.py --backend serial --port /dev/ttyACM0 --seconds 5
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--simulate` | 꺼짐 | `--backend sim`과 동일 |
| `--backend` | 없음 (필수 지정) | `sim`, `serial`, `bno085` 중 하나 |
| `--rate` | 500 | `sim` 백엔드의 목표 출력 주기 (Hz) |
| `--seconds` | 5 | 측정 시간 (초) |
| `--report-every` | 1.0 | 진행 상황 출력 간격 (초) |
| `--port` | `/dev/ttyACM0` | `serial` 백엔드 장치 경로 |
| `--expect-hz` | 0 | 0이 아니면 측정 주기가 이 값보다 낮을 때 종료 코드 1 |

### 출력 예

```
t=  1.00s  rate= 500.0 Hz  q=(+0.9...., +0.0..., ...)
요약: 샘플 ..., 측정 주기 ... Hz, 최대 간격 ... ms (백엔드: sim)
```

## 구조

- `Sample`: 타임스탬프(`t`)와 쿼터니언(`quat`)을 담는 데이터 클래스
- `ImuBackend`: 백엔드 인터페이스 (`samples()`, `close()`)
- `SimBackend`, `SerialBackend`, `Bno085I2cBackend`: 구현체
- `measure()`: 주기 및 최대 샘플 간격 측정
- 새 센서를 추가하려면 `ImuBackend`를 상속해 `samples()`가 `Sample`을 yield하도록 구현하고 `build_backend()`에 등록합니다.

## 알려진 제한

- `bno085` 백엔드는 아직 없습니다. 실제 BNO085는 SHTP 프로토콜로 통신하므로 I2C 드라이버 작성이 필요합니다.
- `serial` 백엔드는 장치 줄 단위로 읽으며, 데이터가 오지 않으면 `--seconds` 제한과 무관하게 대기합니다 (Ctrl-C로 중단).
- `sim` 모드의 주기 정확도는 Python `time.sleep` 정밀도에 따라 달라집니다. 실제 IMU 주기 검증은 하드웨어로 수행해야 합니다 ([docs/VERIFICATION.md](../../docs/VERIFICATION.md) 참고).
