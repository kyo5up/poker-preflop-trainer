<script lang="ts">
  import pushFoldData from './data/push_fold_hu.json'

  type PushFoldTable = Record<string, { sb_push: string[]; bb_call: string[] }>
  const table = pushFoldData as PushFoldTable

  const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
  const SUITS = ['s', 'h', 'd', 'c']

  type Quiz = {
    stack: number
    hand: string
    cards: [string, string]
    correct: boolean
  }

  let quiz: Quiz | null = null
  let result: 'correct' | 'wrong' | null = null
  let score = 0
  let total = 0

  function randomStack(): number {
    return 5 + Math.floor(Math.random() * 16) // 5〜20
  }

  function randomHand(): { hand: string; cards: [string, string] } {
    const r1 = RANKS[Math.floor(Math.random() * RANKS.length)]
    const r2 = RANKS[Math.floor(Math.random() * RANKS.length)]
    const i1 = RANKS.indexOf(r1)
    const i2 = RANKS.indexOf(r2)

    if (r1 === r2) {
      const suits = [...SUITS].sort(() => Math.random() - 0.5).slice(0, 2)
      return { hand: `${r1}${r2}`, cards: [`${r1}${suits[0]}`, `${r2}${suits[1]}`] }
    }

    const high = i1 > i2 ? r1 : r2
    const low = i1 > i2 ? r2 : r1
    const suited = Math.random() < 0.5
    if (suited) {
      const suit = SUITS[Math.floor(Math.random() * SUITS.length)]
      return { hand: `${high}${low}s`, cards: [`${high}${suit}`, `${low}${suit}`] }
    } else {
      const suits = [...SUITS].sort(() => Math.random() - 0.5).slice(0, 2)
      return { hand: `${high}${low}o`, cards: [`${high}${suits[0]}`, `${low}${suits[1]}`] }
    }
  }

  function nextQuiz() {
    const stack = randomStack()
    const { hand, cards } = randomHand()
    const pushRange = table[String(stack)]?.sb_push ?? []
    const correct = pushRange.includes(hand)
    quiz = { stack, hand, cards, correct }
    result = null
  }

  function answer(choice: 'push' | 'fold') {
    if (!quiz) return
    const isCorrect = (choice === 'push') === quiz.correct
    result = isCorrect ? 'correct' : 'wrong'
    total += 1
    if (isCorrect) score += 1
  }

  function suitMark(suit: string): string {
    switch (suit) {
      case 's': return '♠'
      case 'h': return '♥'
      case 'd': return '♦'
      case 'c': return '♣'
      default: return ''
    }
  }

  function suitColor(suit: string): string {
    return suit === 'h' || suit === 'd' ? 'red' : 'black'
  }

  nextQuiz()
</script>

<main>
  <h1>プリフロップ Push/Fold トレーナー</h1>
  <p class="subtitle">ヘッズアップ SBプッシュ判断クイズ</p>

  {#if quiz}
    <div class="info">
      <span class="stack">スタック: {quiz.stack}bb</span>
    </div>

    <div class="cards">
      {#each quiz.cards as card}
        <div class="card" class:red={suitColor(card.slice(-1)) === 'red'}>
          <span class="rank">{card.slice(0, -1)}</span>
          <span class="suit">{suitMark(card.slice(-1))}</span>
        </div>
      {/each}
    </div>

    {#if result === null}
      <div class="buttons">
        <button class="push" on:click={() => answer('push')}>PUSH</button>
        <button class="fold" on:click={() => answer('fold')}>FOLD</button>
      </div>
    {:else}
      <div class="feedback" class:ok={result === 'correct'} class:ng={result === 'wrong'}>
        {#if result === 'correct'}
          <p>正解！</p>
        {:else}
          <p>不正解。正解は {quiz.correct ? 'PUSH' : 'FOLD'} でした。</p>
        {/if}
        <button class="next" on:click={nextQuiz}>次の問題</button>
      </div>
    {/if}
  {/if}

  <div class="score">スコア: {score} / {total}</div>
</main>

<style>
  main {
    max-width: 480px;
    margin: 0 auto;
    padding: 2rem 1rem;
    text-align: center;
    font-family: sans-serif;
  }

  h1 {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }

  .subtitle {
    color: #888;
    margin-bottom: 1.5rem;
  }

  .info {
    margin-bottom: 1rem;
    font-size: 1.1rem;
    font-weight: bold;
  }

  .cards {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .card {
    width: 80px;
    height: 110px;
    border: 2px solid #333;
    border-radius: 8px;
    background: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: bold;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  }

  .card.red {
    color: #c0392b;
  }

  .suit {
    font-size: 2.2rem;
  }

  .buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  button {
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    color: white;
  }

  .push {
    background: #2980b9;
  }

  .fold {
    background: #7f8c8d;
  }

  .feedback {
    margin-bottom: 1.5rem;
  }

  .feedback.ok p {
    color: #27ae60;
    font-weight: bold;
  }

  .feedback.ng p {
    color: #c0392b;
    font-weight: bold;
  }

  .next {
    background: #34495e;
    margin-top: 0.5rem;
  }

  .score {
    color: #555;
    font-size: 1rem;
  }
</style>
