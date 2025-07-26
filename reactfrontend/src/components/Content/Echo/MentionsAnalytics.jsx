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
import { shallow } from 'zustand/shallow';


// widgets
import WordCloud from './Widgets/WordCloud';
import TopPublicationsChart from './Widgets/TopPublications';
import TopCountriesChart from './Widgets/TopCountries';
import TrendAreaChart from './Widgets/TopTrends';
import AISummary from './Widgets/AiSummary';
import { useSearchStore } from '../../../store';

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

const MentionsAnalytics = () => {



  const isLoading = useSearchStore(state => state.isLoading);




  if (isLoading) {
    return <div className="loading-analytics">Loading analytics...</div>;
  }

  return (
    <div className="mentions-analytics">
      <div className="ai_summary">
        <AISummary  />
      </div>

      <div className="trend_line">
        <TrendAreaChart   />
      </div>

      <div className="word_cloud">
        <WordCloud />
      </div>

      <div className="top_pub">
        <TopPublicationsChart />
      </div>

      <div className="top_countries">
        <TopCountriesChart  />
      </div>
    </div>
  );
};




export default React.memo(MentionsAnalytics);