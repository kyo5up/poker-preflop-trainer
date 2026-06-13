<script lang="ts">
  import { onMount } from 'svelte';
  import pushFoldData from './data/push_fold_hu.json';
  import nineMaxData from './data/open_ranges_9max.json';
  import skinData from './data/skins.json';
  import Card from './lib/components/Card.svelte';

  type PushFoldTable = Record<string, { sb_push: string[]; bb_call: string[] }>;
  const huTable = pushFoldData as PushFoldTable;

  type RangeSpot = {
    label: string;
    note: string;
    ranges: string[];
    position?: string;
    heroPosition?: string;
    villainPosition?: string;
  };

  type NineMaxData = {
    stackRange: { min: number; max: number };
    openSpots: RangeSpot[];
    threeBetSpots: RangeSpot[];
  };
  const nineMax = nineMaxData as NineMaxData;

  type Skin = {
    id: string;
    name: string;
    colors: Record<string, string>;
  };
  const skins = skinData.skins as Skin[];
  let currentSkinId = 'classic-dark';
  $: currentSkin = skins.find((skin) => skin.id === currentSkinId) || skins[0];
  let cardLayout: 'simple' | 'standard' = 'standard';

  $: cssVariables = Object.entries(currentSkin.colors)
    .map(([key, value]) => `--${key}: ${value}`)
    .join('; ');

  const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];
  const SUITS = ['s', 'h', 'd', 'c'];
  const FULL_RING_SEATS = ['UTG', 'UTG+1', 'MP', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'] as const;

  const SEAT_LAYOUT: Record<string, { top: string; left: string }> = {
    UTG: { top: '12%', left: '18%' },
    'UTG+1': { top: '8%', left: '38%' },
    MP: { top: '8%', left: '62%' },
    LJ: { top: '12%', left: '82%' },
    HJ: { top: '38%', left: '90%' },
    CO: { top: '68%', left: '82%' },
    BTN: { top: '82%', left: '62%' },
    SB: { top: '82%', left: '38%' },
    BB: { top: '68%', left: '18%' }
  };

  type ModeId = 'hu' | 'nine-max-open' | 'nine-max-3bet';
  type GameMode = {
    id: ModeId;
    name: string;
    subtitle: string;
    positiveAction: string;
    negativeAction: string;
    instruction: string;
    playerCount: number;
  };

  const gameModes: GameMode[] = [
    {
      id: 'hu',
      name: 'HEADS-UP',
      subtitle: 'Heads-Up SB Push/Fold Decision',
      positiveAction: 'PUSH',
      negativeAction: 'FOLD',
      instruction: 'Hero is SB. Decide whether to push all-in.',
      playerCount: 2
    },
    {
      id: 'nine-max-open',
      name: '9-MAX OPEN',
      subtitle: '9-handed Open/Fold Decision',
      positiveAction: 'OPEN',
      negativeAction: 'FOLD',
      instruction: 'Unopened pot. Decide whether hero should open-raise.',
      playerCount: 9
    },
    {
      id: 'nine-max-3bet',
      name: '9-MAX 3BET',
      subtitle: '9-handed 3bet/Fold Decision',
      positiveAction: '3BET',
      negativeAction: 'FOLD',
      instruction: 'Villain opened first. Decide whether hero should 3bet.',
      playerCount: 9
    }
  ];

  type Quiz = {
    stack: number;
    hand: string;
    cards: [string, string];
    shouldAct: boolean;
    position: string;
    villainPosition: string | null;
    seats: string[];
    spotLabel: string;
    note: string;
  };

  let currentModeId: ModeId = 'hu';
  $: currentMode = gameModes.find((mode) => mode.id === currentModeId) ?? gameModes[0];

  let quiz: Quiz | null = null;
  let result: 'correct' | 'wrong' | null = null;
  let score = 0;
  let total = 0;
  let cardFlipped = false;
  let isAnimating = false;

  function randomStack(modeId: ModeId): number {
    if (modeId === 'hu') {
      return 5 + Math.floor(Math.random() * 16);
    }

    const { min, max } = nineMax.stackRange;
    return min + Math.floor(Math.random() * (max - min + 1));
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
    }

    const suits = [...SUITS].sort(() => Math.random() - 0.5).slice(0, 2);
    return { hand: `${high}${low}o`, cards: [`${high}${suits[0]}`, `${low}${suits[1]}`] };
  }

  function expandRangeToken(token: string): string[] {
    if (token.length === 2) {
      return [token];
    }

    if (token.length === 3 && token[0] === token[1] && token[2] === '+') {
      const startIndex = RANKS.indexOf(token[0]);
      return RANKS.slice(startIndex).map((rank) => `${rank}${rank}`);
    }

    if (token.length === 4) {
      return [token];
    }

    if (token.length === 5 && token[3] === '+') {
      const high = token[0];
      const low = token[1];
      const suitedness = token[2];
      const highIndex = RANKS.indexOf(high);
      const lowIndex = RANKS.indexOf(low);

      if (highIndex <= lowIndex) {
        return [token.slice(0, 3)];
      }

      const combos: string[] = [];
      for (let index = lowIndex; index < highIndex; index += 1) {
        combos.push(`${high}${RANKS[index]}${suitedness}`);
      }
      return combos;
    }

    return [token];
  }

  function buildRange(tokens: string[]): Set<string> {
    return new Set(tokens.flatMap(expandRangeToken));
  }

  const huRanges = Object.fromEntries(
    Object.entries(huTable).map(([stack, spot]) => [stack, new Set(spot.sb_push)])
  ) as Record<string, Set<string>>;

  const openRanges = Object.fromEntries(
    nineMax.openSpots.map((spot) => [spot.position ?? '', buildRange(spot.ranges)])
  ) as Record<string, Set<string>>;

  const threeBetRanges = Object.fromEntries(
    nineMax.threeBetSpots.map((spot) => [`${spot.heroPosition}|${spot.villainPosition}`, buildRange(spot.ranges)])
  ) as Record<string, Set<string>>;

  function pickOpenSpot(): RangeSpot {
    return nineMax.openSpots[Math.floor(Math.random() * nineMax.openSpots.length)];
  }

  function pickThreeBetSpot(): RangeSpot {
    return nineMax.threeBetSpots[Math.floor(Math.random() * nineMax.threeBetSpots.length)];
  }

  function nextQuiz() {
    isAnimating = true;
    cardFlipped = false;

    const stack = randomStack(currentModeId);
    const { hand, cards } = randomHand();
    let position = 'SB';
    let villainPosition: string | null = null;
    let spotLabel = 'HU Push/Fold';
    let note = 'Short stack heads-up spot.';
    let shouldAct = false;
    let seats = ['SB', 'BB'];

    if (currentModeId === 'hu') {
      shouldAct = huRanges[String(stack)]?.has(hand) ?? false;
    } else if (currentModeId === 'nine-max-open') {
      const spot = pickOpenSpot();
      position = spot.position ?? 'CO';
      spotLabel = spot.label;
      note = spot.note;
      seats = [...FULL_RING_SEATS];
      shouldAct = openRanges[position]?.has(hand) ?? false;
    } else {
      const spot = pickThreeBetSpot();
      position = spot.heroPosition ?? 'BTN';
      villainPosition = spot.villainPosition ?? 'CO';
      spotLabel = spot.label;
      note = spot.note;
      seats = [...FULL_RING_SEATS];
      shouldAct = threeBetRanges[`${position}|${villainPosition}`]?.has(hand) ?? false;
    }

    quiz = {
      stack,
      hand,
      cards,
      shouldAct,
      position,
      villainPosition,
      seats,
      spotLabel,
      note
    };

    result = null;

    setTimeout(() => {
      cardFlipped = true;
      isAnimating = false;
    }, 450);
  }

  function answer(choice: 'positive' | 'negative') {
    if (!quiz || isAnimating) return;

    const isCorrect = (choice === 'positive') === quiz.shouldAct;
    result = isCorrect ? 'correct' : 'wrong';
    total += 1;
    if (isCorrect) score += 1;
  }

  function changeMode(modeId: ModeId) {
    currentModeId = modeId;
    nextQuiz();
  }

  function seatClass(seat: string): string {
    if (!quiz) return '';
    if (seat === quiz.position) return 'hero-seat';
    if (quiz.villainPosition && seat === quiz.villainPosition) return 'villain-seat';
    if (currentModeId === 'hu' && seat !== quiz.position) return 'inactive-seat';
    return '';
  }

  function noteForResult(): string {
    if (!quiz) return '';
    if (currentModeId === 'hu') {
      return `At ${quiz.stack}bb, this hand is ${quiz.shouldAct ? 'strong enough to jam' : 'too weak to jam'} from SB.`;
    }
    if (currentModeId === 'nine-max-open') {
      return `${quiz.position} is an ${quiz.shouldAct ? 'open' : 'fold'} here. ${quiz.note}`;
    }
    return `${quiz.position} versus ${quiz.villainPosition} is a ${quiz.shouldAct ? '3bet' : 'fold'} here. ${quiz.note}`;
  }

  onMount(() => {
    nextQuiz();
  });
</script>

<main style={cssVariables}>
  <div class="skin-selector">
    <span class="selector-label">THEME:</span>
    <div class="selector-buttons">
      {#each skins as skin}
        <button
          class="skin-btn"
          class:active={currentSkinId === skin.id}
          on:click={() => (currentSkinId = skin.id)}
        >
          {skin.name}
        </button>
      {/each}
    </div>
  </div>

  <div class="mode-selector">
    <span class="selector-label">MODE:</span>
    <div class="selector-buttons">
      {#each gameModes as mode}
        <button
          class="skin-btn"
          class:active={currentModeId === mode.id}
          on:click={() => changeMode(mode.id)}
        >
          {mode.name}
        </button>
      {/each}
    </div>
  </div>

  <div class="layout-selector">
    <span class="selector-label">CARD:</span>
    <div class="selector-buttons">
      <button
        class="skin-btn"
        class:active={cardLayout === 'simple'}
        on:click={() => (cardLayout = 'simple')}
      >
        SIMPLE
      </button>
      <button
        class="skin-btn"
        class:active={cardLayout === 'standard'}
        on:click={() => (cardLayout = 'standard')}
      >
        STANDARD
      </button>
    </div>
  </div>

  <header>
    <h1>PREFLOP TRAINER</h1>
    <p class="subtitle">{currentMode.subtitle}</p>
    <p class="mode-note">{currentMode.instruction}</p>
  </header>

  {#if quiz}
    <div class="quiz-container">
      <div class="top-panels">
        <div class="info-panel">
          <span class="info-label">STACK SIZE</span>
          <span class="stack-value">{quiz.stack} <span class="bb">BB</span></span>
        </div>
        <div class="info-panel">
          <span class="info-label">HERO POSITION</span>
          <span class="stack-value">{quiz.position}</span>
        </div>
      </div>

      <div class="context-panel">
        <div class="context-item">
          <span class="context-label">SPOT</span>
          <span class="context-value">{quiz.spotLabel}</span>
        </div>
        {#if quiz.villainPosition}
          <div class="context-item">
            <span class="context-label">VILLAIN</span>
            <span class="context-value">{quiz.villainPosition} opens</span>
          </div>
        {/if}
      </div>

      <div class="table-felt">
        <div class="seat-map">
          {#each quiz.seats as seat}
            <div
              class="seat-badge {seatClass(seat)}"
              style={`top: ${SEAT_LAYOUT[seat].top}; left: ${SEAT_LAYOUT[seat].left};`}
            >
              {seat}
            </div>
          {/each}
        </div>

        <div class="cards-area">
          {#each quiz.cards as card, i}
            <div class="card-wrapper" style="animation-delay: {i * 150}ms">
              <Card {card} flipped={cardFlipped} layout={cardLayout} />
            </div>
          {/each}
        </div>
      </div>

      {#if result === null}
        <div class="action-panel">
          <button class="action-btn btn-fold" on:click={() => answer('negative')} disabled={isAnimating}>
            {currentMode.negativeAction}
          </button>
          <button class="action-btn btn-push" on:click={() => answer('positive')} disabled={isAnimating}>
            {currentMode.positiveAction}
          </button>
        </div>
      {:else}
        <div class="feedback-panel" class:correct={result === 'correct'} class:wrong={result === 'wrong'}>
          <div class="feedback-text">
            {#if result === 'correct'}
              <span class="feedback-title">CORRECT</span>
              <p>
                Strong choice. <strong>{quiz.hand}</strong> is a correct
                <strong>{quiz.shouldAct ? currentMode.positiveAction : currentMode.negativeAction}</strong>.
              </p>
            {:else}
              <span class="feedback-title">WRONG</span>
              <p>
                Better line: <strong>{quiz.shouldAct ? currentMode.positiveAction : currentMode.negativeAction}</strong>.
                <strong>{quiz.hand}</strong> in this spot.
              </p>
            {/if}
          </div>
          <div class="spot-explainer">
            <span class="context-label">WHY</span>
            <p>{noteForResult()}</p>
          </div>
          <button class="next-btn" on:click={nextQuiz}>
            NEXT HAND
          </button>
        </div>
      {/if}
    </div>
  {/if}

  <footer class="scoreboard">
    <div class="score-item">
      <span class="score-label">MODE</span>
      <span class="score-val small">{currentMode.playerCount}P</span>
    </div>
    <div class="score-divider"></div>
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

  .mode-note {
    margin: 0.4rem 0 0;
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.72);
  }

  .skin-selector,
  .mode-selector,
  .layout-selector {
    background: rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 30px;
    padding: 4px 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .selector-label,
  .context-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.5);
    letter-spacing: 1px;
  }

  .selector-label {
    padding-left: 8px;
  }

  .selector-buttons {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    justify-content: center;
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

  .quiz-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    flex-grow: 1;
    justify-content: center;
  }

  .top-panels,
  .context-panel {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.8rem;
  }

  .info-panel,
  .context-item {
    background: var(--panel-bg);
    border: var(--panel-border);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 10px 18px;
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

  .stack-value,
  .context-value {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.1;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }

  .stack-value {
    font-size: 2rem;
  }

  .stack-value .bb {
    font-size: 1.1rem;
    opacity: 0.7;
    margin-left: 2px;
  }

  .table-felt {
    width: 100%;
    max-width: 420px;
    aspect-ratio: 1.2 / 1;
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

  .seat-map {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .seat-badge {
    position: absolute;
    transform: translate(-50%, -50%);
    min-width: 52px;
    padding: 0.28rem 0.55rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
  }

  .hero-seat {
    background: rgba(0, 255, 204, 0.18);
    color: #ffffff;
    border-color: rgba(0, 255, 204, 0.35);
    box-shadow: 0 0 0 2px rgba(0, 255, 204, 0.08);
  }

  .villain-seat {
    background: rgba(255, 51, 102, 0.2);
    color: #ffffff;
    border-color: rgba(255, 51, 102, 0.35);
    box-shadow: 0 0 0 2px rgba(255, 51, 102, 0.08);
  }

  .inactive-seat {
    opacity: 0.72;
  }

  .cards-area {
    display: flex;
    gap: 1.2rem;
    justify-content: center;
    align-items: center;
    position: relative;
    z-index: 1;
  }

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

  .feedback-text,
  .spot-explainer {
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

  .feedback-text p,
  .spot-explainer p {
    font-size: 0.9rem;
    margin: 0.2rem 0 0;
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

  .score-val.small {
    font-size: 1.2rem;
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

    .top-panels,
    .context-panel {
      grid-template-columns: 1fr;
    }

    .table-felt {
      aspect-ratio: 1 / 1;
    }

    .seat-badge {
      min-width: 44px;
      padding: 0.22rem 0.4rem;
      font-size: 0.58rem;
    }

    .scoreboard {
      padding: 10px 16px;
    }

    .score-divider {
      margin: 0 12px;
    }
  }
</style>
