"""
Created: 2026-06-13
Updated: 2026-06-13 15:44

yokosawa_range_check.md の各色グループのハンド一覧から、
13x13の手札テーブルと同じ形式で、該当ハンドに✅をつけたテーブルを生成する。
"""

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


# 各色グループのハンドリスト（yokosawa_range_check.mdから転記、注記は除く）
COLOR_GROUPS = {
    "グレー（中間グレー）": [
        "T2s", "A9o", "93s", "92s", "A8o", "T8o", "98o", "88", "83s", "82s", "A7o", "T7o", "97o", "87o", "77",
        "73s", "72s", "A6o", "T6o", "96o", "86o", "76o", "66", "62s", "T5o", "95o", "85o", "75o", "65o", "55",
        "52s", "T4o", "94o", "84o", "74o", "64o", "54o", "44", "42s", "T3o", "93o", "83o", "73o", "63o", "53o",
        "43o", "33", "32s", "82o", "72o", "62o", "52o", "42o", "32o",
    ],
    "グレー（薄め・白系）": [
        "AA", "KK", "KQs", "K6s", "K5s", "K3s", "K2s", "QQ", "Q6s", "Q5s", "QJo", "K9o", "Q9o", "T9o", "99",
        "98s", "96s", "J8o", "J7o", "75s", "64s", "K6o", "Q6o", "K5o", "K3o", "Q3o", "A2o", "K2o", "Q2o", "AKo",
        "KTo", "K8o", "K7o", "KJo", "QTo", "KQo", "K4o", "AQo",
    ],
    "青系（紺・濃い青）": ["AJs", "KJs", "KTs", "J9o", "22"],
    "赤": ["A9s", "A8s", "J9s", "T8s", "97s"],
    "黒系": ["ATs", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "A3o"],
    "緑": ["K8s", "K7s", "K4s", "JTs", "T7s", "65s", "54s", "JTo", "Q8s", "Q7s"],
    "茶・オレンジ": [
        "K9s", "JJ", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "Q9s", "76s",
    ],
    "ピンク（桃色）": [
        "J4s", "J3s", "J2s", "T5s", "T4s", "T3s", "94s", "88", "77", "T8o", "98o", "J6o", "T6o", "T7o",
        "63s", "53o", "43s", "J5o", "T5o", "J4o", "J3o", "J2o",
    ],
    "マゼンタ・紫": ["95s", "87s", "85s", "J5s"],
    "ダークグレー": ["J6s", "T2o", "92o"],
    "その他（要確認）": ["QJs", "QTs", "Q2s", "J8s", "J7s"],
}


def build_table(hands_set: set) -> str:
    header = "|       | " + " | ".join(f"{r:^3}" for r in RANKS) + " |"
    sep = "|-------|" + "|".join(["-----"] * 13) + "|"
    lines = [header, sep]
    for row in range(13):
        cells = []
        for col in range(13):
            label = hand_label(row, col)
            mark = label if label in hands_set else "-"
            cells.append(f"{mark:^3}")
        lines.append(f"| **{RANKS[row]}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "_tmp")
    out_path = os.path.join(out_dir, "color_tables.md")
    with open(out_path, "w", encoding="utf-8") as f:
        for name, hands in COLOR_GROUPS.items():
            f.write(f"## {name}\n\n")
            f.write(build_table(set(hands)))
            f.write("\n\n")
    print(f"出力完了: {out_path}")


if __name__ == "__main__":
    main()
