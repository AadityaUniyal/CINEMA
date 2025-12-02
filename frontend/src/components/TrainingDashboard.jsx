import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/TrainingDashboard.css';

const TrainingDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);

  useEffect(() => {
    fetchMetrics();
    fetchHistory();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/ml/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/ml/metrics/history');
      setHistory(response.data.history || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    setTrainResult(null);
    
    try {
      const response = await axios.post('http://localhost:5000/api/ml/train');
      setTrainResult({
        success: true,
        message: 'Model trained successfully!',
        data: response.data
      });
      fetchMetrics();
      fetchHistory();
    } catch (error) {
      setTrainResult({
        success: false,
        message: error.response?.data?.error || 'Training failed'
      });
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="training-dashboard">
        <div className="loading-spinner-large"></div>
        <p>Loading ML Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="training-dashboard">
      <div className="dashboard-header">
        <h1>🤖 ML Training Dashboard</h1>
        <p>Monitor and manage machine learning models</p>
      </div>

      <div className="metrics-section">
        <h2>Current Model Performance</h2>
        {metrics && metrics.metrics ? (
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-label">RMSE</div>
                <div className="metric-value">{metrics.metrics.rmse?.toFixed(4) || 'N/A'}</div>
                <div className="metric-description">Lower is better</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-content">
                <div className="metric-label">Precision@10</div>
                <div className="metric-value">{(metrics.metrics.precision_at_10 * 100)?.toFixed(1) || 'N/A'}%</div>
                <div className="metric-description">Recommendation accuracy</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🔍</div>
              <div className="metric-content">
                <div className="metric-label">Recall@10</div>
                <div className="metric-value">{(metrics.metrics.recall_at_10 * 100)?.toFixed(1) || 'N/A'}%</div>
                <div className="metric-description">Coverage of relevant items</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🌐</div>
              <div className="metric-content">
                <div className="metric-label">Coverage</div>
                <div className="metric-value">{(metrics.metrics.coverage * 100)?.toFixed(1) || 'N/A'}%</div>
                <div className="metric-description">Recommendation diversity</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="no-metrics">
            <p>No model trained yet. Train your first model to see metrics!</p>
          </div>
        )}

        {metrics && (
          <div className="model-info">
            <p><strong>Version:</strong> {metrics.current_version}</p>
            <p><strong>Trained:</strong> {new Date(metrics.trained_at).toLocaleString()}</p>
          </div>
        )}
      </div>

      <div className="training-section">
        <h2>Train New Model</h2>
        <button 
          onClick={handleTrain} 
          disabled={training}
          className="train-btn"
        >
          {training ? '⏳ Training...' : '🚀 Train Model'}
        </button>

        {trainResult && (
          <div className={`train-result ${trainResult.success ? 'success' : 'error'}`}>
            <p>{trainResult.message}</p>
            {trainResult.success && trainResult.data && (
              <div className="train-metrics">
                <p>RMSE: {trainResult.data.metrics.rmse?.toFixed(4)}</p>
                <p>Precision@10: {(trainResult.data.metrics.precision_at_10 * 100)?.toFixed(1)}%</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="history-section">
        <h2>Training History</h2>
        {history.length > 0 ? (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>Version</th>
                  <th>Date</th>
                  <th>RMSE</th>
                  <th>Precision@10</th>
                  <th>Recall@10</th>
                  <th>Coverage</th>
                </tr>
              </thead>
              <tbody>
                {history.slice().reverse().map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.version}</td>
                    <td>{new Date(item.saved_at).toLocaleDateString()}</td>
                    <td>{item.metrics.rmse?.toFixed(4)}</td>
                    <td>{(item.metrics.precision_at_10 * 100)?.toFixed(1)}%</td>
                    <td>{(item.metrics.recall_at_10 * 100)?.toFixed(1)}%</td>
                    <td>{(item.metrics.coverage * 100)?.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No training history available</p>
        )}
      </div>
    </div>
  );
};

export default TrainingDashboard;
