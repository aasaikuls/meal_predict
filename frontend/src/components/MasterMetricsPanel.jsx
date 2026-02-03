import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

function MasterMetricsPanel({ metrics, onMetricsUpdate, disabled }) {
  const [localMetrics, setLocalMetrics] = useState(metrics);
  const [masterData, setMasterData] = useState(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [expanded, setExpanded] = useState('panel1');

  useEffect(() => {
    // Load master metrics data from backend
    axios.get(`${API_BASE_URL}/api/master-metrics`)
      .then(response => {
        setMasterData(response.data);
      })
      .catch(err => {
        console.error('Error loading master metrics:', err);
      });
  }, []);

  useEffect(() => {
    setLocalMetrics(metrics);
  }, [metrics]);

  const handleSliderChange = (metric, value) => {
    const newMetrics = { ...localMetrics, [metric]: value };
    setLocalMetrics(newMetrics);
    onMetricsUpdate(newMetrics);
  };

  const handleReset = () => {
    const defaultMetrics = {
      nationality_importance: 40,
      age_importance: 20,
      destination_importance: 25,
      mealtime_importance: 15,
    };
    setLocalMetrics(defaultMetrics);
    onMetricsUpdate(defaultMetrics);
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  const renderProteinTable = (data, title) => {
    if (!data || data.length === 0) return null;

    const proteinColumns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
    const displayColumns = data.length > 0 ? Object.keys(data[0]).filter(key => 
      proteinColumns.includes(key)
    ) : [];

    return (
      <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: 'primary.lighter' }}>
                {title === 'Nationality' ? 'Country' : title === 'Age' ? 'Age Group' : 
                 title === 'Destination' ? 'Airport' : 'Meal Time'}
              </TableCell>
              {displayColumns.map(col => (
                <TableCell key={col} align="center" sx={{ fontWeight: 'bold', bgcolor: 'primary.lighter' }}>
                  {col}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.slice(0, 10).map((row, idx) => (
              <TableRow key={idx} hover>
                <TableCell>
                  {row.nationality_code || row.age_group || row.airport_code || row.meal_time || 'N/A'}
                </TableCell>
                {displayColumns.map(col => (
                  <TableCell key={col} align="center">
                    {(parseFloat(row[col]) * 100).toFixed(1)}%
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const totalImportance = 
    localMetrics.nationality_importance +
    localMetrics.age_importance +
    localMetrics.destination_importance +
    localMetrics.mealtime_importance;

  const isBalanced = Math.abs(totalImportance - 100) < 0.1;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          Master Metrics Management
        </Typography>
        <Button
          startIcon={<RestartAltIcon />}
          onClick={handleReset}
          disabled={disabled}
          size="small"
          variant="outlined"
        >
          Reset to Defaults
        </Button>
      </Box>

      {!isBalanced && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Total importance: {totalImportance.toFixed(1)}% (should equal 100%)
        </Alert>
      )}

      {/* Nationality - 40% */}
      <Accordion 
        expanded={expanded === 'panel1'} 
        onChange={handleAccordionChange('panel1')}
        disabled={disabled}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
            <Typography sx={{ flexGrow: 1, fontWeight: 'medium' }}>
              Weekday-Adjusted Nationality
            </Typography>
            <Chip 
              label={`${localMetrics.nationality_importance}%`} 
              color="primary" 
              size="small"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ px: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              What a nationality would prefer on a specific weekday
            </Typography>
            <Slider
              value={localMetrics.nationality_importance}
              onChange={(e, value) => handleSliderChange('nationality_importance', value)}
              min={35}
              max={45}
              step={1}
              marks
              valueLabelDisplay="auto"
              disabled={disabled}
              sx={{ mb: 3 }}
            />
            {masterData && renderProteinTable(masterData.nationality_sample, 'Nationality')}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Age Group - 20% */}
      <Accordion 
        expanded={expanded === 'panel2'} 
        onChange={handleAccordionChange('panel2')}
        disabled={disabled}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
            <Typography sx={{ flexGrow: 1, fontWeight: 'medium' }}>
              Age Group
            </Typography>
            <Chip 
              label={`${localMetrics.age_importance}%`} 
              color="primary" 
              size="small"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ px: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Age-based protein preferences
            </Typography>
            <Slider
              value={localMetrics.age_importance}
              onChange={(e, value) => handleSliderChange('age_importance', value)}
              min={15}
              max={25}
              step={1}
              marks
              valueLabelDisplay="auto"
              disabled={disabled}
              sx={{ mb: 3 }}
            />
            {masterData && renderProteinTable(masterData.age_sample, 'Age')}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Destination - 25% */}
      <Accordion 
        expanded={expanded === 'panel3'} 
        onChange={handleAccordionChange('panel3')}
        disabled={disabled}
        sx={{ mb: 2 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
            <Typography sx={{ flexGrow: 1, fontWeight: 'medium' }}>
              Destination of Flight
            </Typography>
            <Chip 
              label={`${localMetrics.destination_importance}%`} 
              color="primary" 
              size="small"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ px: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Regional protein preferences by destination
            </Typography>
            <Slider
              value={localMetrics.destination_importance}
              onChange={(e, value) => handleSliderChange('destination_importance', value)}
              min={20}
              max={30}
              step={1}
              marks
              valueLabelDisplay="auto"
              disabled={disabled}
              sx={{ mb: 3 }}
            />
            {masterData && renderProteinTable(masterData.destination_sample, 'Destination')}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Meal Time - 15% */}
      <Accordion 
        expanded={expanded === 'panel4'} 
        onChange={handleAccordionChange('panel4')}
        disabled={disabled}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
            <Typography sx={{ flexGrow: 1, fontWeight: 'medium' }}>
              Meal Time
            </Typography>
            <Chip 
              label={`${localMetrics.mealtime_importance}%`} 
              color="primary" 
              size="small"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ px: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Time-of-day meal preferences (Breakfast, Lunch, Dinner, etc.)
            </Typography>
            <Slider
              value={localMetrics.mealtime_importance}
              onChange={(e, value) => handleSliderChange('mealtime_importance', value)}
              min={10}
              max={20}
              step={1}
              marks
              valueLabelDisplay="auto"
              disabled={disabled}
              sx={{ mb: 3 }}
            />
            {masterData && renderProteinTable(masterData.mealtime_sample, 'Meal Time')}
          </Box>
        </AccordionDetails>
      </Accordion>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          Adjust the importance weights for each category. All weights should sum to 100% for optimal predictions.
        </Typography>
      </Box>
    </Box>
  );
}

export default MasterMetricsPanel;
