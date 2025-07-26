import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
import { useSearchStore } from '../../../../store';
import { Box, Skeleton, Typography } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const WordCloud = ({ width = 500, height = 300 }) => {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const words = useSearchStore(state => state.wordcloud_data);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);

    // Clear previous content
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    // Skip if no words
    if (!words || words.length === 0) {
      setIsLoading(false);
      return;
    }

    // Filter valid words
    const validWords = words.filter(
      word => word?.text && typeof word.size === 'number'
    );

    if (validWords.length === 0) {
      setIsLoading(false);
      return;
    }

    // Create SVG element
    const svg = d3.select(containerRef.current)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${width} ${height}`);

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Calculate sizes
    const maxSize = d3.max(validWords, d => d.size) || 1;
    const minSize = d3.min(validWords, d => d.size) || 1;
    const fontSizeScale = d3.scaleLinear()
      .domain([minSize, maxSize])
      .range([12, 60])
      .clamp(true);

    // Generate word cloud
    cloud()
      .size([width, height])
      .words(validWords.map(word => ({
        text: String(word.text).substring(0, 30),
        size: fontSizeScale(word.size),
        originalSize: word.size
      })))
      .padding(5)
      .rotate(() => 0)
      .font('sans-serif')
      .fontSize(d => d.size)
      .on('end', (cloudWords) => {
        if (!isMounted) return;

        g.selectAll('text')
          .data(cloudWords)
          .enter()
          .append('text')
          .attr('text-anchor', 'middle')
          .attr('transform', d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
          .style('font-size', d => `${d.size}px`)
          .style('fill', d => {
            const scale = d3.scaleLinear()
              .domain([0, maxSize * 0.5, maxSize])
              .range(['#6366f1', '#8b5cf6', '#ec4899']);
            return scale(d.originalSize);
          })
          .text(d => d.text);

        setIsLoading(false);
      })
      .start();

    return () => {
      isMounted = false;
      // Cleanup is handled by D3's selection.remove()
    };
  }, [words, width, height]);

  const showSkeleton = isLoading || !words?.length;

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      minHeight: `${height}px`,
      display: 'flex',
      flexDirection: 'column'
    }}>

 
      
      {/* Content Area */}
      <Box sx={{ 
        flex: 1,
        position: 'relative',
        overflow: 'hidden'
      }}>
        {showSkeleton ? (
          <>
          <TitleSkeleton />
          <WordCloudSkeleton />
          </>
        ) : (
          <>
          <TitleSkeleton />
          <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
          </>
        )}
      </Box>
    </Box>
  );
};

const WordCloudSkeleton = () => {
  const words = Array.from({ length: 12 }, () => ({
    width: Math.random() * 60 + 40,
    size: Math.random() * 24 + 12,
  }));

  return (
    <Box sx={{ 
      width: '100%',
      height: '100%',
      p: 2,
      display: 'flex',
      flexDirection: 'column'
    }}>
 

      {/* Skeleton Content */}
      <Box sx={{
        width: '100%', 
        flex: 1,
        display: 'flex',
        flexWrap: 'wrap',
        alignContent: 'center',
        justifyContent: 'center',
        gap: 2
      }}>
        {words.map((word, index) => (
          <Skeleton
            key={index}
            variant="text"
            width={`${word.width}px`}
            height={`${word.size}px`}
            sx={{
              bgcolor: 'rgba(120, 120, 120, 0.1)',
              borderRadius: '4px',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

const TitleSkeleton =()=>{
  return      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        pl: 2, 
        pb: 1,
        height: 40
      }}>
        <TrendingUpIcon fontSize="small" sx={{color:'#666666'}} />
        <Typography sx={{
          fontSize: 16,
          fontWeight: 'bold',
          pl: 1,
          color: '#666666'
        }}>
          Top Keywords
        </Typography>
      </Box>
}

export default WordCloud;