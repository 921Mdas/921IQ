

import React from 'react';
import './Mentions.scss';
import { useSearchStore } from '../../../store';
import ResultsHeader from './ResultsBar';
import { 
  Box, 
  Card, 
  CardContent, 
  CircularProgress, 
  Typography,
  Link,
  Avatar
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import KeyboardReturnIcon from '@mui/icons-material/KeyboardReturn';
import { useState, useEffect } from 'react';

// Article list card component
export function NewsCard({ article }) {
  const { title, url, source_name, date, source_logo, country  } = article;
  const [logoUrl, setLogoUrl] = useState('/static/Images/news-icon.png');

  useEffect(() => {
    const validateLogo = (logo) => {
      try {
        if (logo && typeof logo === 'string') {
          if (logo.startsWith('data:image/')) {
            const base64Part = logo.split(',')[1];
            if (base64Part && window.atob(base64Part)) {
              return logo;
            }
          } else if (logo.startsWith('http')) {
            return logo;
          }
        }
        return null;
      } catch (e) {
        return null;
      }
    };

    const validLogo = validateLogo(source_logo);
    setLogoUrl(validLogo || '/static/Images/news-icon.png');
  }, [source_logo]);

  const handleImageError = (e) => {
    e.target.onerror = null;
    e.target.src = '/static/Images/news-icon.png';
  };

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'row',
      p: 2,
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      background:'white',
      borderRadius:'10px',
      marginBottom:'5px',
      marginTop:'5px'
    }}>
      <Box sx={{ display: 'flex', flexDirection: 'row', gap: 2 }}>
        <Avatar
          alt={source_name || 'News icon'}
          src={logoUrl}
          variant="rounded"
          sx={{ width: 40, height: 40 }}
          imgProps={{ onError: handleImageError }}
        />
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            {source_name || 'Unknown Source'} 
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
            {new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
           {' - '}
          {country}
            </Typography>

          </Box>
          <Link
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            underline="hover"
            sx={{ fontSize: 14, fontWeight: 480, mt: 1, color: '#111' }}
          >
            {title}
          </Link>
          
        </Box>
      </Box>
    </Box>
  );
}

// Main mentions component
const Mentions = () => {

  const articles = useSearchStore((state) => state.articles);
  const isLoading = useSearchStore((state) => state.isLoading);
  const total_articles = useSearchStore((state) => state.total_articles);

  return (
    <div className='mentions-container'>

      <div className="header_results">
             <ResultsHeader total={total_articles} />
      </div>
      
      {isLoading ? (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          height: '200px',
          width: '100%',
        }}>
          <CircularProgress />
        </Box>
      ) : Array.isArray(articles) && articles.length > 0 ? (
        articles.map((article, idx) => (
          <NewsCard article={article} key={`${article.url}-${idx}`} />
        ))
      ) : (
        <Card sx={{ 
          maxWidth: 600, 
          height:600,
          margin: '40px auto',
          textAlign: 'center',
          boxShadow: 'none',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '24px'
        }}>
        <SkeletonMsg />
        </Card>
      )}
    </div>
  );
};

// Skeleton Message

const SkeletonMsg = () => {
  return (
    <Box sx={{ textAlign: 'center', mt: 4 }}>
      <Typography 
        variant="h5" 
        sx={{ 
          mb: 3,
          fontWeight: 600,
          color: '#666666',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 1
        }}
      >
        <SearchIcon fontSize="medium" />
        No mentions found
      </Typography>
      
      <Typography 
        variant="body1" 
        color="text.secondary" 
        sx={{ mb: 4, maxWidth: 400, mx: 'auto' }}
      >
        Enter keywords to search for relevant articles and analytics
      </Typography>

      <Card sx={{
        maxWidth: 345,
        height: 400,
        margin: '0 auto',
        textAlign: 'left',
        boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.08)',
        border: 'none',
        borderRadius: '12px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {/* Skeleton Image Placeholder */}
        <Box sx={{
          height: 140,
          width: '100%',
          bgcolor: 'rgba(0, 0, 0, 0.04)',
        
        }} />
        
        <CardContent sx={{ pt: 3 }}>
          {/* Skeleton Title */}
          <Box sx={{
            height: 24,
            width: '80%',
            bgcolor: 'rgba(0, 0, 0, 0.06)',
            mb: 2,
            borderRadius: '4px',
           
          }} />
          
          {/* Skeleton Metadata */}
          <Box sx={{
            height: 16,
            width: '40%',
            bgcolor: 'rgba(0, 0, 0, 0.04)',
            mb: 3,
            borderRadius: '4px',
           
          }} />
          
          {/* Skeleton Paragraphs */}
          {[100, 90, 85, 70].map((width, index) => (
            <Box key={index} sx={{
              height: 16,
              width: `${width}%`,
              bgcolor: 'rgba(0, 0, 0, 0.04)',
              mb: 1.5,
              borderRadius: '4px',
            }} />
          ))}
        </CardContent>
        
   
      </Card>
    </Box>
  );
};

export default Mentions;
