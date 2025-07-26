// import React, { useState } from 'react';
// import { useSearchStore } from '../../../../store';
// import {
//   Card,
//   CardContent,
//   Typography,
//   Grid,
//   Dialog,
//   CircularProgress,
//   Avatar,
//   Box,
//   Skeleton
// } from '@mui/material';
// import SearchOffIcon from '@mui/icons-material/SearchOff';
// import VisibilityIcon from '@mui/icons-material/Visibility'
// import PersonaDialog from './Dialogue';
// import './Entities.scss';

// const Entities = () => {
//   const [selectedEntity, setSelectedEntity] = useState(null);
//   const [showPersona, setShowPersona] = useState(false);

//   const entities = useSearchStore(state => state.entities);
//   const isLoading = useSearchStore(state => state.isLoadingEntity);
//   const top10 = entities.slice(0, 10);

//   const showSkeleton = isLoading;
//   const showNoResults = !isLoading && entities.length === 0;

//   return (
//     <div className='entities-wrapper'>
//       <Grid container spacing={2} justifyContent='center' sx={{ overflowY: 'auto', maxHeight: '70vh' }}>
//         {showSkeleton &&
//           Array.from({ length: 10 }).map((_, idx) => (
//             <Grid item key={idx}>
//               <Card
//                 sx={{
//                   display: 'flex',
//                   flexDirection: 'row',
//                   width: 300,
//                   height: 180,
//                   boxShadow: 1,
//                   alignItems: 'center',
//                   padding: 2,
//                 }}
//               >
//                 <Skeleton variant='circular' width={64} height={64} sx={{ marginRight: 2 }} />
//                 <Box sx={{ flex: 1 }}>
//                   <Skeleton variant='text' width='80%' height={28} />
//                   <Skeleton variant='text' width='60%' height={20} />
//                   <Skeleton variant='text' width='40%' height={20} />
//                 </Box>
//               </Card>
//             </Grid>
//           ))}

//         {!showSkeleton && top10.map((entity, idx) => {
//           const sentimentValue = entity.sentiment || 70;
//           const initials = entity.name
//             .split(' ')
//             .map(n => n[0])
//             .join('');

//           return (
//             <Grid item key={idx}>
//   <Card
//     className='entity-card'
//     onClick={() => {
//       setSelectedEntity(entity);
//       setShowPersona(true);
//     }}
//     sx={{
//       display: 'flex',
//       flexDirection: 'row',
//       alignItems: 'center',
//       justifyContent: 'space-between',
//       cursor: 'pointer',
//       boxShadow: 3,
//       width: 300,
//       minWidth: 300,
//       height: 180,
//       padding: 2,
//       borderRadius: 3,
//       transition: '0.2s ease-in-out',
//       '&:hover': {
//         boxShadow: 6,
//         transform: 'translateY(-2px)',
//       },
//     }}
//   >
//     {/* Avatar with sentiment ring */}
//     <Box
//       sx={{
//         position: 'relative',
//         width: 64,
//         height: 64,
//         flexShrink: 0,
//         marginRight: 2,
//       }}
//     >
//       <CircularProgress
//         variant='determinate'
//         value={sentimentValue}
//         size={64}
//         thickness={4}
//         sx={{
//           color: '#b5b5f9fb',
//           position: 'absolute',
//           top: 0,
//           left: 0,
//         }}
//       />
//       <Avatar
//         alt={entity.name}
//         src={entity.wiki_image || undefined}
//         sx={{
//           width: 48,
//           height: 48,
//           position: 'absolute',
//           top: 8,
//           left: 8,
//           backgroundColor: '#eee',
//           color: '#333',
//           fontWeight: 'bold',
//           fontSize: 14,
//         }}
//       >
//         {initials}
//       </Avatar>
//     </Box>

//     {/* Text content */}
//     <CardContent
//       sx={{
//         overflow: 'hidden',
//         paddingY: 0,
//         paddingRight: 1,
//         flex: 1,
//       }}
//     >
//       <Typography
//         variant='subtitle1'
//         fontWeight='bold'
//         sx={{
//           display: '-webkit-box',
//           WebkitLineClamp: 2,
//           WebkitBoxOrient: 'vertical',
//           overflow: 'hidden',
//         }}
//       >
//         {entity.name}
//       </Typography>
//       <Typography variant='body2'>Mentions: {entity.count}</Typography>
//       <Typography variant='body2'>Sources: {entity.source_diversity}</Typography>

//       {/* View more icon */}
//       <Box mt={1} display="flex" alignItems="center" gap={0.5} color="text.secondary">
//         <VisibilityIcon fontSize="small" />
//         <Typography variant="caption">View more</Typography>
//       </Box>
//     </CardContent>
//   </Card>
// </Grid>

//             // <Grid item key={idx} onClick={() => setShowPersona(true)}>
//             //   <Card
//             //     className='entity-card'
//             //     onClick={() => setSelectedEntity(entity)}
//             //     sx={{
//             //       display: 'flex',
//             //       flexDirection: 'row',
//             //       cursor: 'pointer',
//             //       boxShadow: 2,
//             //       width: 300,
//             //       minWidth: 300,
//             //       height: 180,
//             //       overflow: 'hidden',
//             //       alignItems: 'center',
//             //     }}
//             //   >
//             //     <Box
//             //       sx={{
//             //         position: 'relative',
//             //         width: 64,
//             //         height: 64,
//             //         margin: 2,
//             //         flexShrink: 0,
//             //       }}
//             //     >
//             //       <CircularProgress
//             //         variant='determinate'
//             //         value={sentimentValue}
//             //         size={64}
//             //         thickness={4}
//             //         sx={{
//             //           color: '#4caf50',
//             //           position: 'absolute',
//             //           top: 0,
//             //           left: 0,
//             //         }}
//             //       />
//             //       <Avatar
//             //         alt={entity.name}
//             //         src={entity.wiki_image || undefined}
//             //         sx={{
//             //           width: 48,
//             //           height: 48,
//             //           position: 'absolute',
//             //           top: 8,
//             //           left: 8,
//             //           backgroundColor: '#eee',
//             //           color: '#333',
//             //           fontWeight: 'bold',
//             //         }}
//             //       >
//             //         {initials}
//             //       </Avatar>
//             //     </Box>

//             //     <CardContent
//             //       sx={{
//             //         overflow: 'auto',
//             //         padding: 2,
//             //         maxHeight: '100%',
//             //         flex: 1,
//             //       }}
//             //     >
//             //       <Typography variant='h6' fontWeight='bold' gutterBottom>
//             //         {entity.name}
//             //       </Typography>
//             //       <Typography variant='body2'>Mentions: {entity.count}</Typography>
//             //       <Typography variant='body2'>Sources: {entity.source_diversity}</Typography>
//             //     </CardContent>
//             //   </Card>
//             // </Grid>
//           );
//         })}

//         {showNoResults && (
//           <Grid item>
//             <Card
//               sx={{
//                 width: 320,
//                 height: 180,
//                 display: 'flex',
//                 flexDirection: 'column',
//                 alignItems: 'center',
//                 justifyContent: 'center',
//                 textAlign: 'center',
//                 boxShadow: 1,
//                 padding: 2,
//               }}
//             >
//               <SearchOffIcon sx={{ fontSize: 48, color: '#9e9e9e', marginBottom: 1 }} />
//               <Typography variant='h6' gutterBottom>
//                 No entities found
//               </Typography>
//               <Typography variant='body2' color='text.secondary'>
//                 Your search sample might be too small. Try expanding your keywords.
//               </Typography>
//             </Card>
//           </Grid>
//         )}
//       </Grid>

//       {showPersona && (
//         <PersonaDialog
//           selectedEntity={selectedEntity}
//           onClose={() => setShowPersona(false)}
//         />
//       )}
//     </div>
//   );
// };

// export default Entities;



import React, { useState } from 'react';
import { useSearchStore } from '../../../../store';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Dialog,
  CircularProgress,
  Avatar,
  Box,
  Skeleton,
  Fade,
  useTheme,
  useMediaQuery
} from '@mui/material';
import SearchOffIcon from '@mui/icons-material/SearchOff';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PersonaDialog from './Dialogue';
import './Entities.scss';

const EntitiesSkeleton = ({ isMobile }) => {
  const cardWidth = isMobile ? 280 : 300;
  const cardHeight = isMobile ? 160 : 180;

  return (
    <Grid container spacing={2} justifyContent='center' sx={{ overflowY: 'auto', maxHeight: '70vh' }}>
      {Array.from({ length: 10 }).map((_, idx) => (
        <Grid item key={idx}>
          <Card
            sx={{
              display: 'flex',
              flexDirection: 'row',
              width: cardWidth,
              minWidth: cardWidth,
              height: cardHeight,
              padding: 2,
              borderRadius: 3,
              boxShadow: 1,
              alignItems: 'center',
            }}
          >
            {/* Avatar with sentiment ring skeleton */}
            <Box sx={{ position: 'relative', width: 64, height: 64, marginRight: 2 }}>
              <Skeleton 
                variant="circular" 
                width={64} 
                height={64} 
                animation="wave"
                sx={{ bgcolor: 'rgba(0, 0, 0, 0.04)' }}
              />
            </Box>
            
            <Box sx={{ flex: 1 }}>
              <Skeleton 
                variant="text" 
                width="80%" 
                height={28} 
                animation="wave"
                sx={{ 
                  mb: 1,
                  bgcolor: 'rgba(0, 0, 0, 0.04)',
                  borderRadius: 1
                }} 
              />
              <Skeleton 
                variant="text" 
                width="60%" 
                height={20} 
                animation="wave"
                sx={{ 
                  mb: 0.5,
                  bgcolor: 'rgba(0, 0, 0, 0.04)',
                  borderRadius: 1
                }} 
              />
              <Skeleton 
                variant="text" 
                width="40%" 
                height={20} 
                animation="wave"
                sx={{ 
                  mb: 0.5,
                  bgcolor: 'rgba(0, 0, 0, 0.04)',
                  borderRadius: 1
                }} 
              />
              {/* View more section */}
              <Box mt={1} display="flex" alignItems="center" gap={0.5}>
                <Skeleton 
                  variant="circular" 
                  width={20} 
                  height={20} 
                  animation="wave"
                  sx={{ bgcolor: 'rgba(0, 0, 0, 0.04)' }}
                />
                <Skeleton 
                  variant="text" 
                  width={60} 
                  height={20} 
                  animation="wave"
                  sx={{ 
                    bgcolor: 'rgba(0, 0, 0, 0.04)',
                    borderRadius: 1
                  }} 
                />
              </Box>
            </Box>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

const NoResultsCard = ({ isMobile }) => (
  <Grid container spacing={2} justifyContent='center'>
    <Grid item>
      <Card
        sx={{
          width: isMobile ? 280 : 320,
          height: isMobile ? 160 : 180,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          boxShadow: 1,
          padding: 2,
        }}
      >
        <SearchOffIcon sx={{ fontSize: 48, color: '#9e9e9e', marginBottom: 1 }} />
        <Typography variant='h6' gutterBottom>
          No entities found
        </Typography>
        <Typography variant='body2' color='text.secondary'>
          Your search sample might be too small. Try expanding your keywords.
        </Typography>
      </Card>
    </Grid>
  </Grid>
);

const EntityCard = ({ entity, onClick, isMobile }) => {
  const sentimentValue = entity.sentiment || 70;
  const initials = entity.name
    .split(' ')
    .map(n => n[0])
    .join('');

  return (
    <Grid item>
      <Card
        className='entity-card'
        onClick={onClick}
        sx={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          boxShadow: 3,
          width: isMobile ? 280 : 300,
          minWidth: isMobile ? 280 : 300,
          height: isMobile ? 160 : 180,
          padding: 2,
          borderRadius: 3,
          transition: '0.2s ease-in-out',
          '&:hover': {
            boxShadow: 6,
            transform: 'translateY(-2px)',
          },
        }}
      >
        {/* Avatar with sentiment ring */}
        <Box
          sx={{
            position: 'relative',
            width: 64,
            height: 64,
            flexShrink: 0,
            marginRight: 2,
          }}
        >
          <CircularProgress
            variant='determinate'
            value={sentimentValue}
            size={64}
            thickness={4}
            sx={{
              color: '#b5b5f9fb',
              position: 'absolute',
              top: 0,
              left: 0,
            }}
          />
          <Avatar
            alt={entity.name}
            src={entity.wiki_image || undefined}
            sx={{
              width: 48,
              height: 48,
              position: 'absolute',
              top: 8,
              left: 8,
              backgroundColor: '#eee',
              color: '#333',
              fontWeight: 'bold',
              fontSize: 14,
            }}
          >
            {initials}
          </Avatar>
        </Box>

        {/* Text content */}
        <CardContent
          sx={{
            overflow: 'hidden',
            paddingY: 0,
            paddingRight: 1,
            flex: 1,
          }}
        >
          <Typography
            variant='subtitle1'
            fontWeight='bold'
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {entity.name}
          </Typography>
          <Typography variant='body2'>Mentions: {entity.count}</Typography>
          <Typography variant='body2'>Sources: {entity.source_diversity}</Typography>

          {/* View more icon */}
          <Box mt={1} display="flex" alignItems="center" gap={0.5} color="text.secondary">
            <VisibilityIcon fontSize="small" />
            <Typography variant="caption">View more</Typography>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
};

const Entities = () => {
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showPersona, setShowPersona] = useState(false);

  const entities = useSearchStore(state => state.entities);
  const isLoading = useSearchStore(state => state.isLoadingEntity);
  const top10 = entities.slice(0, 10);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const showNoResults = !isLoading && entities.length === 0;

  const handleCardClick = (entity) => {
    setSelectedEntity(entity);
    setShowPersona(true);
  };

  return (
    <div className='entities-wrapper'>
      <Fade in={true} timeout={300}>
        <div>
          {isLoading ? (
            <EntitiesSkeleton isMobile={isMobile} />
          ) : showNoResults ? (
            <NoResultsCard isMobile={isMobile} />
          ) : (
            <Grid container spacing={2} justifyContent='center' sx={{ overflowY: 'auto', maxHeight: '70vh' }}>
              {top10.map((entity, idx) => (
                <EntityCard 
                  key={idx} 
                  entity={entity} 
                  onClick={() => handleCardClick(entity)}
                  isMobile={isMobile}
                />
              ))}
            </Grid>
          )}
        </div>
      </Fade>

      {showPersona && (
        <PersonaDialog
          selectedEntity={selectedEntity}
          onClose={() => setShowPersona(false)}
        />
      )}
    </div>
  );
};

export default Entities;