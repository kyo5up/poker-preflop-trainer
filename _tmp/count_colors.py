"""
Created: 2026-06-13
Updated: 2026-06-13 15:48

image-36.png から169セルの背景色を抽出し、
量子化後の色の種類数と各色の出現数を集計する。
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


def quantize(rgb: tuple, step: int = 24) -> tuple:
    return tuple((c // step) * step for c in rgb)


def main():
    img_path = os.path.join(
        os.path.dirname(__file__), "..", "_materials", "image-36.png"
    )
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    print(f"画像サイズ: {w}x{h}")

    cell_w = w / 13
    cell_h = h / 13

    offsets = [
        (0.12, 0.12),
        (0.5, 0.12),
        (0.88, 0.12),
        (0.12, 0.5),
        (0.88, 0.5),
        (0.12, 0.88),
        (0.5, 0.88),
        (0.88, 0.88),
    ]

    cell_colors = {}
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
            cell_colors[label] = most_common

    color_counter = Counter(cell_colors.values())
    print(f"\n量子化(step=24)後のユニーク色数: {len(color_counter)}")
    print("\n色ごとの出現数（多い順）:")
    for rgb, count in color_counter.most_common():
        hands = [h for h, c in cell_colors.items() if c == rgb]
        print(f"  RGB{rgb}: {count}セル -> {', '.join(hands)}")


if __name__ == "__main__":
    main()
