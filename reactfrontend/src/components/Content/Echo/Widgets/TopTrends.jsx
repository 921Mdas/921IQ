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

Chart.register(LineElement, LinearScale, PointElement, CategoryScale, Filler, Tooltip);

const TrendAreaChart = React.memo(({ data }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  console.log('testing trend data', data);

  useEffect(() => {
    if (!data?.labels?.length || !canvasRef.current) return;

    const ctx = canvasRef.current.getContext('2d');

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data,
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
          padding: {
            top: 20, // Add some top padding to avoid clipping
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: { mode: 'index', intersect: false },
          title: { display: false },
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
              display: true,       // Show y-axis labels
              color: '#9CA3AF',
              font: { size: 12 },
              padding: 4,
            },
            beginAtZero: true,
            suggestedMax: data?.data?.length ? Math.max(...data.data) + 2 : 10, // Headroom above max data point
          },
        },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [data]);

  return (
    <div style={{ width: '100%' }}>
      <div
        style={{
          fontSize: '14px',
          fontWeight: '600',
          marginBottom: '8px',
          color: '#111827', // Tailwind's gray-900
          textAlign: 'center',
        }}
      >
        📈 Mentions Trend
      </div>
      <div style={{ width: '100%', height: '200px', position: 'relative' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
});

export default TrendAreaChart;
