import React, { useState, useEffect } from 'react';
import { CircularProgress, Typography, Box, Button } from '@mui/material';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import Toolbar from './Toolbar';
import { fetchDocumentData } from '../services/documentService';

const LoadingScreen = () => {
  const [status, setStatus] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { documentId } = useParams();
  const filename = location.state?.filename || 'document';

  const loadingTexts = [
    "extracting contract text...",
    "identifying contract metadata...",
    "creating contract summary...",
    "analysing potential risks...",
    "executing analysis engine..."
  ];

  const errorMessages = {
    1: "Failed to extract text from document",
    2: "Failed to identify contract metadata",
    3: "Failed to create contract summary",
    4: "Failed to analyze potential risks",
    5: "Failed to finalize analysis"
  };

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await fetchDocumentData(documentId);
        
        // Check if the previous status failed (status didn't increment after a timeout)
        if (data.status === status && status !== 5) {
          const timeoutDuration = 60000; // 1 min timeout
          setTimeout(() => {
            if (data.status === status) {
              setError(`${errorMessages[status + 1] || 'Processing failed'}`);
            }
          }, timeoutDuration);
        }

        if (data.status === 5) {
          // Analysis complete, navigate to visualization
          navigate(`/visualization/${documentId}`);
        } else {
          setStatus(data.status);
        }
      } catch (error) {
        console.error('Error checking status:', error);
        setError('Failed to connect to server');
      }
    };

    // Check status immediately and then every .5 seconds
    if (!error) {
      checkStatus();
      const intervalId = setInterval(checkStatus, 500);
      // Cleanup interval on component unmount
      return () => clearInterval(intervalId);
    }
  }, [documentId, navigate, status, error]);

  const handleRetry = () => {
    setError(null);
    setStatus(0);
  };

  if (error) {
    return (
      <div>
        <Toolbar />
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="80vh"
        >
          <Typography
            variant="h6"
            style={{
              marginBottom: '2rem',
              color: '#d32f2f',
              fontFamily: 'monospace',
            }}
          >
            {error}
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleRetry}
            style={{ marginTop: '1rem' }}
          >
            Retry
          </Button>
          <Button 
            variant="text" 
            onClick={() => navigate('/')}
            style={{ marginTop: '1rem' }}
          >
            Return to Home
          </Button>
        </Box>
      </div>
    );
  }

  return (
    <div>
      <Toolbar />
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="80vh"
      >
        <CircularProgress size={60} thickness={4} />
        <Typography
          variant="h6"
          style={{
            marginTop: '2rem',
            color: '#666',
            fontFamily: 'monospace',
            opacity: 0.8
          }}
        >
          {loadingTexts[status] || "Processing..."}
        </Typography>
        <Typography
          variant="body2"
          style={{
            marginTop: '1rem',
            color: '#999',
            fontFamily: 'monospace'
          }}
        >
          Processing: {filename}
        </Typography>
      </Box>
    </div>
  );
};

export default LoadingScreen; 