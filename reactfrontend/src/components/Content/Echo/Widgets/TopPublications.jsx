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
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar } from 'react-chartjs-2';
import { Box, Typography } from '@mui/material';
import { useSearchStore } from '../../../../store';

// Register required chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels // Register the plugin
);

const TopPublicationsChart = React.memo(() => {

  const data = useSearchStore(state => state.top_publications)



  if (!Array.isArray(data) || data.length === 0) {
    return (
      <Box textAlign="center" p={2}>
        <Typography>No publication data to display.</Typography>
      </Box>
    );
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
      clip: false, // 👈 important for label visibility
    },
  ],
};


const options = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: {
      right: 40, // 👈 ensures label fits at the end
    },
  },
  plugins: {
    legend: { display: false },
    title: {
      display: true,
      text: '📰 Top 10 Media Sources',
      font: { size: 14 },
      padding: { top: 10, bottom: 20 },
    },
    datalabels: {
      anchor: 'end',
      align: 'end',
      clamp: true, // 👈 prevents labels from going too far outside
      clip: false, // 👈 allows overflow outside the chart area
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
      display: true,  // show labels
      drawTicks: false, // hide small tick lines
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
      <Bar data={chartData} options={options} plugins={[ChartDataLabels]} />
    </Box>
  );
});

export default TopPublicationsChart;
