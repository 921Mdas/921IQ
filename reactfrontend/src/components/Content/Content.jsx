import * as React from 'react';

// subcomponents or different routes for the main content UI
// different features of the App
// Echo is the media and ad monitoring feature (tracking, listening and instant analytics - smaller version of analytics interactive)
import Echo from './Echo/Echo';
import Home from './Home/Home';
import Insight from './Insights/Insight';
import Analytics from './Analytics/Analytics'

const Content = () => {
  return (
    <div className='Content'>
       <Echo/>

    </div>
  )
}

export default Content