import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Skeleton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ThumbUpAltOutlinedIcon from '@mui/icons-material/ThumbUpAltOutlined';
import ThumbDownAltOutlinedIcon from '@mui/icons-material/ThumbDownAltOutlined';
import LoopIcon from '@mui/icons-material/Loop';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { useSearchStore } from '../../../../store';

const AISummary = () => {
  const summary = useSearchStore(state => state.summary);
  const isLoading = useSearchStore(state => state.isLoadingSummary);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: '10px',
        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)',
        p: isMobile ? 1 : 2,
        height: isMobile ? 'auto' : 170,
        minHeight: 140,
        position: 'relative'
      }}
    >
      <CardContent sx={{ p: 0 }}>
        {/* Title with MUI Icon */}
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <SmartToyIcon 
            fontSize={isMobile ? 'small' : 'medium'} 
            sx={{ color: '#666666' }} 
          />
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            fontSize={isMobile ? 11 : 16}
            sx={{ color: '#666666' }}
          >
            AI Summary
          </Typography>
        </Box>

        {isLoading ? (
          <AISummarySkeleton />
        ) : summary ? (
          <Typography
            variant="body2"
            color="text.primary"
            mb={2}
            sx={{
              fontSize: isMobile ? '0.75rem' : '0.85rem',
              minHeight: 80,
              lineHeight: 1.5,
            }}
          >
            {summary}
          </Typography>
        ) : (
          <AISummarySkeleton />
        )}

        {/* Action Buttons */}
        <Box
          display="flex"
          justifyContent="flex-start"
          flexWrap="wrap"
          gap={1}
          sx={{ 
            fontSize: '0.55rem', 
            position: 'absolute', 
            bottom: 10,
            left: isMobile ? 8 : 16
          }}
        >
          <Tooltip title="Like">
            <IconButton size="small" sx={{ p: 0.3 }}>
              <ThumbUpAltOutlinedIcon fontSize="inherit" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Dislike">
            <IconButton size="small" sx={{ p: 0.3 }}>
              <ThumbDownAltOutlinedIcon fontSize="inherit" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton size="small" sx={{ p: 0.3 }}>
              <LoopIcon fontSize="inherit" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Copy to Clipboard">
            <IconButton
              size="small"
              sx={{ p: 0.3 }}
              onClick={() => summary && navigator.clipboard.writeText(summary)}
            >
              <ContentCopyIcon fontSize="inherit" />
            </IconButton>
          </Tooltip>
        </Box>
      </CardContent>
    </Card>
  );
};

export const AISummarySkeleton = () => {
  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1.5,
        width: '100%',
        mt: 1,
        mb: 3
      }}
    >
      <Skeleton
        variant="rectangular"
        width="95%"
        height={12}
        animation="wave"
        sx={{ 
          borderRadius: 1,
          bgcolor: 'rgba(0, 0, 0, 0.04)'
        }}
      />
      <Skeleton
        variant="rectangular"
        width="80%"
        height={12}
        animation="wave"
        sx={{ 
          borderRadius: 1,
          bgcolor: 'rgba(0, 0, 0, 0.04)'
        }}
      />
      <Skeleton
        variant="rectangular"
        width="65%"
        height={12}
        animation="wave"
        sx={{ 
          borderRadius: 1,
          bgcolor: 'rgba(0, 0, 0, 0.04)'
        }}
      />
    </Box>
  );
};

export default AISummary;