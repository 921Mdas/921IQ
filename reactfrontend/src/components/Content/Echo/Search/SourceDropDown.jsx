import React, { useEffect, useState } from "react";
import {
  Checkbox,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Menu,
  Box,
  Typography,
  Collapse,
  Divider,
  IconButton,
  Button,
  Stack,
} from "@mui/material";
import { useSearchStore } from "../../../../store";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ClearIcon from "@mui/icons-material/Clear";

import {sourceData} from './Sourcedata';

const NestedMenuItem = ({
  item,
  selectedSources,
  handleSelect,
  level = 0,
}) => {
  const [open, setOpen] = useState(false);
  const hasChildren = item.publications || item.subreddits;
  const children = item.publications || item.subreddits || [];

  // Get all child values (without parent prefix)
  const getAllChildValues = () => {
    return children.map(child => child.value);
  };

  // Check if all children are selected
  const allChildrenSelected = children.length > 0 && 
    children.every(child => selectedSources.includes(child.value));

  // Handle parent checkbox change
  const handleParentSelect = (value) => {
    const childValues = getAllChildValues();
    let newSelected = [...selectedSources];

    if (selectedSources.includes(value) || allChildrenSelected) {
      // Remove parent and all children
      newSelected = newSelected.filter(
        v => v !== value && !childValues.includes(v)
      );
    } else {
      // Add parent and all children
      if (!newSelected.includes(value)) newSelected.push(value);
      childValues.forEach(childValue => {
        if (!newSelected.includes(childValue)) {
          newSelected.push(childValue);
        }
      });
    }

    handleSelect(newSelected);
  };

  return (
    <>
      <MenuItem
        sx={{
          pl: 2 + level * 2,
          py: 0.5,
          "&:hover": { backgroundColor: "action.hover" },
        }}
      >
        <ListItemIcon sx={{ minWidth: 36 }}>
          <Checkbox
            edge="start"
            checked={selectedSources.includes(item.value) || allChildrenSelected}
            indeterminate={
              selectedSources.includes(item.value) && !allChildrenSelected
            }
            onChange={() => handleParentSelect(item.value)}
            size="small"
            disableRipple
          />
        </ListItemIcon>
        <ListItemText primary={item.label} />
        {hasChildren && (
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setOpen(!open);
            }}
            sx={{ p: 0.5 }}
          >
            {open ? (
              <ExpandLessIcon fontSize="small" />
            ) : (
              <ExpandMoreIcon fontSize="small" />
            )}
          </IconButton>
        )}
      </MenuItem>

      {hasChildren && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          {children.map((child) => (
            <NestedMenuItem
              key={child.value}
              item={child}
              selectedSources={selectedSources}
              handleSelect={handleSelect}
              level={level + 1}
            />
          ))}
        </Collapse>
      )}
    </>
  );
};

const SourceSelector = ({ onSelect }) => {
  const selectedSources = useSearchStore((state) => state.selectedSources);
  const setSelectedSources = useSearchStore((state) => state.setSelectedSources);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  // Get all country values (top-level only)
  const getAllCountryValues = () => {
    return sourceData.map(country => country.value);
  };

  // Initialize with all top-level country values only
  const initializeSources = () => {
    const countryValues = getAllCountryValues();
    setSelectedSources(countryValues);
    onSelect?.(countryValues);
  };

  useEffect(() => {
    initializeSources();
  }, []);

  const handleToggle = (event) => {
    setAnchorEl(anchorEl ? null : event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSelect = (newSelected) => {
    setSelectedSources(newSelected);
    onSelect?.(newSelected);
  };

  const handleClear = () => {
    // Completely clear all selections (including countries)
    setSelectedSources([]);
    onSelect?.([]);
  };

  return (
    <Box>
      <Box
        display="flex"
        alignItems="center"
        onClick={handleToggle}
        sx={{
          cursor: "pointer",
          "&:hover": { opacity: 0.8 },
        }}
      >
        <Typography variant="body1">Source type</Typography>
        <ExpandMoreIcon fontSize="small" sx={{ ml: 0.5 }} />
      </Box>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        PaperProps={{
          style: {
            maxHeight: "60vh",
            width: 300,
            overflow: "auto",
          },
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center" px={2} py={1}>
          <Typography variant="subtitle2">
            SELECTED ({selectedSources.length})
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              startIcon={<ClearIcon />}
              onClick={handleClear}
              size="small"
              sx={{ minWidth: 0 }}
            >
              Clear All
            </Button>
          
          </Stack>
        </Stack>
        <Divider />

        {sourceData.map((source, idx) => (
          <NestedMenuItem
            key={idx}
            item={source}
            selectedSources={selectedSources}
            handleSelect={handleSelect}
  
          />
        ))}
      </Menu>
    </Box>
  );
};

export default SourceSelector;