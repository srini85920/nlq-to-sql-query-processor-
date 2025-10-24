import React, { useState } from 'react';
import axios from 'axios';
import './QueryInterface.css'; // Import styles for this component

function QueryInterface() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSql, setShowSql] = useState(false); // <-- ADDED

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResponse(null);
    setShowSql(false); // <-- ADDED: Reset on submit

    axios.post('http://127.0.0.1:8000/api/nlq-to-sql', { question })
      .then(res => {
        setResponse(res.data);
        setIsLoading(false);
      })
      .catch(error => {
        setError(error.response?.data?.detail || error.message);
        setIsLoading(false);
      });
  };

  /**
   * Helper function to render the results.
   * If it's an array of objects, it builds a table.
   * Otherwise, it displays the raw result.
   */
  const renderResults = () => {
    const data = response.result;

    // Check for valid data
    if (!data || !Array.isArray(data) || data.length === 0) {
      return <p className="no-results">No results found.</p>;
    }

    // Get headers from the first object
    const headers = Object.keys(data[0]);

    return (
      <div className="table-container">
        <table className="results-table">
          <thead>
            <tr>
              {/* Create table headers, replacing underscores with spaces */}
              {headers.map(header => (
                <th key={header}>{header.replace(/_/g, ' ')}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Create a row for each item in the data array */}
            {data.map((row, index) => (
              <tr key={index}>
                {/* Create a cell for each header */}
                {headers.map(header => (
                  <td key={`${index}-${header}`}>{String(row[header])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="query-interface">
      <form onSubmit={handleSubmit} className="query-form">
        <input 
          type="text"
          className="query-input"
          placeholder="Ask a question (e.g., 'Who bought a laptop?')" 
          value={question}
          // --- THIS LINE IS NOW FIXED ---
          onChange={(e) => setQuestion(e.target.value)} 
        />
        <button type="submit" className="query-button" disabled={isLoading}>
          {isLoading ? 'Analyzing...' : 'Ask AI'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      
      {isLoading && <div className="loading-spinner"></div>}

      {/* Add the toggle button *before* the results, 
          but only if there is a response */}
      {response && (
        <button 
          className="sql-toggle-button" 
          onClick={() => setShowSql(!showSql)}
        >
          {showSql ? 'Hide Generated SQL' : 'Show Generated SQL'}
        </button>
      )}

      {response && (
        // Add a conditional class to the container
        <div className={`results-container ${showSql ? 'show-sql' : ''}`}>
          <div className="result-box">
            <h3>Result</h3>
            {/* Use the new renderResults function */}
            {renderResults()}
          </div>
          
          {/* Conditionally render the SQL box */}
          {showSql && (
            <div className="result-box">
              <h3>Generated SQL Query</h3>
              <pre className="code-block">{response.sql_query}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QueryInterface;
