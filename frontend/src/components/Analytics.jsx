import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

const Analytics = () => {
  const [genreData, setGenreData] = useState(null);
  const [ratingData, setRatingData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [topRated, setTopRated] = useState([]);
  const [userActivity, setUserActivity] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [genreRes, ratingRes, trendsRes, topRatedRes, activityRes] = await Promise.all([
        axios.get('http://localhost:5000/api/analytics/genre-distribution'),
        axios.get('http://localhost:5000/api/analytics/rating-distribution'),
        axios.get('http://localhost:5000/api/analytics/trends'),
        axios.get('http://localhost:5000/api/analytics/top-rated', { params: { min_ratings: 100, limit: 10 } }),
        axios.get('http://localhost:5000/api/analytics/user-activity')
      ]);

      // Genre distribution
      const genres = Object.keys(genreRes.data.distribution).slice(0, 10);
      const genreCounts = Object.values(genreRes.data.distribution).slice(0, 10);
      setGenreData({
        labels: genres,
        datasets: [{
          data: genreCounts,
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
            '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
          ]
        }]
      });

      // Rating distribution
      const ratings = Object.keys(ratingRes.data.distribution).sort();
      const ratingCounts = ratings.map(r => ratingRes.data.distribution[r]);
      setRatingData({
        labels: ratings,
        datasets: [{
          label: 'Number of Ratings',
          data: ratingCounts,
          backgroundColor: '#667eea'
        }]
      });

      // Trends
      const years = trendsRes.data.yearly_trends.map(t => t.year);
      const avgRatings = trendsRes.data.yearly_trends.map(t => t.avg_rating);
      setTrendsData({
        labels: years,
        datasets: [{
          label: 'Average Rating',
          data: avgRatings,
          borderColor: '#667eea',
          backgroundColor: 'rgba(102, 126, 234, 0.1)',
          tension: 0.4
        }]
      });

      setTopRated(topRatedRes.data.top_rated);
      setUserActivity(activityRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading analytics...</div>;

  return (
    <div className="analytics-dashboard">
      <h2>Platform Analytics</h2>

      {userActivity && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Users</h3>
            <p className="stat-value">{userActivity.total_users.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h3>Total Ratings</h3>
            <p className="stat-value">{userActivity.total_ratings.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h3>Avg Ratings/User</h3>
            <p className="stat-value">{userActivity.avg_ratings_per_user.toFixed(1)}</p>
          </div>
        </div>
      )}

      <div className="charts-container">
        <div className="chart-box">
          <h3>Genre Distribution</h3>
          {genreData && <Pie data={genreData} />}
        </div>

        <div className="chart-box">
          <h3>Rating Distribution</h3>
          {ratingData && <Bar data={ratingData} options={{ scales: { y: { beginAtZero: true } } }} />}
        </div>
      </div>

      <div className="chart-box-wide">
        <h3>Rating Trends Over Time</h3>
        {trendsData && <Line data={trendsData} options={{ scales: { y: { beginAtZero: false } } }} />}
      </div>

      <div className="top-rated-section">
        <h3>Top Rated Movies</h3>
        <div className="top-rated-list">
          {topRated.map((movie, idx) => (
            <div key={movie.movieId} className="top-rated-item">
              <span className="rank">#{idx + 1}</span>
              <div className="movie-info">
                <h4>{movie.title}</h4>
                <p>{movie.genres}</p>
              </div>
              <div className="rating-info">
                <span className="rating">⭐ {movie.avg_rating.toFixed(2)}</span>
                <span className="count">({movie.rating_count} ratings)</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
