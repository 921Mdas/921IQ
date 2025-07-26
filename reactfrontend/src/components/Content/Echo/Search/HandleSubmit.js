import { api } from "../../../../api";
import { useSearchStore } from "../../../../store";

export const handleSubmit = async (e, keywords, selectedSources) => {
  e.preventDefault();

  // 1. Merge existing query params from URL with current keywords
  const urlParams = new URLSearchParams(window.location.search);
  const existingQuery = {
    and: urlParams.getAll("and"),
    or: urlParams.getAll("or"),
    not: urlParams.getAll("not"),
  };


  const mergedQuery = {
    and: Array.from(new Set([...existingQuery.and, ...keywords.and])),
    or: Array.from(new Set([...existingQuery.or, ...keywords.or])),
    not: Array.from(new Set([...existingQuery.not, ...keywords.not])),
    sources: selectedSources,
  };

  // 2. Check if the query is empty
  const isEmpty =
    mergedQuery.and.length === 0 &&
    mergedQuery.or.length === 0 &&
    mergedQuery.not.length === 0;

  if (isEmpty) {
    // Reset Zustand store and clear URL
    useSearchStore.getState().setQuery({ and: [], or: [], not: [] });
    useSearchStore.getState().setArticles([]);
    useSearchStore.getState().resetAnalytics();
    window.history.replaceState(null, "", window.location.pathname);
    return;
  }

  // 3. Set query in Zustand store
  useSearchStore.getState().setQuery(mergedQuery);

  // 4. Update the browser URL with new query params
  const params = new URLSearchParams();
  mergedQuery.and.forEach((k) => params.append("and", k));
  mergedQuery.or.forEach((k) => params.append("or", k));
  mergedQuery.not.forEach((k) => params.append("not", k));
  mergedQuery.sources.forEach((s) => params.append("source", s));

  window.history.pushState(null, "", `?${params.toString()}`);

  
  // 5. Fetch data from API and update Zustand (commented out as in original)
  try {
    const data = await api.getData(params);
    useSearchStore.getState().setArticles(data?.articles || []);
    useSearchStore.getState().setTopPublications(data?.top_publications || []);
    useSearchStore.getState().setWordcloudData(data?.wordcloud_data || []);
    useSearchStore.getState().setTopCountries(data?.top_countries || []);
    useSearchStore.getState().setTrendData(data?.trend_data || []);
    useSearchStore.getState().setTotalArticles(data?.total_articles || 0);
    console.log('received data in handleSubmit', data)
  } catch (err) {
    console.error("Failed to fetch data:", err);
  }
};