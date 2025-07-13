import React, { useEffect, useMemo, useRef } from 'react';
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Title,
  Legend,
  Tooltip as ChartTooltip,
} from 'chart.js';

// widgets
import WordCloud from './Widgets/WordCloud';
import TopPublicationsChart from './Widgets/TopPublications';
import TopCountriesChart from './Widgets/TopCountries';
import TrendAreaChart from './Widgets/TopTrends';
import AISummary from './Widgets/AiSummary';

import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Tooltip,
  Skeleton,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  ThumbUpAltOutlined as ThumbUpAltOutlinedIcon,
  ThumbDownAltOutlined as ThumbDownAltOutlinedIcon,
  Loop as LoopIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material';

// Register Chart.js components
Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Title,
  Legend,
  ChartTooltip
);

const MentionsAnalytics = ({data}) => {
//   const summary = useSearchStore(state => state.summary);
//   const isLoading = useSearchStore(state => state.isLoading);
// const top_publications = useSearchStore(state => state.top_publications || []);
// const top_countries = useSearchStore(state => state.top_countries || []);
// const wordcloud_data = useSearchStore(state => state.wordcloud_data || []);
// const trend_data = useSearchStore(state => state.trend_data || { labels: [], data: [] });

const {summary, isLoading, trend_data, wordcloud_data, top_publications, top_countries} = data;


  const summaryValue = useMemo(() => (
    typeof summary === 'string' ? summary : summary?.summary || ''
  ), [summary]);

  if (isLoading) {
    return <div className="loading-analytics">Loading analytics...</div>;
  }

  return (
    <div className="mentions-analytics">
      <div className="ai_summary">
        <AISummary summary={summaryValue} />
      </div>

      <div className="trend_line">
        <TrendAreaChart data={trend_data} />
      </div>

      <div className="word_cloud">
        <WordCloud words={wordcloud_data} />
      </div>

      <div className="top_pub">
        <TopPublicationsChart data={top_publications} />
      </div>

      <div className="top_countries">
        <TopCountriesChart data={top_countries} />
      </div>
    </div>
  );
};

// const AISummary = ({ summary }) => {
//   const isLoading = !summary;

//   return (
//     <Card
//       variant="outlined"
//       sx={{
//         border: '1px solid transparent',
//         borderImage: 'linear-gradient(to right,rgba(1, 1, 143, 0.22),rgba(24, 33, 201, 0.24)) 1',
//         borderRadius: 0,
//         boxShadow: 1,
//         p: 1,
//         height: 170
//       }}
//     >
//       <CardContent>
//         <Box display="flex" alignItems="center" gap={1} mb={1}>
//           <AutoAwesomeIcon color="secondary" fontSize="small" />
//           <Typography variant="subtitle2" fontWeight="bold" color="primary" fontSize={12}>
//             AI-Powered Insight
//           </Typography>
//         </Box>

//         {isLoading ? (
//           <Skeleton
//             variant="rectangular"
//             width="100%"
//             height={60}
//             animation="pulse"
//             sx={{
//               borderRadius: 1,
//               mb: 2,
//             }}
//           />
//         ) : (
//           <Typography variant="body2" color="text.primary" mb={2}>
//             {summary}
//           </Typography>
//         )}

//         <Box 
//           display="flex" 
//           justifyContent="flex-start" 
//           gap={0.5} 
//           sx={{ fontSize: '0.55rem' }}
//         >
//           <Tooltip title="Like">
//             <IconButton size="small" sx={{ p: 0.3 }}>
//               <ThumbUpAltOutlinedIcon fontSize="inherit" />
//             </IconButton>
//           </Tooltip>
//           <Tooltip title="Dislike">
//             <IconButton size="small" sx={{ p: 0.3 }}>
//               <ThumbDownAltOutlinedIcon fontSize="inherit" />
//             </IconButton>
//           </Tooltip>
//           <Tooltip title="Refresh">
//             <IconButton size="small" sx={{ p: 0.3 }}>
//               <LoopIcon fontSize="inherit" />
//             </IconButton>
//           </Tooltip>
//           <Tooltip title="Copy to Clipboard">
//             <IconButton 
//               size="small" 
//               sx={{ p: 0.3 }} 
//               onClick={() => navigator.clipboard.writeText(summary)}
//             >
//               <ContentCopyIcon fontSize="inherit" />
//             </IconButton>
//           </Tooltip>
//         </Box>
//       </CardContent>
//     </Card>
//   );
// };




export default React.memo(MentionsAnalytics);