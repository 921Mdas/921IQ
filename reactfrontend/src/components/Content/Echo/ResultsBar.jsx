import React from 'react';
import { Typography, Chip, Box, Divider } from '@mui/material';
import { Sort } from '@mui/icons-material';

const ResultsHeader = ({total}) => {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, background:
"white", borderRadius:'10px',color:'#6658d1',
      position:'sticky', top:0, zIndex:10
   
      }}>
      <Typography variant="h7" sx={{fontWeight:'bold'}} component="div">
        {total <= 1 ?  `${total} Result` : `${total} Results` } 
      </Typography>
    
    </Box>
  );
};

export default ResultsHeader;