

// import "./Search.scss";
// import React, { useState, useEffect, useCallback } from "react";
// import { TextField, Chip, Box, Button, Snackbar, Alert } from "@mui/material";
// import { useSearchStore } from "../../../../store";
// import { handleSubmit } from "./HandleSubmit";
// import SourceSelector from "./SourceDropDown";
// import ActiveTABS from "../ActiveTABS";
// import {
//   removeTag,
//   addTag,
//   handleKeyDown,
//   handleBlur,
//   clearAll
// } from "./formHelpers";

// const BooleanSearch = () => {
//   // Local state
//   const [keywords, setKeywords] = useState({ and: [], or: [], not: [] });
//   const [inputs, setInputs] = useState({ and: "", or: "", not: "" });
//   const [error, setError] = useState(null);

//   // Zustand store with direct selectors
//   const selectedSources = useSearchStore(state => state.selectedSources);
//   const setSelectedSources = useSearchStore(state => state.setSelectedSources);
//   const isLoading = useSearchStore(state => state.isLoading);
//   const setIsLoading = useSearchStore(state => state.setLoading);

//   // Initialize from URL params - runs only once
//   useEffect(() => {
//     const initializeFromUrl = () => {
//       try {
//         const urlParams = new URLSearchParams(window.location.search);
        
//         setKeywords({
//           and: urlParams.getAll("and"),
//           or: urlParams.getAll("or"),
//           not: urlParams.getAll("not"),
//         });

//         const sources = urlParams.getAll("source").filter(Boolean);
//         setSelectedSources(sources);
//       } catch (err) {
//         console.error("Initialization error:", err);
//         setError({
//           message: "Failed to initialize search parameters",
//           details: err
//         });
//       }
//     };

//     initializeFromUrl();
//   }, [setSelectedSources]);

//   // Stable handlers
//   const handleSourceSelect = useCallback((selected) => {
//     setSelectedSources(selected);
//   }, [setSelectedSources]);

//   const handleFormSubmit = useCallback(async (e) => {
//     e.preventDefault();
//     setIsLoading(true);
//     setError(null);
    
//     try {
//       await handleSubmit(e, keywords, selectedSources);
//     } catch (err) {
//       console.error("Search error:", err);
//       setError({
//         message: "Search failed",
//         details: err,
//         userMessage: "Failed to perform search. Please try again."
//       });
//     } finally {
//       setIsLoading(false);
//     }
//   }, [keywords, selectedSources, setIsLoading]);

//   const handleClear = useCallback(() => {
//     clearAll(setKeywords, setInputs);
//   }, []);

//   // Render function for input groups
//   const renderInputGroup = (type, label) => (
//     <Box
//       sx={{
//         border: "1px solid rgba(207, 207, 207, 0.44)",
//         borderRadius: 2,
//         padding: 1,
//         display: "flex",
//         flexWrap: "wrap",
//         gap: 0.5,
//         backgroundColor: "white",
//         minWidth: 300,
//         flexGrow: 1,
//       }}
//     >
//       {keywords[type].map((tag) => (
//         <Chip
//           key={tag}
//           label={tag}
//           onDelete={() => removeTag(type, tag, keywords, setKeywords, selectedSources)}
//           sx={{ backgroundColor: "#6c5ce7", color: "white" }}
//         />
//       ))}
//       <TextField
//         variant="standard"
//         placeholder={`${label}...`}
//         sx={{ width: '100%',
//           backgroundColor: "white", // Restore this
//     color: "white", // Restore this
//          }}
//         value={inputs[type]}
//         onChange={(e) => setInputs(prev => ({ ...prev, [type]: e.target.value }))}
//         onKeyDown={(e) => handleKeyDown(e, type, inputs, addTag, setInputs, keywords, setKeywords)}
//         onBlur={() => handleBlur(type, inputs, addTag, setInputs, keywords, setKeywords)}
//         InputProps={{
//           disableUnderline: true,
//           sx: { ml: 1, minWidth: 120, flexGrow: 1 },
//         }}
//       />
//     </Box>
//   );

//   return (
//     <>
//       <Snackbar
//         open={!!error}
//         autoHideDuration={6000}
//         onClose={() => setError(null)}
//         anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
//       >
//         <Alert severity="error" onClose={() => setError(null)}>
//           {error?.userMessage || "An unexpected error occurred"}
//         </Alert>
//       </Snackbar>

//       <Box
//         component="form"
//         onSubmit={handleFormSubmit}
//         className="boolean-search-form"
//         sx={{
//           mx: "auto",
//           display: "grid",
//           gap: 1,
//           gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
//           alignItems: "center",
//           padding: '1em'
//         }}
//           noValidate  // Restore this
//   autoComplete="off"  // Restore this
//       >
//         {renderInputGroup("and", "Keyword AND")}
//         {renderInputGroup("or", "Keyword OR")}
//         {renderInputGroup("not", "Keyword NOT")}
        
//         <Box sx={{ padding: 2, maxWidth: 150, maxHeight: 200 }}>
//           <SourceSelector
//             selectedSources={selectedSources}
//             onSelect={handleSourceSelect}
//           />
//         </Box>
        
//         <ActiveTABS />
        
//         <Box sx={{ display: 'flex', gap: 1 }}>
//           <Button 
//             onClick={handleClear}
//             sx={{
//               fontSize: 13,
//               color: '#6658d1',
//               border: 'solid 1px #6658d1'
//             }}
//           >
//             Clear
//           </Button>
//           <Button
//             variant="contained"
//             type="submit"
//             disabled={isLoading}
//             sx={{
//               backgroundColor: '#6658d1',
//               color: '#fff',
//               fontSize: 13,
//               width: 100,
//               fontWeight: 'bold',
//               '&:hover': { backgroundColor: '#251f9a' },
//               '&:disabled': { backgroundColor: '#cccccc' }
//             }}
//           >
//             {isLoading ? 'Searching...' : 'Search'}
//           </Button>
//         </Box>
//       </Box>
//     </>
//   );
// };

// export default BooleanSearch;


import "./Search.scss";
import React, { useState, useEffect, useCallback } from "react";
import { TextField, Chip, Box, Button, Snackbar, Alert } from "@mui/material";
import { useSearchStore } from "../../../../store";
import { handleSubmit } from "./HandleSubmit";
import SourceSelector from "./SourceDropDown";
import ActiveTABS from "../ActiveTABS";
import {
  removeTag,
  addTag,
  handleKeyDown,
  handleBlur,
  clearAll
} from "./formHelpers";

const BooleanSearch = () => {
  // Local state
  const [keywords, setKeywords] = useState({ and: [], or: [], not: [] });
  const [inputs, setInputs] = useState({ and: "", or: "", not: "" });
  const [error, setError] = useState(null);

  // Zustand store with direct selectors
  const selectedSources = useSearchStore(state => state.selectedSources);
  const setSelectedSources = useSearchStore(state => state.setSelectedSources);
  const isLoading = useSearchStore(state => state.isLoading);
  const setIsLoading = useSearchStore(state => state.setLoading);

  // Initialize from URL params - runs only once
  useEffect(() => {
    const initializeFromUrl = () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        
        setKeywords({
          and: urlParams.getAll("and"),
          or: urlParams.getAll("or"),
          not: urlParams.getAll("not"),
        });

        const sources = urlParams.getAll("source").filter(Boolean);
        setSelectedSources(sources);
      } catch (err) {
        console.error("Initialization error:", err);
        setError({
          message: "Failed to initialize search parameters",
          details: err
        });
      }
    };

    initializeFromUrl();
  }, [setSelectedSources]);

  // Stable handlers
  const handleSourceSelect = useCallback((selected) => {
    setSelectedSources(selected);
  }, [setSelectedSources]);

  const handleFormSubmit = useCallback(async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      await handleSubmit(e, keywords, selectedSources);
    } catch (err) {
      console.error("Search error:", err);
      setError({
        message: "Search failed",
        details: err,
        userMessage: "Failed to perform search. Please try again."
      });
    } finally {
      setIsLoading(false);
    }
  }, [keywords, selectedSources, setIsLoading]);

  const handleClear = useCallback(() => {
    clearAll(setKeywords, setInputs);
  }, []);

  // Render function for input groups
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
          onDelete={() => removeTag(type, tag, keywords, setKeywords, selectedSources)}
          sx={{ backgroundColor: "#6c5ce7", color: "white" }}
        />
      ))}
      <TextField
        variant="standard"
        placeholder={`${label}...`}
        sx={{ 
          backgroundColor: "white",
          color: "white", 
          width: '100%' 
        }}
        value={inputs[type]}
        onChange={(e) => setInputs(prev => ({ ...prev, [type]: e.target.value }))}
        onKeyDown={(e) => handleKeyDown(e, type, inputs, addTag, setInputs, keywords, setKeywords)}
        onBlur={() => handleBlur(type, inputs, addTag, setInputs, keywords, setKeywords)}
        InputProps={{
          disableUnderline: true,
          sx: { ml: 1, minWidth: 120, flexGrow: 1 },
        }}
        inputProps={{ "aria-label": `${label} keywords input` }}
      />
    </Box>
  );

  return (
    <>
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error?.userMessage || "An unexpected error occurred"}
        </Alert>
      </Snackbar>

      <Box
        component="form"
        onSubmit={handleFormSubmit}
        className="boolean-search-form"
        sx={{
          mx: "auto",
          display: "grid",
          gap: 1,
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          alignItems: "center",
          padding: '1em'
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
            selectedSources={selectedSources}
            onSelect={handleSourceSelect}
          />
        </Box>
        
        <ActiveTABS />
        
        <Box className="buttons-container">
          <Button 
            onClick={handleClear}
            sx={{
              fontSize: 13,
              color: '#6658d1',
              border: 'solid 1px #6658d1'
            }}
          >
            Clear
          </Button>
          <Button
            variant="contained"
            type="submit"
            disabled={isLoading}
            disableElevation
            sx={{
              backgroundColor: '#6658d1',
              color: '#fff',
              fontSize: 13,
              width: 100,
              fontWeight: 'bold',
              '&:hover': {
                backgroundColor: '#251f9a',
              },
              '&:disabled': {
                backgroundColor: '#cccccc'
              }
            }}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </Button>
        </Box>
      </Box>
    </>
  );
};

export default BooleanSearch;