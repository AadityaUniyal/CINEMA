import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import GenrePreference from './components/GenrePreference';
import MovieList from './components/MovieList';
import Recommendations from './components/Recommendations';
import Dashboard from './components/Dashboard';
import Watchlist from './components/Watchlist';
import RandomMovies from './components/RandomMovies';
import Analytics from './components/Analytics';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showGenrePreference, setShowGenrePreference] = useState(false);
  const [activeTab, setActiveTab] = useState('movies');
  const [userId, setUserId] = useState(null);
  const [userName, setUserName] = useState('');
  const [userGenres, setUserGenres] = useState([]);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogin = async (id, name = '') => {
    setUserId(id);
    setUserName(name);
    setIsLoggedIn(true);

    try {
      const response = await fetch(`http:
      const data = await response.json();
      
      if (data.success && data.profile) {
        const hasPreferences = data.profile.preferredGenres && data.profile.preferredGenres.length > 0;
        if (!hasPreferences) {
          
          setShowGenrePreference(true);
        } else {
          
          setUserGenres(data.profile.preferredGenres);
          setShowGenrePreference(false);
        }
      } else {
        
        setShowGenrePreference(true);
      }
    } catch (error) {
      console.error('Error checking preferences:', error);
      
      setShowGenrePreference(true);
    }
  };

  const handleGenrePreferenceComplete = (genres) => {
    setUserGenres(genres);
    setShowGenrePreference(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setShowGenrePreference(false);
    setUserId(null);
    setUserName('');
    setUserGenres([]);
    setActiveTab('movies');
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  if (showGenrePreference) {
    return <GenrePreference userId={userId} onComplete={handleGenrePreferenceComplete} />;
  }

  return (
    <div className="app">
      <header className={`header ${scrolled ? 'scrolled' : ''}`}>
        <div className="header-content">
          <h1 className="app-logo">CINÉMA</h1>
          <p className="app-tagline">Unlimited movies, endless possibilities</p>
          
          <div className="user-info-header">
            <span className="user-badge">
              {userName ? userName.split(' ')[0] : `User ${userId}`}
            </span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>

          <nav className="nav">
            <button 
              onClick={() => handleTabChange('movies')} 
              className={activeTab === 'movies' ? 'active' : ''}
            >
              Browse
            </button>
            <button 
              onClick={() => handleTabChange('recommendations')} 
              className={activeTab === 'recommendations' ? 'active' : ''}
            >
              For You
            </button>
            <button 
              onClick={() => handleTabChange('discover')} 
              className={activeTab === 'discover' ? 'active' : ''}
            >
              Discover
            </button>
            <button 
              onClick={() => handleTabChange('analytics')} 
              className={activeTab === 'analytics' ? 'active' : ''}
            >
              Trending
            </button>
            <button 
              onClick={() => handleTabChange('watchlist')} 
              className={activeTab === 'watchlist' ? 'active' : ''}
            >
              Watchlist
            </button>
            <button 
              onClick={() => handleTabChange('dashboard')} 
              className={activeTab === 'dashboard' ? 'active' : ''}
            >
              Dashboard
            </button>
          </nav>
        </div>
      </header>

      <main className="main-content">
        {activeTab === 'movies' && <MovieList userId={userId} key={userId} />}
        {activeTab === 'recommendations' && <Recommendations userId={userId} key={userId} />}
        {activeTab === 'discover' && <RandomMovies userId={userId} key={userId} />}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'watchlist' && <Watchlist userId={userId} key={userId} />}
        {activeTab === 'dashboard' && <Dashboard userId={userId} key={userId} />}
      </main>
    </div>
  );
}

export default App;
