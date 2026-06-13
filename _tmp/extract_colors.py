"""
Created: 2026-06-13
Updated: 2026-06-13 15:14

ヨコサワハンドレンジ表(image-36.png)の13x13グリッドから
各セルの代表色(RGB)とハンド表記を抽出するスクリプト。
セル内の複数ポイント（四隅寄り）をサンプリングし、
最頻色を背景色として採用することで文字ピクセルの影響を避ける。
"""

from PIL import Image
from collections import Counter
import os

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]


def hand_label(row: int, col: int) -> str:
    r1 = RANKS[row]
    r2 = RANKS[col]
    if row == col:
        return f"{r1}{r2}"
    elif row < col:
        return f"{r1}{r2}s"
    else:
        return f"{r2}{r1}o"


def quantize(rgb: tuple, step: int = 16) -> tuple:
    return tuple((c // step) * step for c in rgb)


def main():
    img_path = os.path.join(os.path.dirname(__file__), "..", "_materials", "image-36.png")
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    print(f"画像サイズ: {w}x{h}")

    cell_w = w / 13
    cell_h = h / 13

    # セル内の四隅寄り9点をサンプリング（文字は中央に集中するため避ける）
    offsets = [
        (0.12, 0.12), (0.5, 0.12), (0.88, 0.12),
        (0.12, 0.5), (0.88, 0.5),
        (0.12, 0.88), (0.5, 0.88), (0.88, 0.88),
    ]

    result = {}
    for row in range(13):
        for col in range(13):
            colors = []
            for ox, oy in offsets:
                px = int(cell_w * col + cell_w * ox)
                py = int(cell_h * row + cell_h * oy)
                rgb = img.getpixel((px, py))
                colors.append(quantize(rgb))
            most_common = Counter(colors).most_common(1)[0][0]
            label = hand_label(row, col)
            result[label] = most_common

    for label, rgb in result.items():
        print(f"{label}: {rgb}")


if __name__ == "__main__":
    main()
