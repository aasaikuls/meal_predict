import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import { API_BASE_URL } from '../config';

function FlightSelector({ onPredictionStart, onPredictionComplete, masterMetrics, disabled }) {
  const [flightNumber, setFlightNumber] = useState('');
  const [flightDate, setFlightDate] = useState('');
  const [availableFlights, setAvailableFlights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Load available flights
    axios.get(`${API_BASE_URL}/api/flights`)
      .then(response => {
        setAvailableFlights(response.data.flights);
        if (response.data.flights.length > 0) {
          setFlightNumber(response.data.flights[0]);
        }
      })
      .catch(err => {
        console.error('Error loading flights:', err);
      });

    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    setFlightDate(today);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!flightNumber || !flightDate) {
      setError('Please select both flight number and date');
      return;
    }

    setLoading(true);
    onPredictionStart();

    // Simulate workflow steps
    const workflowSteps = [
      { delay: 2000, message: 'Loading passenger data...' },
      { delay: 3000, message: 'Analyzing nationality distribution...' },
      { delay: 2000, message: 'Processing age demographics...' },
      { delay: 3000, message: 'Evaluating destination preferences...' },
      { delay: 2000, message: 'Calculating meal time factors...' },
      { delay: 4000, message: 'Running LLM prediction model...' },
      { delay: 3000, message: 'Optimizing meal proportions...' },
      { delay: 2000, message: 'Generating recommendations...' },
    ];

    let totalDelay = 0;
    workflowSteps.forEach(step => {
      totalDelay += step.delay;
    });

    // Wait for workflow to complete
    setTimeout(async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/predict`, {
          flight_number: flightNumber,
          flight_date: flightDate,
          master_metrics: masterMetrics,
        });

        setLoading(false);
        onPredictionComplete(response.data);
      } catch (err) {
        setLoading(false);
        setError('Error running prediction: ' + (err.response?.data?.detail || err.message));
        onPredictionComplete(null);
      }
    }, totalDelay);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Flight Selection
      </Typography>

      <form onSubmit={handleSubmit}>
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="flight-select-label">Flight Number</InputLabel>
          <Select
            labelId="flight-select-label"
            value={flightNumber}
            label="Flight Number"
            onChange={(e) => setFlightNumber(e.target.value)}
            disabled={disabled || loading}
          >
            {availableFlights.map((flight) => (
              <MenuItem key={flight} value={flight}>
                {flight}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <TextField
          fullWidth
          label="Flight Date"
          type="date"
          value={flightDate}
          onChange={(e) => setFlightDate(e.target.value)}
          InputLabelProps={{
            shrink: true,
          }}
          sx={{ mb: 3 }}
          disabled={disabled || loading}
        />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          type="submit"
          variant="contained"
          size="large"
          fullWidth
          endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
          disabled={disabled || loading}
          sx={{ py: 1.5 }}
        >
          {loading ? 'Running Prediction...' : 'Run Prediction'}
        </Button>
      </form>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.lighter', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Select a flight and date to generate meal predictions based on the master metrics configuration.
        </Typography>
      </Box>
    </Box>
  );
}

export default FlightSelector;
