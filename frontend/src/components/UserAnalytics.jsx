import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const UserAnalytics = ({ userId }) => {
  const [stats, setStats] = useState(null);
  const [similarUsers, setSimilarUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      const [statsRes, similarRes] = await Promise.all([
        axios.get(`http:
        axios.get(`http:
      ]);
      
      setStats(statsRes.data);
      setSimilarUsers(similarRes.data.similar_users);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user data:', error);
      setLoading(false);
    }
  };

  const exportUserData = async () => {
    try {
      const response = await axios.get(`http:
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `user_${userId}_data.json`;
      a.click();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  if (loading) return <div>Loading analytics...</div>;
  if (!stats) return <div>No data available</div>;

  const genreData = {
    labels: stats.favorite_genres,
    datasets: [{
      data: stats.favorite_genres.map((_, i) => 10 - i),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    }]
  };

  return (
    <div className="user-analytics">
      <h2>Your Analytics</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Ratings</h3>
          <p className="stat-value">{stats.total_ratings}</p>
        </div>
        <div className="stat-card">
          <h3>Average Rating</h3>
          <p className="stat-value">{stats.avg_rating.toFixed(2)}</p>
        </div>
      </div>

      <div className="chart-container">
        <h3>Favorite Genres</h3>
        <Pie data={genreData} />
      </div>

      <div className="similar-users">
        <h3>Users with Similar Taste</h3>
        {similarUsers.map((user, idx) => (
          <div key={idx} className="similar-user-card">
            <p>User {user.userId}</p>
            <p>{user.total_ratings} ratings</p>
            <p>Avg: {user.avg_rating.toFixed(2)}</p>
          </div>
        ))}
      </div>

      <button onClick={exportUserData} className="export-btn">
        📥 Export My Data
      </button>
    </div>
  );
};

export default UserAnalytics;
