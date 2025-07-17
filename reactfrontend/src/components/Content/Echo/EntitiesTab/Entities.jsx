import React, { useState } from 'react'
import { useSearchStore } from '../../../../store'
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Avatar,
  CircularProgress,
  Box,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import PersonaDialog from './Dialogue'
import './Entities.scss'


const Entities = () => {
  const [selectedEntity, setSelectedEntity] = useState(null)
  const [showPersona, setShowPersona] = useState(false);
  const top10 = useSearchStore(state => state.entities).slice(0, 10)

  return (
    <div className='entities-wrapper'>
      <Grid container spacing={2} justifyContent='center' sx={{ overflowY:'auto', maxHeight:'60vh'}}>
        {top10.map((entity, idx) => {
          const sentimentValue = entity.sentiment || 70
          const initials = entity.name
            .split(' ')
            .map(n => n[0])
            .join('')

          return (
            <Grid item key={idx} onClick={()=>setShowPersona(true)}>
              <Card
                className='entity-card'
                onClick={() => setSelectedEntity(entity)}
                sx={{
                  display: 'flex',
                  flexDirection: 'row',
                  cursor: 'pointer',
                  boxShadow: 2,
                  width: 300,               // Fixed width for uniform sizing
                  minWidth: 300,            // Enforces minimum width
                  height: 180,              // Fixed height for all cards
                  overflow: 'hidden',
                  alignItems:'center',
                }}
              >
                {/* Avatar & Sentiment Progress */}
                <Box
                  sx={{
                    position: 'relative',
                    width: 64,
                    height: 64,
                    margin: 2,
                    flexShrink: 0,
                  }}
                >
                  <CircularProgress
                    variant='determinate'
                    value={sentimentValue}
                    size={64}
                    thickness={4}
                    sx={{
                      color: '#4caf50',
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
                    }}
                  >
                    {initials}
                  </Avatar>
                </Box>

                {/* Scrollable Content */}
                <CardContent
                  sx={{
                    overflow: 'auto',
                    padding: 2,
                    maxHeight: '100%',
                    flex: 1,
                  }}
                >
                  <Typography variant='h6' fontWeight='bold' gutterBottom>
                    {entity.name}
                  </Typography>
                  <Typography variant='body2'>Mentions: {entity.count}</Typography>
                  <Typography variant='body2'>Sources: {entity.source_diversity}</Typography>
              
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

{showPersona && (
  <PersonaDialog selectedEntity={selectedEntity} onClose={() => setShowPersona(false)} />
)}



   
    </div>
  )
}

export default Entities
