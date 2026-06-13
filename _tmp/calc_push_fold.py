"""
Created: 2026-06-13
Updated: 2026-06-13 15:06

ヘッズアップ Push/Fold Nash均衡レンジ計算スクリプト
- チップEVベース（ICMなし）の簡易Nash均衡計算
- スタック深度 5bb〜20bb（1bb刻み）でSB(プッシュ側)とBB(コール側)のレンジを計算
- 169ハンド（スーテッド/オフスート/ペア）の勝率テーブルはpreflop equity近似値を使用
"""

import json
import os

# 169ハンドの並び順（強い順）と、ヘッズアップ全レンジ対戦時の各ハンドの推定エクイティ
# 簡易近似: 標準的なHU equityチャートをベースにしたランキング値（0.0〜1.0でランダムハンドに対する強さの近似指数）
HAND_RANK = [
    "AA", "KK", "QQ", "JJ", "AKs", "TT", "AQs", "AJs", "AKo", "ATs",
    "99", "AQo", "KQs", "A9s", "88", "KJs", "ATo", "A8s", "QJs", "KQo",
    "77", "A7s", "KTs", "A9o", "QTs", "K9s", "JTs", "A6s", "66", "A8o",
    "KJo", "Q9s", "A5s", "J9s", "QJo", "55", "K8s", "A7o", "T9s", "A4s",
    "K9o", "Q8s", "KTo", "A3s", "J8s", "44", "A6o", "K7s", "QTo", "T8s",
    "98s", "A2s", "Q9o", "33", "K6s", "J9o", "A5o", "K5s", "97s", "T9o",
    "22", "K8o", "Q7s", "A4o", "87s", "K4s", "J8o", "98o", "Q6s", "T7s",
    "A3o", "K7o", "K3s", "76s", "Q8o", "97o", "J7s", "K6o", "A2o", "K2s",
    "Q5s", "86s", "T8o", "87o", "J6s", "Q4s", "K5o", "65s", "T6s", "76o",
    "Q3s", "J5s", "K4o", "Q7o", "96s", "75s", "54s", "J7o", "K3o", "Q2s",
    "T7o", "85s", "J4s", "64s", "T5s", "K2o", "Q6o", "96o", "53s", "J3s",
    "86o", "Q5o", "43s", "T4s", "J2s", "65o", "75o", "95s", "84s", "Q4o",
    "T3s", "54o", "J6o", "T6o", "Q3o", "74s", "94s", "63s", "T2s", "85o",
    "J5o", "52s", "Q2o", "93s", "64o", "42s", "J4o", "T4o", "83s", "53o",
    "73s", "J3o", "92s", "43o", "62s", "T3o", "82s", "J2o", "95o", "T2o",
    "84o", "32s", "94o", "72s", "63o", "93o", "52o", "74o", "62o", "92o",
    "42o", "82o", "32o", "72o",
]


def push_fold_threshold(stack_bb: float) -> tuple[float, float]:
    """
    スタック深度(bb)から、SBプッシュレンジ・BBコールレンジの
    169ハンド中の上位何ハンドを含めるかを返す（近似式）。

    Nash均衡の厳密解ではなく、一般に知られているHU Push/Foldの
    傾向（スタックが浅いほどプッシュ/コールレンジが広がる）を
    線形近似でモデル化したもの。
    戻り値: (push_count, call_count) 169ハンド中の採用数
    """
    # スタックが浅いほどレンジが広がる（最大169=オールハンド）
    # 経験則: 5bbでpushは約90%（152ハンド）、20bbで約45%（76ハンド）
    push_ratio = 0.45 + (20 - stack_bb) / 15 * 0.45
    push_ratio = max(0.0, min(1.0, push_ratio))

    # コールレンジはプッシュレンジより少し狭い（5bbで約75%、20bbで約25%）
    call_ratio = 0.25 + (20 - stack_bb) / 15 * 0.50
    call_ratio = max(0.0, min(1.0, call_ratio))

    push_count = round(push_ratio * 169)
    call_count = round(call_ratio * 169)
    return push_count, call_count


def build_range_table() -> dict:
    """5bb〜20bbのSBプッシュ・BBコールレンジをハンドリストで生成"""
    table = {}
    for stack in range(5, 21):
        push_count, call_count = push_fold_threshold(float(stack))
        table[str(stack)] = {
            "sb_push": HAND_RANK[:push_count],
            "bb_call": HAND_RANK[:call_count],
        }
    return table


def main():
    table = build_range_table()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "src", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "push_fold_hu.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(table, f, ensure_ascii=False, indent=2)
    print(f"出力完了: {out_path}")
    for stack, ranges in table.items():
        print(f"  {stack}bb: push={len(ranges['sb_push'])}ハンド, call={len(ranges['bb_call'])}ハンド")


if __name__ == "__main__":
    main()
