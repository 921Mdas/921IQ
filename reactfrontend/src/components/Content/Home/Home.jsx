import React from 'react';
import { Link } from 'react-router-dom';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import InsightsIcon from '@mui/icons-material/Insights';
import SchoolIcon from '@mui/icons-material/School';

import './Home.scss';

const Home = () => {
  return (
    <div className="home-page">
      {/* Hero Section - Simplified */}
      <section className="hero">
        <div className="hero-content">
<SchoolIcon className="icon" sx={{color:'white', fontSize:50}} />

          <h1>Media Intelligence Training Resources</h1>
          <p>Educational materials for understanding media monitoring, reputation analysis, and public narrative tracking.</p>
        </div>
      </section>

      {/* About Echo - Kept as informational */}
      <section className="echo-info">
        <div className="echo-header">
          <h2>What is Echo?</h2>
          <p>Echo is a conceptual framework for analyzing media narratives and public discourse, particularly in African contexts. These training materials demonstrate how such analysis can be conducted.</p>
        </div>

        <div className="echo-features">
          <div className="feature">
            <GraphicEqIcon className="icon" />
            <div>
              <h3>Media Monitoring Basics</h3>
              <p>Learn techniques for tracking mentions across news, blogs, and social platforms.</p>
            </div>
          </div>

          <div className="feature">
            <AnalyticsIcon className="icon" />
            <div>
              <h3>Sentiment Analysis</h3>
              <p>Understand how to gauge public sentiment from media coverage.</p>
            </div>
          </div>

          <div className="feature">
            <InsightsIcon className="icon" />
            <div>
              <h3>Narrative Mapping</h3>
              <p>Training on identifying and visualizing dominant narratives in media ecosystems.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Training Resources Section */}
      <section className="training-resources">
        <h2>Available Training Modules</h2>
        <div className="resource-cards">
          <div className="card">
            <h3>Introduction to Media Monitoring</h3>
            <p>Fundamentals of tracking media coverage and mentions.</p>
            <Link to="/training/media-monitoring" className="resource-link">
              View Module
            </Link>
          </div>
          <div className="card">
            <h3>Sentiment Analysis Techniques</h3>
            <p>Methods for analyzing tone and sentiment in media.</p>
            <Link to="/training/sentiment-analysis" className="resource-link">
              View Module
            </Link>
          </div>
          <div className="card">
            <h3>African Media Landscape</h3>
            <p>Understanding media ecosystems across African regions.</p>
            <Link to="/training/african-media" className="resource-link">
              View Module
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;