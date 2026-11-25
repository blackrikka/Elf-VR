# ELF VR

저가형 경량 VR 헤드셋 프로젝트입니다. 3D 프린트 셸과 Linux 기반 OS를 사용하며, PC에 연결하는 방식(tethered)과 단독 실행(standalone) 방식을 모두 지원하는 것을 목표로 합니다. 예산을 최소화하는 것이 핵심 설계 제약입니다.

## 목표

저렴한 LCD 패널, 범용 렌즈, 저가 IMU 브레이크아웃 보드를 조합해 3DoF(머리 회전 추적) VR 경험을 먼저 구현합니다. 1단계(Phase 0)는 PC에 유선으로 연결하는 프로토타입으로, 총 예산 상한은 약 $120입니다. 이후 단계에서 SBC 기반 단독 실행(Phase 1)과 글로벌 셔터 카메라 기반 6DoF(Phase 2)로 확장합니다.

## 단계별 로드맵

| 단계 | 내용 | 추정 비용 (USD) | 추적 자유도 | 핵심 구성 |
|------|------|-----------------|-------------|-----------|
| Phase 0 | PC 유선 연결 프로토타입 | $80 - $120 | 3DoF | 5.5-6" 1440p LCD, 렌즈, IMU, PETG/ASA 셸 |
| Phase 1 | 단독 실행 (RK3588 SBC) | $230 - $270 (누적) | 3DoF | Phase 0 + RK3588 SBC, 배터리, 방열 |
| Phase 2 | 6DoF (SLAM) | +$60 - $80 | 6DoF | Phase 1 + 글로벌 셔터 카메라 2-4개, Monado SLAM |

비용은 대략적인 추정치이며, 구매 전 실제 가격을 확인해야 합니다. 자세한 내역은 [docs/BOM.md](docs/BOM.md)를 참고하세요.

## 저장소 구조

```
Elf-VR/
├── README.md                  # 이 문서
├── docs/
│   ├── BOM.md                 # 부품 목록 (단계별 비용)
│   ├── ARCHITECTURE.md        # 소프트웨어/하드웨어 아키텍처
│   └── VERIFICATION.md        # Phase 0 인수 체크리스트
├── hardware/
│   ├── README.md              # 셸 파라미터, STL 내보내기 방법
│   └── shell/
│       └── elf_shell.scad    # 파라메트릭 OpenSCAD 헤드셋 셸
├── firmware/
│   └── imu/
│       ├── README.md          # IMU 리더 사용법
│       └── read_imu.py        # IMU 읽기 스크립트 (시뮬레이션 모드 포함)
├── os/
│   └── README.md              # OS 이미지 빌드 계획 (TODO)
└── .gitignore
```

## 개발 역할 분담

- 기획 및 검증(planning/verification): Sonnet 5.5
- 구현(implementation): Haiku 5.5

## 빠른 시작

셸 파라미터 확인 및 STL 생성은 [hardware/README.md](hardware/README.md)를, IMU 시뮬레이션 실행은 [firmware/imu/README.md](firmware/imu/README.md)를 참고하세요.

```bash
python3 firmware/imu/read_imu.py --simulate --seconds 2
```

## 라이선스

미정.
