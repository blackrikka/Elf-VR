// ELF VR - parametric headset shell (Phase 0 prototype)
//
// 단순한 박스형 셸입니다. 앞면 플레이트에 렌즈 구멍 2개(IPD 간격), 뒤쪽에 패널 포켓,
// 아래쪽 가운데에 코 절개부가 있습니다. 패널은 뒤에서 삽입하며 렌즈 평면에서
// lens_to_panel 만큼 떨어진 곳의 선반(ledge)에 놓입니다.
//
// 좌표계 (mm):
//   X: 가로 (0 ~ face_w)
//   Y: 세로 (0 = 셸 아랫면)
//   Z: 깊이 (0 = 얼굴 쪽 면, depth = 뒤쪽 면)
//      렌즈 플레이트는 Z 0 ~ wall, 패널 앞면은 Z = wall + lens_to_panel.
//
// 렌더링/내보내기는 hardware/README.md 를 참고하세요.

/* [Display panel] */
// 패널 외곽 가로 길이 (실측 후 입력)
panel_w = 122;
// 패널 외곽 세로 길이
panel_h = 68;
// 패널 + 드라이버 보드 두께
panel_t = 8;
// 패널 포켓 여유 간격 (인쇄 공차)
clearance = 0.6;

/* [Optics] */
// 렌즈 외경
lens_d = 44;
// 렌즈 구멍 직경 (렌즈보다 약간 크게)
lens_hole_extra = 1.0;
// 렌즈 평면에서 패널 앞면까지 거리 (초점 거리에 맞춰 조정)
lens_to_panel = 45;
// 두 렌즈 중심 간격 (IPD)
ipd = 63;

/* [Shell] */
// 벽 두께
wall = 2.5;
// 셸 전체 가로 길이 (face width)
face_w = 150;
// 상하 여유 (스트랩 및 여백)
vertical_margin = 14;

/* [Nose cutout] */
// 코 절개부 가로 길이
nose_w = 34;
// 코 절개부 높이 (아랫면부터)
nose_h = 18;

/* [Render quality] */
$fn = 96;

// --- 파생 값 (직접 수정하지 마세요) ---
lens_hole_d = lens_d + lens_hole_extra;
shell_h = panel_h + 2 * wall + vertical_margin;
shell_d = wall + lens_to_panel + panel_t + wall;

// 설정값 확인용 출력
echo(str("ELF shell: ", face_w, " x ", shell_h, " x ", shell_d, " mm, IPD ", ipd, " mm"));

// 외곽 박스
module outer_body() {
    cube([face_w, shell_h, shell_d]);
}

// 렌즈 플레이트 뒤쪽 눈/광학 공간 (렌즈와 패널 사이)
module optical_cavity() {
    translate([wall, wall, wall])
        cube([face_w - 2 * wall, shell_h - 2 * wall, lens_to_panel + 0.01]);
}

// 패널 포켓: 패널 앞면 평면부터 뒤쪽 끝까지 뚫어 뒤에서 삽입
module panel_pocket() {
    pw = panel_w + 2 * clearance;
    ph = panel_h + 2 * clearance;
    translate([(face_w - pw) / 2, (shell_h - ph) / 2, wall + lens_to_panel])
        cube([pw, ph, shell_d]);
}

// 렌즈 구멍 2개, IPD 간격, 셸 세로 중앙
module lens_holes() {
    for (sx = [-1, 1])
        translate([face_w / 2 + sx * ipd / 2, shell_h / 2, -1])
            cylinder(d = lens_hole_d, h = wall + 2);
}

// 코 절개부: 아랫면 가운데, 앞면 플레이트만 관통
module nose_cutout() {
    translate([(face_w - nose_w) / 2, -1, -1])
        cube([nose_w, nose_h + 1, wall + 2]);
}

difference() {
    outer_body();
    optical_cavity();
    panel_pocket();
    lens_holes();
    nose_cutout();
}
