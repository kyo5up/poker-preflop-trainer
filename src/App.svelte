<script lang="ts">
  import { onMount } from 'svelte';
  import pushFoldData from './data/push_fold_hu.json';
  import nineMaxData from './data/open_ranges_9max.json';
  import skinData from './data/skins.json';
  import Card from './lib/components/Card.svelte';
  import Glossary from './lib/components/Glossary.svelte';

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
    callSpots: RangeSpot[];
    fourBetSpots: RangeSpot[];
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

  type ModeId = 'hu' | 'nine-max-open' | 'nine-max-3bet' | 'nine-max-call' | 'nine-max-4bet';
  type SpotType = 'open' | 'threeBet' | 'call' | 'fourBet' | 'hu';
  type GameMode = {
    id: ModeId;
    name: string;
    subtitle: string;
    positiveAction: string;
    negativeAction: string;
    instruction: string;
    playerCount: number;
    spotType: SpotType;
  };

  const gameModes: GameMode[] = [
    {
      id: 'hu',
      name: 'HEADS-UP',
      subtitle: 'Heads-Up SB Push/Fold Decision',
      positiveAction: 'PUSH',
      negativeAction: 'FOLD',
      instruction: 'Hero is SB. Decide whether to push all-in.',
      playerCount: 2,
      spotType: 'hu'
    },
    {
      id: 'nine-max-open',
      name: '9-MAX OPEN',
      subtitle: '9-handed Open/Fold Decision',
      positiveAction: 'OPEN',
      negativeAction: 'FOLD',
      instruction: 'Unopened pot. Decide whether hero should open-raise.',
      playerCount: 9,
      spotType: 'open'
    },
    {
      id: 'nine-max-3bet',
      name: '9-MAX 3BET',
      subtitle: '9-handed 3bet/Fold Decision',
      positiveAction: '3BET',
      negativeAction: 'FOLD',
      instruction: 'Villain opened first. Decide whether hero should 3bet.',
      playerCount: 9,
      spotType: 'threeBet'
    },
    {
      id: 'nine-max-call',
      name: '9-MAX CALL',
      subtitle: '9-handed Call/Fold Decision',
      positiveAction: 'CALL',
      negativeAction: 'FOLD',
      instruction: 'Villain opened first. Decide whether hero should flat-call.',
      playerCount: 9,
      spotType: 'call'
    },
    {
      id: 'nine-max-4bet',
      name: '9-MAX 4BET',
      subtitle: '9-handed 4bet/Fold Decision',
      positiveAction: '4BET',
      negativeAction: 'FOLD',
      instruction: 'Hero opened, villain 3bet. Decide whether hero should 4bet.',
      playerCount: 9,
      spotType: 'fourBet'
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
    spotType: SpotType;
    rangeTokens: string[];
    spotKey: string;
  };

  let currentModeId: ModeId = 'hu';
  $: currentMode = gameModes.find((mode) => mode.id === currentModeId) ?? gameModes[0];

  let quiz: Quiz | null = null;
  let result: 'correct' | 'wrong' | null = null;
  let score = 0;
  let total = 0;
  let cardFlipped = false;
  let isAnimating = false;
  let cardLayout: 'simple' | 'standard' = 'standard';
  let glossaryOpen = false;
  let selectedGlossaryTerm: string | null = null;

  // アクションシーケンス演出用の状態
  let seatActions: Record<string, string> = {};
  let activeActionSeat: string | null = null;
  let isActionAnimating = false;
  let actionTimer: any = null;

  function isCardRed(cardStr: string): boolean {
    if (!cardStr) return false;
    const suit = cardStr.slice(-1);
    return suit === 'h' || suit === 'd';
  }

  function showTerm(term: string) {
    selectedGlossaryTerm = term;
    glossaryOpen = true;
  }

  let editorValue = '';
  let editorMessage = '';

  type RangeOverrideMap = Record<string, string[]>;
  let rangeOverrides: RangeOverrideMap = {};

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

  function expandPairRange(start: string, end: string): string[] {
    const startIndex = RANKS.indexOf(start);
    const endIndex = RANKS.indexOf(end);
    const low = Math.min(startIndex, endIndex);
    const high = Math.max(startIndex, endIndex);
    return RANKS.slice(low, high + 1).map((rank) => `${rank}${rank}`);
  }

  function expandNonPairDash(token: string): string[] {
    const [start, end] = token.split('-');
    if (!start || !end || start.length !== 3 || end.length !== 3) return [token];

    const high1 = start[0];
    const low1 = start[1];
    const suitedness = start[2];
    const high2 = end[0];
    const low2 = end[1];

    if (high1 !== high2 || suitedness !== end[2]) return [token];

    const lowIndex1 = RANKS.indexOf(low1);
    const lowIndex2 = RANKS.indexOf(low2);
    const from = Math.min(lowIndex1, lowIndex2);
    const to = Math.max(lowIndex1, lowIndex2);
    const highIndex = RANKS.indexOf(high1);
    const combos: string[] = [];

    for (let index = from; index <= to; index += 1) {
      if (index < highIndex) {
        combos.push(`${high1}${RANKS[index]}${suitedness}`);
      }
    }

    return combos.length > 0 ? combos : [token];
  }

  function expandRangeToken(token: string): string[] {
    if (token.includes('-')) {
      const [start, end] = token.split('-');
      if (start?.length === 2 && end?.length === 2 && start[0] === start[1] && end[0] === end[1]) {
        return expandPairRange(start[0], end[0]);
      }
      return expandNonPairDash(token);
    }

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

  function spotKeyForType(spotType: SpotType, spot: RangeSpot): string {
    if (spotType === 'open') return `open:${spot.position}`;
    if (spotType === 'threeBet') return `threeBet:${spot.heroPosition}:${spot.villainPosition}`;
    if (spotType === 'call') return `call:${spot.heroPosition}:${spot.villainPosition}`;
    if (spotType === 'fourBet') return `fourBet:${spot.heroPosition}:${spot.villainPosition}`;
    return 'hu';
  }

  function tokensForSpot(spotType: SpotType, spot: RangeSpot): string[] {
    const key = spotKeyForType(spotType, spot);
    return rangeOverrides[key] ?? spot.ranges;
  }

  function buildSpotMap(spotType: SpotType, spots: RangeSpot[]): Record<string, Set<string>> {
    return Object.fromEntries(
      spots.map((spot) => [spotKeyForType(spotType, spot), buildRange(tokensForSpot(spotType, spot))])
    ) as Record<string, Set<string>>;
  }

  $: openRanges = buildSpotMap('open', nineMax.openSpots);
  $: threeBetRanges = buildSpotMap('threeBet', nineMax.threeBetSpots);
  $: callRanges = buildSpotMap('call', nineMax.callSpots);
  $: fourBetRanges = buildSpotMap('fourBet', nineMax.fourBetSpots);

  function pickSpot(spots: RangeSpot[]): RangeSpot {
    return spots[Math.floor(Math.random() * spots.length)];
  }

  function setEditorForQuiz(nextQuiz: Quiz | null) {
    if (!nextQuiz || nextQuiz.spotType === 'hu') {
      editorValue = '';
      editorMessage = '';
      return;
    }
    editorValue = nextQuiz.rangeTokens.join(', ');
    editorMessage = '';
  }

  function nextQuiz() {
    isAnimating = true;
    cardFlipped = false;

    const stack = randomStack(currentModeId);
    const { hand, cards } = randomHand();
    let next: Quiz;

    if (currentMode.spotType === 'hu') {
      next = {
        stack,
        hand,
        cards,
        shouldAct: huRanges[String(stack)]?.has(hand) ?? false,
        position: 'SB',
        villainPosition: null,
        seats: ['SB', 'BB'],
        spotLabel: 'HU Push/Fold',
        note: 'Short stack heads-up spot.',
        spotType: 'hu',
        rangeTokens: [],
        spotKey: 'hu'
      };
    } else {
      const spots =
        currentMode.spotType === 'open'
          ? nineMax.openSpots
          : currentMode.spotType === 'threeBet'
            ? nineMax.threeBetSpots
            : currentMode.spotType === 'call'
              ? nineMax.callSpots
              : nineMax.fourBetSpots;
      const spot = pickSpot(spots);
      const key = spotKeyForType(currentMode.spotType, spot);
      const tokens = tokensForSpot(currentMode.spotType, spot);
      const rangeMap =
        currentMode.spotType === 'open'
          ? openRanges
          : currentMode.spotType === 'threeBet'
            ? threeBetRanges
            : currentMode.spotType === 'call'
              ? callRanges
              : fourBetRanges;

      next = {
        stack,
        hand,
        cards,
        shouldAct: rangeMap[key]?.has(hand) ?? false,
        position: spot.position ?? spot.heroPosition ?? 'CO',
        villainPosition: spot.villainPosition ?? null,
        seats: [...FULL_RING_SEATS],
        spotLabel: spot.label,
        note: spot.note,
        spotType: currentMode.spotType,
        rangeTokens: tokens,
        spotKey: key
      };
    }

    quiz = next;
    result = null;
    setEditorForQuiz(next);

    startActionSequence();
  }

  function startActionSequence() {
    if (!quiz) return;
    
    if (actionTimer) {
      clearTimeout(actionTimer);
      actionTimer = null;
    }
    
    isActionAnimating = true;
    seatActions = {};
    activeActionSeat = null;
    
    const order = currentModeId === 'hu' ? ['SB', 'BB'] : [...FULL_RING_SEATS];
    const queue: { seat: string; action: string }[] = [];
    
    if (currentModeId === 'hu') {
      queue.push({ seat: 'SB', action: 'DECIDING' });
    } else {
      const heroSeat = quiz.position;
      const villainSeat = quiz.villainPosition;
      const spotType = currentMode.spotType;
      
      if (spotType === 'fourBet') {
        const heroIdx = order.indexOf(heroSeat);
        const villainIdx = order.indexOf(villainSeat as any);
        
        let currentIdx = 0;
        while (currentIdx < heroIdx) {
          queue.push({ seat: order[currentIdx], action: 'FOLD' });
          currentIdx++;
        }
        queue.push({ seat: heroSeat, action: 'OPEN' });
        currentIdx++;
        
        if (heroIdx < villainIdx) {
          while (currentIdx < villainIdx) {
            queue.push({ seat: order[currentIdx], action: 'FOLD' });
            currentIdx++;
          }
          queue.push({ seat: order[villainIdx], action: '3BET' });
          currentIdx++;
          
          while (currentIdx < order.length) {
            queue.push({ seat: order[currentIdx], action: 'FOLD' });
            currentIdx++;
          }
          queue.push({ seat: heroSeat, action: 'DECIDING' });
        } else {
          while (currentIdx < order.length) {
            queue.push({ seat: order[currentIdx], action: 'FOLD' });
            currentIdx++;
          }
          
          let idx2 = 0;
          while (idx2 < villainIdx) {
            queue.push({ seat: order[idx2], action: 'FOLD' });
            idx2++;
          }
          queue.push({ seat: order[villainIdx], action: '3BET' });
          idx2++;
          
          while (idx2 < heroIdx) {
            queue.push({ seat: order[idx2], action: 'FOLD' });
            idx2++;
          }
          queue.push({ seat: heroSeat, action: 'DECIDING' });
        }
      } else {
        for (const seat of order) {
          if (seat === heroSeat) {
            queue.push({ seat, action: 'DECIDING' });
            break;
          }
          if (spotType === 'open') {
            queue.push({ seat, action: 'FOLD' });
          } else {
            if (seat === villainSeat) {
              queue.push({ seat, action: 'OPEN' });
            } else {
              queue.push({ seat, action: 'FOLD' });
            }
          }
        }
      }
    }
    
    let step = 0;
    function runNextStep() {
      if (!isActionAnimating) return;
      
      if (step < queue.length) {
        const item = queue[step];
        activeActionSeat = item.seat;
        seatActions = {
          ...seatActions,
          [item.seat]: item.action
        };
        step++;
        const delay = item.action === 'FOLD' ? 220 : 600;
        actionTimer = setTimeout(runNextStep, delay) as any;
      } else {
        activeActionSeat = quiz?.position ?? null;
        isActionAnimating = false;
        isAnimating = false;
        cardFlipped = true;
      }
    }
    runNextStep();
  }

  function skipActionSequence() {
    if (!isActionAnimating || !quiz) return;
    
    if (actionTimer) {
      clearTimeout(actionTimer);
      actionTimer = null;
    }
    
    const order = currentModeId === 'hu' ? ['SB', 'BB'] : [...FULL_RING_SEATS];
    const heroSeat = quiz.position;
    const villainSeat = quiz.villainPosition;
    const spotType = currentMode.spotType;
    
    const finalActions: Record<string, string> = {};
    let passedHero = false;
    
    if (currentModeId === 'hu') {
      finalActions['SB'] = 'DECIDING';
    } else {
      if (spotType === 'fourBet') {
        for (const seat of order) {
          if (seat === heroSeat) {
            finalActions[seat] = 'DECIDING';
          } else if (seat === villainSeat) {
            finalActions[seat] = '3BET';
          } else {
            finalActions[seat] = 'FOLD';
          }
        }
      } else {
        for (const seat of order) {
          if (seat === heroSeat) {
            finalActions[seat] = 'DECIDING';
            passedHero = true;
          } else if (!passedHero) {
            if (spotType === 'open') {
              finalActions[seat] = 'FOLD';
            } else {
              finalActions[seat] = seat === villainSeat ? 'OPEN' : 'FOLD';
            }
          }
        }
      }
    }
    
    seatActions = finalActions;
    activeActionSeat = heroSeat;
    isActionAnimating = false;
    isAnimating = false;
    cardFlipped = true;
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
    if (currentMode.spotType === 'hu') {
      return `At ${quiz.stack}bb, this hand is ${quiz.shouldAct ? 'strong enough to jam' : 'too weak to jam'} from SB.`;
    }
    const verb =
      currentMode.spotType === 'open'
        ? 'open'
        : currentMode.spotType === 'threeBet'
          ? '3bet'
          : currentMode.spotType === 'call'
            ? 'call'
            : '4bet';
    const villainText = quiz.villainPosition ? ` versus ${quiz.villainPosition}` : '';
    return `${quiz.position}${villainText} is a ${quiz.shouldAct ? verb : 'fold'} here. ${quiz.note}`;
  }

  function applyEditor() {
    if (!quiz || quiz.spotType === 'hu') return;
    const tokens = editorValue
      .split(',')
      .map((token) => token.trim())
      .filter(Boolean);

    if (tokens.length === 0) {
      editorMessage = 'Range is empty.';
      return;
    }

    rangeOverrides = {
      ...rangeOverrides,
      [quiz.spotKey]: tokens
    };
    editorMessage = 'Applied to this spot.';
    nextQuiz();
  }

  function resetEditor() {
    if (!quiz || quiz.spotType === 'hu') return;
    const nextOverrides = { ...rangeOverrides };
    delete nextOverrides[quiz.spotKey];
    rangeOverrides = nextOverrides;
    editorMessage = 'Reset to default.';
    nextQuiz();
  }

  onMount(() => {
    nextQuiz();
  });
</script>

<main style={cssVariables}>
  <!-- 用語集トグルボタン -->
  <button class="glossary-toggle-btn" on:click={() => glossaryOpen = true} title="Open Poker Glossary">
    <svg viewBox="0 0 24 24" class="glossary-icon">
      <path d="M12,19.5 C10.05,18.3 7.42,17.5 5,17.5 C3.3,17.5 1.5,18.05 1,18.5 L1,5.5 C1.5,5 3.3,4.5 5,4.5 C7.42,4.5 10.05,5.3 12,6.5 C13.95,5.3 16.58,4.5 19,4.5 C20.7,4.5 22.5,5 23,5.5 L23,18.5 C22.5,18.05 20.7,17.5 19,17.5 C16.58,17.5 13.95,18.3 12,19.5 Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
      <path d="M12,6.5 L12,19.5" stroke="currentColor" stroke-width="2" />
    </svg>
  </button>

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
    <button type="button" class="subtitle term-link term-btn" on:click={() => showTerm('Preflop')}>
      {currentMode.subtitle}
    </button>
    <p class="mode-note">{currentMode.instruction}</p>
  </header>

  {#if quiz}
    <div class="quiz-container">
      <div class="top-panels">
        <div class="info-panel">
          <button type="button" class="info-label term-link term-btn" on:click={() => showTerm('Stack')}>
            STACK SIZE
          </button>
          <span class="stack-value">{quiz.stack} <span class="bb">BB</span></span>
        </div>
        <div class="info-panel">
          <button type="button" class="info-label term-link term-btn" on:click={() => showTerm(quiz?.position ?? '')}>
            HERO POSITION
          </button>
          <span class="stack-value">{quiz.position}</span>
        </div>
      </div>

      <div class="context-panel">
        <div class="context-item">
          <button type="button" class="context-label term-link term-btn" on:click={() => showTerm(quiz?.spotLabel ?? '')}>
            SPOT
          </button>
          <span class="context-value">{quiz.spotLabel}</span>
        </div>
        {#if quiz.villainPosition}
          <div class="context-item">
            <button type="button" class="context-label term-link term-btn" on:click={() => showTerm('Villain')}>
              VILLAIN
            </button>
            <span class="context-value">{quiz.villainPosition}</span>
          </div>
        {/if}
      </div>

      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
      <div 
        class="table-felt" 
        class:clickable={isActionAnimating}
        on:click={skipActionSequence}
      >
        <div class="seat-map">
          {#each quiz.seats as seat}
            <div
              class="seat-container"
              style={`top: ${SEAT_LAYOUT[seat].top}; left: ${SEAT_LAYOUT[seat].left};`}
            >
              <div class="seat-badge {seatClass(seat)}" class:active-turn={activeActionSeat === seat}>
                {seat}
                {#if seatActions[seat] && seatActions[seat] !== 'none'}
                  <span class="seat-action-label {seatActions[seat] === '3BET' ? 'three-bet' : seatActions[seat].toLowerCase()}">{seatActions[seat]}</span>
                {/if}
              </div>

              <!-- 席に配られたカード（Heroは表、他は裏向き） -->
              <div class="seat-cards" class:folded={seatActions[seat] === 'FOLD'}>
                {#if seat !== quiz.position}
                  {#if !seatActions[seat] || seatActions[seat] === 'DECIDING' || seatActions[seat] === 'OPEN' || seatActions[seat] === '3BET'}
                    <div class="mini-card-back"></div>
                    <div class="mini-card-back"></div>
                  {/if}
                {:else}
                  <div class="mini-card-front" class:red={isCardRed(quiz.cards[0])}>
                    {quiz.cards[0].slice(0, -1)}
                  </div>
                  <div class="mini-card-front" class:red={isCardRed(quiz.cards[1])}>
                    {quiz.cards[1].slice(0, -1)}
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>

        {#if isActionAnimating}
          <div class="skip-hint">CLICK FELT TO SKIP</div>
        {/if}

        <div class="cards-area">
          {#each quiz.cards as card, i}
            <div class="card-wrapper" style="animation-delay: {i * 150}ms">
              <Card {card} flipped={cardFlipped} layout={cardLayout} />
            </div>
          {/each}
        </div>
      </div>

      <div class="editor-panel">
        <div class="editor-header">
          <span class="context-label">RANGE EDITOR</span>
          <span class="editor-hint">comma separated tokens</span>
        </div>
        {#if quiz.spotType === 'hu'}
          <p class="editor-disabled">Heads-up mode uses fixed push/fold data.</p>
        {:else}
          <textarea bind:value={editorValue} rows="3"></textarea>
          <div class="editor-actions">
            <button class="mini-btn" on:click={applyEditor}>APPLY</button>
            <button class="mini-btn secondary" on:click={resetEditor}>RESET</button>
          </div>
          {#if editorMessage}
            <p class="editor-message">{editorMessage}</p>
          {/if}
        {/if}
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

  <Glossary bind:open={glossaryOpen} bind:selectedTerm={selectedGlossaryTerm} />
</main>

<style>
  main {
    max-width: 680px;
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

  .term-btn {
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
    font: inherit;
    text-align: inherit;
  }

  .mode-note {
    margin: 0.4rem 0 0;
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.72);
  }

  .skin-selector,
  .mode-selector,
  .layout-selector,
  .editor-panel {
    background: rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 8px 10px;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .editor-panel {
    width: 100%;
    max-width: 520px;
    flex-direction: column;
    align-items: stretch;
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

  .skin-btn,
  .mini-btn {
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

  .skin-btn:hover,
  .mini-btn:hover {
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
    max-width: 440px;
    aspect-ratio: 1.25 / 1;
    background: var(--bg-table);
    border-radius: 120px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    
    /* Padded Leather/Wood Rail (立体的な外枠クッション) */
    border: 10px solid #14161f;
    box-shadow: 
      /* 外側へのドロップシャドウ */
      0 20px 50px rgba(0, 0, 0, 0.65), 
      /* クッションのハイライトと影 */
      inset 0 4px 10px rgba(255, 255, 255, 0.15),
      inset 0 -4px 10px rgba(0, 0, 0, 0.6),
      /* フェルト部分の沈み込みを表現するインナーシャドウ */
      inset 0 12px 40px rgba(0, 0, 0, 0.95);
      
    overflow: visible;
    transition: background 0.5s ease;
  }

  /* ベッティングライン (Betting Line) */
  .table-felt::before {
    content: '';
    position: absolute;
    top: 15px;
    left: 15px;
    right: 15px;
    bottom: 15px;
    border-radius: 105px;
    border: 1px dashed rgba(255, 255, 255, 0.12);
    pointer-events: none;
    z-index: 1;
  }

  /* ネオン・サイバー時のベッティングライン (発光) */
  :global([style*="neon-cyber"]) .table-felt::before {
    border: 1px solid rgba(255, 0, 127, 0.35);
    box-shadow: 0 0 8px rgba(255, 0, 127, 0.2), inset 0 0 8px rgba(255, 0, 127, 0.2);
  }

  /* ロイヤル・ゴールド時のベッティングライン (金色) */
  :global([style*="royal-gold"]) .table-felt::before {
    border: 1px dashed rgba(184, 151, 66, 0.4);
  }

  /* ヴィンテージ時のベッティングライン */
  :global([style*="vintage-classic"]) .table-felt::before {
    border: 1px solid rgba(140, 37, 48, 0.2);
  }

  /* フェルト中央の透かしロゴマーク */
  .table-felt::after {
    content: 'PREFLOP TRAINER';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Outfit', sans-serif;
    font-size: 1.4rem;
    font-weight: 900;
    letter-spacing: 0.18em;
    color: rgba(255, 255, 255, 0.035);
    pointer-events: none;
    z-index: 0;
    text-transform: uppercase;
  }
  
  :global([style*="neon-cyber"]) .table-felt::after {
    color: rgba(0, 240, 255, 0.035);
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.05);
  }

  .seat-map {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  .seat-container {
    position: absolute;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    z-index: 10;
    pointer-events: none;
  }

  .seat-badge {
    min-width: 52px;
    padding: 0.28rem 0.55rem;
    border-radius: 999px;
    background: rgba(0, 0, 0, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .hero-seat {
    background: rgba(0, 255, 204, 0.18) !important;
    color: #ffffff !important;
    border-color: rgba(0, 255, 204, 0.45) !important;
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.2), 0 4px 8px rgba(0, 0, 0, 0.4) !important;
  }

  .villain-seat {
    background: rgba(255, 51, 102, 0.25) !important;
    color: #ffffff !important;
    border-color: rgba(255, 51, 102, 0.45) !important;
    box-shadow: 0 0 10px rgba(255, 51, 102, 0.2), 0 4px 8px rgba(0, 0, 0, 0.4) !important;
  }

  .inactive-seat {
    opacity: 0.45;
  }

  .active-turn {
    border-color: var(--btn-push, #2980b9) !important;
    box-shadow: 0 0 12px var(--btn-push, #2980b9), 0 4px 8px rgba(0, 0, 0, 0.4) !important;
    background: rgba(41, 128, 185, 0.25) !important;
    color: #ffffff !important;
    transform: scale(1.08);
  }

  /* アクションラベル */
  .seat-action-label {
    position: absolute;
    top: -16px;
    font-size: 0.58rem;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    animation: actionPop 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    color: #ffffff;
    pointer-events: none;
  }

  @keyframes actionPop {
    from { transform: scale(0.6); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }

  .seat-action-label.fold {
    background: #4a4a4a;
    border: 1px solid #666666;
    color: #bbbbbb;
  }

  .seat-action-label.open {
    background: #27ae60;
    border: 1px solid #2ecc71;
    box-shadow: 0 0 8px rgba(39, 174, 96, 0.5);
  }

  .seat-action-label.three-bet {
    background: #d35400;
    border: 1px solid #e67e22;
    box-shadow: 0 0 8px rgba(211, 84, 0, 0.5);
  }

  .seat-action-label.deciding {
    background: var(--btn-push, #2980b9);
    border: 1px solid #3498db;
    animation: pulseDecide 0.8s infinite alternate;
  }

  @keyframes pulseDecide {
    from { opacity: 0.85; box-shadow: 0 0 4px var(--btn-push, #2980b9); }
    to { opacity: 1; box-shadow: 0 0 12px var(--btn-push, #2980b9); }
  }

  /* ミニカードエリア */
  .seat-cards {
    display: flex;
    gap: 2px;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
    height: 18px;
    pointer-events: none;
  }

  .seat-cards.folded {
    opacity: 0;
    transform: scale(0.7) translateY(6px);
  }

  /* ミニカード裏面 */
  .mini-card-back {
    width: 12px;
    height: 17px;
    border-radius: 2px;
    background: var(--bg-card-back, #2e5d77);
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }

  /* ミニカード表面 */
  .mini-card-front {
    width: 12px;
    height: 17px;
    border-radius: 2px;
    background: #ffffff;
    border: 1px solid #cccccc;
    color: #2c3e50;
    font-size: 0.52rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    font-family: 'Outfit', sans-serif;
    line-height: 1;
  }

  .mini-card-front.red {
    color: #e74c3c;
  }

  /* スキップヒントとクリック可能 felt */
  .table-felt.clickable {
    cursor: pointer;
  }

  .skip-hint {
    position: absolute;
    bottom: 24%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.65rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.35);
    background: rgba(0, 0, 0, 0.4);
    padding: 4px 10px;
    border-radius: 12px;
    letter-spacing: 1.5px;
    pointer-events: none;
    border: 1px solid rgba(255, 255, 255, 0.05);
    animation: blinkHint 1.2s infinite alternate;
  }

  @keyframes blinkHint {
    from { opacity: 0.4; }
    to { opacity: 0.8; }
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

  .editor-header,
  .editor-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
  }

  .editor-hint,
  .editor-message,
  .editor-disabled {
    font-size: 0.78rem;
    color: rgba(255, 255, 255, 0.65);
    margin: 0;
  }

  textarea {
    width: 100%;
    resize: vertical;
    min-height: 72px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(0, 0, 0, 0.18);
    color: #fff;
    padding: 0.8rem;
    font: inherit;
  }

  .mini-btn {
    background: rgba(255, 255, 255, 0.12);
    color: #fff;
  }

  .mini-btn.secondary {
    background: rgba(255, 255, 255, 0.06);
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

    .seat-container {
      gap: 3px;
    }

    .mini-card-back,
    .mini-card-front {
      width: 9px;
      height: 13px;
      font-size: 0.4rem;
    }

    .seat-action-label {
      top: -12px;
      font-size: 0.48rem;
      padding: 1px 4px;
    }

    .skip-hint {
      bottom: 26%;
      font-size: 0.55rem;
    }

    .scoreboard {
      padding: 10px 16px;
    }

    .score-divider {
      margin: 0 12px;
    }
  }

  /* 用語リンクスタイル */
  .term-link {
    cursor: pointer;
    border-bottom: 1px dotted var(--btn-push, #2980b9);
    color: var(--btn-push, #2980b9);
    transition: all 0.2s;
    text-shadow: 0 0 4px rgba(41, 128, 185, 0.2);
    font-weight: 600;
  }

  .term-link:hover {
    color: var(--text-primary, #ffffff);
    border-bottom-color: var(--text-primary, #ffffff);
    text-shadow: 0 0 8px rgba(41, 128, 185, 0.6);
  }

  /* 用語集トグルボタン */
  .glossary-toggle-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 90;
    color: var(--text-primary, #ffffff);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  .glossary-toggle-btn:hover {
    transform: scale(1.08);
    background: var(--btn-push, #2980b9);
    color: #ffffff;
    box-shadow: 0 12px 36px rgba(41, 128, 185, 0.4);
    border-color: transparent;
  }

  .glossary-icon {
    width: 22px;
    height: 22px;
    fill: currentColor;
    transition: transform 0.3s ease;
  }

  .glossary-toggle-btn:hover .glossary-icon {
    transform: rotate(5deg);
  }

  @media (max-width: 768px) {
    .glossary-toggle-btn {
      top: 12px;
      right: 12px;
      width: 40px;
      height: 40px;
    }
    
    .glossary-icon {
      width: 18px;
      height: 18px;
    }
  }
</style>
