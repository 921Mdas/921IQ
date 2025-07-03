import './Echo.scss'
import React, { useState, useEffect, useRef } from 'react'
import BooleanSearch from './Search/Search'
import Mentions from './Mentions'
import MentionsAnalytics from './MentionsAnalytics'
import IconButton from '@mui/material/IconButton'
import InsightsIcon from '@mui/icons-material/Insights'
import CloseIcon from '@mui/icons-material/Close'

const Echo = () => {
  const [showAnalytics, setShowAnalytics] = useState(false)
  const analyticsRef = useRef(null)

  const toggleAnalytics = () => {
    setShowAnalytics(prev => !prev)
  }

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setShowAnalytics(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  // Close on outside click (only when open)
  useEffect(() => {
    if (!showAnalytics) return

    const handleClickOutside = (e) => {
      if (
        analyticsRef.current &&
        !analyticsRef.current.contains(e.target) &&
        !e.target.closest('.hamburger-toggle')
      ) {
        setShowAnalytics(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showAnalytics])

  return (
    <div className='echo_container'>
      <BooleanSearch />

      {/* Hamburger toggle (only visible on mobile via CSS) */}
      <HamburgerBtn toggleAnalytics={toggleAnalytics} showAnalytics={showAnalytics} />

      <div className='responsive-container'>
        {/* Articles/Mentions Section */}
        <div className='articles-column'>
          <Mentions />
        </div>

        {/* Analytics Panel */}
        <div
          ref={analyticsRef}
          className={`widgets-column analytics ${showAnalytics ? 'active' : ''}`}
        >
          <MentionsAnalytics />
        </div>
      </div>
    </div>
  )
}



const HamburgerBtn = ({toggleAnalytics, showAnalytics})=>{


{/* Inside the JSX */}
return <IconButton
  className='hamburger-toggle'
  onClick={toggleAnalytics}
  aria-label='Toggle analytics'
  size='large'
  sx={{
    position: 'fixed',
    top: '1rem',
    right: '1rem',
    zIndex: 1100,
    backgroundColor: '#333',
    color: '#fff',
    '&:hover': {
      backgroundColor: '#555',
    },
    display: { xs: 'flex', md: 'none' },
  }}
>
  {showAnalytics ? <CloseIcon /> : <InsightsIcon />}
</IconButton>

}

export default Echo
