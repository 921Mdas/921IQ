import React, { useRef, useEffect } from 'react';
import {
  Chart,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  Filler,
  Tooltip,
} from 'chart.js';
import { useSearchStore } from '../../../../store';
import { Box, Skeleton, Typography } from '@mui/material';
import ShowChartIcon from '@mui/icons-material/ShowChart';


Chart.register(LineElement, LinearScale, PointElement, CategoryScale, Filler, Tooltip);

const TrendAreaChart = () => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const labels = useSearchStore(state => state.trend_data?.labels || []);
  const dataTrend = useSearchStore(state => state.trend_data?.data || []);
  const isLoading = useSearchStore(state => state.isLoading);


  useEffect(() => {
    if (!labels.length || !canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          data: dataTrend,
          backgroundColor: 'rgba(79, 70, 229, 0.2)', // Indigo fill
          borderColor: 'transparent',
          pointRadius: 0,
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 20 },
        },
        plugins: {
          legend: { display: false },
          tooltip: { mode: 'index', intersect: false },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              display: true,
              color: '#9CA3AF',
              font: { size: 12 },
            },
          },
          y: {
            grid: { display: false },
            ticks: {
              display: true,
              color: '#9CA3AF',
              font: { size: 12 },
              padding: 4,
            },
            beginAtZero: true,
            suggestedMax: dataTrend.length ? Math.max(...dataTrend) + 2 : 10,
          },
        },
      },
    });


    return () => {
      chartRef.current?.destroy();
    };
  }, [dataTrend, labels, isLoading]);

  if (isLoading || !labels.length) {
    return <TrendChartSkeleton />;
  }

  return (
    <div style={{ width: '100%' }}>
      <Box sx={{
        fontSize: '16px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#666666',
        display: 'flex',
        alignItems: 'center'
      }}>
        <ShowChartIcon fontSize="small"sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          ml: 1,
          color: '#666666'
        }}>
          Mentions Trend
        </Typography>
      </Box>
      <div style={{ width: '100%', height: '200px', position: 'relative' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
};

export const TrendChartSkeleton = () => {
  return (
    <Box sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {/* Actual Title */}
      <Box sx={{
        fontSize: '16px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#666666',
        display: 'flex',
        alignItems: 'center'
      }}>
        <ShowChartIcon fontSize="small" sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          ml: 1,
          color: '#666666'
        }}>
          Mentions Trend
        </Typography>
      </Box>

      {/* Chart Skeleton Area */}
      <Box sx={{ 
        width: '100%', 
        height: 200, 
        position: 'relative',
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        px: 2,
        pb: 1,
        bgcolor: 'background.paper' // Ensures white background
      }}>
        {/* X-axis line */}
        <Box sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 1,
          bgcolor: 'rgba(0, 0, 0, 0.1)' // Very subtle axis line
        }} />
        
        {/* Y-axis line */}
        <Box sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          top: 0,
          width: 1,
          bgcolor: 'white' // Very subtle axis line
        }} />
        
        {/* Transparent gray bars */}
        {[...Array(10)].map((_, i) => (
          <Box 
            key={i} 
            sx={{
              width: 24,
              height: `${Math.random() * 70 + 30}%`,
              position: 'relative',
              overflow: 'hidden',
              borderRadius: '4px 4px 0 0',
              bgcolor: 'rgba(184, 183, 183, 0.1)', // Semi-transparent gray
            
            }}
          />
        ))}
      </Box>
    </Box>
  );
};


export default React.memo(TrendAreaChart);
