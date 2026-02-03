import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ToastProvider } from './components/ui';
import FlightSelectionScreen from './screens/FlightSelectionScreen';
import MasterMetricsScreen from './screens/MasterMetricsScreen';
import PredictionScreen from './screens/PredictionScreen';
import './index.css';

function App() {
  const [selectedFlight, setSelectedFlight] = React.useState(null);
  const [flightDate, setFlightDate] = React.useState('');
  const [masterMetrics, setMasterMetrics] = React.useState({
    nationality_importance: 40,
    age_importance: 20,
    destination_importance: 25,
    mealtime_importance: 15,
  });
  const [predictionResults, setPredictionResults] = React.useState(null);

  return (
    <ToastProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-gold-50">
          {/* Background pattern overlay */}
          <div className="fixed inset-0 opacity-[0.03] pointer-events-none">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(147, 51, 234, 0.4) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(234, 179, 8, 0.3) 0%, transparent 50%)'
            }} />
          </div>

          <AnimatePresence mode="wait">
            <Routes>
              <Route
                path="/"
                element={
                  <FlightSelectionScreen
                    selectedFlight={selectedFlight}
                    setSelectedFlight={setSelectedFlight}
                    flightDate={flightDate}
                    setFlightDate={setFlightDate}
                  />
                }
              />
              <Route
                path="/metrics"
                element={
                  <MasterMetricsScreen
                    selectedFlight={selectedFlight}
                    flightDate={flightDate}
                    masterMetrics={masterMetrics}
                    setMasterMetrics={setMasterMetrics}
                    setPredictionResults={setPredictionResults}
                  />
                }
              />
              <Route
                path="/prediction"
                element={
                  <PredictionScreen
                    selectedFlight={selectedFlight}
                    flightDate={flightDate}
                    masterMetrics={masterMetrics}
                    predictionResults={predictionResults}
                    setPredictionResults={setPredictionResults}
                  />
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </div>
      </Router>
    </ToastProvider>
  );
}

export default App;

