import { useSearchStore } from "../../../../store";

export const removeTag = (type, value, keywords, setKeywords, selectedSources) => {
  setKeywords(prev => {
    const updated = {
      ...prev,
      [type]: prev[type].filter(v => v !== value)
    };

    // Get current state
    const store = useSearchStore.getState();
    
    // Update Zustand store
    store.setQuery(updated);
    
    // Clear selected sources if we removed the last keyword
    if (updated.and.length === 0 && updated.or.length === 0 && updated.not.length === 0) {
      store.setSelectedSources([]);
    }

    // Update URL
    const params = new URLSearchParams();
    updated.and.forEach(k => params.append("and", k));
    updated.or.forEach(k => params.append("or", k));
    updated.not.forEach(k => params.append("not", k));
    
    if (store.selectedSources.length > 0) {
      store.selectedSources.forEach(s => params.append("sources", s));
    }
    
    window.history.pushState(null, "", `?${params.toString()}`);

    return updated;
  });
};

export const addTag = (type, value, keywords, setKeywords) => {
  const trimmed = value.trim();
  if (!trimmed || keywords[type].includes(trimmed)) return;

  setKeywords(prev => ({
    ...prev,
    [type]: [...prev[type], trimmed]
  }));
};

export const handleKeyDown = (e, type, inputs, addTag, setInputs, keywords, setKeywords) => {
  if (e.key === "Enter") {
    e.preventDefault();
    addTag(type, inputs[type], keywords, setKeywords);
    setInputs(prev => ({ ...prev, [type]: "" }));
  }
};

export const handleBlur = (type, inputs, addTag, setInputs, keywords, setKeywords) => {
  if (inputs[type].trim() !== "") {
    addTag(type, inputs[type], keywords, setKeywords);
    setInputs(prev => ({ ...prev, [type]: "" }));
  }
};

export const clearAll = (setKeywords, setInputs) => {
  const store = useSearchStore.getState();

  setKeywords({ and: [], or: [], not: [] });
  setInputs({ and: "", or: "", not: "" });

  store.setQuery({ and: [], or: [], not: [] });
  store.setArticles([]);
  store.setArticles([]);
  store.setTopCountries([]);
  store.setTopPublications([]);
  store.setWordcloudData([]);
  store.setTotalArticles(0);
  store.setTrendData([]);
  store.setSummary("");
  store.resetAnalytics();

  useSearchStore.getState().resetAnalytics();
  window.history.replaceState(null, "", window.location.pathname);
};