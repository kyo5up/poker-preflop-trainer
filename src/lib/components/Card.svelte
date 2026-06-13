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
      <div class="card-inner-frame">
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
                    <path d="M50,90 C25,90 15,70 15,50 C15,30 25,10 50,10" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="1 2" opacity="0.3"/>
                    <path d="M50,90 C75,90 85,70 85,50 C85,30 75,10 50,10" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="1 2" opacity="0.3"/>
                    <path d="M50,15 C62,38 82,42 82,62 C82,78 68,78 60,72 C57,82 62,88 62,88 L38,88 C38,88 43,82 40,72 C32,78 18,78 18,62 C18,42 38,38 50,15 Z" fill="currentColor" />
                    <path d="M50,23 C58,42 74,45 74,61 C74,72 64,72 58,67 C55,75 58,82 58,82 L42,82 C42,82 45,75 42,67 C36,72 26,72 26,61 C26,45 42,42 50,23 Z" fill="none" stroke="var(--bg-card-front, #ffffff)" stroke-width="1.2" opacity="0.85" />
                    <circle cx="50" cy="53" r="3.5" fill="none" stroke="var(--bg-card-front, #ffffff)" stroke-width="0.75" />
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
                  {#if rank === 'K'}
                    <svg viewBox="0 0 60 90" class="court-svg">
                      <circle cx="30" cy="45" r="18" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" opacity="0.25"/>
                      <g transform="translate(0, 0)">
                        <path d="M22,12 L38,12 L35,22 L30,17 L25,22 Z" fill="currentColor" />
                        <path d="M20,22 C20,22 23,28 30,28 C37,28 40,22 40,22 L36,36 L24,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <line x1="30" y1="26" x2="30" y2="40" stroke="currentColor" stroke-width="1.5" />
                        <line x1="27" y1="29" x2="33" y2="29" stroke="currentColor" stroke-width="1.5" />
                        <path d="M24,36 L15,45 L45,45 L36,36" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M22,12 L38,12 L35,22 L30,17 L25,22 Z" fill="currentColor" />
                        <path d="M20,22 C20,22 23,28 30,28 C37,28 40,22 40,22 L36,36 L24,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <line x1="30" y1="26" x2="30" y2="40" stroke="currentColor" stroke-width="1.5" />
                        <line x1="27" y1="29" x2="33" y2="29" stroke="currentColor" stroke-width="1.5" />
                        <path d="M24,36 L15,45 L45,45 L36,36" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                    </svg>
                  {:else if rank === 'Q'}
                    <svg viewBox="0 0 60 90" class="court-svg">
                      <circle cx="30" cy="45" r="18" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" opacity="0.25"/>
                      <g transform="translate(0, 0)">
                        <path d="M25,14 L35,14 L33,20 L30,16 L27,20 Z" fill="currentColor" />
                        <path d="M22,20 C22,20 22,26 30,26 C38,26 38,20 38,20 L35,36 L25,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <circle cx="30" cy="31" r="3" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <path d="M28,31 C28,29 32,29 32,31 C32,33 28,33 28,31 Z" fill="currentColor" opacity="0.8"/>
                        <path d="M25,36 C18,41 18,45 18,45 L42,45 C42,45 42,41 35,36 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M25,14 L35,14 L33,20 L30,16 L27,20 Z" fill="currentColor" />
                        <path d="M22,20 C22,20 22,26 30,26 C38,26 38,20 38,20 L35,36 L25,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <circle cx="30" cy="31" r="3" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <path d="M28,31 C28,29 32,29 32,31 C32,33 28,33 28,31 Z" fill="currentColor" opacity="0.8"/>
                        <path d="M25,36 C18,41 18,45 18,45 L42,45 C42,45 42,41 35,36 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                    </svg>
                  {:else if rank === 'J'}
                    <svg viewBox="0 0 60 90" class="court-svg">
                      <circle cx="30" cy="45" r="18" fill="none" stroke="currentColor" stroke-width="0.5" stroke-dasharray="2 2" opacity="0.25"/>
                      <g transform="translate(0, 0)">
                        <path d="M24,15 C24,15 30,8 36,15 L33,21 L27,21 Z" fill="currentColor" />
                        <path d="M23,21 C23,21 24,27 30,27 C36,27 37,21 37,21 L34,36 L26,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <path d="M19,25 L21,20 L23,25 L21,30 Z" fill="currentColor"/>
                        <line x1="21" y1="30" x2="21" y2="45" stroke="currentColor" stroke-width="1.2"/>
                        <path d="M26,36 L17,45 L43,45 L34,36 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M24,15 C24,15 30,8 36,15 L33,21 L27,21 Z" fill="currentColor" />
                        <path d="M23,21 C23,21 24,27 30,27 C36,27 37,21 37,21 L34,36 L26,36 Z" fill="none" stroke="currentColor" stroke-width="1.2" />
                        <path d="M19,25 L21,20 L23,25 L21,30 Z" fill="currentColor"/>
                        <line x1="21" y1="30" x2="21" y2="45" stroke="currentColor" stroke-width="1.2"/>
                        <path d="M26,36 L17,45 L43,45 L34,36 Z" fill="none" stroke="currentColor" stroke-width="1" opacity="0.8"/>
                      </g>
                    </svg>
                  {/if}
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
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .card-back {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 6px;
  }

  /* 表面のスタイル */
  .card-front {
    background: var(--bg-card-front, #ffffff);
    color: var(--suit-black, #2c3e50);
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.05);
    padding: 0;
    
    /* 高級リネンフィニッシュ（格子エンボステクスチャ） */
    background-image: 
      radial-gradient(circle at 50% 50%, transparent 60%, rgba(0, 0, 0, 0.02) 100%),
      repeating-linear-gradient(0deg, rgba(0, 0, 0, 0.012) 0px, rgba(0, 0, 0, 0.012) 1px, transparent 1px, transparent 2px),
      repeating-linear-gradient(90deg, rgba(0, 0, 0, 0.012) 0px, rgba(0, 0, 0, 0.012) 1px, transparent 1px, transparent 2px);
    background-blend-mode: multiply;
  }

  .card-front.red {
    color: var(--suit-red, #e74c3c);
  }

  /* インナーフレーム (飾り枠) */
  .card-inner-frame {
    width: 100%;
    height: 100%;
    border: 1px solid rgba(0, 0, 0, 0.04);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 5px;
    box-sizing: border-box;
    position: relative;
  }

  /* スキン切り替え時の枠カラー */
  :global([style*="neon-cyber"]) .card-inner-frame {
    border-color: rgba(255, 0, 127, 0.3);
    box-shadow: inset 0 0 5px rgba(255, 0, 127, 0.15);
  }

  :global([style*="royal-gold"]) .card-inner-frame {
    border-color: rgba(184, 151, 66, 0.45);
    box-shadow: inset 0 0 5px rgba(184, 151, 66, 0.2);
  }

  :global([style*="vintage-classic"]) .card-inner-frame {
    border-color: rgba(140, 37, 48, 0.25);
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
    font-size: 1.15rem;
    font-weight: 800;
    font-family: 'Cinzel', 'Playfair Display', 'Georgia', serif;
    line-height: 0.9;
  }

  /* ネオン・サイバースキンではシャープなフォントを維持 */
  :global([style*="neon-cyber"]) .rank {
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
    width: 54px;
    height: 80px;
    position: relative;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.08);
    background: rgba(0, 0, 0, 0.02);
    border-radius: 4px;
    border: 1px solid rgba(0,0,0,0.08);
    overflow: hidden;
  }

  /* サイバースキンの時の絵札の背景と枠 */
  :global([style*="neon-cyber"]) .court-graphic {
    border-color: rgba(0, 240, 255, 0.25);
    background: rgba(255, 255, 255, 0.02);
    box-shadow: inset 0 0 6px rgba(0, 240, 255, 0.1);
  }

  /* ゴールドスキンの時の絵札の背景と枠 */
  :global([style*="royal-gold"]) .court-graphic {
    border-color: rgba(184, 151, 66, 0.35);
    background: rgba(184, 151, 66, 0.03);
    box-shadow: inset 0 0 8px rgba(184, 151, 66, 0.1);
  }

  /* ヴィンテージスキンの時の絵札 */
  :global([style*="vintage-classic"]) .court-graphic {
    border-color: rgba(140, 37, 48, 0.15);
    background: rgba(140, 37, 48, 0.02);
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
