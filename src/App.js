import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoadingScreen from './components/LoadingScreen';
import VisualizationPage from './components/VisualizationPage';
import UploadPage from './components/UploadPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/loading/:documentId" element={<LoadingScreen />} />
        <Route path="/visualization/:documentId" element={<VisualizationPage />} />
      </Routes>
    </Router>
  );
}

export default App;
