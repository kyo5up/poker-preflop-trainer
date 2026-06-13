<script lang="ts">
  export let card: string;
  export let flipped: boolean = true;

  $: rank = card.slice(0, -1);
  $: suit = card.slice(-1);

  function suitMark(s: string): string {
    switch (s) {
      case 's': return '♠';
      case 'h': return '♥';
      case 'd': return '♦';
      case 'c': return '♣';
      default: return '';
    }
  }

  function getSuitName(s: string): string {
    switch (s) {
      case 's': return 'spade';
      case 'h': return 'heart';
      case 'd': return 'diamond';
      case 'c': return 'club';
      default: return '';
    }
  }

  $: isRed = suit === 'h' || suit === 'd';
</script>

<div class="card-container" class:flipped>
  <div class="card-inner">
    <!-- 裏面 -->
    <div class="card-back">
      <div class="pattern"></div>
    </div>
    <!-- 表面 -->
    <div class="card-front" class:red={isRed}>
      <div class="top-left">
        <span class="rank">{rank}</span>
        <span class="suit-mini">{suitMark(suit)}</span>
      </div>
      <div class="center-suit {getSuitName(suit)}">
        {suitMark(suit)}
      </div>
      <div class="bottom-right">
        <span class="rank">{rank}</span>
        <span class="suit-mini">{suitMark(suit)}</span>
      </div>
    </div>
  </div>
</div>

<style>
  .card-container {
    width: 95px;
    height: 140px;
    perspective: 1000px;
    display: inline-block;
  }

  .card-inner {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: var(--card-shadow, 0 8px 16px rgba(0, 0, 0, 0.4));
    border-radius: 12px;
  }

  /* flipped = true のときは表面を表示、false のときは裏面（Y軸180度回転） */
  .card-container.flipped .card-inner {
    transform: rotateY(0deg);
  }
  
  .card-container:not(.flipped) .card-inner {
    transform: rotateY(180deg);
  }

  .card-front, .card-back {
    width: 100%;
    height: 100%;
    position: absolute;
    backface-visibility: hidden;
    border-radius: 12px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  /* 表面のスタイル */
  .card-front {
    background: var(--bg-card-front, #ffffff);
    color: var(--suit-black, #2c3e50);
    box-shadow: inset 0 0 0 2px rgba(0, 0, 0, 0.02), inset 0 0 0 4px rgba(0, 0, 0, 0.01);
  }

  .card-front.red {
    color: var(--suit-red, #e74c3c);
  }

  /* 裏面のスタイル */
  .card-back {
    background: var(--bg-card-back, #2c3e50);
    transform: rotateY(180deg);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 5px solid #faf6eb; /* クラシックな太めの白枠 */
  }

  .pattern {
    width: 100%;
    height: 100%;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background-image: 
      radial-gradient(rgba(255, 255, 255, 0.08) 15%, transparent 16%),
      radial-gradient(rgba(255, 255, 255, 0.08) 15%, transparent 16%),
      linear-gradient(45deg, rgba(255, 255, 255, 0.03) 25%, transparent 25%, transparent 75%, rgba(255, 255, 255, 0.03) 75%),
      linear-gradient(-45deg, rgba(255, 255, 255, 0.03) 25%, transparent 25%, transparent 75%, rgba(255, 255, 255, 0.03) 75%);
    background-size: 6px 6px, 6px 6px, 12px 12px, 12px 12px;
    background-position: 0 0, 3px 3px, 0 0, 0 0;
  }

  .pattern::before {
    content: '♠';
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.12);
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 50%;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.05);
  }

  /* コーナーのスート記号 */
  .top-left, .bottom-right {
    display: flex;
    flex-direction: column;
    align-items: center;
    line-height: 0.9;
  }

  .bottom-right {
    transform: rotate(180deg);
  }

  .rank {
    font-size: 1.3rem;
    font-weight: 800;
    font-family: 'Outfit', 'Inter', sans-serif;
  }

  .suit-mini {
    font-size: 1rem;
    margin-top: 1px;
  }

  /* 中央の巨大スート */
  .center-suit {
    align-self: center;
    font-size: 3.2rem;
    line-height: 1;
    margin-bottom: 2px;
    opacity: 0.95;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    user-select: none;
  }

  .center-suit.heart, .center-suit.diamond {
    transform: scale(1.05);
  }
</style>
