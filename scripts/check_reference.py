#!/usr/bin/env python3
"""Validate the local high-resolution character reference without Pillow."""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_SHA256 = "a8699cd228353110c0ddc16b0d46721143400d6d5008273a24f03c340eacfb4b"
EXPECTED_SIZE = (1254, 1254)
EXPECTED_COLOR_TYPE = 6  # RGBA truecolour with alpha


def read_png_ihdr(path: Path) -> tuple[int, int, int, int]:
    with path.open("rb") as stream:
        signature = stream.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("文件不是有效 PNG（签名不匹配）")

        length_raw = stream.read(4)
        chunk_type = stream.read(4)
        if len(length_raw) != 4 or chunk_type != b"IHDR":
            raise ValueError("PNG 缺少首个 IHDR 块")

        length = struct.unpack(">I", length_raw)[0]
        if length != 13:
            raise ValueError(f"IHDR 长度异常：{length}")

        payload = stream.read(length)
        if len(payload) != length:
            raise ValueError("IHDR 数据不完整")

        width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", payload)
        return width, height, bit_depth, color_type


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="校验本地 Q 版角色主参考图")
    parser.add_argument(
        "path",
        nargs="?",
        default="assets/reference/local/character_reference_source.png",
        help="主参考图路径",
    )
    parser.add_argument(
        "--allow-different-hash",
        action="store_true",
        help="仅检查 PNG 结构和尺寸，不强制与登记源文件哈希相同",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"[FAIL] 未找到主参考图：{path}", file=sys.stderr)
        print("请阅读 assets/reference/README.md。", file=sys.stderr)
        return 2

    try:
        width, height, bit_depth, color_type = read_png_ihdr(path)
    except (OSError, ValueError, struct.error) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 3

    errors: list[str] = []
    if (width, height) != EXPECTED_SIZE:
        errors.append(f"尺寸应为 {EXPECTED_SIZE[0]}×{EXPECTED_SIZE[1]}，实际为 {width}×{height}")
    if bit_depth != 8:
        errors.append(f"位深应为 8，实际为 {bit_depth}")
    if color_type != EXPECTED_COLOR_TYPE:
        errors.append(f"PNG color type 应为 6（RGBA），实际为 {color_type}")

    actual_hash = sha256_file(path)
    if not args.allow_different_hash and actual_hash != EXPECTED_SHA256:
        errors.append(
            "SHA-256 与登记的原始主图不一致：\n"
            f"  expected: {EXPECTED_SHA256}\n"
            f"  actual:   {actual_hash}"
        )

    if errors:
        print("[FAIL] 主参考图校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("[OK] 主参考图校验通过")
    print(f"path: {path}")
    print(f"size: {width}x{height}")
    print(f"bit_depth: {bit_depth}")
    print(f"color_type: {color_type} (RGBA)")
    print(f"sha256: {actual_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
