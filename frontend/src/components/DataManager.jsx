import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DataManager.css'; // Import styles for this component

function DataManager() {
  const [schema, setSchema] = useState(null);
  const [selectedTable, setSelectedTable] = useState('');
  const [formData, setFormData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  // This state replaces useToast
  const [message, setMessage] = useState({ type: '', text: '' });

  // Fetch the database schema
  useEffect(() => {
    setIsLoading(true);
    axios.get('http://127.0.0.1:8000/api/schema')
      .then(response => {
        setSchema(response.data);
        setIsLoading(false);
      })
      .catch(error => {
        setIsLoading(false);
        setMessage({ type: 'error', text: 'Error fetching schema' });
      });
  }, []);

  const handleTableChange = (e) => {
    const tableName = e.target.value;
    setSelectedTable(tableName);
    setFormData({}); 
    setMessage({ type: '', text: '' });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const isNumber = e.target.type === 'number';
    setFormData(prev => ({ 
      ...prev, 
      [name]: isNumber && value !== '' ? Number(value) : value 
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    // Filter out empty strings from form data
    const cleanData = Object.fromEntries(
      Object.entries(formData).filter(([_, value]) => value !== '')
    );
    
    axios.post('http://127.0.0.1:8000/api/add-record', { table: selectedTable, data: cleanData })
      .then(response => {
        setMessage({ type: 'success', text: 'Record added successfully!' });
        setFormData({});
        setIsLoading(false);
      })
      .catch(error => {
        setMessage({ type: 'error', text: error.response?.data?.detail || error.message });
        setIsLoading(false);
      });
  };
  
  const columns = schema && selectedTable ? schema.tables[selectedTable] : [];

  return (
    <div className="data-manager">
      <h2>Database Schema</h2>
      {isLoading && !schema && <p>Loading schema...</p>}
      {schema ? (
        <div className="schema-container">
          {Object.entries(schema.tables).map(([tableName, columns]) => (
            <div key={tableName} className="schema-table">
              <h3>{tableName}</h3>
              <div className="schema-columns">
                {columns.map(col => (
                  <span key={col} className="schema-column-tag">
                    {col}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : null}

      <h2 className="form-heading">Add New Record</h2>
      <form onSubmit={handleSubmit} className="data-form">
        <div className="form-group">
          <label>Select Table</label>
          <select 
            className="form-select"
            onChange={handleTableChange} 
            value={selectedTable}
          >
            <option value="">Choose a table to add data</option>
            {schema && Object.keys(schema.tables).map(tableName => (
              <option key={tableName} value={tableName}>{tableName}</option>
            ))}
          </select>
        </div>

        {columns.map(column => {
          // Auto-detect if the column should be a number input
          const isNum = column.includes('_id') || column === 'quantity' || column.includes('price') || column.includes('amount');
          return (
            <div className="form-group" key={column}>
              <label>{column}</label>
              <input 
                name={column}
                value={formData[column] || ''}
                onChange={handleInputChange} 
                placeholder={`Enter ${column}`}
                className="form-input"
                type={isNum ? 'number' : 'text'}
              />
            </div>
          );
        })}

        {selectedTable && 
          <button 
            type="submit" 
            className="form-button"
            disabled={isLoading}
          >
            {isLoading ? 'Adding...' : `Add Record to "${selectedTable}"`}
          </button>
        }
      </form>
      
      {/* This section replaces the toast */}
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  );
}

export default DataManager;