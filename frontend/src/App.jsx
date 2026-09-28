import React, { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import EmbedPage from './pages/EmbedPage';

export default function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  if (currentPath === '/embed') {
    return <EmbedPage />;
  }

  return <HomePage />;
}
