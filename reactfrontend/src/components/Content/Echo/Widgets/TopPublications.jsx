import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Box, Skeleton, Typography } from '@mui/material';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar } from 'react-chartjs-2';
import { useSearchStore } from '../../../../store';
import NewspaperIcon from '@mui/icons-material/Newspaper';

// Register required chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

const TopPublicationsSkeleton = () => {
  return (
    <Box sx={{ width: '100%', height: 400, p: 2 }}>
      {/* Title with MUI Icon */}
      <Box sx={{ display: 'flex', alignItems: 'center', pb: 2 }}>
        <NewspaperIcon fontSize="small" sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          pl: 1,
          color: '#666666'
        }}>
          Top 10 Media Sources
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
            <Skeleton 
              variant="text" 
              width={`${Math.random() * 40 + 30}%`} 
              height={20}
              sx={{ mb: 0.5 }}
            />
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

const TopPublicationsChart = React.memo(() => {
  const data = useSearchStore(state => state.top_publications);

  if (!Array.isArray(data) || data.length === 0) {
    return <TopPublicationsSkeleton />;
  }

  const chartData = {
    labels: data.map((item) => item.source_name),
    datasets: [
      {
        label: 'Number of Mentions',
        data: data.map((item) => item.count),
        backgroundColor: '#4F46E5',
        borderRadius: 4,
        barThickness: 20,
        clip: false,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        right: 40,
      },
    },
    plugins: {
      legend: { display: false },
      title: {
        display: false // Disabled since we use MUI title
      },
      datalabels: {
        anchor: 'end',
        align: 'end',
        clamp: true,
        clip: false,
        color: '#000',
        font: {
          weight: 'bold',
        },
        formatter: (value) => value,
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          display: false,
          drawBorder: false,
          borderWidth: 0,
        },
        ticks: {
          display: false,
          drawTicks: false,
        },
      },
      y: {
        grid: {
          display: false,
          drawBorder: false,
          borderWidth: 0,
        },
        ticks: {
          display: true,
          drawTicks: false,
          color: '#000',
          font: {
            weight: '500',
          },
        },
      },
    }
  };

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
        <NewspaperIcon fontSize="small" sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          pl: 1,
          color: '#666666'
        }}>
          Top 10 Media Sources
        </Typography>
      </Box>
      
      {/* Chart Area */}
      <Box sx={{ height: 'calc(100% - 40px)' }}>
        <Bar data={chartData} options={options} plugins={[ChartDataLabels]} />
      </Box>
    </Box>
  );
});

export default TopPublicationsChart;