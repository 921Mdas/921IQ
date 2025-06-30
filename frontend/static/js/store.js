// static/js/store.js
class SearchStore {
  constructor() {
    this._state = {
      query: { and: [], or: [], not: [] },
      articles: [],
      summary: null,
      analyticsVisible: false,
      paginationVisible: false // NEW
    };
    this.subscribers = [];
  }

  get state() {
    return this._state;
  }

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

  // ✅ New explicit setter for analytics visibility
  setAnalyticsVisible(value) {
    this._state.analyticsVisible = value;
    this._notify();
  }

  // ✅ New setter for pagination
  setPaginationVisible(value) {
    this._state.paginationVisible = value;
    this._notify();
  }

  subscribe(callback) {
    this.subscribers.push(callback);
    callback(this._state);
  }

  _notify() {
    this.subscribers.forEach(cb => cb(this._state));
  }

  _getMockArticles() {
    return [{
      id: 'mock-1',
      title: 'No keywords entered',
      content: 'Please enter keywords to fetch relevant articles.',
      isMock: true
    }];
  }
}

const storeInstance = new SearchStore();
export default storeInstance;
