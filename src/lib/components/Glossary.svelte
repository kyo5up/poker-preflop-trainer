<script lang="ts">
  import glossaryData from '../../data/glossary.json';

  export let open: boolean = false;
  export let selectedTerm: string | null = null;

  type TermItem = {
    term: string;
    definition: string;
    description: string;
  };
  const items = glossaryData as TermItem[];

  let searchQuery = '';
  let activeIndex: number | null = null;

  // selectedTermが渡されたら、自動で検索＆アコーディオン展開する
  $: if (selectedTerm) {
    const termUpper = selectedTerm.toUpperCase().replace(/-/g, '').trim();
    const foundIdx = items.findIndex(item => {
      const dbTerm = item.term.toUpperCase().replace(/-/g, '').trim();
      const dbDef = item.definition.toUpperCase().trim();
      return dbTerm.includes(termUpper) || dbDef.includes(termUpper) || termUpper.includes(dbTerm);
    });
    if (foundIdx !== -1) {
      activeIndex = foundIdx;
      searchQuery = ''; // 検索条件をクリアして全体を表示
    }
  }

  $: filteredItems = items.filter(item => 
    item.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.definition.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  function toggleIndex(index: number) {
    activeIndex = activeIndex === index ? null : index;
  }

  function closePanel() {
    open = false;
    selectedTerm = null;
  }
</script>

<!-- バックドロップ -->
{#if open}
  <button type="button" class="backdrop" aria-label="Close glossary" on:click={closePanel}></button>
{/if}

<!-- スライドパネル -->
<div class="glossary-panel" class:open>
  <div class="panel-header">
    <h2>POKER GLOSSARY</h2>
    <button class="close-btn" on:click={closePanel}>&times;</button>
  </div>

  <div class="panel-body">
    <!-- 検索窓 -->
    <div class="search-box">
      <input 
        type="text" 
        placeholder="Search term..." 
        bind:value={searchQuery}
      />
      {#if searchQuery}
        <button class="clear-btn" on:click={() => searchQuery = ''}>&times;</button>
      {/if}
    </div>

    <!-- 用語リスト -->
    <div class="terms-list">
      {#each filteredItems as item}
        {@const globalIdx = items.indexOf(item)}
        {@const isItemActive = activeIndex === globalIdx}
        {@const isHighlighted = selectedTerm && (
          item.term.toUpperCase().replace(/-/g, '').trim().includes(selectedTerm.toUpperCase().replace(/-/g, '').trim()) ||
          selectedTerm.toUpperCase().replace(/-/g, '').trim().includes(item.term.toUpperCase().replace(/-/g, '').trim())
        )}
        <div 
          class="term-card" 
          class:active={isItemActive} 
          class:highlight={isHighlighted}
        >
          <button class="term-header" on:click={() => toggleIndex(globalIdx)}>
            <div class="title-group">
              <span class="term-title">{item.term}</span>
              <span class="term-def">{item.definition}</span>
            </div>
            <span class="chevron" class:expanded={isItemActive}>▼</span>
          </button>
          
          <div class="term-content-wrapper" style="max-height: {isItemActive ? '200px' : '0px'}">
            <div class="term-content">
              <p>{item.description}</p>
            </div>
          </div>
        </div>
      {/each}
      {#if filteredItems.length === 0}
        <p class="no-results">No terms found matching "{searchQuery}"</p>
      {/if}
    </div>
  </div>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 100;
    animation: fadeIn 0.3s ease;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .glossary-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 380px;
    max-width: 100%;
    height: 100vh;
    background: var(--panel-bg);
    border-left: var(--panel-border);
    backdrop-filter: blur(20px);
    z-index: 101;
    transform: translateX(100%);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);
  }

  .glossary-panel.open {
    transform: translateX(0);
  }

  .panel-header {
    padding: 1.5rem 1.2rem 1rem 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: var(--panel-border);
  }

  .panel-header h2 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: 1.5px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    color: var(--text-primary, #ffffff);
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-primary, #ffffff);
    font-size: 2rem;
    cursor: pointer;
    line-height: 1;
    padding: 0;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .close-btn:hover {
    opacity: 1;
  }

  .panel-body {
    flex-grow: 1;
    overflow-y: auto;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* 検索ボックス */
  .search-box {
    position: relative;
    width: 100%;
  }

  .search-box input {
    width: 100%;
    padding: 10px 36px 10px 14px;
    border-radius: 20px;
    border: var(--panel-border);
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary, #ffffff);
    font-size: 0.9rem;
    font-family: inherit;
    transition: all 0.3s;
  }

  .search-box input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.08);
    border-color: var(--btn-push, #ff3366);
  }

  .clear-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
  }

  /* アコーディオンリスト */
  .terms-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    overflow-y: auto;
    flex-grow: 1;
    padding-bottom: 2rem;
  }

  .term-card {
    border: var(--panel-border);
    background: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    overflow: hidden;
    transition: all 0.3s;
    color: var(--text-primary, #ffffff);
  }

  .term-card:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  .term-card.active {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.15);
  }

  .term-card.highlight {
    animation: flashHighlight 1.5s ease infinite alternate;
  }

  @keyframes flashHighlight {
    from {
      box-shadow: 0 0 0 rgba(0, 255, 204, 0);
      border-color: var(--panel-border);
    }
    to {
      box-shadow: 0 0 10px rgba(0, 255, 204, 0.4);
      border-color: var(--btn-push, #00f0ff);
    }
  }

  .term-header {
    width: 100%;
    background: transparent;
    border: none;
    color: inherit;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
  }

  .title-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .term-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .term-def {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.5);
  }

  .chevron {
    font-size: 0.65rem;
    opacity: 0.5;
    transition: transform 0.3s ease;
  }

  .chevron.expanded {
    transform: rotate(180deg);
  }

  .term-content-wrapper {
    transition: max-height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    overflow: hidden;
  }

  .term-content {
    padding: 0 14px 14px 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
  }

  .term-content p {
    font-size: 0.85rem;
    margin: 8px 0 0 0;
    color: rgba(255, 255, 255, 0.75);
    line-height: 1.4;
  }

  .no-results {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.5);
    text-align: center;
    margin-top: 2rem;
  }
</style>
