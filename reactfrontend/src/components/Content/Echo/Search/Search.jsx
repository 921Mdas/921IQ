import "./Search.scss";
import React, { useState, useEffect } from "react";
import { TextField, Chip, Box, Button, Snackbar, Alert } from "@mui/material";
import { useSearchStore } from "../../../../store";
import { api } from "../../../../api";
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

// Enhanced error logging
const logError = (error, context) => {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    context,
    error: {
      message: error.message,
      stack: error.stack,
      ...(error.response && {
        status: error.response.status,
        data: error.response.data
      })
    }
  };
  console.error("Application Error:", errorInfo);
  return errorInfo;
};

window.testApi = api; // Expose to global scope for testing

function BooleanSearch() {
  const [keywords, setKeywords] = useState({ and: [], or: [], not: [] });
  const [inputs, setInputs] = useState({ and: "", or: "", not: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const selectedSources = useSearchStore(state => state.selectedSources);
  const setSelectedSources = useSearchStore(state => state.setSelectedSources);

  // Initialize from URL params with error handling
  useEffect(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      
      console.debug("Initializing from URL params:", {
        and: urlParams.getAll("and"),
        or: urlParams.getAll("or"),
        not: urlParams.getAll("not"),
        sources: urlParams.getAll("source")
      });

      setKeywords({
        and: urlParams.getAll("and"),
        or: urlParams.getAll("or"),
        not: urlParams.getAll("not"),
      });

      const sources = urlParams.getAll("source").filter(source => 
        source !== null && source !== "" && source !== "null" && source !== "undefined"
      );
      
      setSelectedSources(sources);
    } catch (err) {
      const errorInfo = logError(err, "URL params initialization");
      setError({
        message: "Failed to initialize search parameters",
        details: errorInfo
      });
    }
  }, [setSelectedSources]);

  // Enhanced submit handler with error handling
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      console.debug("Submitting search with:", { keywords, selectedSources });
      await handleSubmit(e, keywords, selectedSources);
    } catch (err) {
      const errorInfo = logError(err, "Search submission");
      setError({
        message: "Search failed",
        details: errorInfo,
        userMessage: "Failed to perform search. Please try again."
      });
    } finally {
      setLoading(false);
    }
  };

  // Render input group with error boundary
  const renderInputGroup = (type, label) => {
    try {
      return (
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
              onDelete={() => {
                try {
                  removeTag(type, tag, keywords, setKeywords, selectedSources);
                } catch (err) {
                  logError(err, `Removing tag: ${tag}`);
                }
              }}
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
            onKeyDown={(e) => {
              try {
                handleKeyDown(e, type, inputs, addTag, setInputs, keywords, setKeywords);
              } catch (err) {
                logError(err, "Keydown event");
              }
            }}
            onBlur={() => {
              try {
                handleBlur(type, inputs, addTag, setInputs, keywords, setKeywords);
              } catch (err) {
                logError(err, "Input blur event");
              }
            }}
            InputProps={{
              disableUnderline: true,
              sx: { ml: 1, minWidth: 120, flexGrow: 1 },
            }}
            inputProps={{ "aria-label": `${label} keywords input` }}
          />
        </Box>
      );
    } catch (err) {
      logError(err, `Rendering input group: ${type}`);
      return (
        <Box sx={{ color: 'error.main' }}>
          Error rendering {label} input
        </Box>
      );
    }
  };

  return (
    <>
      {/* Error notification */}
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
            onSelect={(selected) => {
              try {
                useSearchStore.getState().setSelectedSources(selected);
              } catch (err) {
                logError(err, "Source selection");
              }
            }}
          />
        </Box>
        
        <ActiveTABS />
        
        <Box className="buttons-container">
          <Button 
            onClick={() => {
              try {
                clearAll(setKeywords, setInputs);
              } catch (err) {
                logError(err, "Clear all");
              }
            }}
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
            disabled={loading}
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
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </Box>
      </Box>
    </>
  );
}

export default BooleanSearch;