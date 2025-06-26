// static/js/store.js
class SearchStore {
  constructor() {
    this._state = {
      query: { and: [], or: [], not: [] },
      articles: [],
      summary: null,
      analyticsVisible: false
    };
    this.subscribers = [];
  }

  get state() {
    return this._state;
  }

  // Utility method to check if query has any keyword
  _hasKeywords() {
    const { and, or, not } = this._state.query;
    return and.length > 0 || or.length > 0 || not.length > 0;
  }

  setQuery(query) {
    this._state.query = query;
    this._notify();
  }

  setArticles(articles) {
    if (this._hasKeywords()) {
      this._state.articles = articles;
    } else {
      this._state.articles = this._getMockArticles();
    }
    this._notify();
  }

  setSummary(summary) {
    this._state.summary = summary;
    this._notify();
  }

  toggleAnalytics() {
    this._state.analyticsVisible = !this._state.analyticsVisible;
    this._notify();
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    // Immediately notify new subscriber with current state
    callback(this._state);
  }

  _notify() {
    this.subscribers.forEach(cb => cb(this._state));
  }

  // Return placeholder articles when no keywords are present
  _getMockArticles() {
    return [{
      id: 'mock-1',
      title: 'No keywords entered',
      content: 'Please enter keywords to fetch relevant articles.',
      isMock: true
    }];
  }
}

// Export a singleton instance
const storeInstance = new SearchStore();
export default storeInstance;
