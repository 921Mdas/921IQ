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

import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ThumbUpAltOutlinedIcon from '@mui/icons-material/ThumbUpAltOutlined';
import ThumbDownAltOutlinedIcon from '@mui/icons-material/ThumbDownAltOutlined';
import LoopIcon from '@mui/icons-material/Loop';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const AISummary = ({ summary }) => {
  const isLoading = !summary;
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: '10px',
        boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
        p: isMobile ? 1 : 2,
        height: isMobile ? 'auto' : 170,
        minHeight: 140,
        position:'relative'
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            fontSize={isMobile ? 11 : 16}
            sx={{
              color:
"#6658d1"
            }}
          >
            🤖 AI Summary
          </Typography>
        </Box>

        {isLoading ? (
          <Skeleton
            variant="rectangular"
            width="100%"
            height={60}
            animation="pulse"
            sx={{ borderRadius: 1, mb: 2 }}
          />
        ) : (
          <Typography
            variant="body2"
            color="text.primary"
            mb={2}
            sx={{
              fontSize: isMobile ? '0.75rem' : '0.85rem',
              minHeight:80,
              lineHeight: 1.5,
            }}
          >
            {summary}
          </Typography>
        )}

        <Box
          display="flex"
          justifyContent="flex-start"
          flexWrap="wrap"
          gap={1}
          sx={{ fontSize: '0.55rem',  position:'absolute', bottom:10 }}
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
              onClick={() => navigator.clipboard.writeText(summary)}
            >
              <ContentCopyIcon fontSize="inherit" />
            </IconButton>
          </Tooltip>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AISummary;
