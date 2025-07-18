import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
import { useSearchStore } from '../../../../store';

const WordCloud = ({  width = 500, height = 300, title = " ↑ Top Keywords" }) => {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const layoutInstance = useRef(null);
  const svgRef = useRef(null);
  const words = useSearchStore(state => state.wordcloud_data)

  // Cleanup function
  const cleanup = () => {
    if (layoutInstance.current) {
      layoutInstance.current.stop();
      layoutInstance.current = null;
    }

    if (containerRef.current && svgRef.current) {
      try {
        if (containerRef.current.contains(svgRef.current)) {
          containerRef.current.removeChild(svgRef.current);
        }
      } catch (err) {
        console.warn('Cleanup error:', err);
      }
      svgRef.current = null;
    }
  };

  useEffect(() => {
    let isMounted = true;

    const initializeWordCloud = () => {
      try {
        if (!Array.isArray(words) || words.length === 0) {
          throw new Error(words ? 'Empty words array' : 'No words provided');
        }

        const validWords = words.filter(
          word => word?.text && typeof word.size === 'number'
        );

        if (validWords.length === 0) {
          throw new Error('No valid words found');
        }

        cleanup();

        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        svgRef.current = svg;

        const maxSize = d3.max(validWords, d => d.size) || 1;
        const minSize = d3.min(validWords, d => d.size) || 1;
        const fontSizeScale = d3.scaleLinear()
          .domain([minSize, maxSize])
          .range([12, 60])
          .clamp(true);

        layoutInstance.current = cloud()
          .size([width, height])
          .words(validWords.map(word => ({
            text: String(word.text).substring(0, 30),
            size: fontSizeScale(word.size),
            originalSize: word.size
          })))
          .padding(5)
          .rotate(() => 10 - 10) // Fixed rotation
          .font('sans-serif')
          .fontSize(d => d.size)
          .on('end', (cloudWords) => {
            if (!isMounted) return;

            try {
              while (svg.firstChild) {
                svg.removeChild(svg.firstChild);
              }

              // Add title to SVG
              const titleText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
              titleText.setAttribute('x', width / 2);
              titleText.setAttribute('y', 10);
              titleText.setAttribute('text-anchor', 'middle');
              titleText.style.fontSize = '11px';
              titleText.style.fontWeight = '600';
              titleText.style.fill = '#334155';
              titleText.textContent = title;
              svg.appendChild(titleText);

              // Word group shifted down to not overlap with title
              const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
              g.setAttribute('transform', `translate(${width / 2}, ${height / 2 + 10})`);
              svg.appendChild(g);

              cloudWords.forEach(word => {
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('transform', `translate(${word.x},${word.y})rotate(${word.rotate})`);
                text.style.fontSize = `${word.size}px`;
                text.style.fill = getColorForSize(word.originalSize, maxSize);
                text.textContent = word.text;
                g.appendChild(text);
              });

              if (containerRef.current && !containerRef.current.contains(svg)) {
                containerRef.current.appendChild(svg);
              }

              setIsLoading(false);
              setError(null);
            } catch (err) {
              if (isMounted) {
                setError('Failed to render words');
                setIsLoading(false);
              }
            }
          });

        layoutInstance.current.start();
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          setIsLoading(false);
        }
      }
    };

    const timer = setTimeout(initializeWordCloud, 50);

    return () => {
      isMounted = false;
      clearTimeout(timer);
      cleanup();
    };
  }, [words, width, height, title]);

  const getColorForSize = (size, maxSize) => {
    const scale = d3.scaleLinear()
      .domain([0, maxSize * 0.5, maxSize])
      .range(['#6366f1', '#8b5cf6', '#ec4899']);
    return scale(size);
  };

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        minHeight: `${height}px`,
        position: 'relative',
        borderRadius: '8px',
        overflow: 'hidden',
        paddingTop: '0px',
      }}
    >
      {isLoading && !error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#64748b',
          fontSize: '14px'
        }}>
          Generating word cloud...
        </div>
      )}

      {error && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#ef4444',
          padding: '16px',
          textAlign: 'center',
          maxWidth: '80%'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
            Failed to generate word cloud
          </div>
          <div style={{ fontSize: '13px', color: '#6b7280' }}>
            {error}
          </div>
        </div>
      )}
    </div>
  );
};

export default WordCloud;
