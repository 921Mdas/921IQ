// import store from './store.js';

// /** Initialize query params from URL and update store */
// function extractKeywordsFromURL() {
//   const urlParams = new URLSearchParams(window.location.search);
//   store.setQuery({
//     and: urlParams.getAll('and'),
//     or: urlParams.getAll('or'),
//     not: urlParams.getAll('not'),
//   });
// }

// extractKeywordsFromURL();

// // Clear any old articles, then optionally load server-side ones
// store.setArticles([]);

// const query = store.state.query;
// const hasKeywords = query.and.length > 0 || query.or.length > 0 || query.not.length > 0;

// if (hasKeywords) {
//   // Load server-side rendered articles only if query exists
//   store.setArticles(window.__INITIAL_ARTICLES__ || []);
// }

// // DOM renderer functions
// function renderArticles(state) {
//   const list = document.querySelector('.article-list');
//   list.innerHTML = '';

//   if (!state.articles || state.articles.length === 0) {
//     list.innerHTML = '<p>No articles found.</p>';
//     return;
//   }

//   for (const article of state.articles) {
//     const li = document.createElement('li');
//     li.className = 'article-card';

//     const imgSrc = article.source_logo || '/static/Images/news-icon.png';
//     const safeDate = article.date ? new Date(article.date).toLocaleDateString() : '';

//     li.innerHTML = `
//       <img src="${imgSrc}"
//            alt="${article.source_name || 'News icon'}"
//            class="article-image"
//            onerror="this.onerror=null; this.src='/static/Images/news-icon.png'">
//       <div class="article-info">
//         <a href="${article.url}" target="_blank" class="article-title">${article.title}</a>
//         <div class="article-date">${safeDate}</div>
//         <div class="source-name">${article.source_name || '<span class="missing">No source_name found</span>'}</div>
//       </div>
//     `;
//     list.appendChild(li);
//   }
// }

// function renderSummary(state) {
//   const summaryEl = document.getElementById('ai-summary');
//   const skeleton = document.querySelector('.skeleton-loader');
//   if (state.summary) {
//     summaryEl.textContent = state.summary;
//     summaryEl.style.display = 'block';
//     skeleton.style.display = 'none';
//   }
// }

// function renderAnalytics(state) {
//   const panel = document.querySelector('.analytics');
//   panel.classList.toggle('active', state.analyticsVisible);
// }

// // Subscribe to state changes
// store.subscribe((state) => {
//   renderArticles(state);
//   renderSummary(state);
//   renderAnalytics(state);
// });

// /** Fetch AI summary on load */
// // if (hasKeywords) {
// //   // Load server-side rendered articles only if query exists
// //   store.setArticles(window.__INITIAL_ARTICLES__ || []);

// //   // Fetch summary only if keywords are present
// //   document.addEventListener('DOMContentLoaded', async () => {
// //     const params = new URLSearchParams(window.location.search);
// //     try {
// //       const response = await fetch(`/get-summary?${params.toString()}`);
// //       if (!response.ok) throw new Error('Network error');
// //       const data = await response.json();
// //       if (data.summary) store.setSummary(data.summary);
// //     } catch (error) {
// //       console.error('Summary load failed:', error);
// //       const skeleton = document.querySelector('.skeleton-loader');
// //       skeleton.textContent = 'Summary unavailable';
// //       skeleton.style.backgroundColor = '#ffeeee';
// //     }
// //   });
// // }

// if (hasKeywords) {
//   store.setArticles(window.__INITIAL_ARTICLES__ || []);

//   document.addEventListener('DOMContentLoaded', async () => {
//     const params = new URLSearchParams(window.location.search);

//     // Fetch AI summary
//     try {
//       const response = await fetch(`/get-summary?${params.toString()}`);
//       if (!response.ok) throw new Error('Network error');
//       const data = await response.json();
//       if (data.summary) store.setSummary(data.summary);
//     } catch (error) {
//       console.error('Summary load failed:', error);
//       const skeleton = document.querySelector('.skeleton-loader');
//       skeleton.textContent = 'Summary unavailable';
//       skeleton.style.backgroundColor = '#ffeeee';
//     }

//     // ✅ Turn on analytics and pagination after fetch
//     store.setAnalyticsVisible(true);
//     store.setPaginationVisible(true);
//   });
// }


// // Debugging tool
// window.store = store;


import store from './store.js';

/** Initialize query params from URL and update store */
function extractKeywordsFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  store.setQuery({
    and: urlParams.getAll('and'),
    or: urlParams.getAll('or'),
    not: urlParams.getAll('not'),
  });
}

extractKeywordsFromURL();

// Utility check
const query = store.state.query;
const hasKeywords = query.and.length > 0 || query.or.length > 0 || query.not.length > 0;

/** Render placeholder if no keywords are present */
// function renderPlaceholder() {
//   const list = document.querySelector('.article-list');
//   list.innerHTML = `
//     <li class="placeholder-message">
//       <p>Please enter keywords to start a search.</p>
//     </li>
//   `;

//   const analytics = document.querySelector('.analytics');
//   const summary = document.getElementById('ai-summary');
//   const skeleton = document.querySelector('.skeleton-loader');
//   const pagination = document.querySelector('.pagination');

//   if (analytics) analytics.classList.remove('active');
//   if (summary) summary.style.display = 'none';
//   if (skeleton) skeleton.style.display = 'none';
//   if (pagination) pagination.style.display = 'none';
// }

// function renderPlaceholder() {
//   const list = document.querySelector('.article-list');
//   list.innerHTML = `
//     <li class="placeholder-message">
//       <div class="placeholder-content">
//         <svg width="96" height="96" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
//           <!-- Replace this with your actual SVG, this is just a sample -->
//           <path d="M12 5v14M5 12h14" />
//         </svg>
//         <h2>Start by filling out the search box above</h2>
//         <p>Search across multiple media types at once, review the results and gain further insights from the instant analytics.</p>
//       </div>
//     </li>
//   `;

//   const analytics = document.querySelector('.analytics');
//   const summary = document.getElementById('ai-summary');
//   const skeleton = document.querySelector('.skeleton-loader');
//   const pagination = document.querySelector('.pagination');

//   if (analytics) analytics.classList.remove('active');
//   if (summary) summary.style.display = 'none';
//   if (skeleton) skeleton.style.display = 'none';
//   if (pagination) pagination.style.display = 'none';
// }
function renderPlaceholder() {
  const container = document.querySelector('.responsive-container');

  // Prevent adding multiple placeholders
  if (container.querySelector('.placeholder-message')) return;

  const placeholder = document.createElement('li');
  placeholder.className = 'placeholder-message';

  placeholder.innerHTML = `
    <div class="placeholder-content">
      <svg width="96" height="96" viewBox="0 0 24 24" fill="none" stroke="#aaa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 5v14M5 12h14" />
      </svg>
      <h2>Start by filling out the search box above</h2>
      <p>Search across multiple media types at once, review the results and gain further insights from the instant analytics.</p>
    </div>
  `;

  container.appendChild(placeholder);

  // Optionally hide components you don’t want visible
  const analytics = document.querySelector('.analytics');
  const summary = document.getElementById('ai-summary');
  const skeleton = document.querySelector('.skeleton-loader');
  const pagination = document.querySelector('.pagination');

  if (analytics) analytics.classList.remove('active');
  if (summary) summary.style.display = 'none';
  if (skeleton) skeleton.style.display = 'none';
  if (pagination) pagination.style.display = 'none';
}


/** Render article list */
function renderArticles(state) {
  const list = document.querySelector('.article-list');
  list.innerHTML = '';

  if (!state.articles || state.articles.length === 0) {
    list.innerHTML = ` <li class="no-articles-message">
    <div class="message-card">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <circle cx="12" cy="16" r="1" />
      </svg>
      <div class="message-content">
        <h3>No articles found</h3>
        <p>Try a different keyword, or refine your filters to get better results.</p>
      </div>
    </div>
  </li>`;
    
    return;
  }

  for (const article of state.articles) {
    const li = document.createElement('li');
    li.className = 'article-card';

    const imgSrc = article.source_logo || '/static/Images/news-icon.png';
    const safeDate = article.date ? new Date(article.date).toLocaleDateString() : '';

    li.innerHTML = `
      <img src="${imgSrc}"
           alt="${article.source_name || 'News icon'}"
           class="article-image"
           onerror="this.onerror=null; this.src='/static/Images/news-icon.png'">
      <div class="article-info">
        <a href="${article.url}" target="_blank" class="article-title">${article.title}</a>
        <div class="article-date">${safeDate}</div>
        <div class="source-name">${article.source_name || '<span class="missing">No source_name found</span>'}</div>
      </div>
    `;
    list.appendChild(li);
  }
}

/** Render summary if present */
function renderSummary(state) {
  const summaryEl = document.getElementById('ai-summary');
  const skeleton = document.querySelector('.skeleton-loader');

  if (state.summary) {
    summaryEl.textContent = state.summary;
    summaryEl.style.display = 'block';
    skeleton.style.display = 'none';
  }
}

/** Render analytics panel */
function renderAnalytics(state) {
  const panel = document.querySelector('.analytics');
  panel.classList.toggle('active', state.analyticsVisible);
}

/** Store subscriber */
store.subscribe((state) => {
  renderArticles(state);
  renderSummary(state);
  renderAnalytics(state);
});

/** Main logic on DOMContentLoaded */
document.addEventListener('DOMContentLoaded', async () => {
  if (!hasKeywords) {
    renderPlaceholder();
    return;
  }

  // Set initial articles from server
  store.setArticles(window.__INITIAL_ARTICLES__ || []);

  // Fetch AI summary
  try {
    const params = new URLSearchParams(window.location.search);
    const response = await fetch(`/get-summary?${params.toString()}`);
    if (!response.ok) throw new Error('Network error');
    const data = await response.json();
    if (data.summary) store.setSummary(data.summary);
  } catch (error) {
    console.error('Summary load failed:', error);
    const skeleton = document.querySelector('.skeleton-loader');
    skeleton.textContent = 'Summary unavailable';
    skeleton.style.backgroundColor = '#ffeeee';
  }

  // Enable panels
  store.setAnalyticsVisible(true);
  store.setPaginationVisible(true);
});

// Debug
window.store = store;

