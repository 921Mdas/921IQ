
import "./Search.scss";
import React, { useState, useEffect, useCallback } from "react";
import { TextField, Chip, Box, Button } from "@mui/material";
import { useSearchStore } from "../../../../store";
import { api } from "../../../../api";
import SourceSelector from "./SourceDropDown";
import ActiveTABS from "../ActiveTABS";

window.testApi = api; // Expose to global scope for testing

function BooleanSearch() {
  const [keywords, setKeywords] = useState({ and: [], or: [], not: [] });
  const [inputs, setInputs] = useState({ and: "", or: "", not: "" });
  const selectedSources = useSearchStore(state => state.selectedSources);




  // Health check on backend
  
  const removeTag = useCallback((type, value) => {
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
      store.setSelectedSources([]); // Reset sources when no keywords left
    }

    // Update URL
    const params = new URLSearchParams();
    updated.and.forEach(k => params.append("and", k));
    updated.or.forEach(k => params.append("or", k));
    updated.not.forEach(k => params.append("not", k));
    
    // Also include selected sources in URL if they exist
    if (store.selectedSources.length > 0) {
      store.selectedSources.forEach(s => params.append("sources", s));
    }
    
    window.history.pushState(null, "", `?${params.toString()}`);

    // Prepare API params
    const apiParams = { ...updated };
    if (store.selectedSources.length > 0) {
      apiParams.sources = store.selectedSources.join(',');
    }

    

    // Fetch data
    api.getData(apiParams).then(({
      articles,
      wordcloud_data,
      total_articles,
      top_publications,
      top_countries,
      trend_data
    }) => {


   

      store.setArticles(articles);
      store.setTopCountries(top_countries);
      // store.setTopPublications(top_publications);
      store.setWordcloudData(wordcloud_data);
      store.setTotalArticles(total_articles);
      store.setTrendData(trend_data);
    });

    // api.getSummary(apiParams).then(({ summary }) => {
    //   store.setSummary(summary);
    // });
    
api.getSummary({ 
  and: keywords.and, 
  or: keywords.or,
  sources: selectedSources 
})
.then(response => {
  if (response.success) {
    store.setSummary(response.summary);
  } else {
    console.error('Backend reported failure:', response);
  }
})
.catch(error => {
  console.error('API Error:', error);
});

 

    return updated;
  });
}, [keywords.and, keywords.or, selectedSources]);
  
  
  


  // Add a tag
  const addTag = (type, value) => {
    const trimmed = value.trim();
    if (!trimmed || keywords[type].includes(trimmed)) return;

    setKeywords(prev => ({
      ...prev,
      [type]: [...prev[type], trimmed]
    }));
  };


  // Handle key press (Enter) to add tag
  const handleKeyDown = (e, type) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addTag(type, inputs[type]);
      setInputs(prev => ({ ...prev, [type]: "" }));
    }
  };

  // Handle blur to add tag
  const handleBlur = (type) => {
    if (inputs[type].trim() !== "") {
      addTag(type, inputs[type]);
      setInputs(prev => ({ ...prev, [type]: "" }));
    }
  };

  // Clear all tags and inputs
const clearAll = () => {
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

    useSearchStore.getState().resetAnalytics(); // ← clean and all-in-one
    window.history.replaceState(null, "", window.location.pathname);

};

  // Submit handler
  const handleSubmit = async (e) => {
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
  sources: selectedSources, // ← independent field
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
    useSearchStore.getState().resetAnalytics(); // ← clean and all-in-one
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
  mergedQuery.sources.forEach((s) => params.append("source", s)); // ← here



  window.history.pushState(null, "", `?${params.toString()}`);

  // 4.5 check health

  // 5. Fetch data from API and update Zustand
  try {
    const {
      articles,
      wordcloud_data,
      total_articles,
      top_publications,
      top_countries,
      trend_data,
    } = await api.getData(mergedQuery);



    useSearchStore.getState().setArticles(articles);
    useSearchStore.getState().setTopCountries(top_countries);
    // useSearchStore.getState().setTopPublications(top_publications);
    useSearchStore.getState().setWordcloudData(wordcloud_data);
    useSearchStore.getState().setTotalArticles(total_articles);
    useSearchStore.getState().setTrendData(trend_data);

    // Fetch summary separately
    const { summary } = await api.getSummary(mergedQuery);
console.log('API MODULE LOADED mergedQuery params', summary);

    useSearchStore.getState().setSummary(summary);

    // // Fetch entities separately
    // const entities = await api.getEntity(mergedQuery) 

    // useSearchStore.getState().setEntities(entities.top_people)

  } catch (err) {
    console.error("Failed to fetch data:", err);
  }
};

// const handleSubmit = async (e) => {
//   e.preventDefault();

//   // Merge parameters
//   const urlParams = new URLSearchParams(window.location.search);
//   const mergedQuery = {
//     and_keywords: Array.from(new Set([
//       ...urlParams.getAll("and"), 
//       ...keywords.and
//     ])),
//     or_keywords: Array.from(new Set([
//       ...urlParams.getAll("or"), 
//       ...keywords.or
//     ])),
//     not_keywords: Array.from(new Set([
//       ...urlParams.getAll("not"),
//       ...keywords.not
//     ])),
//     sources: selectedSources
//   };

//   // Check if empty
//   const isEmpty = !mergedQuery.and_keywords.length && 
//                  !mergedQuery.or_keywords.length && 
//                  !mergedQuery.not_keywords.length;


//   if (isEmpty) {
//     useSearchStore.getState().setQuery({ and_keywords: [], or_keywords: [], not_keywords: [] });
//     useSearchStore.getState().setArticles([]);
//     useSearchStore.getState().resetAnalytics();
//     window.history.replaceState(null, "", window.location.pathname);
//     return;
//   }

//   // Update URL
//   const urlSearchParams = new URLSearchParams();
//   mergedQuery.and_keywords.forEach(k => urlSearchParams.append("and", k));
//   mergedQuery.or_keywords.forEach(k => urlSearchParams.append("or", k));
//   mergedQuery.not_keywords.forEach(k => urlSearchParams.append("not", k));
//   mergedQuery.sources.forEach(s => urlSearchParams.append("source", s));
//   window.history.pushState(null, "", `?${urlSearchParams.toString()}`);



//   try {
//     const [dataResponse] = await Promise.all([
//       api.getData(mergedQuery),
//       // api.getSummary(mergedQuery)
//     ]);


//     useSearchStore.getState().setQuery(mergedQuery);
//     useSearchStore.getState().setArticles(dataResponse.articles || []);
//     useSearchStore.getState().setTopCountries(dataResponse.top_countries || []);
//     useSearchStore.getState().setWordcloudData(dataResponse.wordcloud_data || []);
//     useSearchStore.getState().setTotalArticles(dataResponse.total_articles || 0);
//     useSearchStore.getState().setTrendData(dataResponse.trend_data || []);

//     // if (summaryResponse.success) {
//     //   useSearchStore.getState().setSummary(summaryResponse.summary);
//     // } else {
//     //   useSearchStore.getState().setSummary("Could not generate summary");
//     // }
//   } catch (err) {
//     useSearchStore.getState().setError(err.message || "Failed to fetch data");
//   }
// };

  useEffect(() => {
  const urlParams = new URLSearchParams(window.location.search);

  // issue here is that drcongo is included as source amongst the sources we put null


  setKeywords({
    and: urlParams.getAll("and"),
    or: urlParams.getAll("or"),
    not: urlParams.getAll("not"),
  });

  // ✅ Restore selectedSources from ?source=...
 const sources = urlParams.getAll("source").filter(source => 
  source !== null && source !== "" && source !== "null" && source !== "undefined"
);


// Update Zustand store with clean values
useSearchStore.getState().setSelectedSources(sources);

}, []);

  // Render input group
  const renderInputGroup = (type, label) => (
    <Box
      sx={{
        border: "1px solid rgba(207, 207, 207, 0.44)",
        borderRadius: 2,
        padding: 1,
        display: "flex",
        flexWrap: "wrap",
        gap: 0.5,
        backgroundColor: "white",
        minWidth: 300,
        flexGrow: 1,
      }}
    >
      {keywords[type].map((tag) => (
        <Chip
          key={tag}
          label={tag}
          onDelete={() => removeTag(type, tag)}
          sx={{ backgroundColor: "#6c5ce7", color: "white" }}
        />
      ))}
      <TextField
        variant="standard"
        placeholder={`${label}...`}
        sx={{ backgroundColor: "white", color: "white", width: '100%' }}
        value={inputs[type]}
        onChange={(e) =>
          setInputs(prev => ({ ...prev, [type]: e.target.value }))
        }
        onKeyDown={(e) => handleKeyDown(e, type)}
        onBlur={() => handleBlur(type)}
        InputProps={{
          disableUnderline: true,
          sx: { ml: 1, minWidth: 120, flexGrow: 1 },
        }}
        inputProps={{ "aria-label": `${label} keywords input` }}
      />
    </Box>
  );

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      className="boolean-search-form"
      sx={{
        mx: "auto",
        display: "grid",
        gap: 1,
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
        alignItems: "center",
        padding:'1em'
      }}
      noValidate
      autoComplete="off"
    >
      {renderInputGroup("and", "Keyword AND")}
      {renderInputGroup("or", "Keyword OR")}
      {renderInputGroup("not", "Keyword NOT")}
 <Box
  sx={{
    borderRadius: 2,
    padding: 2,
    maxWidth: 150,
    maxHeight: 200,
    overflowY: "auto",
    gap: 1,
  }}
>
  <SourceSelector
    onSelect={(selected) => {
      useSearchStore.getState().setSelectedSources(selected);
    }}
  />
 </Box> 
 <ActiveTABS />
 <Box

        className="buttons-container"
      >
        
        <Button  onClick={clearAll} sx={{
            fontSize: 13,
            color:'#6658d1',
            border:'solid 1px #6658d1'
        }}>
          Clear
        </Button>
        <Button
          variant="contained"
          type="submit"
          disableElevation
          sx={{
            backgroundColor: '#6658d1',
            color: '#fff',
            fontSize: 13,
            width:100,
            fontWeight:'bold',
            '&:hover': {
              backgroundColor: '#251f9a',
            },
          }}
        >
          Search
        </Button>
      </Box>
    </Box>
  );
}

export default BooleanSearch;
