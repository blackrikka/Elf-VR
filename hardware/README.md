# 하드웨어: 헤드셋 셸

3D 프린트용 파라메트릭 셸 모델입니다. 현재 파일은 `shell/elf_shell.scad` 하나이며, OpenSCAD로 열어 파라미터를 바꾸거나 STL로 내보낼 수 있습니다.

## 파일

| 파일 | 설명 |
|------|------|
| `shell/elf_shell.scad` | 셸 본체 (박스형, 렌즈 구멍 2개, 패널 포켓, 코 절개부) |

## 파라미터

모든 단위는 mm입니다. 값은 `elf_shell.scad` 상단에서 수정합니다.

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `panel_w` | 122 | 패널 외곽 가로 길이 (실측 필요) |
| `panel_h` | 68 | 패널 외곽 세로 길이 (실측 필요) |
| `panel_t` | 8 | 패널 + 드라이버 보드 두께 |
| `clearance` | 0.6 | 패널 포켓 인쇄 공차 |
| `lens_d` | 44 | 렌즈 외경 |
| `lens_hole_extra` | 1.0 | 렌즈 구멍 여유 (구멍 직경 = `lens_d + lens_hole_extra`) |
| `lens_to_panel` | 45 | 렌즈 평면에서 패널 앞면까지 거리 (초점 거리에 맞춰 조정) |
| `ipd` | 63 | 두 렌즈 중심 간격 (IPD) |
| `wall` | 2.5 | 벽 두께 |
| `face_w` | 150 | 셸 전체 가로 길이 |
| `vertical_margin` | 14 | 상하 여유 (스트랩 공간) |
| `nose_w` | 34 | 코 절개부 가로 길이 |
| `nose_h` | 18 | 코 절개부 높이 (아랫면 기준) |
| `$fn` | 96 | 원형 해상도 (내보내기 시 높이면 정밀하지만 느려짐) |

파생 값(`shell_h`, `shell_d`, `lens_hole_d`)은 자동 계산되므로 직접 수정하지 않습니다.

### 좌표계

- X: 가로 (0 ~ `face_w`)
- Y: 세로 (0 = 셸 아랫면)
- Z: 깊이 (0 = 얼굴 쪽 면, 끝 = 뒤쪽 면)
- 렌즈 플레이트: Z 0 ~ `wall`
- 패널 앞면: Z = `wall + lens_to_panel`
- 패널은 뒤쪽 개구부로 삽입합니다.

## 렌더링 및 STL 내보내기

OpenSCAD CLI를 사용합니다. 설치되어 있지 않다면 먼저 설치하세요 (Debian/Ubuntu: `sudo apt install openscad`).

```bash
# 프로젝트 루트에서 실행
openscad -o hardware/shell/elf_shell.stl hardware/shell/elf_shell.scad
```

파라미터를 명령줄에서 바꿔 내보낼 수도 있습니다 (`-D` 옵션):

```bash
# IPD 65mm로 변경하여 내보내기
openscad -D 'ipd=65' -o /tmp/elf_shell_ipd65.stl hardware/shell/elf_shell.scad
```

> 생성된 `.stl` 파일은 `.gitignore`에 포함되어 있어 저장소에 커밋되지 않습니다.

구문 검사만 하려면 임시 파일로 내보내면 됩니다:

```bash
openscad -o "$(mktemp --suffix=.stl)" hardware/shell/elf_shell.scad
```

## 인쇄 참고

- 재료: PETG 또는 ASA (열 안정성이 필요하면 ASA 권장)
- 얼굴과 닿는 면에는 폼 패드를 부착합니다 (셸 자체 모델에는 포함되지 않음).
- 렌즈 구멍 직경과 패널 포켓 공차는 실측 후 조정하세요.
- 프린트 전 패널과 렌즈를 실제로 측정해 `panel_w`, `panel_h`, `lens_d`, `lens_to_panel`을 맞추는 것이 필수입니다.
