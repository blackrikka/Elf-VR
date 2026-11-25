#!/usr/bin/env python3
"""ELF VR IMU 리더 (Phase 0 스캐폴드).

BNO085 계열 IMU에서 방향 쿼터니언(w, x, y, z)을 읽고 실제 출력 주기(Hz)를 측정합니다.
백엔드는 교체 가능하도록 구성되어 있습니다.

백엔드:
  sim     : 가짜 쿼터니언 스트림 (--rate Hz). 하드웨어 불필요, 외부 패키지 불필요.
  serial  : "w,x,y,z" 형식의 텍스트 줄을 보내는 장치 (예: MCU 브리지, /dev/ttyACM0).
            표준 라이브러리만 사용. 보드레이트는 미리 stty로 설정해야 합니다.
  bno085  : I2C(SHTP) 직접 드라이버. 아직 구현되지 않음 (자리 표시자).

사용 예:
  python3 read_imu.py --simulate --seconds 2
  python3 read_imu.py --simulate --rate 500 --seconds 10 --expect-hz 500
  python3 read_imu.py --backend serial --port /dev/ttyACM0 --seconds 5
"""

import argparse
import math
import sys
import time
from dataclasses import dataclass
from typing import Iterator, Optional, Tuple

Quat = Tuple[float, float, float, float]  # (w, x, y, z)


@dataclass
class Sample:
    t: float    # 단조 증가 타임스탬프 (time.monotonic 기준, 초)
    quat: Quat  # 방향 쿼터니언


class ImuBackend:
    """모든 백엔드가 구현해야 하는 인터페이스."""

    name = "base"

    def samples(self) -> Iterator[Sample]:
        raise NotImplementedError

    def close(self) -> None:
        pass


def euler_to_quat(yaw: float, pitch: float, roll: float) -> Quat:
    """ZYX 오일러 각(라디안)을 쿼터니언 (w, x, y, z)으로 변환."""
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cr, sr = math.cos(roll * 0.5), math.sin(roll * 0.5)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return (w, x, y, z)


class SimBackend(ImuBackend):
    """가짜 헤드 움직임 데이터를 목표 주기로 생성한다."""

    name = "sim"

    def __init__(self, rate_hz: float, seconds: float):
        if rate_hz <= 0:
            raise ValueError("rate_hz must be positive")
        self.rate_hz = rate_hz
        self.seconds = seconds

    def samples(self) -> Iterator[Sample]:
        period = 1.0 / self.rate_hz
        start = time.monotonic()
        next_t = start
        while True:
            now = time.monotonic()
            elapsed = now - start
            if elapsed >= self.seconds:
                return
            # 느린 머리 움직임: 요 ±30도 (0.25Hz), 피치 ±10도 (0.1Hz)
            yaw = math.radians(30.0) * math.sin(2 * math.pi * 0.25 * elapsed)
            pitch = math.radians(10.0) * math.sin(2 * math.pi * 0.10 * elapsed)
            yield Sample(t=now, quat=euler_to_quat(yaw, pitch, 0.0))

            # 목표 주기 유지: 다음 시각까지 대기, 뒤처지면 재동기화
            next_t += period
            delay = next_t - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                next_t = time.monotonic()


class SerialBackend(ImuBackend):
    """장치 파일에서 'w,x,y,z' 텍스트 줄을 읽는다 (표준 라이브러리만 사용)."""

    name = "serial"

    def __init__(self, port: str):
        self.port = port
        self._f = open(port, "r", encoding="ascii", errors="ignore")

    def samples(self) -> Iterator[Sample]:
        for line in self._f:
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue
            try:
                quat = tuple(float(p) for p in parts)
            except ValueError:
                continue
            yield Sample(t=time.monotonic(), quat=quat)  # type: ignore[arg-type]

    def close(self) -> None:
        self._f.close()


class Bno085I2cBackend(ImuBackend):
    """BNO085 I2C(SHTP) 드라이버 자리 표시자. 아직 구현되지 않았다."""

    name = "bno085"

    def __init__(self, bus: int = 1, addr: int = 0x4A):
        raise NotImplementedError(
            "BNO085 I2C/SHTP 드라이버는 아직 구현되지 않았습니다. "
            "--simulate 또는 --backend serial 을 사용하세요."
        )


def format_quat(q: Quat) -> str:
    return "(" + ", ".join(f"{v:+.4f}" for v in q) + ")"


def measure(backend: ImuBackend, seconds: float, report_every: float):
    """샘플을 읽으며 주기를 측정하고 진행 상황을 출력한다.

    반환: (샘플 수, 측정 주기 Hz, 최대 샘플 간격 ms)
    """
    t_first: Optional[float] = None
    t_prev: Optional[float] = None
    win_start: Optional[float] = None
    win_count = 0
    count = 0
    max_dt = 0.0
    last_q: Optional[Quat] = None

    try:
        for s in backend.samples():
            if t_first is None:
                t_first = win_start = s.t
            else:
                max_dt = max(max_dt, s.t - t_prev)  # type: ignore[operator]
            t_prev = s.t
            count += 1
            win_count += 1
            last_q = s.quat

            window = s.t - win_start  # type: ignore[operator]
            if window >= report_every:
                rate = win_count / window
                print(f"t={s.t - t_first:6.2f}s  rate={rate:7.1f} Hz  q={format_quat(s.quat)}")
                win_start = s.t
                win_count = 0

            if s.t - t_first >= seconds:  # type: ignore[operator]
                break
    except KeyboardInterrupt:
        print("\n중단됨 (Ctrl-C)")
    finally:
        backend.close()

    if count < 2 or t_first is None or t_prev is None:
        return count, 0.0, max_dt * 1000.0

    duration = t_prev - t_first
    measured_hz = (count - 1) / duration if duration > 0 else 0.0
    if last_q is not None:
        print(f"마지막 쿼터니언: {format_quat(last_q)}")
    return count, measured_hz, max_dt * 1000.0


def build_backend(args: argparse.Namespace) -> ImuBackend:
    if args.backend == "sim":
        return SimBackend(rate_hz=args.rate, seconds=args.seconds)
    if args.backend == "serial":
        return SerialBackend(args.port)
    if args.backend == "bno085":
        return Bno085I2cBackend()
    raise ValueError(f"unknown backend: {args.backend}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ELF VR IMU 리더 및 주기 측정")
    parser.add_argument("--simulate", action="store_true",
                        help="가짜 데이터 사용 (--backend sim 과 동일)")
    parser.add_argument("--backend", choices=["sim", "serial", "bno085"],
                        help="데이터 소스 백엔드")
    parser.add_argument("--rate", type=float, default=500.0,
                        help="sim 백엔드의 목표 출력 주기 (Hz, 기본 500)")
    parser.add_argument("--seconds", type=float, default=5.0,
                        help="측정 시간 (초, 기본 5)")
    parser.add_argument("--report-every", type=float, default=1.0,
                        help="진행 상황 출력 간격 (초, 기본 1)")
    parser.add_argument("--port", default="/dev/ttyACM0",
                        help="serial 백엔드 장치 경로 (기본 /dev/ttyACM0)")
    parser.add_argument("--expect-hz", type=float, default=0.0,
                        help="측정 주기가 이 값보다 낮으면 종료 코드 1 반환 (0이면 검사 안 함)")
    args = parser.parse_args(argv)

    if args.simulate:
        args.backend = "sim"
    if args.backend is None:
        parser.error("--simulate 또는 --backend 중 하나를 지정하세요")

    try:
        backend = build_backend(args)
    except NotImplementedError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"오류: 장치를 열 수 없습니다: {exc}", file=sys.stderr)
        return 2

    count, hz, max_dt_ms = measure(backend, args.seconds, args.report_every)
    print(f"요약: 샘플 {count}개, 측정 주기 {hz:.1f} Hz, 최대 간격 {max_dt_ms:.2f} ms "
          f"(백엔드: {backend.name})")

    if args.expect_hz and hz < args.expect_hz:
        print(f"실패: 측정 주기 {hz:.1f} Hz < 기대값 {args.expect_hz:.1f} Hz", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
