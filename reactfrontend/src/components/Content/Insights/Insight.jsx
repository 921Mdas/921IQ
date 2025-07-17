import React from 'react';
import ConstructionIcon from '@mui/icons-material/Construction';
import Construction from '../../UnderConstruct/Construction';
import './Insight.scss';

const Insight = () => {
    const info = {
    message:'This feature is currently under development. Stay tuned for powerful insights!',
    feature:'Insights'
  }
  return  <Construction data={info} />
};

export default Insight;
