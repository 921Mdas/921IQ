import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

const EmptyState = () => {
  return (
    <Box 
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        width: '100%',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          p: 4,
          maxWidth: 500,
          border: '1px dashed #ccc',
          backgroundColor: 'transparent',
        }}
      >
        <InfoOutlinedIcon 
          sx={{ 
            fontSize: 48, 
            color: 'text.secondary',
            mb: 2 
          }} 
        />
        <Typography 
          variant="h3" 
          gutterBottom
          sx={{ fontWeight: 500 }}
        >
          Start by filling out the search box above
        </Typography>
        <Typography 
          variant="body1" 
          color="text.secondary"
        >
          Search across multiple media  at once, review the results and gain further insights from the instant analytics.
        </Typography>
      </Paper>
    </Box>
  );
};

export default EmptyState;