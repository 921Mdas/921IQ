import React from 'react'
import QueryStatsIcon from '@mui/icons-material/QueryStats'; // You can change this to any other icon if needed
import "./Construction.scss";

const Construction = ({ data }) => {
  return (
    <div className="construction-wrapper">
      <div className="construction-card">
        <QueryStatsIcon className="construction-icon" />
        <h2>{data.feature} Coming Soon</h2>
        <p>{data.message}</p>
      </div>
    </div>
  );
};

export default Construction;
