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
      <!-- 左上コーナー (枠の外側) -->
      <div class="corner top-left">
        <span class="rank">{rank}</span>
        <span class="suit-mini">{suitMark(suit)}</span>
      </div>

      <!-- インナー境界枠 -->
      <div class="card-main-frame">
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
                      <circle cx="30" cy="45" r="18" fill="none" stroke="var(--court-gold)" stroke-width="0.75" stroke-dasharray="1 3" opacity="0.4"/>
                      <g transform="translate(0, 0)">
                        <path d="M14,35 L12,45 L48,45 L46,35 Z" fill="var(--court-blue)" />
                        <path d="M12,45 C12,45 10,30 15,22 C20,14 40,14 45,22 C50,30 48,45 48,45 Z" fill="var(--court-red)" opacity="0.9" />
                        <path d="M24,25 L36,25 L34,35 L26,35 Z" fill="var(--court-gold)" />
                        <path d="M21,12 L39,12 L36,20 L30,16 L24,20 Z" fill="var(--court-gold)" />
                        <circle cx="30" cy="12" r="1.5" fill="var(--court-red)" />
                        <path d="M21,20 C21,20 22,25 30,25 C38,25 39,20 39,20 L36,35 L24,35 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M21,12 L39,12 L36,20 L30,16 L24,20 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <line x1="30" y1="21" x2="30" y2="38" stroke="var(--court-outline)" stroke-width="1.5" />
                        <line x1="26" y1="25" x2="34" y2="25" stroke="var(--court-outline)" stroke-width="1.5" />
                        <circle cx="30" cy="38" r="1.5" fill="var(--court-gold)" />
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M14,35 L12,45 L48,45 L46,35 Z" fill="var(--court-blue)" />
                        <path d="M12,45 C12,45 10,30 15,22 C20,14 40,14 45,22 C50,30 48,45 48,45 Z" fill="var(--court-red)" opacity="0.9" />
                        <path d="M24,25 L36,25 L34,35 L26,35 Z" fill="var(--court-gold)" />
                        <path d="M21,12 L39,12 L36,20 L30,16 L24,20 Z" fill="var(--court-gold)" />
                        <circle cx="30" cy="12" r="1.5" fill="var(--court-red)" />
                        <path d="M21,20 C21,20 22,25 30,25 C38,25 39,20 39,20 L36,35 L24,35 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M21,12 L39,12 L36,20 L30,16 L24,20 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <line x1="30" y1="21" x2="30" y2="38" stroke="var(--court-outline)" stroke-width="1.5" />
                        <line x1="26" y1="25" x2="34" y2="25" stroke="var(--court-outline)" stroke-width="1.5" />
                        <circle cx="30" cy="38" r="1.5" fill="var(--court-gold)" />
                      </g>
                    </svg>
                  {:else if rank === 'Q'}
                    <svg viewBox="0 0 60 90" class="court-svg">
                      <circle cx="30" cy="45" r="18" fill="none" stroke="var(--court-gold)" stroke-width="0.75" stroke-dasharray="1 3" opacity="0.4"/>
                      <g transform="translate(0, 0)">
                        <path d="M13,45 C13,45 11,28 17,20 C23,12 37,12 43,20 C49,28 47,45 47,45 Z" fill="var(--court-blue)" opacity="0.9" />
                        <path d="M22,20 L38,20 L35,26 L25,26 Z" fill="var(--court-gold)" />
                        <path d="M25,26 L35,26 L33,36 L27,36 Z" fill="var(--court-red)" />
                        <circle cx="30" cy="32" r="3.5" fill="var(--court-red)" />
                        <circle cx="30" cy="32" r="1.5" fill="var(--court-gold)" />
                        <path d="M24,13 L36,13 L34,18 L30,15 L26,18 Z" fill="var(--court-gold)" />
                        <path d="M22,20 C22,20 22,26 30,26 C38,26 38,20 38,20 L35,36 L25,36 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M24,13 L36,13 L34,18 L30,15 L26,18 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M15,45 C15,45 16,36 25,36 L35,36 C44,36 45,45 45,45 Z" fill="none" stroke="var(--court-outline)" stroke-width="1" opacity="0.7"/>
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M13,45 C13,45 11,28 17,20 C23,12 37,12 43,20 C49,28 47,45 47,45 Z" fill="var(--court-blue)" opacity="0.9" />
                        <path d="M22,20 L38,20 L35,26 L25,26 Z" fill="var(--court-gold)" />
                        <path d="M25,26 L35,26 L33,36 L27,36 Z" fill="var(--court-red)" />
                        <circle cx="30" cy="32" r="3.5" fill="var(--court-red)" />
                        <circle cx="30" cy="32" r="1.5" fill="var(--court-gold)" />
                        <path d="M24,13 L36,13 L34,18 L30,15 L26,18 Z" fill="var(--court-gold)" />
                        <path d="M22,20 C22,20 22,26 30,26 C38,26 38,20 38,20 L35,36 L25,36 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M24,13 L36,13 L34,18 L30,15 L26,18 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M15,45 C15,45 16,36 25,36 L35,36 C44,36 45,45 45,45 Z" fill="none" stroke="var(--court-outline)" stroke-width="1" opacity="0.7"/>
                      </g>
                    </svg>
                  {:else if rank === 'J'}
                    <svg viewBox="0 0 60 90" class="court-svg">
                      <circle cx="30" cy="45" r="18" fill="none" stroke="var(--court-gold)" stroke-width="0.75" stroke-dasharray="1 3" opacity="0.4"/>
                      <g transform="translate(0, 0)">
                        <path d="M13,45 C13,45 11,28 17,20 C23,12 37,12 43,20 C49,28 47,45 47,45 Z" fill="var(--court-red)" opacity="0.9" />
                        <path d="M24,25 L36,25 L34,35 L26,35 Z" fill="var(--court-blue)" />
                        <path d="M23,13 C23,13 30,7 37,13 L35,19 L25,19 Z" fill="var(--court-gold)" />
                        <circle cx="30" cy="8" r="2.5" fill="var(--court-red)" />
                        <path d="M22,19 C22,19 23,25 30,25 C37,25 38,19 38,19 L35,35 L25,35 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M23,13 C23,13 30,7 37,13 L35,19 L25,19 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M18,24 L20,18 L22,24 L20,29 Z" fill="var(--court-gold)" />
                        <path d="M18,24 L20,18 L22,24 L20,29 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <line x1="20" y1="29" x2="20" y2="45" stroke="var(--court-outline)" stroke-width="1.5" />
                      </g>
                      <g transform="translate(60, 90) rotate(180)">
                        <path d="M13,45 C13,45 11,28 17,20 C23,12 37,12 43,20 C49,28 47,45 47,45 Z" fill="var(--court-red)" opacity="0.9" />
                        <path d="M24,25 L36,25 L34,35 L26,35 Z" fill="var(--court-blue)" />
                        <path d="M23,13 C23,13 30,7 37,13 L35,19 L25,19 Z" fill="var(--court-gold)" />
                        <circle cx="30" cy="8" r="2.5" fill="var(--court-red)" />
                        <path d="M22,19 C22,19 23,25 30,25 C37,25 38,19 38,19 L35,35 L25,35 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M23,13 C23,13 30,7 37,13 L35,19 L25,19 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <path d="M18,24 L20,18 L22,24 L20,29 Z" fill="var(--court-gold)" />
                        <path d="M18,24 L20,18 L22,24 L20,29 Z" fill="none" stroke="var(--court-outline)" stroke-width="1.2" />
                        <line x1="20" y1="29" x2="20" y2="45" stroke="var(--court-outline)" stroke-width="1.5" />
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
      </div>

      <!-- 右下コーナー (枠の外側) -->
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

    /* デフォルトの絵札配色カラー */
    --court-red: #c0392b;
    --court-blue: #2980b9;
    --court-gold: #f1c40f;
    --court-outline: #2c3e50;
  }

  .card-front.red {
    color: var(--suit-red, #e74c3c);
  }

  /* サイバースキンでの絵札カラー上書き */
  :global([style*="neon-cyber"]) .card-front {
    --court-red: #ff007f;
    --court-blue: #00f0ff;
    --court-gold: rgba(0, 240, 255, 0.2);
    --court-outline: #00f0ff;
  }

  /* ゴールドスキンでの絵札カラー上書き */
  :global([style*="royal-gold"]) .card-front {
    --court-red: #b89742;
    --court-blue: rgba(184, 151, 66, 0.4);
    --court-gold: #f7e5a9;
    --court-outline: #b89742;
  }

  /* インナーフレーム (カード内ベッティングライン・画像に忠実な枠線) */
  .card-main-frame {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    bottom: 10px;
    border: 1px solid rgba(0, 0, 0, 0.08); /* デフォルトの薄い枠 */
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    pointer-events: none;
  }

  /* スキン切り替え時の枠カラー */
  :global([style*="neon-cyber"]) .card-main-frame {
    border-color: rgba(0, 240, 255, 0.35);
    box-shadow: inset 0 0 6px rgba(0, 240, 255, 0.15);
  }

  :global([style*="royal-gold"]) .card-main-frame {
    border-color: rgba(184, 151, 66, 0.45);
    box-shadow: inset 0 0 6px rgba(184, 151, 66, 0.2);
  }

  :global([style*="vintage-classic"]) .card-main-frame {
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
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    line-height: 0.85;
    z-index: 2;
  }

  .top-left {
    top: 6px;
    left: 6px;
  }

  .bottom-right {
    bottom: 6px;
    right: 6px;
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
