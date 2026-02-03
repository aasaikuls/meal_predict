import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import DataObjectIcon from '@mui/icons-material/DataObject';

const workflowSteps = [
  { 
    label: 'Loading Passenger Data', 
    description: 'Fetching forward booking data with passenger details and meal selections',
    duration: 2000,
    icon: <DataObjectIcon />
  },
  { 
    label: 'Analyzing Nationality Distribution', 
    description: 'Processing weekday-adjusted nationality preferences',
    duration: 3000,
    icon: <DataObjectIcon />
  },
  { 
    label: 'Processing Age Demographics', 
    description: 'Evaluating age group protein preferences',
    duration: 2000,
    icon: <DataObjectIcon />
  },
  { 
    label: 'Evaluating Destination Preferences', 
    description: 'Analyzing regional and cultural meal preferences',
    duration: 3000,
    icon: <DataObjectIcon />
  },
  { 
    label: 'Calculating Meal Time Factors', 
    description: 'Determining time-of-day meal patterns',
    duration: 2000,
    icon: <DataObjectIcon />
  },
  { 
    label: 'Running LLM Prediction Model', 
    description: 'AI model processing all factors and master metrics',
    duration: 4000,
    icon: <SmartToyIcon />
  },
  { 
    label: 'Optimizing Meal Proportions', 
    description: 'Fine-tuning predictions based on constraints',
    duration: 3000,
    icon: <SmartToyIcon />
  },
  { 
    label: 'Generating Recommendations', 
    description: 'Finalizing meal count predictions',
    duration: 2000,
    icon: <SmartToyIcon />
  },
];

function WorkflowProgress() {
  const [activeStep, setActiveStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    let currentStep = 0;
    let currentProgress = 0;
    const totalDuration = workflowSteps.reduce((sum, step) => sum + step.duration, 0);
    
    const runWorkflow = async () => {
      for (let i = 0; i < workflowSteps.length; i++) {
        const step = workflowSteps[i];
        setActiveStep(i);
        
        // Add log entry
        setLogs(prev => [...prev, {
          step: i,
          message: step.label,
          timestamp: new Date().toLocaleTimeString(),
        }]);

        // Animate progress for this step
        const stepProgress = (step.duration / totalDuration) * 100;
        const startProgress = currentProgress;
        const endProgress = currentProgress + stepProgress;
        const progressSteps = 20;
        const progressIncrement = stepProgress / progressSteps;
        const intervalDuration = step.duration / progressSteps;

        for (let j = 0; j < progressSteps; j++) {
          await new Promise(resolve => setTimeout(resolve, intervalDuration));
          currentProgress += progressIncrement;
          setProgress(Math.min(currentProgress, 100));
        }
      }
      
      // Complete
      setProgress(100);
    };

    runWorkflow();
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SmartToyIcon sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            AI Prediction Workflow
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Processing your meal prediction request...
          </Typography>
        </Box>
        <Chip 
          label={`${Math.round(progress)}%`} 
          color="primary" 
          sx={{ fontWeight: 'bold' }}
        />
      </Box>

      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ mb: 4, height: 8, borderRadius: 4 }}
      />

      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
        {/* Stepper */}
        <Box sx={{ flex: 1 }}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {workflowSteps.map((step, index) => (
              <Step key={step.label} completed={index < activeStep}>
                <StepLabel
                  StepIconComponent={() => (
                    index < activeStep ? (
                      <CheckCircleIcon color="success" />
                    ) : index === activeStep ? (
                      <HourglassEmptyIcon color="primary" sx={{ animation: 'spin 2s linear infinite' }} />
                    ) : (
                      <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'action.disabled' }} />
                    )
                  )}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: index === activeStep ? 'bold' : 'normal' }}>
                    {step.label}
                  </Typography>
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" color="text.secondary">
                    {step.description}
                  </Typography>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Box>

        {/* Live Logs */}
        <Paper 
          variant="outlined" 
          sx={{ 
            flex: 1, 
            p: 2, 
            bgcolor: 'grey.900', 
            color: 'common.white',
            maxHeight: 400,
            overflow: 'auto',
            fontFamily: 'monospace',
          }}
        >
          <Typography variant="caption" sx={{ color: 'grey.400', mb: 2, display: 'block' }}>
            LIVE PROCESSING LOGS
          </Typography>
          <List dense>
            {logs.map((log, index) => (
              <Fade in key={index} timeout={500}>
                <ListItem sx={{ px: 0, py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 30 }}>
                    <Typography variant="caption" sx={{ color: 'success.light' }}>
                      ▶
                    </Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="caption" component="span">
                        <span style={{ color: '#64b5f6' }}>[{log.timestamp}]</span>{' '}
                        <span style={{ color: '#81c784' }}>Step {log.step + 1}:</span>{' '}
                        {log.message}
                      </Typography>
                    }
                  />
                </ListItem>
              </Fade>
            ))}
          </List>
        </Paper>
      </Box>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </Paper>
  );
}

export default WorkflowProgress;
