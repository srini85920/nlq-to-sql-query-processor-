import React, { useState } from 'react';
import QueryInterface from './components/QueryInterface';
import DataManager from './components/DataManager';
import './App.css'; // Import our new tab styles

function App() {
  // We will manually control which tab is active
  const [activeTab, setActiveTab] = useState('query');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>E-commerce Database Assistant 🛒</h1>
      </header>
      
      {/* These are our new tabs */}
      <nav className="app-tabs">
        <button 
          className={activeTab === 'query' ? 'active' : ''}
          onClick={() => setActiveTab('query')}
        >
          Query with AI
        </button>
        <button 
          className={activeTab === 'manage' ? 'active' : ''}
          onClick={() => setActiveTab('manage')}
        >
          Manage Data
        </button>
      </nav>
      
      {/* This is the content for the tabs */}
      <main className="app-content">
        {activeTab === 'query' && <QueryInterface />}
        {activeTab === 'manage' && <DataManager />}
      </main>
    </div>
  );
}

export default App;

