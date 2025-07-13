import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(ChartDataLabels);

const countryFlagEmojiMap = {
  "Congo (DRC)": "🇨🇩",
  "United States": "🇺🇸",
  "France": "🇫🇷",
  // add more as needed
};

const TopCountriesChart = React.memo(({ data }) => {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const maxValue = Math.max(...data.map(d => d.count));


  useEffect(() => {
    if (!Array.isArray(data) || !canvasRef.current) return;

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
            display: true,
            text: '🌎 Top Countries by Mentions',
            font: { size: 14 },
            padding: { top: 10, bottom: 20, },
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
            max: maxValue + maxValue * 0.15, // 15% padding to the right
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
  }, [data]);

  return <canvas ref={canvasRef} style={{ width: '100%', height: 400 }} />;
});

export default TopCountriesChart;
