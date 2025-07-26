import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Box, Skeleton, Typography } from '@mui/material';
import { useSearchStore } from '../../../../store';
import PublicIcon from '@mui/icons-material/Public';

Chart.register(ChartDataLabels);

const countryFlagEmojiMap = {
  "Congo (DRC)": "🇨🇩",
  "United States": "🇺🇸",
  "France": "🇫🇷",
  // add more as needed
};

// Skeleton Component
const TopCountriesSkeleton = () => {
  return (
    <Box sx={{ width: '100%', height: 400, p: 2 }}>
      {/* Title with MUI Icon */}
      <Box sx={{ display: 'flex', alignItems: 'center', pb: 2 }}>
        <PublicIcon fontSize="small" sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          pl: 1,
          color: '#666666'
        }}>
          Top Countries by Mentions
        </Typography>
      </Box>

      {/* Horizontal Bars Skeleton */}
      <Box sx={{ 
        width: '100%', 
        height: 'calc(100% - 40px)',
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {[...Array(5)].map((_, i) => (
          <Box key={i} sx={{ width: '100%' }}>
            {/* Country name with flag skeleton */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Skeleton variant="circular" width={20} height={20} sx={{ mr: 1 }} />
              <Skeleton variant="text" width={`${Math.random() * 40 + 30}%`} height={20} />
            </Box>
            {/* Bar */}
            <Skeleton
              variant="rectangular"
              width={`${100 - (i * 15)}%`}
              height={20}
              sx={{ 
                borderRadius: '4px',
                animation: 'pulse 1.5s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 0.6 },
                  '50%': { opacity: 0.3 },
                  '100%': { opacity: 0.6 }
                }
              }}
            />
          </Box>
        ))}
      </Box>
    </Box>
  );
};

const TopCountriesChart = React.memo(() => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const data = useSearchStore(state => state.top_countries);
  const maxValue = data?.length ? Math.max(...data.map(d => d.count)) : 0;

  useEffect(() => {
    if (!Array.isArray(data) || data.length === 0 || !canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.country),
        datasets: [
          {
            label: 'Mentions',
            data: data.map(d => d.count),
            backgroundColor: '#4F46E5',
            borderRadius: 4,
            barThickness: 20,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: {
            display: false // Disable Chart.js title since we're using MUI
          },
          datalabels: {
            display: true,
            anchor: 'end',
            align: 'end',
            color: '#000',
            font: { weight: 'bold' },
            formatter: (value) => value,
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            max: maxValue + maxValue * 0.15,
            grid: { display: false, drawBorder: false, borderWidth: 0 },
            ticks: { display: false, drawTicks: false, precision: 0 },
          },
          y: {
            grid: { display: false, drawBorder: false, borderWidth: 0 },
            ticks: {
              display: true,
              drawTicks: false,
              color: '#000',
              font: { weight: '500' },
              callback: function(value) {
                const label = this.getLabelForValue(value);
                const flag = countryFlagEmojiMap[label] || "";
                return flag + " " + label;
              },
            },
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data, maxValue]);

  if (!Array.isArray(data) || data.length === 0) {
    return <TopCountriesSkeleton />;
  }

  return (
    <Box sx={{ width: '100%', height: 400 }}>
      {/* MUI Title Section */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        pl: 2, 
        pb: 1,
        height: 40
      }}>
        <PublicIcon fontSize="small" sx={{color:'#666666'}}/>
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          pl: 1,
          color: '#666666'
        }}>
          Top Countries by Mentions
        </Typography>
      </Box>
      
      {/* Chart Area */}
      <Box sx={{ height: 'calc(100% - 40px)' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
      </Box>
    </Box>
  );
});

export default TopCountriesChart;