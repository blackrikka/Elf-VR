# ELF VR 넷리스트 (가상 설계, r0)

> **가상 설계안 — 부품 호환성·핀 배치는 구매 전 데이터시트로 검증 필요.**
> 미검증 상태이며, 아래 표는 `elf_vr_viewer.html` 회로도(시트 A, 시트 B)와 동일한 연결만 담습니다.
> 스펙에 없는 전기적 연결은 추가하지 않았습니다. 단, 회로 성립에 필요한 GND 귀환 경로처럼
> 비고란에 "귀환(GND)"으로 표시한 항목만 예외입니다.

표기 규칙: `부품.핀`. 핀 번호가 정해지지 않은 항목은 `(핀 미정)`으로 적었습니다.

---

## 시트 A — Phase 0 (PC 연결)

| 넷 이름 | 출발 (부품.핀) | 도착 (부품.핀) | 비고 |
|---|---|---|---|
| HDMI_PC | PC.HDMI_OUT | DRV.HDMI_IN | HDMI 케이블 경유 (TMDS 데이터) |
| 5V_DRV | PC.USB-A#2 (5V) | DRV.5V_IN | 별도 USB 포트 또는 전원 허브 사용. 패널 보드 전류 1 A 이상 확인 |
| GND_DRV | PC.USB-A#2 (GND) | DRV.GND | 5V 공급과 함께 가는 귀환(GND) 경로 |
| MIPI_FPC | DRV.MIPI_OUT | LCD.MIPI_IN | FPC 케이블 |
| USB_FS | PC.USB-A#1 (D+/D-) | PICO.USB (micro-USB) | USB 2.0 Full Speed. VBUS/GND는 USB 표준 배선으로 여기서는 별도 넷으로 나열하지 않음 |
| 3V3 | PICO.pin36 (3V3 OUT) | BNO.VIN | BNO085 브레이크아웃 전원 |
| GND | PICO.pin38 (GND) | BNO.GND | 공통 GND |
| I2C_SDA | PICO.pin6 (GP4, I2C0 SDA) | BNO.SDA | I2C 400 kHz 가정. 4.7 kΩ 풀업 R1 (3V3 ↔ I2C_SDA). 브레이크아웃에 있으면 생략 |
| I2C_SCL | PICO.pin7 (GP5, I2C0 SCL) | BNO.SCL | 4.7 kΩ 풀업 R2 (3V3 ↔ I2C_SCL). 브레이크아웃에 있으면 생략 |
| IMU_INT | BNO.INT (H_INTN) | PICO.pin9 (GP6) | 인터럽트, BNO085 → Pico |
| IMU_RST | PICO.pin10 (GP7) | BNO.RST (NRST) | 리셋, Pico → BNO085 |
| BNO_PS0 | BNO.PS0 | GND | I2C 모드 선택 (PS0 = GND) |
| BNO_PS1 | BNO.PS1 | GND | I2C 모드 선택 (PS1 = GND) |
| BNO_ADR | BNO.ADR (SA0) | GND | I2C 주소 0x4A |
| R1 | 3V3 | I2C_SDA | 4.7 kΩ 풀업 |
| R2 | 3V3 | I2C_SCL | 4.7 kΩ 풀업 |

**I2C/BNO085 주의 (실측 후 결정):** I2C 400 kHz 한계와 BNO085 클럭 스트레칭 문제가 있으면 SPI 모드(PS0/PS1 = 3V3) 또는 UART-RVC로 전환합니다.

---

## 시트 B — Phase 1 (독립형, SBC)

IMU 모듈(Pico + BNO085)은 시안 A와 동일한 회로를 축약 블록으로 두고, USB로 SBC에 연결합니다.

### B-1. 전원 체인

| 넷 이름 | 출발 (부품.핀) | 도착 (부품.핀) | 비고 |
|---|---|---|---|
| BAT_B+ | BAT.B+ | BMS.B+ | 2S 셀 직렬 상단 (최대 8.4 V) |
| BAT_BMID | BAT.B-mid | BMS.B-mid | 셀 중간 탭 (밸런스) |
| BAT_B- | BAT.B- | BMS.B- | 셀 직렬 하단 |
| CHG+ | CHG_JACK.+ (DC 8.4 V) | BMS.P+ | 충전 경로. BMS 충전 입력 배선은 BMS 매뉴얼 확인 (P+/P- 공용 가정) |
| CHG- | CHG_JACK.- | BMS.P- | 위와 동일 (충전 경로) |
| PACK+ | BMS.P+ | SW1.1 | 방전 출력 (+) |
| SW_F1 | SW1.2 | F1.1 | 슬라이드 스위치 → 5 A 퓨즈 |
| VBAT_BUCK | F1.2 | BUCK.VIN+ | VIN 6–8.4 V |
| PWR_GND | BMS.P- | BUCK.VIN- | 귀환(GND). 명시 목록 외 항목이지만 회로 성립에 필요 |
| 5V_RAIL | BUCK.5V+ | SBC.pin2 (5V), SBC.pin4 (5V) | 5 V 공급. 보드별 전원 입력 확인 (Type-C 또는 40핀 헤더) |
| 5V_DRV_F2 | 5V_RAIL | F2.1 | 드라이버 보드 전용 퓨즈 |
| 5V_DRV | F2.2 | DRV.5V_IN | 1.5 A 퓨즈 F2 경유 |
| GND | BUCK.5V- | SBC.pin6 (GND), DRV.GND | 공통 GND (귀환) |

### B-2. 디스플레이 / 팬 / 영상

| 넷 이름 | 출발 (부품.핀) | 도착 (부품.핀) | 비고 |
|---|---|---|---|
| HDMI_SHORT | SBC.HDMI_OUT | DRV.HDMI_IN | 짧은 HDMI 케이블 |
| MIPI_FPC | DRV.MIPI_OUT | LCD.MIPI_IN | FPC 케이블 |
| FAN_5V | SBC.pin4 (5V, 헤더) | FAN.+ | 40 mm 팬 5 V, 헤더 5 V 경유 |
| FAN_GND | SBC.pin6 (GND, 헤더) | FAN.- | 헤더 GND 경유 |
| FAN_PWM (선택, 점선) | SBC.GPIO (핀 미정) | Q1.GATE | 로직 레벨 MOSFET 경유 PWM. 드레인/소스 배선은 미정 (스펙 미기재) |

### B-3. 데이터 / 센서 / 카메라 / 무선

| 넷 이름 | 출발 (부품.핀) | 도착 (부품.핀) | 비고 |
|---|---|---|---|
| USB_IMU | SBC.USB-A#1 | IMU.USB (micro-USB) | IMU 모듈 (Pico + BNO085, 시트 A와 동일) |
| CAM1_USB (Phase 2, 점선) | CAM1.USB | HUB.DN1 | OV9281 USB 글로벌 셔터 (모서리 1) |
| CAM2_USB (Phase 2, 점선) | CAM2.USB | HUB.DN2 | OV9281 USB 글로벌 셔터 (모서리 2) |
| CAM3_USB (Phase 2, 점선) | CAM3.USB | HUB.DN3 | OV9281 USB 글로벌 셔터 (모서리 3) |
| CAM4_USB (Phase 2, 점선) | CAM4.USB | HUB.DN4 | OV9281 USB 글로벌 셔터 (모서리 4) |
| HUB_UP (Phase 2, 점선) | HUB.UP | SBC.USB-A#2 | USB 허브 경유 |
| WIFI_LINK (점선) | SBC.ANT (Wi-Fi 6 / BT 5.0) | RTR.WLAN (PC + Wi-Fi 6 라우터) | 무선 스트리밍 (HEVC). **클라이언트 직접 개발 필요** |
| ETH | RTR.LAN | RTR.ETH (PC 유선 연결) | 라우터 ↔ PC 유선 이더넷 |

### 전력 콜아웃

- 전형적 소비 ≈ 3 A @ 5 V, 피크 ≈ 5 A @ 5 V
- 강압 컨버터 정격 6 A 선택 (피크 대비 여유)

---

## 전력 예산 (Power budget)

| 항목 | 전력 (W) | 비고 |
|---|---|---|
| Orange Pi 5B SBC | 8 – 12 | 부하에 따라 변동 |
| 패널 + 드라이버 보드 | 3 – 4 | |
| 팬 (40 mm) | 1 | |
| Pico + IMU | 0.3 | |
| **합계 (전형)** | **≈ 12 – 17** | 12.3 – 17.3 W 합산 |

| 배터리 항목 | 값 | 계산 |
|---|---|---|
| 셀 구성 | 2S 18650, 3000 mAh 2개 | |
| 공칭 에너지 | 22.2 Wh | 7.4 V × 3.0 Ah |
| 사용 가능 에너지 | ≈ 18 Wh | 22.2 × 0.9 (방전 심도) × 0.9 (효율 약 85–90%) ≈ 18.0 Wh |
| 런타임 (계산) | ≈ 1.0 – 1.5 h | 18 Wh ÷ 17.3 W ≈ 1.0 h, 18 Wh ÷ 12.3 W ≈ 1.5 h |
| 런타임 연장 | — | 런타임 연장은 3000 mAh 셀 → 더 큰 용량 셀 또는 3S 구성으로 검토 |

---

## 무게 추정 (Weight estimate)

| 구분 | 추정 (g) | 목표 (g) | 비고 |
|---|---|---|---|
| Phase 0 앞면 유닛 | 293 | 280 – 320 | 렌즈 30, 패널 50, 드라이버 20, FPC 3, Pico 2, BNO085 3, 폼 패드 20, 스트랩 25, 셸 80, PC 연결 케이블 45, 기타 15 |
| Phase 1 후면 팩 | 232 | ≈ 230 | SBC 45, 배터리 95, BMS 8, 벅 10, 팬 8, 하우징 35, 스위치·퓨즈·잭 6, 배선 10, 마운트 15 |
| 합계 (Phase 0 + 1) | 525 | ≤ 550 | Quest 3 참고치 ≈ 515 g |
| Phase 2 카메라 (앞면, 선택) | 20 | | OV9281 × 4 (3D 구상 기준), 개당 5 g |
| 합계 (Phase 0 + 1 + 2) | 545 | ≤ 550 | |

---

## 비용 추정 (USD, 대략치, 검증 필요)

| 구분 | 추정 (USD) | 목표 (USD) | 비고 |
|---|---|---|---|
| Phase 0 본체 (Pico 제외) | 115 | 95 – 135 | |
| Pico (RP2040) | 6 | 4 – 8 | Phase 0에 추가 |
| Phase 1 | 132 | 120 – 160 | 증분 |
| Phase 2 | 60 | 50 – 80 | OV9281 ×4, $50–80 (개당 $12–20) |

---

## 확인 필요 항목 (불일치 및 미정)

1. **BNO085 3D 배치:** 스펙 좌표(Pico 중심 y=80, BNO085 z=33)는 Pico와 체적이 겹침. 3D 구상도에서는 BNO085를 Pico 위(y ≈ 81.35)로 올려 겹침을 피함. 회로에는 영향 없음.
2. **팬 PWM 드레인/소스 배선:** 스펙에 없으므로 미정으로 둠.
3. **SBC 전원 핀:** Orange Pi 5B 입력(Type-C 또는 40핀 헤더)과 핀 배치는 보드 매뉴얼로 확인 필요.
4. **충전 경로:** 충전 잭을 BMS P+/P- 공용으로 가정. BMS 모델별 매뉴얼 확인 필요.
