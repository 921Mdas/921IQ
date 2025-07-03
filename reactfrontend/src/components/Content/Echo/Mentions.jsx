import React from 'react'
import './Mentions.scss';
import { useSearchStore } from '../../../store';

// Material UI imports
import { Box } from '@mui/material';
import Link from '@mui/material/Link'; // ✅ correct
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';
import {  Chip } from '@mui/material';



// article list card
// export function NewsCard({ article }) {
//   const { title, url, source_name, date, source_logo } = article;

//   return (
//     <Box className="news-card">
//       <Avatar
//         className="article-image"
//         alt={source_name || 'News icon'}
//         src={source_logo}
//         imgProps={{
//           onError: (e) => {
//             e.target.onerror = null;
//             e.target.src = '/static/Images/news-icon.png';
//           },
//         }}
//         variant="square"
//       />
//       <Box className="article-info">
//         <Link
//           href={url}
//           target="_blank"
//           rel="noopener noreferrer"
//           className="article-title"
//         >
//           {title}
//         </Link>
//         <Typography className="article-date">
//           {new Date(date).toLocaleDateString()}
//         </Typography>
//         <Typography className="source-name">
//           {source_name || <span className="missing">No source_name found</span>}
//         </Typography>
//       </Box>
//     </Box>
//   );
// }


export function NewsCard({ article }) {
  const {
    title,
    url,
    source_name,
    // date,
    source_logo,
    // image,
    // snippet,
    // reach = '124k Reach',
    // views = '21 Views',
    // sentiment = 'Negative',
    // keyword = 'Kabila',
  } = article;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        p: 2,
        borderBottom: '1px solid #e0e0e0',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
      }}
    >
      {/* Left Section: Avatar + Info */}
      <Box sx={{ display: 'flex', flexDirection: 'row', gap: 2 }}>
        {/* Avatar */}
        <Avatar
          alt={source_name || 'News icon'}
          src={source_logo}
          variant="rounded"
          sx={{ width: 40, height: 40 }}
          imgProps={{
            onError: (e) => {
              e.target.onerror = null;
              e.target.src = '/static/Images/news-icon.png';
            },
          }}
        />

        {/* Info */}
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          {/* Source & Date */}
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            {source_name || 'Unknown Source'}
          </Typography>

          {/* future ones */}
          {/* <Typography variant="caption" color="text.secondary">
            News | US | {new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Typography> */}

          {/* Title */}
          <Link
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            underline="hover"
            sx={{ fontSize: 14, fontWeight: 480, mt: 1, color: '#111' }}
          >
            {title}
          </Link>

          {/* Snippet */}
          {/* <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1 }}
          >
            {snippet || 'Lorem ipsum preview text of the news article...'}
          </Typography> */}

          {/* Highlighted Word */}
          {/* <Box sx={{ mt: 1 }}>
            <Chip
              label={keyword}
              variant="outlined"
              size="small"
              sx={{ fontWeight: 500, fontSize: 12 }}
            />
          </Box> */}

          {/* Bottom Stats */}
          {/* <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {reach}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {views}
            </Typography>
          </Box> */}
        </Box>
      </Box>

      {/* Flag/Image & Sentiment */}
      {/* <Box sx={{ textAlign: 'right' }}>
        {image && (
          <img
            src={image}
            alt="news visual"
            style={{
              width: 60,
              height: 40,
              objectFit: 'cover',
              borderRadius: 4,
              marginBottom: 8,
            }}
          />
        )}
        <Typography
          variant="caption"
          color="error"
          sx={{ fontWeight: 500 }}
        >
          {sentiment}
        </Typography>
      </Box> */}
    </Box>
  );
}


// UI list of articles or social mentions
const Mentions = () => {
  const articles = useSearchStore((state) => state.articles);

  return (
    <div className='mentions-container'>
      {Array.isArray(articles) && articles.length > 0 ? (
        articles.map((article, idx) => (
          <NewsCard article={article} key={idx} />
        ))
      ) : (
        <p>No mentions available.</p>
      )}
    </div>
  );
};

export default Mentions