import React, { useState, useEffect } from 'react';
import { Typography, Box, Paper, Grid, CircularProgress } from '@mui/material';
import { useParams } from 'react-router-dom';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import HighchartsTimeline from 'highcharts/modules/timeline';
import Toolbar from './Toolbar';
import { fetchDocumentData } from '../services/documentService';

const VisualizationPage = () => {
  const [documentData, setDocumentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { documentId } = useParams();

  useEffect(() => {
    const getDocumentData = async () => {
      try {
        const data = await fetchDocumentData(documentId);
        setDocumentData(data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };

    getDocumentData();
  }, [documentId]);

  const getTimelineOptions = (startDate, endDate, renewalStartDate, renewalEndDate) => {
    // Convert dates to timestamps
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Calculate dates 1 year before and after
    const beforeStart = new Date(start);
    beforeStart.setFullYear(start.getFullYear() - 1);
    const afterEnd = new Date(end);
    afterEnd.setFullYear(end.getFullYear() + 1);

    // Create base timeline data
    const timelineData = [
      {
        name: `Pre-contract Period`,
        color: '#cccccc'
      },
      {
        name: `Contract Term`,
        label: `${start.getFullYear()}/${start.getMonth()+1}/${start.getDate()} - ${end.getFullYear()}/${end.getMonth()+1}/${end.getDate()}`,
        color: '#ff9800'
      }
    ];

    // Add renewal period only if valid dates are provided
    if (renewalStartDate && renewalEndDate && 
        !isNaN(new Date(renewalStartDate)) && !isNaN(new Date(renewalEndDate))) {
      const renewalStart = new Date(renewalStartDate);
      const renewalEnd = new Date(renewalEndDate);
      
      timelineData.push({
        name: `Renewal Period`,
        label: `${renewalStart.getFullYear()}/${renewalStart.getMonth()+1}/${renewalStart.getDate()} - ${renewalEnd.getFullYear()}/${renewalEnd.getMonth()+1}/${renewalEnd.getDate()}`,
        color: '#4caf50'
      });
    }

    // Add post-contract period
    timelineData.push({
      name: `Post-contract Period`,
      color: '#cccccc'
    });

    return {
      chart: {
        type: 'timeline',
        height: '200px'
      },
      xAxis: {
        visible: false
      },
      yAxis: {
        visible: false
      },
      title: {
        text: 'Contract Timeline'
      },
      series: [{
        data: timelineData
      }]
    };
  };

  if (loading) {
    return (
      <>
        <Toolbar />
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" sx={{ mt: '64px' }}>
          <CircularProgress />
        </Box>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Toolbar />
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh" sx={{ mt: '64px' }}>
          <Typography color="error">Error: {error}</Typography>
        </Box>
      </>
    );
  }

  return (
    <>
      <Toolbar />
      <Box sx={{ p: 3, mt: '64px', position: 'relative', zIndex: 0 }}>
        <Grid container spacing={3}>
          {/* Summary Card */}
          <Grid item xs={12} sx={{ mt: 3 }}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Contract Summary
              </Typography>
              <Typography variant="body1">
                {documentData?.contract_summary || 'No summary available'}
              </Typography>
            </Paper>
          </Grid>

          {/* Metadata Card */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Contract Metadata
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>File Name:</strong> {documentData?.filename}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Upload Date:</strong> {new Date(documentData?.upload_date).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Parties Involved:</strong> {documentData?.parties_involved?.join(', ') || 'N/A'}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Effective Dates:</strong> {documentData?.effective_dates?.join(' - ') || 'N/A'}
              </Typography>
              <Typography variant="body2">
                <strong>Renewal Terms:</strong> {documentData?.renewal_terms?.join(' - ') || 'N/A'}
              </Typography>
            </Paper>
          </Grid>

          {/* Risk Analysis Card */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Risk Analysis
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Risk Level:</strong> {documentData?.risk || 'N/A'}
              </Typography>
              <Typography variant="body2" paragraph>
                <strong>Compliance Status:</strong> {documentData?.compliance ? 'Compliant' : 'Non-compliant'}
              </Typography>
              <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                <strong>Potential Risks:</strong><br />
                {documentData?.potential_risks || 'No risks identified'}
              </Typography>
            </Paper>
          </Grid>

          {/* Compliance Requirements Card */}
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Compliance Requirements
              </Typography>
              <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                {documentData?.compliance_requirements?.map((req, index) => (
                  <li key={index}>
                    <Typography variant="body2">{req}</Typography>
                  </li>
                )) || <Typography variant="body2">No compliance requirements found</Typography>}
              </ul>
            </Paper>
          </Grid>

          {/* Timeline Card */}
          <Grid item xs={12}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Contract Timeline
              </Typography>
              {documentData?.effective_dates?.[0] && documentData?.effective_dates?.[1] ? (
                <HighchartsReact
                  highcharts={Highcharts}
                  options={getTimelineOptions(
                    documentData.effective_dates[0],
                    documentData.effective_dates[1],
                    documentData.renewal_terms[0],
                    documentData.renewal_terms[1]
                  )}
                />
              ) : (
                <Typography variant="body2">No date information available</Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default VisualizationPage;
