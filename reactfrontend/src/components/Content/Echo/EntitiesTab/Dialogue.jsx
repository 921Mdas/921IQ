import {
  Typography,
  Box,
  Chip,
  Divider,
  Stack,
  LinearProgress,
  IconButton,
} from '@mui/material';
import {
  TrendingUp,
  Article,
  Source,
  Public,
  SentimentSatisfied,
  SentimentDissatisfied,
  Close,
} from '@mui/icons-material';

export default function PersonaDialog({ selectedEntity, onClose }) {
 const sentiment = selectedEntity?.sentiment || {};
const sentimentTotal =
  sentiment.positive + sentiment.negative + sentiment.neutral || 1;

const positivePercent = (sentiment.positive / sentimentTotal) * 100;
const negativePercent = (sentiment.negative / sentimentTotal) * 100;
const neutralPercent = (sentiment.neutral / sentimentTotal) * 100;

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        zIndex: 1300,
        width: '100vw',
        height: '100vh',
        bgcolor: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 600,
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: 24,
          p: 4,
          position: 'relative',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
      >
        {/* Close Button */}
        <IconButton
          onClick={onClose}
          sx={{ position: 'absolute', top: 8, right: 8 }}
          color="default"
        >
          <Close />
        </IconButton>

        {/* Content */}
        <Box display="flex" flexDirection="column" gap={2}>
          <Typography variant="h6" fontWeight="bold">
            {selectedEntity?.name || 'Unknown Entity'}
          </Typography>

          <Stack direction="row" spacing={2} alignItems="center">
            <TrendingUp color="primary" />
            <Typography>Total Mentions: {selectedEntity?.count}</Typography>

            <Article color="primary" />
            <Typography>Articles: {selectedEntity?.article_count}</Typography>
          </Stack>

          <Stack direction="row" spacing={2} alignItems="center">
            <Source color="primary" />
            <Typography>Sources: {selectedEntity?.source_diversity}</Typography>

            <Public color="primary" />
            <Typography>
              Countries: {selectedEntity?.country_coverage?.join(', ') || 'N/A'}
            </Typography>
          </Stack>

          <Divider />

          <Typography variant="subtitle2" gutterBottom>
            Related Topics:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {selectedEntity?.top_topics?.length ? (
              selectedEntity.top_topics.map((t, i) => (
                <Chip key={i} label={t} variant="outlined" color="secondary" />
              ))
            ) : (
              <Typography variant="body2" color="textSecondary">
                None
              </Typography>
            )}
          </Box>

          <Divider />

          <Typography variant="subtitle2" gutterBottom>
            Sentiment
          </Typography>

    <Stack direction="row" spacing={1} alignItems="center">
            <SentimentSatisfied color="success" />
            <Typography variant="body2">
              Positive: {selectedEntity?.sentiment.positive}
            </Typography>

            <SentimentDissatisfied color="error" />
            <Typography variant="body2">
              Negative: {selectedEntity?.sentiment.negative}
            </Typography>

  <SentimentSatisfied color="disabled" />
  <Typography variant="body2">
    Neutral: {sentiment.neutral}
  </Typography>
</Stack>

     <Box mt={1}>
  {/* Composite Sentiment Progress Bar */}
  <Box
    sx={{
      height: 10,
      borderRadius: 5,
      backgroundColor: '#eceff1',
      overflow: 'hidden',
      display: 'flex',
    }}
  >
    <Box
      sx={{
        width: `${positivePercent}%`,
        backgroundColor: '#4caf50',
      }}
    />
    <Box
      sx={{
        width: `${neutralPercent}%`,
        backgroundColor: '#9e9e9e',
      }}
    />
    <Box
      sx={{
        width: `${negativePercent}%`,
        backgroundColor: '#f44336',
      }}
    />
  </Box>

   <Box display="flex"  justifyContent="space-between" mt={0.5}>
    <Typography variant="caption" color="success.main">
      Positive {positivePercent.toFixed(0)}%
    </Typography>
    <Typography variant="caption" color="text.secondary">
      Neutral {neutralPercent.toFixed(0)}%
    </Typography>
    <Typography variant="caption" color="error.main">
      Negative {negativePercent.toFixed(0)}%
    </Typography>
  </Box>

  {/* Wikipedia Section */}
</Box>
{selectedEntity?.wiki_summary && (
  <>
    <Divider />



    {/* Image and summary layout */}
    <Box display="flex" gap={2} flexDirection={{ xs: 'column', sm: 'row' }} alignItems="flex-start">
      {selectedEntity?.wiki_image && (
        <Box
          component="img"
          src={selectedEntity.wiki_image}
          alt={`${selectedEntity.name} portrait`}
          sx={{
            width: 120,
            height: 120,
            borderRadius: 2,
            objectFit: 'cover',
            flexShrink: 0,
            boxShadow: 2,
          }}
        />
      )}
      <Box>
        <Typography variant="body2" color="text.secondary" whiteSpace="pre-line">
          {selectedEntity.wiki_summary}
        </Typography>

      </Box>
    </Box>
  </>
)}
        </Box>
      </Box>
    </Box>
  );
}