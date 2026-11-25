# OS 이미지 빌드 계획

Phase 1 단독 실행용 OS 이미지를 만드는 계획입니다. Phase 0은 PC에서 Monado를 실행하므로 이 이미지가 필요하지 않습니다. 아래는 TODO 목록이며 스크립트는 아직 없습니다.

## 기반

- [ ] Armbian 베이스 이미지 선택 (RK3588 보드 지원 버전 확인: Orange Pi 5 또는 Rock 5)
- [ ] Debian 기반 최소 설치로 대체 가능한지 검토 (이미지 크기 및 부팅 시간 비교)
- [ ] 부팅 시 자동 로그인 및 전용 서비스 계정 설정

## 패키지

- [ ] `monado` (OpenXR 런타임) 설치 가능 여부 확인 (Armbian/Debian 패키지 또는 소스 빌드)
- [ ] `libopenxr` (OpenXR 로더) 설치
- [ ] Vulkan 드라이버 (RK3588 Mali GPU용 Panfrost 또는 Mali 블롭) 준비
- [ ] IMU 드라이버 및 I2C 도구 (`i2c-tools`)
- [ ] 디스플레이 DRM 도구 (`libdrm`, `modetest`) 및 DRM lease 동작 확인
- [ ] 개발용 도구 (`git`, `python3`, `cmake`)

## 디스플레이 및 센서

- [ ] 패널 디바이스 트리 오버레이 작성 (DSI 또는 eDP 설정)
- [ ] Monado 렌즈 왜곡 프로파일 작성 (렌즈 직경, 거리 값 반영)
- [ ] IMU 디바이스 트리 노드 추가 (I2C 주소, 인터럽트 핀)

## 전원 및 시스템

- [ ] 배터리 잔량 확인 및 저전력 상태 처리
- [ ] 팬 제어 (온도 기준 속도 조절)
- [ ] 읽기 전용 루트 파일 시스템 검토 (SD 카드 보호)

## 빌드 자동화

- [ ] 이미지 빌드 스크립트 작성 (Armbian build framework 활용 검토)
- [ ] CI에서 이미지 빌드 검증 (구성 파일 기준)
- [ ] 이미지 체크섬 생성 및 배포 방식 결정

## 미정

- 단독 실행 시 PC 스트리밍 기능 포함 여부 (무선 스트리밍은 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) 참고)
- 업데이트 방식 (OTA 또는 SD 재설치)
