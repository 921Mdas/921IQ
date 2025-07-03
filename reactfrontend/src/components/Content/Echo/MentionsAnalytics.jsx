import React from 'react'
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
  Tooltip as ChartTooltip, // renamed to avoid conflict with MUI
} from 'chart.js';


import * as d3 from 'd3';
import cloud from 'd3-cloud';
import  { useEffect, useRef } from 'react';
import { useSearchStore } from '../../../store';

// material UI 
// components/AIInsightCard.jsx
import { Card, CardContent, Typography, Box, IconButton, Tooltip } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ThumbUpAltOutlinedIcon from '@mui/icons-material/ThumbUpAltOutlined';
import ThumbDownAltOutlinedIcon from '@mui/icons-material/ThumbDownAltOutlined';
import LoopIcon from '@mui/icons-material/Loop';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { Skeleton } from '@mui/material'; // 🆕 Add this import



// Register Chart.js components for your chart types
Chart.register(BarController, BarElement, CategoryScale, LinearScale, LineController, LineElement, PointElement, Title,ChartTooltip, Legend);

// graphs of real-time analytics to go side by side with UI mentions
const MentionsAnalytics = () => {

const summary = useSearchStore((state) => state.summary) || '';
const summaryValue = typeof summary === 'string' ? summary : summary?.summary || '';

const {trend_data, total_articles, wordcloud_data, top_publications, top_countries} = useSearchStore((state) => state)


console.log('testing wordcloud',wordcloud_data)


  // AI summary content
  return (
    <div className='mentions-analytics'>
      <div className="ai_summary">
        <AISummary summary={summaryValue} />
      </div>


      <div className='trend_line'>
        <TrendLineChart data={trend_data} />
      </div>


      <div className='word_cloud'>
        <WordCloud words={wordcloud_data} />
      </div>

      <div className='top_pub'>
        <TopPublicationsChart data={top_publications} />
      </div> 

       <div className='top_countries'>
        <TopCountriesChart data={top_countries} />
      </div>


    </div>
  );
};



// charts

function TopPublicationsChart({ data }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data) return;

    const ctx = canvasRef.current.getContext('2d');
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Number of Mentions',
          data: data.data,
          backgroundColor: '#4F46E5',
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Top 10 Media Sources',
            font: { size: 16 }
          }
        },
        scales: {
          x: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });

    return () => chart.destroy(); // cleanup on unmount
  }, [data]);

  return <canvas ref={canvasRef} />;
}



function WordCloud({ words }) {
  const ref = useRef();

  useEffect(() => {
    d3.select(ref.current).selectAll("*").remove();
    if (!words || words.length === 0) return;

    const width = 500;
    const height = 300;

    // Dynamically scale word sizes
    const maxWordSize = d3.max(words, d => d.size);
    const fontScale = d3.scaleLinear()
      .domain([0, maxWordSize])
      .range([10, 60]); // <-- adjust output size range here

    cloud()
      .size([width, height])
      .words(words.map(d => ({
        text: d.text,
        size: fontScale(d.size), // scaled size
      })))
      .padding(8)
      .rotate(() => 0)
      .font("sans-serif")
      .fontSize(d => d.size) // already scaled
      .on("end", draw)
      .start();

    function draw(words) {
      const svg = d3.select(ref.current)
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("preserveAspectRatio", "xMidYMid meet");

      svg.append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`)
        .selectAll("text")
        .data(words)
        .enter()
        .append("text")
        .style("font-size", d => `${d.size}px`) // use scaled size directly
        .style("fill", "#4F46E5")
        .attr("text-anchor", "middle")
        .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
        .text(d => d.text);
    }
  }, [words]);

  return (
    <div
      ref={ref}
      style={{
        width: "100%",
        height: "300px",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    />
  );
}



const AISummary = ({ summary }) => {
  const isLoading = !summary;

  return (
    <Card
      variant="outlined"
      sx={{
        border: '1px solid transparent',
        borderImage: 'linear-gradient(to right,rgba(1, 1, 143, 0.22),rgba(24, 33, 201, 0.24)) 1',
        borderRadius: 0,
        boxShadow: 1,
        p: 1,
        height:170
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <AutoAwesomeIcon color="secondary" fontSize="small" />
          <Typography variant="subtitle2" fontWeight="bold" color="primary" fontSize={12}>
            AI-Powered Insight
          </Typography>
        </Box>

        {isLoading ? (
          <Skeleton
            variant="rectangular"
            width="100%"
            height={60}
            animation="pulse"
            sx={{
              borderRadius: 1,
              mb: 2,
            }}
          />
        ) : (
          <Typography variant="body2" color="text.primary" mb={2}>
            {summary}
          </Typography>
        )}

      <Box 
  display="flex" 
  justifyContent="flex-start" 
  gap={0.5} 
  sx={{ fontSize: '0.55rem' }} // optional for text-based size reduction
>
  <Tooltip title="Like">
    <IconButton size="small" sx={{ p: 0.3 }}>
      <ThumbUpAltOutlinedIcon fontSize="inherit" />
    </IconButton>
  </Tooltip>
  <Tooltip title="Dislike">
    <IconButton size="small" sx={{ p: 0.3 }}>
      <ThumbDownAltOutlinedIcon fontSize="inherit" />
    </IconButton>
  </Tooltip>
  <Tooltip title="Refresh">
    <IconButton size="small" sx={{ p: 0.3 }}>
      <LoopIcon fontSize="inherit" />
    </IconButton>
  </Tooltip>
  <Tooltip title="Copy to Clipboard">
    <IconButton size="small" sx={{ p: 0.3 }} onClick={() => navigator.clipboard.writeText(summary)}>
      <ContentCopyIcon fontSize="inherit" />
    </IconButton>
  </Tooltip>
</Box>

      </CardContent>
    </Card>
  );
};

function TopCountriesChart({ data }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !Array.isArray(data)) return;

    const ctx = canvasRef.current.getContext('2d');

    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(d => d.country),
        datasets: [{
          label: 'Mentions',
          data: data.map(d => d.count),
          backgroundColor: '#4F46E5',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Top Countries by Mentions',
            font: { size: 16 }
          }
        },
        scales: {
          x: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });

    return () => chart.destroy();
  }, [data]);

  return <canvas ref={canvasRef} />;
}

function TrendLineChart({ data }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!data || !data.labels || !Array.isArray(data.labels)) return;

    const ctx = canvasRef.current.getContext('2d');

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Mentions Over Time',
          data: data.data,
          fill: false,
          borderColor: '#4F46E5',
          tension: 0.3,
          pointRadius: 2
        }]
      },
      options: {
        responsive: true,          // <-- Important for resizing
        maintainAspectRatio: false, // <-- Important to allow height stretch
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Trend Over Time',
            font: { size: 16 }
          },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          x: { title: { display: true, text: 'Date' } },
          y: { beginAtZero: true, title: { display: true, text: 'Mentions' } }
        }
      }
    });

    return () => chart.destroy();
  }, [data]);

  return (
    <div style={{ width: '100%', height: '300px', position: 'relative' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}



export default MentionsAnalytics