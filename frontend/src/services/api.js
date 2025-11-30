import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const movieService = {
  getMovies: (page = 1, perPage = 20, genre = null) =>
    api.get('/movies', { params: { page, per_page: perPage, genre } }),
  
  getMovie: (movieId) => api.get(`/movies/${movieId}`),
  
  searchMovies: (query, limit = 50) =>
    api.get('/search', { params: { q: query, limit } }),
  
  getRandomMovies: (n = 10, genre = null) =>
    api.get('/movies/random', { params: { n, genre } }),
  
  rateMovie: (userId, movieId, rating) =>
    api.post('/rate', { userId, movieId, rating })
};

export const recommendationService = {
  getRecommendations: (userId, n = 10) =>
    api.get(`/recommendations/${userId}`, { params: { n } }),
  
  getSimilarUsers: (userId, n = 5) =>
    api.get(`/similar-users/${userId}`, { params: { n } })
};

export const analyticsService = {
  getTopRated: (minRatings = 50, limit = 20) =>
    api.get('/analytics/top-rated', { params: { min_ratings: minRatings, limit } }),
  
  getGenreDistribution: () => api.get('/analytics/genre-distribution'),
  
  getRatingDistribution: () => api.get('/analytics/rating-distribution'),
  
  getTrends: () => api.get('/analytics/trends'),
  
  getUserActivity: () => api.get('/analytics/user-activity')
};

export const userService = {
  getUserStats: (userId) => api.get(`/user/${userId}/stats`),
  
  exportUserData: (userId, format = 'json') =>
    api.get(`/export/user/${userId}`, { params: { format } })
};

export const watchlistService = {
  getWatchlist: (userId) => api.get(`/watchlist/${userId}`),
  
  addToWatchlist: (userId, movieId) =>
    api.post(`/watchlist/${userId}/${movieId}`),
  
  removeFromWatchlist: (userId, movieId) =>
    api.delete(`/watchlist/${userId}/${movieId}`),
  
  markAsWatched: (userId, movieId) =>
    api.put(`/watchlist/${userId}/${movieId}/watched`)
};

export default api;
