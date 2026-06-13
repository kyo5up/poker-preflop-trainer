<script lang="ts">
  import { onMount } from 'svelte';
  import pushFoldData from './data/push_fold_hu.json';
  import skinData from './data/skins.json';
  import Card from './lib/components/Card.svelte';

  type PushFoldTable = Record<string, { sb_push: string[]; bb_call: string[] }>;
  const table = pushFoldData as PushFoldTable;

  type Skin = {
    id: string;
    name: string;
    colors: Record<string, string>;
  };
  const skins = skinData.skins as Skin[];
  let currentSkinId = 'classic-dark';
  $: currentSkin = skins.find(s => s.id === currentSkinId) || skins[0];

  // CSS変数の文字列を動的に生成
  $: cssVariables = Object.entries(currentSkin.colors)
    .map(([key, value]) => `--${key}: ${value}`)
    .join('; ');

  const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];
  const SUITS = ['s', 'h', 'd', 'c'];

  type Quiz = {
    stack: number;
    hand: string;
    cards: [string, string];
    correct: boolean;
  };

  let quiz: Quiz | null = null;
  let result: 'correct' | 'wrong' | null = null;
  let score = 0;
  let total = 0;

  // カードのめくりアニメーション制御用フラグ
  let cardFlipped = false;
  let isAnimating = false;

  function randomStack(): number {
    return 5 + Math.floor(Math.random() * 16); // 5〜20
  }

  function randomHand(): { hand: string; cards: [string, string] } {
    const r1 = RANKS[Math.floor(Math.random() * RANKS.length)];
    const r2 = RANKS[Math.floor(Math.random() * RANKS.length)];
    const i1 = RANKS.indexOf(r1);
    const i2 = RANKS.indexOf(r2);

    if (r1 === r2) {
      const suits = [...SUITS].sort(() => Math.random() - 0.5).slice(0, 2);
      return { hand: `${r1}${r2}`, cards: [`${r1}${suits[0]}`, `${r2}${suits[1]}`] };
    }

    const high = i1 > i2 ? r1 : r2;
    const low = i1 > i2 ? r2 : r1;
    const suited = Math.random() < 0.5;
    if (suited) {
      const suit = SUITS[Math.floor(Math.random() * SUITS.length)];
      return { hand: `${high}${low}s`, cards: [`${high}${suit}`, `${low}${suit}`] };
    } else {
      const suits = [...SUITS].sort(() => Math.random() - 0.5).slice(0, 2);
      return { hand: `${high}${low}o`, cards: [`${high}${suits[0]}`, `${low}${suits[1]}`] };
    }
  }

  function nextQuiz() {
    isAnimating = true;
    cardFlipped = false; // 一旦裏返す

    const stack = randomStack();
    const { hand, cards } = randomHand();
    const pushRange = table[String(stack)]?.sb_push ?? [];
    const correct = pushRange.includes(hand);
    
    quiz = { stack, hand, cards, correct };
    result = null;

    // カードが配られてから表になるようなアニメーションディレイ
    setTimeout(() => {
      cardFlipped = true;
      isAnimating = false;
    }, 450);
  }

  function answer(choice: 'push' | 'fold') {
    if (!quiz || isAnimating) return;
    const isCorrect = (choice === 'push') === quiz.correct;
    result = isCorrect ? 'correct' : 'wrong';
    total += 1;
    if (isCorrect) score += 1;
  }

  // 初期化時に最初の問題を読み込む
  onMount(() => {
    nextQuiz();
  });
</script>

<main style={cssVariables}>
  <!-- スキンセレクター -->
  <div class="skin-selector">
    <span class="selector-label">THEME:</span>
    <div class="selector-buttons">
      {#each skins as skin}
        <button 
          class="skin-btn" 
          class:active={currentSkinId === skin.id}
          on:click={() => currentSkinId = skin.id}
        >
          {skin.name}
        </button>
      {/each}
    </div>
  </div>

  <header>
    <h1>PREFLOP TRAINER</h1>
    <p class="subtitle">Heads-Up SB Push/Fold Decision</p>
  </header>

  {#if quiz}
    <div class="quiz-container">
      <div class="info-panel">
        <span class="info-label">STACK SIZE</span>
        <span class="stack-value">{quiz.stack} <span class="bb">BB</span></span>
      </div>

      <div class="table-felt">
        <div class="cards-area">
          {#each quiz.cards as card, i}
            <div class="card-wrapper" style="animation-delay: {i * 150}ms">
              <Card {card} flipped={cardFlipped} />
            </div>
          {/each}
        </div>
      </div>

      {#if result === null}
        <div class="action-panel">
          <button class="action-btn btn-fold" on:click={() => answer('fold')} disabled={isAnimating}>
            FOLD
          </button>
          <button class="action-btn btn-push" on:click={() => answer('push')} disabled={isAnimating}>
            PUSH
          </button>
        </div>
      {:else}
        <div class="feedback-panel" class:correct={result === 'correct'} class:wrong={result === 'wrong'}>
          <div class="feedback-text">
            {#if result === 'correct'}
              <span class="feedback-title">✓ CORRECT</span>
              <p>Excellent decision! SB Push range includes <strong>{quiz.hand}</strong>.</p>
            {:else}
              <span class="feedback-title">✗ WRONG</span>
              <p>Incorrect! Correct play was <strong>{quiz.correct ? 'PUSH' : 'FOLD'}</strong> with <strong>{quiz.hand}</strong>.</p>
            {/if}
          </div>
          <button class="next-btn" on:click={nextQuiz}>
            NEXT HAND
          </button>
        </div>
      {/if}
    </div>
  {/if}

  <!-- スコアボード -->
  <footer class="scoreboard">
    <div class="score-item">
      <span class="score-label">ACCURACY</span>
      <span class="score-val">{total > 0 ? Math.round((score / total) * 100) : 0}%</span>
    </div>
    <div class="score-divider"></div>
    <div class="score-item">
      <span class="score-label">SCORE</span>
      <span class="score-val">{score} / {total}</span>
    </div>
  </footer>
</main>

<style>
  main {
    max-width: 600px;
    width: 100%;
    margin: 0 auto;
    padding: 1.5rem 1rem 3rem 1rem;
    text-align: center;
    color: var(--text-primary, #ffffff);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
  }

  /* 背景色の適用 */
  :global(body) {
    background: var(--bg-table);
  }

  header {
    margin-bottom: 1rem;
  }

  h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 0;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  }

  .subtitle {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
    margin: 0.2rem 0 0 0;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  /* スキンセレクター */
  .skin-selector {
    background: rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 30px;
    padding: 4px 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .selector-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.5);
    padding-left: 8px;
    letter-spacing: 1px;
  }

  .selector-buttons {
    display: flex;
    gap: 4px;
  }

  .skin-btn {
    background: transparent;
    border: none;
    padding: 6px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 20px;
    color: rgba(255, 255, 255, 0.6);
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .skin-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
  }

  .skin-btn.active {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  /* クイズエリア */
  .quiz-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    flex-grow: 1;
    justify-content: center;
  }

  /* スタックサイズ表示 */
  .info-panel {
    background: var(--panel-bg);
    border: var(--panel-border);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 10px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  }

  .info-label {
    font-size: 0.7rem;
    letter-spacing: 1.5px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
  }

  .stack-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }

  .stack-value .bb {
    font-size: 1.1rem;
    opacity: 0.7;
    margin-left: 2px;
  }

  /* テーブルフェルト */
  .table-felt {
    width: 100%;
    max-width: 420px;
    aspect-ratio: 2.2 / 1;
    background: rgba(0, 0, 0, 0.15);
    border-radius: 100px;
    border: 3px solid rgba(255, 255, 255, 0.05);
    box-shadow: inset 0 10px 30px rgba(0, 0, 0, 0.5), 0 4px 20px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    position: relative;
  }

  .cards-area {
    display: flex;
    gap: 1.2rem;
    justify-content: center;
    align-items: center;
  }

  /* カード配りアニメーション */
  .card-wrapper {
    animation: dealCard 0.55s cubic-bezier(0.19, 1, 0.22, 1) both;
  }

  @keyframes dealCard {
    0% {
      opacity: 0;
      transform: translateY(80px) rotate(15deg) scale(0.8);
    }
    100% {
      opacity: 1;
      transform: translateY(0) rotate(0) scale(1);
    }
  }

  /* ボタン操作パネル */
  .action-panel {
    display: flex;
    gap: 1.5rem;
    width: 100%;
    max-width: 400px;
  }

  .action-btn {
    flex: 1;
    padding: 1rem 2rem;
    font-size: 1.2rem;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    letter-spacing: 1px;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    color: #ffffff;
  }

  .btn-push {
    background: var(--btn-push);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .btn-push:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 255, 204, 0.2);
    filter: brightness(1.1);
  }

  .btn-fold {
    background: var(--btn-fold);
  }

  .btn-fold:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    filter: brightness(1.1);
  }

  .action-btn:active:not(:disabled) {
    transform: translateY(1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }

  .action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* フィードバックパネル */
  .feedback-panel {
    width: 100%;
    max-width: 420px;
    background: var(--panel-bg);
    border: var(--panel-border);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    animation: slideUp 0.4s cubic-bezier(0.19, 1, 0.22, 1);
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(15px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .feedback-text {
    text-align: left;
    padding: 0 0.5rem;
  }

  .feedback-title {
    display: block;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
  }

  .correct .feedback-title {
    color: #00ffcc;
  }

  .wrong .feedback-title {
    color: #ff3366;
  }

  .feedback-text p {
    font-size: 0.9rem;
    margin: 0;
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.4;
  }

  .feedback-text strong {
    color: #ffffff;
    font-size: 0.95rem;
  }

  .next-btn {
    width: 100%;
    padding: 0.9rem;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 700;
    font-family: 'Outfit', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
  }

  .next-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-1px);
  }

  /* スコアボード */
  .scoreboard {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 10px 30px;
    margin-top: 1.5rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  }

  .score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 80px;
  }

  .score-label {
    font-size: 0.65rem;
    letter-spacing: 1px;
    color: rgba(255, 255, 255, 0.45);
    font-weight: 700;
    margin-bottom: 2px;
  }

  .score-val {
    font-family: 'Outfit', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
  }

  .score-divider {
    width: 1px;
    height: 30px;
    background: rgba(255, 255, 255, 0.1);
    margin: 0 20px;
  }

  @media (max-width: 480px) {
    h1 {
      font-size: 1.8rem;
    }
    .table-felt {
      aspect-ratio: 1.8 / 1;
    }
  }
</style>
