<script lang="ts">
  export let card: string;
  export let flipped: boolean = true;
  export let layout: 'simple' | 'standard' = 'standard';

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

  // 2〜10のカードに対するスートの絶対位置（%指定）
  type Pip = { x: number; y: number; rotate?: boolean };
  const getPips = (r: string): Pip[] => {
    switch (r) {
      case '2':
        return [
          { x: 50, y: 22 },
          { x: 50, y: 78, rotate: true }
        ];
      case '3':
        return [
          { x: 50, y: 22 },
          { x: 50, y: 50 },
          { x: 50, y: 78, rotate: true }
        ];
      case '4':
        return [
          { x: 30, y: 22 }, { x: 70, y: 22 },
          { x: 30, y: 78, rotate: true }, { x: 70, y: 78, rotate: true }
        ];
      case '5':
        return [
          { x: 30, y: 22 }, { x: 70, y: 22 },
          { x: 50, y: 50 },
          { x: 30, y: 78, rotate: true }, { x: 70, y: 78, rotate: true }
        ];
      case '6':
        return [
          { x: 30, y: 22 }, { x: 70, y: 22 },
          { x: 30, y: 50 }, { x: 70, y: 50 },
          { x: 30, y: 78, rotate: true }, { x: 70, y: 78, rotate: true }
        ];
      case '7':
        return [
          { x: 30, y: 22 }, { x: 70, y: 22 },
          { x: 50, y: 36 },
          { x: 30, y: 50 }, { x: 70, y: 50 },
          { x: 30, y: 78, rotate: true }, { x: 70, y: 78, rotate: true }
        ];
      case '8':
        return [
          { x: 30, y: 22 }, { x: 70, y: 22 },
          { x: 50, y: 36 },
          { x: 30, y: 50 }, { x: 70, y: 50 },
          { x: 50, y: 64, rotate: true },
          { x: 30, y: 78, rotate: true }, { x: 70, y: 78, rotate: true }
        ];
      case '9':
        return [
          { x: 30, y: 20 }, { x: 70, y: 20 },
          { x: 30, y: 40 }, { x: 70, y: 40 },
          { x: 50, y: 50 },
          { x: 30, y: 60, rotate: true }, { x: 70, y: 60, rotate: true },
          { x: 30, y: 80, rotate: true }, { x: 70, y: 80, rotate: true }
        ];
      case '10':
        return [
          { x: 30, y: 20 }, { x: 70, y: 20 },
          { x: 50, y: 30 },
          { x: 30, y: 40 }, { x: 70, y: 40 },
          { x: 30, y: 60, rotate: true }, { x: 70, y: 60, rotate: true },
          { x: 50, y: 70, rotate: true },
          { x: 30, y: 80, rotate: true }, { x: 70, y: 80, rotate: true }
        ];
      default:
        return [];
    }
  };

  $: isPipsCard = ['2', '3', '4', '5', '6', '7', '8', '9', '10'].includes(rank);
  $: isCourtCard = ['J', 'Q', 'K'].includes(rank);
  $: isAce = rank === 'A';
</script>

<div class="card-container" class:flipped>
  <div class="card-inner">
    <!-- 裏面 -->
    <div class="card-back">
      <div class="pattern"></div>
    </div>
    
    <!-- 表面 -->
    <div class="card-front" class:red={isRed}>
      <!-- 左上コーナー -->
      <div class="corner top-left">
        <span class="rank">{rank}</span>
        <span class="suit-mini">{suitMark(suit)}</span>
      </div>

      <!-- メインエリア -->
      <div class="main-area">
        {#if layout === 'simple'}
          <!-- 簡易レイアウト（常に中央に巨大スートが1個） -->
          <div class="center-suit-simple {getSuitName(suit)}">
            {suitMark(suit)}
          </div>
        {:else}
          <!-- 標準レイアウト -->
          {#if isAce}
            {#if suit === 's'}
              <!-- スペードAの豪華装飾ロゴ -->
              <div class="court-graphic spade-ace">
                <svg viewBox="0 0 100 100" class="spade-ace-svg">
                  <path d="M50,15 C60,40 85,45 85,65 C85,82 68,82 60,75 C57,85 62,90 62,90 L38,90 C38,90 43,85 40,75 C32,82 15,82 15,65 C15,45 40,40 50,15 Z" fill="currentColor" />
                  <path d="M50,23 C47,38 28,42 28,62 C28,72 38,74 45,67 C48,76 48,82 48,82 L52,82 C52,82 52,76 55,67 C62,74 72,72 72,62 C72,42 53,38 50,23 Z" fill="none" stroke="var(--bg-card-front, #ffffff)" stroke-width="1.5" opacity="0.9" />
                  <circle cx="50" cy="52" r="4" fill="none" stroke="var(--bg-card-front, #ffffff)" stroke-width="1" />
                </svg>
              </div>
            {:else}
              <div class="center-suit-standard {getSuitName(suit)}">
                {suitMark(suit)}
              </div>
            {/if}
          {:else if isPipsCard}
            <!-- 2〜10のスート配置 -->
            <div class="pips-layout">
              {#each getPips(rank) as pip}
                <div class="pip {getSuitName(suit)}" class:rotate={pip.rotate} style="left: {pip.x}%; top: {pip.y}%;">
                  {suitMark(suit)}
                </div>
              {/each}
            </div>
          {:else if isCourtCard}
            <!-- 絵札 J, Q, K の肖像画 -->
            <div class="court-graphic card-{rank}">
              <div class="court-border">
                <svg viewBox="0 0 60 90" class="court-svg">
                  <rect x="2" y="2" width="56" height="86" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="1 1" opacity="0.3" />
                  <line x1="2" y1="45" x2="58" y2="45" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" opacity="0.3" />
                  
                  {#if rank === 'K'}
                    <g transform="translate(0, 0)">
                      <path d="M18,35 L42,35 L40,15 L34,23 L30,12 L26,23 L20,15 Z" fill="currentColor" opacity="0.85" />
                      <circle cx="30" cy="28" r="3" fill="none" stroke="var(--bg-card-front)" stroke-width="1" />
                    </g>
                    <g transform="translate(60, 90) rotate(180)">
                      <path d="M18,35 L42,35 L40,15 L34,23 L30,12 L26,23 L20,15 Z" fill="currentColor" opacity="0.85" />
                      <circle cx="30" cy="28" r="3" fill="none" stroke="var(--bg-card-front)" stroke-width="1" />
                    </g>
                  {:else if rank === 'Q'}
                    <g transform="translate(0, 0)">
                      <path d="M22,35 C22,20 38,20 38,35 Z" fill="currentColor" opacity="0.85" />
                      <path d="M24,20 L36,20 L33,26 L30,16 L27,26 Z" fill="currentColor" />
                    </g>
                    <g transform="translate(60, 90) rotate(180)">
                      <path d="M22,35 C22,20 38,20 38,35 Z" fill="currentColor" opacity="0.85" />
                      <path d="M24,20 L36,20 L33,26 L30,16 L27,26 Z" fill="currentColor" />
                    </g>
                  {:else if rank === 'J'}
                    <g transform="translate(0, 0)">
                      <path d="M20,35 L40,35 C40,25 35,15 25,18 Z" fill="currentColor" opacity="0.85" />
                      <path d="M16,14 C22,12 35,16 35,26" fill="none" stroke="currentColor" stroke-width="2" />
                    </g>
                    <g transform="translate(60, 90) rotate(180)">
                      <path d="M20,35 L40,35 C40,25 35,15 25,18 Z" fill="currentColor" opacity="0.85" />
                      <path d="M16,14 C22,12 35,16 35,26" fill="none" stroke="currentColor" stroke-width="2" />
                    </g>
                  {/if}
                </svg>
                <span class="court-suit top-l">{suitMark(suit)}</span>
                <span class="court-suit bottom-r">{suitMark(suit)}</span>
              </div>
            </div>
          {/if}
        {/if}
      </div>

      <!-- 右下コーナー -->
      <div class="corner bottom-right">
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
    padding: 6px;
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

  /* インデックス（四隅）のレイアウト */
  .corner {
    display: flex;
    flex-direction: column;
    align-items: center;
    line-height: 0.85;
    z-index: 2;
  }

  .bottom-right {
    transform: rotate(180deg);
  }

  .rank {
    font-size: 1.1rem;
    font-weight: 800;
    font-family: 'Outfit', 'Inter', sans-serif;
  }

  .suit-mini {
    font-size: 0.85rem;
    margin-top: 1px;
  }

  /* メインエリア */
  .main-area {
    flex-grow: 1;
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2px 0;
    overflow: hidden;
  }

  /* 1. 簡易レイアウト用 (Simple Layout) */
  .center-suit-simple {
    font-size: 3.2rem;
    line-height: 1;
    opacity: 0.95;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    user-select: none;
  }

  .center-suit-simple.heart, .center-suit-simple.diamond {
    transform: scale(1.05);
  }

  /* 2. 標準レイアウト用 (Standard Layout) */
  .center-suit-standard {
    font-size: 2.8rem;
    line-height: 1;
    opacity: 0.9;
    user-select: none;
  }

  /* スペードAのグラフィック */
  .spade-ace {
    width: 58px;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--suit-black, #1c1c1c);
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
  }

  .spade-ace-svg {
    width: 100%;
    height: 100%;
  }

  /* 2〜10のピップスレイアウト */
  .pips-layout {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }

  .pip {
    position: absolute;
    transform: translate(-50%, -50%);
    font-size: 0.9rem;
    line-height: 1;
    user-select: none;
  }

  .pip.rotate {
    transform: translate(-50%, -50%) rotate(180deg);
  }

  /* 絵札の肖像画 */
  .court-graphic {
    width: 56px;
    height: 84px;
    position: relative;
    box-shadow: inset 0 0 6px rgba(0,0,0,0.05);
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    border: 1px solid rgba(0,0,0,0.08);
  }

  .court-border {
    width: 100%;
    height: 100%;
    position: relative;
  }

  .court-svg {
    width: 100%;
    height: 100%;
    color: inherit;
  }

  /* 絵札用の四隅の極小スートマーク */
  .court-suit {
    position: absolute;
    font-size: 0.55rem;
    line-height: 1;
    opacity: 0.7;
  }

  .court-suit.top-l {
    top: 4px;
    left: 4px;
  }

  .court-suit.bottom-r {
    bottom: 4px;
    right: 4px;
    transform: rotate(180deg);
  }
</style>
