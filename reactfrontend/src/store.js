


import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Type definitions for better IDE support (optional but recommended)
/**
 * @typedef {Object} Article
 * @property {string} id
 * @property {string} title
 * @property {string} content
 * @property {boolean} [isMock]
 */

/**
 * @typedef {Object} StoreState
 * @property {{ and: string[], or: string[], not: string[] }} query
 * @property {Article[]} articles
 * @property {string|null} summary
 * @property {boolean} analyticsVisible
 * @property {boolean} paginationVisible
 * @property {number} total_articles
 * @property {string[]} selectedSources
 * @property {boolean} isLoading
 * @property {{ labels: string[], data: number[] }} top_publications
 * @property {Array<{country: string, count: number}>} top_countries
 * @property {Array<{text: string, size: number}>} wordcloud_data
 * @property {{ labels: string[], data: number[] }} trend_data
 * @property {string|null} error
 */

const getMockArticles = () => [{
  id: 'mock-1',
  title: 'No keywords entered',
  content: 'Please enter keywords to fetch relevant articles.',
  isMock: true
}];

const hasKeywords = (query) => {
  return query.and.length > 0 || query.or.length > 0 || query.not.length > 0;
};

const initialState = {
  query: { and: [], or: [], not: [] },
  articles: [],
  summary: null,
  analyticsVisible: false,
  paginationVisible: false,
  total_articles: 0,
  selectedSources: [],
  isLoading: false,
  error: null,
  top_publications: { labels: [], data: [] },
  top_countries: [],
  wordcloud_data: [],
  trend_data: { labels: [], data: [] },
  entities: [],
  activeTab: 'volume', // Default to VOLUME
  isLoadingEntity: false,
  TABS : {
  VOLUME: 'volume',
  ENTITIES: 'entities',
  isLoadingSummary: false,

}
};

export const useSearchStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Debugging helper
      logState: () => {
        console.log('Current store state:', get());
      },

      // Safe state updaters
      setError: (error) => set({ 
        error: error instanceof Error ? error.message : String(error),
        isLoading: false 
      }),

      setLoading: (loading) => set({ 
        isLoading: Boolean(loading),
        ...(loading ? { error: null } : {}) // Clear error when loading starts
      }),

       setActiveTab: (tab) => {
        const validTabs = Object.values(get().TABS);
        if (validTabs.includes(tab)) {
          set({ activeTab: tab });
        }
      },

      getActiveTab: () => get().activeTab,

      getTabsConfig: () => get().TABS,


      setQuery: (query) => set({
        query: {
          and: Array.isArray(query?.and) ? query.and : [],
          or: Array.isArray(query?.or) ? query.or : [],
          not: Array.isArray(query?.not) ? query.not : []
        }
      }),

      setIsLoadingSummary: (isLoading) => set({ isLoadingSummary: isLoading }),

      setIsLoadingEntity: (isLoading) => set({ isLoadingEntity: isLoading }),

      setSelectedSources: (sources) => set({ 
        selectedSources: Array.isArray(sources) ? sources : [] 
      }),

      clearSelectedSources: () => set({ selectedSources: [] }),

      setArticles: (articles) => set((state) => ({
        articles: Array.isArray(articles) 
          ? (hasKeywords(state.query) ? articles : getMockArticles())
          : state.articles
      })),

      setEntities: (entities)=>set({
        entities: Array.isArray(entities) ? entities : []
      }),

      setSummary: (summary) => set({ 
        summary: typeof summary === 'string' ? summary : null 
      }),

      toggleAnalytics: () => set((state) => ({
        analyticsVisible: !state.analyticsVisible
      })),

      setAnalyticsVisible: (value) => set({ 
        analyticsVisible: Boolean(value) 
      }),

      setPaginationVisible: (value) => set({ 
        paginationVisible: Boolean(value) 
      }),

      // Analytics data setters with validation
      setWordcloudData: (data) => set({ 
        wordcloud_data: Array.isArray(data) ? data : [] 
      }),

      setTopPublications: (data) => set({ 
            
              labels: Array.isArray(data.labels) ? data.labels : [],
              data: Array.isArray(data.data) ? data.data : []
      }),

      setTopCountries: (data) => set({ 
        top_countries: Array.isArray(data) 
          ? data.filter(item => item?.country && typeof item.count === 'number')
          : [] 
      }),

      setTotalArticles: (count) => set({ 
        total_articles: Number.isInteger(count) ? count : 0 
      }),

      setTrendData: (data) => set({ 
        trend_data: data?.labels && data?.data 
          ? { 
              labels: Array.isArray(data.labels) ? data.labels : [],
              data: Array.isArray(data.data) ? data.data : []
            } 
          : initialState.trend_data
      }),

      // Atomic update for all analytics data
      setAllAnalyticsData: (data) => {
        if (!data) return;
        
        set({
          wordcloud_data: Array.isArray(data.wordcloud_data) ? data.wordcloud_data : get().wordcloud_data,
          top_publications: data.top_publications?.labels ? data.top_publications : get().top_publications,
          top_countries: Array.isArray(data.top_countries) ? data.top_countries : get().top_countries,
          trend_data: data.trend_data?.labels ? data.trend_data : get().trend_data,
          total_articles: Number.isInteger(data.total_articles) ? data.total_articles : get().total_articles,
          isLoading: false,
          error: null
        });
      },

      // Reset with proper fallbacks
      resetAnalytics: () => set({
        articles: [],
        summary: null,
        wordcloud_data: [],
        top_publications: { labels: [], data: [] },
        top_countries: [],
        total_articles: 0,
        trend_data: { labels: [], data: [] },
        isLoading: false,
        error: null
      }),

      // Full reset
      resetAll: () => set(initialState)
    }),
    {
      name: 'search-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist these values
        query: state.query,
        selectedSources: state.selectedSources,
        // Analytics data
        wordcloud_data: state.wordcloud_data,
        top_publications: state.top_publications,
        top_countries: state.top_countries,
        trend_data: state.trend_data,
        total_articles: state.total_articles
      }),
      version: 1,
      migrate: (persistedState) => {
        // Migration logic if store structure changes in future
        return persistedState;
      }
    }
  )
);