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

Chart.register(LineElement, LinearScale, PointElement, CategoryScale, Filler, Tooltip);

const TrendAreaChart = () => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const labels = useSearchStore(state => state.trend_data?.labels || []);
  const dataTrend = useSearchStore(state => state.trend_data?.data || []);


    console.log('testing trends', dataTrend, labels)

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

    console.log('testing trends', dataTrend, labels)

    return () => {
      chartRef.current?.destroy();
    };
  }, [dataTrend, labels]);

  return (
    <div style={{ width: '100%' }}>
      <div style={{
        fontSize: '14px',
        fontWeight: '600',
        marginBottom: '8px',
        color: '#111827',
        textAlign: 'center',
      }}>
        📈 Mentions Trend
      </div>
      <div style={{ width: '100%', height: '200px', position: 'relative' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
};

export default React.memo(TrendAreaChart);
