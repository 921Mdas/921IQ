// src/App.jsx
import React from 'react';

import './styles/layout.scss';

import Nav from './components/Nav/Nav';
import Aside from './components/Aside/Aside';
import Content from './components/Content/Content';

function App() {
  return (
      <div className="layout">
        <Nav />
        <Aside />
        <Content />
      </div>
  );
}

export default App;
