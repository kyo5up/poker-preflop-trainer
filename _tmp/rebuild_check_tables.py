"""
Created: 2026-06-13
Updated: 2026-06-13 16:55

yokosawa_range_check.md の各色グループについて、
ユーザーが手作業で@マークをつけたフル手札テーブルから、
@がついたセルのみハンド名を残し、他を-にした13x13テーブルを再生成する。
セクション9（グレー）は、1-8で@マークされていないハンド全部を埋める。
"""

import os
import re

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


def parse_at_marked_table(table_lines: list) -> set:
    """テーブルの行から@がついているセルのハンド名集合を返す。
    - セルが「-」+@ の場合: そのセルの行・列からハンド名を算出して追加
    - セルがハンド名+@ の場合: そのハンド名をそのまま追加
    """
    hands = set()
    row_idx = -1
    for line in table_lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        if "---" in line or line.startswith("|       |"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        row_idx += 1
        # cells[0] はランク行ラベル（**A**など）
        for col_idx, cell in enumerate(cells[1:]):
            if "@" in cell:
                content = cell.replace("@", "").strip()
                if content == "-":
                    hands.add(hand_label(row_idx, col_idx))
                elif content:
                    hands.add(content)
    return hands


def main():
    md_path = os.path.join(
        os.path.dirname(__file__), "..", "_materials", "yokosawa_range_check.md"
    )
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    # 各セクションの@付きテーブルからハンドを抽出
    section_hands = {}
    current_section = None
    table_buffer = []
    in_table = False

    for line in lines:
        m = re.match(r"^## (\d+)\.", line)
        if m:
            if current_section is not None and table_buffer:
                section_hands[current_section] = parse_at_marked_table(table_buffer)
            current_section = int(m.group(1))
            table_buffer = []
            in_table = False
            continue
        stripped = line.strip()
        if stripped.startswith("|"):
            table_buffer.append(line)
            in_table = True
        elif in_table and not stripped.startswith("|"):
            # テーブルブロック終了。ただし最初に見つかったテーブルのみ使う
            if (
                current_section is not None
                and current_section not in section_hands
                and table_buffer
            ):
                section_hands[current_section] = parse_at_marked_table(table_buffer)
            in_table = False
            table_buffer = []

    if (
        current_section is not None
        and current_section not in section_hands
        and table_buffer
    ):
        section_hands[current_section] = parse_at_marked_table(table_buffer)

    print("=== 抽出結果 ===")
    for sec in sorted(section_hands):
        print(f"セクション{sec}: {sorted(section_hands[sec])}")

    # セクション9（グレー）: 1-8で使われたハンド以外の全ハンドを割り当て
    all_hands = {hand_label(r, c) for r in range(13) for c in range(13)}
    used = set()
    for sec in range(1, 9):
        used |= section_hands.get(sec, set())
    section_hands[9] = all_hands - used

    out_path = os.path.join(os.path.dirname(__file__), "rebuilt_tables.md")
    with open(out_path, "w", encoding="utf-8") as f:
        for sec in sorted(section_hands):
            f.write(f"### セクション{sec}\n\n")
            f.write(build_table(section_hands[sec]))
            f.write("\n\n")

    print(f"\n出力完了: {out_path}")


if __name__ == "__main__":
    main()
