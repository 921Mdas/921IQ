import { create } from 'zustand';

const getMockArticles = () => [{
  id: 'mock-1',
  title: 'No keywords entered',
  content: 'Please enter keywords to fetch relevant articles.',
  isMock: true
}];

const hasKeywords = (query) => {
  return query.and.length > 0 || query.or.length > 0 || query.not.length > 0;
};

export const useSearchStore = create((set) => ({
  // Initial state
  query: { and: [], or: [], not: [] },
  articles: [],
  summary: null,
  analyticsVisible: false,
  paginationVisible: false,
  wordcloud_data: [],
  top_publications: [],
  top_countries: [],
  total_articles: 0,
  trend_data: [],
  
  setError: (error) => set({ error }), // ← new


  // Actions
  setQuery: (query) => set({ query }),

  setArticles: (articles) => set((state) => ({
    articles: hasKeywords(state.query) ? articles : getMockArticles()
  })),

  setSummary: (summary) => set({ summary }),

  toggleAnalytics: () => set((state) => ({
    analyticsVisible: !state.analyticsVisible
  })),

  setAnalyticsVisible: (value) => set({ analyticsVisible: value }),
  setPaginationVisible: (value) => set({ paginationVisible: value }),

  // 🆕 Setters for analytics data
  setWordcloudData: (data) => set({ wordcloud_data: data }),
  setTopPublications: (data) => set({ top_publications: data }),
  setTopCountries: (data) => set({ top_countries: data }),
  setTotalArticles: (count) => set({ total_articles: count }),
  setTrendData: (data) => set({ trend_data: data }),

  resetAnalytics: () => set({
  articles: [],
  summary: null,
  wordcloud_data: [],
  top_publications: [],
  top_countries: [],
  total_articles: 0,
  trend_data: [],
})

}));
