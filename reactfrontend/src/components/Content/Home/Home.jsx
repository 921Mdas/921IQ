// src/pages/Home.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import InsightsIcon from '@mui/icons-material/Insights';

import './Home.scss';

const Home = () => {
  return (
    <div className="home-page">
      {/* Hero Section */}
    <section className="hero">
  <div className="hero-content">
    <h1>Guesswork doesn't work.<br />Power your team with insights that drive results.</h1>
    <p>Monitor online conversations, spot trends, and make smarter decisions with Echo — a media intelligence tool built for modern teams.</p>
    <Link to="/request-demo" className="cta-button">
      <span className="dot" /> REQUEST DEMO
    </Link>
  </div>

  <div className="hero-image">
    <img src="/assets/analytics.png" alt="Analytics dashboard" />
  </div>
</section>

      {/* Echo Section */}
      <section className="echo-info">
        <div className="echo-header">
          <h2>What is Echo?</h2>
          <p>
            Echo is our media analysis tool designed to help organizations understand and act on online conversations across the digital landscape.
          </p>
        </div>

        <div className="echo-features">
          <div className="feature">
            <GraphicEqIcon className="icon" />
            <div>
              <h3>Live Media Monitoring</h3>
              <p>Track social media, news sites, blogs, and forums in real-time to stay updated on public sentiment and breaking stories.</p>
            </div>
          </div>

          <div className="feature">
            <AnalyticsIcon className="icon" />
            <div>
              <h3>AI-Powered Analysis</h3>
              <p>Leverage advanced AI to classify mentions, detect sentiment, and highlight emerging trends without manual effort.</p>
            </div>
          </div>

          <div className="feature">
            <InsightsIcon className="icon" />
            <div>
              <h3>Actionable Insights</h3>
              <p>Generate intuitive visual reports that help your team make strategic decisions backed by real-time media intelligence.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
