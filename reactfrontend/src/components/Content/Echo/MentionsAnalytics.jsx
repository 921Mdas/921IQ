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




export default React.memo(MentionsAnalytics);