import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  CheckCircle2,
  Database,
  Users,
  Cake,
  MapPin,
  UtensilsCrossed,
  Bot,
  Settings,
  ClipboardCheck
} from 'lucide-react';
import axios from 'axios';
import Container from '../components/layout/Container';
import PageTransition from '../components/layout/PageTransition';
import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import ResultsDisplay from '../components/ResultsDisplay';
import { API_BASE_URL } from '../config';

const workflowSteps = [
  { 
    id: 1,
    label: 'Loading Passenger Data', 
    description: 'Fetching booking data and passenger details',
    duration: 3000,
    icon: Database,
    color: '#3B82F6',
  },
  { 
    id: 2,
    label: 'Analyzing Nationality', 
    description: 'Processing weekday-adjusted nationality preferences',
    duration: 3000,
    icon: Users,
    color: '#9333EA',
  },
  { 
    id: 3,
    label: 'Processing Age Demographics', 
    description: 'Evaluating age group protein preferences',
    duration: 3000,
    icon: Cake,
    color: '#EC4899',
  },
  { 
    id: 4,
    label: 'Evaluating Destination', 
    description: 'Analyzing regional and cultural preferences',
    duration: 3000,
    icon: MapPin,
    color: '#14B8A6',
  },
  { 
    id: 5,
    label: 'Calculating Meal Time', 
    description: 'Determining time-of-day patterns',
    duration: 3000,
    icon: UtensilsCrossed,
    color: '#F59E0B',
  },
  { 
    id: 6,
    label: 'Running LLM Model', 
    description: 'AI processing all factors and metrics',
    duration: 3000,
    icon: Bot,
    color: '#8B5CF6',
  },
  { 
    id: 7,
    label: 'Optimizing Proportions', 
    description: 'Fine-tuning meal predictions',
    duration: 3000,
    icon: Settings,
    color: '#F97316',
  },
  { 
    id: 8,
    label: 'Generating Results', 
    description: 'Finalizing recommendations',
    duration: 3000,
    icon: ClipboardCheck,
    color: '#06B6D4',
  },
];

function PredictionScreen({ selectedFlight, flightDate, masterMetrics, predictionResults, setPredictionResults }) {
  const navigate = useNavigate();
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  const startPredictionRef = React.useRef();
  
  startPredictionRef.current = async () => {
    setIsRunning(true);
    setCurrentStep(0);
    setProgress(0);
    setElapsedTime(0);

    const totalDuration = workflowSteps.reduce((sum, step) => sum + step.duration, 0);
    let accumulatedTime = 0;

    // Start API call immediately in parallel with animation
    const apiPromise = (async () => {
      try {
        const flightLabel = `${selectedFlight.flightNumber} (${selectedFlight.origin} → ${selectedFlight.destination})`;
        const response = await axios.post(`${API_BASE_URL}/predict`, {
          flight_number: flightLabel,
          flight_date: flightDate,
          master_metrics: masterMetrics,
        });
        
        setPredictionResults(response.data);
        return response.data;
      } catch (error) {
        console.error('[PredictionScreen] Error fetching prediction:', error);
        throw error;
      }
    })();

    // Run through workflow steps animation in parallel
    for (let i = 0; i < workflowSteps.length; i++) {
      setCurrentStep(i);
      
      const step = workflowSteps[i];
      const stepProgress = (step.duration / totalDuration) * 100;
      const startProgress = (accumulatedTime / totalDuration) * 100;
      
      // Animate progress for this step
      const progressSteps = 20;
      const progressIncrement = stepProgress / progressSteps;
      const intervalDuration = step.duration / progressSteps;
      
      for (let j = 0; j < progressSteps; j++) {
        await new Promise(resolve => setTimeout(resolve, intervalDuration));
        setProgress(Math.min(startProgress + (progressIncrement * (j + 1)), 100));
      }
      
      accumulatedTime += step.duration;
    }

    // Wait for API to complete if animation finishes first
    await apiPromise;
    
    setProgress(100);
    setCurrentStep(workflowSteps.length);
    setIsRunning(false);
  };

  useEffect(() => {
    if (!selectedFlight) {
      navigate('/');
      return;
    }

    // Start prediction automatically
    if (!isRunning && !predictionResults) {
      startPredictionRef.current();
    }
  }, [selectedFlight, navigate, isRunning, predictionResults]);

  useEffect(() => {
    let timer;
    if (isRunning) {
      timer = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isRunning]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getBoxState = (stepIndex) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) return 'active';
    return 'pending';
  };

  const renderWorkflowBox = (step, index) => {
    const state = getBoxState(index);
    const Icon = step.icon;
    
    return (
      <motion.div
        key={step.id}
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ 
          opacity: 1, 
          scale: state === 'active' ? 1.02 : 1,
          y: 0,
        }}
        transition={{ 
          duration: 0.4, 
          delay: index * 0.08,
          type: 'spring',
          stiffness: 100,
        }}
        className="relative"
      >
        <Card className={`
          h-full transition-all duration-300 overflow-visible
          ${state === 'active' ? 'border-primary border-3 shadow-xl shadow-primary/30' : ''}
          ${state === 'completed' ? 'border-green-500 border-2 bg-gradient-to-br from-primary/5 to-green-50' : ''}
          ${state === 'pending' ? 'border-gray-200 bg-gray-50/50' : ''}
          hover:-translate-y-1 hover:shadow-lg
        `}>
          <CardContent className="text-center py-6 px-4">
            {/* Icon Container */}
            <div className={`
              mb-4 mx-auto w-18 h-18 rounded-full flex items-center justify-center
              ${state === 'active' ? 'bg-gradient-to-br from-primary to-primary/90 shadow-lg shadow-primary/50 animate-pulse' : ''}
              ${state === 'completed' ? 'bg-gradient-to-br from-green-500 to-green-600 shadow-md' : ''}
              ${state === 'pending' ? 'bg-gray-200' : ''}
            `}>
              {state === 'completed' ? (
                <CheckCircle2 className="w-12 h-12 text-white" />
              ) : state === 'active' ? (
                <Icon className="w-12 h-12 text-white animate-pulse" />
              ) : (
                <Icon className="w-12 h-12 text-gray-400" />
              )}
            </div>

            {/* Label */}
            <h3 className={`
              text-base font-bold mb-2 transition-colors
              ${state === 'active' ? 'text-foreground' : ''}
              ${state === 'completed' ? 'text-green-900' : ''}
              ${state === 'pending' ? 'text-gray-500' : ''}
            `}>
              {step.label}
            </h3>

            {/* Description */}
            <p className={`
              text-sm transition-colors
              ${state === 'active' ? 'text-primary/80' : ''}
              ${state === 'completed' ? 'text-green-700' : ''}
              ${state === 'pending' ? 'text-gray-400' : ''}
            `}>
              {step.description}
            </p>

            {/* Status Badge */}
            <div className="mt-3">
              {state === 'completed' && (
                <Badge variant="default" className="bg-green-500">
                  Complete
                </Badge>
              )}
              {state === 'active' && (
                <Badge variant="default" className="bg-primary animate-pulse">
                  Processing
                </Badge>
              )}
              {state === 'pending' && (
                <Badge variant="outline" className="text-gray-500">
                  Pending
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-white to-blue-50">
        {/* Header */}
        <div className="bg-gradient-to-r from-[hsl(var(--primary-dark,215_100%_25%))] to-primary shadow-lg">
          <Container>
            <div className="py-6 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Meal Prediction Analysis
                </h1>
                <p className="text-white/80">
                  Flight {selectedFlight?.route} • {flightDate}
                </p>
              </div>
              <Button
                variant="outline"
                onClick={() => navigate('/')}
                className="bg-white/10 border-white/30 text-white hover:bg-white/20"
              >
                <Home className="w-4 h-4 mr-2" />
                Home
              </Button>
            </div>
          </Container>
        </div>

        <Container className="py-8">
          <AnimatePresence mode="wait">
            {isRunning && (
              <motion.div
                key="workflow"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {/* Title */}
                <div className="text-center mb-8">
                  <h2 className="text-4xl font-bold bg-gradient-to-r from-[hsl(var(--primary-dark,215_100%_25%))] to-primary bg-clip-text text-transparent mb-3">
                    AI Prediction in Progress
                  </h2>
                  <p className="text-lg text-gray-600">
                    Processing meal predictions for your flight
                  </p>
                </div>

                {/* Overall Progress */}
                <Card className="mb-8 border-2 border-primary/20 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-bold text-foreground">
                        Overall Progress
                      </h3>
                      <div className="flex gap-6 items-center">
                        <span className="text-sm text-gray-600">
                          Time: {formatTime(elapsedTime)}
                        </span>
                        <span className="text-lg font-bold text-primary">
                          {Math.round(progress)}%
                        </span>
                      </div>
                    </div>
                    {/* Progress Bar */}
                    <div className="relative h-4 bg-primary/10 rounded-full overflow-hidden">
                      <motion.div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-primary/90 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Workflow Boxes */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {workflowSteps.map((step, index) => renderWorkflowBox(step, index))}
                </div>
              </motion.div>
            )}

            {!isRunning && predictionResults && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <ResultsDisplay 
                  results={predictionResults} 
                  selectedFlight={selectedFlight}
                  flightDate={flightDate}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </Container>
      </div>
    </PageTransition>
  );
}

export default PredictionScreen;
