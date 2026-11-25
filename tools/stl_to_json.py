#!/usr/bin/env python3
"""STL(ASCII 또는 binary) 파일을 읽어 {"positions": [x,y,z, ...]} JSON을 출력합니다.

positions 는 삼각형당 정점 3개, 정점당 float 3개(평탄 배열)입니다.
표준 라이브러리만 사용합니다.

사용법:
    python3 tools/stl_to_json.py input.stl                # stdout 출력
    python3 tools/stl_to_json.py input.stl -o out.json    # 파일 저장
"""
import argparse
import json
import struct
import sys


def read_binary(data):
    n = struct.unpack_from("<I", data, 80)[0]
    positions = []
    off = 84
    for _ in range(n):
        # 법선(12바이트) 건너뛰고 정점 3개(36바이트) 읽기, 속성 2바이트 건너뜀
        vals = struct.unpack_from("<12f", data, off)
        positions.extend(vals[3:12])
        off += 50
    return positions


def read_ascii(text):
    positions = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == "vertex":
            positions.extend(float(v) for v in parts[1:4])
    return positions


def is_binary(data):
    # 바이너리 STL 은 헤더 84바이트 + 삼각형 수 * 50바이트 와 크기가 정확히 일치합니다.
    if len(data) < 84:
        return False
    n = struct.unpack_from("<I", data, 80)[0]
    return len(data) == 84 + 50 * n


def load_positions(path):
    with open(path, "rb") as f:
        data = f.read()
    if is_binary(data):
        return read_binary(data)
    return read_ascii(data.decode("utf-8", errors="replace"))


def main():
    ap = argparse.ArgumentParser(description="STL -> positions JSON")
    ap.add_argument("stl")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    positions = load_positions(args.stl)
    if len(positions) % 9 != 0 or not positions:
        sys.exit("오류: 삼각형 정점 데이터를 읽을 수 없습니다 (vertex 개수 불일치 또는 빈 파일)")

    text = json.dumps({"positions": positions})
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{len(positions) // 9} triangles -> {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
