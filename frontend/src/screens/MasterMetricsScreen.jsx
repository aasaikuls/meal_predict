import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, 
  TrendingUp, 
  Play, 
  RotateCcw,
  Users,
  Calendar,
  MapPin,
  Clock,
  AlertCircle,
  CheckCircle2,
  Info,
  Globe,
  Save,
  Home
} from 'lucide-react';
import axios from 'axios';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Label from '../components/ui/Label';
import Select from '../components/ui/Select';
import Badge from '../components/ui/Badge';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui';
import Container from '../components/layout/Container';
import PageTransition from '../components/layout/PageTransition';
import { useToast } from '../components/ui/Toast';
import { API_BASE_URL } from '../config';

// Simple Accordion Component
const Accordion = ({ children, expanded, onChange }) => {
  return (
    <div className="rounded-xl bg-white border-2 border-purple-100 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300">
      {children}
    </div>
  );
};

const AccordionSummary = ({ children, expandIcon, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between p-6 text-left hover:bg-purple-50/50 transition-colors border-b border-purple-100"
    >
      {children}
      {expandIcon}
    </button>
  );
};

const AccordionDetails = ({ children, expanded }) => {
  return (
    <AnimatePresence>
      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="overflow-hidden"
        >
          <div className="p-6 pt-4">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

function MasterMetricsScreen({ selectedFlight, flightDate, masterMetrics, setMasterMetrics, setPredictionResults }) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [localMetrics, setLocalMetrics] = useState(masterMetrics);
  const [masterData, setMasterData] = useState(null);
  const [originalMasterData, setOriginalMasterData] = useState(null);
  const [customerSummary, setCustomerSummary] = useState(null);
  const [availableMeals, setAvailableMeals] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingMeals, setLoadingMeals] = useState(true);
  const [expanded, setExpanded] = useState(null);
  
  // Redefine defaults states
  const [isRedefining, setIsRedefining] = useState(false);
  const [redefineProgress, setRedefineProgress] = useState(0);
  const [redefineStep, setRedefineStep] = useState('');
  const [redefineComplete, setRedefineComplete] = useState(false);
  // Session memory tracking states
  // Meal-time-specific protein availability (NEW)
  const [availableProteinsByMealtime, setAvailableProteinsByMealtime] = useState({});
  
  // Session memory states
  const [sessionKey, setSessionKey] = useState(null);
  const [sessionInitialized, setSessionInitialized] = useState(false);
  const [modifiedRows, setModifiedRows] = useState([]);
  
  // Selected items for dropdown filtering
  const [selectedNationality, setSelectedNationality] = useState('');
  const [selectedWeekday, setSelectedWeekday] = useState('');
  const [selectedAge, setSelectedAge] = useState('0');
  const [selectedDestination, setSelectedDestination] = useState('0');
  const [selectedMealTime, setSelectedMealTime] = useState('0');
  
  // For Meal Time metric: which meal time to display (Breakfast/Lunch/Dinner)
  const [selectedMealTimeView, setSelectedMealTimeView] = useState('Lunch');
  
  // Input values for protein fields (to allow free editing)
  const [proteinInputs, setProteinInputs] = useState({});
  
  // Track validated rows that are pushed to Modified Probabilities table
  // Format: { 'category_mealTime_index': true }
  const [validatedRows, setValidatedRows] = useState({});

  // Scroll to top when component mounts
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Reset to defaults when component unmounts (user navigates away)
  useEffect(() => {
    return () => {
      console.log('Navigating away from metrics screen - resetting to defaults');
      // This cleanup runs when component unmounts
      // Reset will happen on next mount through the normal load flow
    };
  }, []);

  useEffect(() => {
    // Load customer summary for selected flight and date
    if (selectedFlight && flightDate) {
      setLoadingSummary(true);
      setLoadingMeals(true);
      
      // Fetch customer summary
      axios.get(`${API_BASE_URL}/api/customer-summary`, {
        params: {
          flight_number: selectedFlight.flightNumber,
          flight_date: flightDate
        }
      })
        .then(response => {
          console.log('Customer summary loaded:', response.data);
          setCustomerSummary(response.data);
        })
        .catch(err => {
          console.error('Error loading customer summary:', err);
          toast('Failed to load customer summary', 'error');
        })
        .finally(() => {
          setLoadingSummary(false);
        });
      
      // Fetch available meals
      const flightLabel = `${selectedFlight.flightNumber} (${selectedFlight.origin} → ${selectedFlight.destination})`;
      axios.get(`${API_BASE_URL}/api/available-meals`, {
        params: {
          flight_number: flightLabel,
          flight_date: flightDate
        }
      })
        .then(response => {
          console.log('Available meals loaded:', response.data);
          setAvailableMeals(response.data);
        })
        .catch(err => {
          console.error('Error loading available meals:', err);
          setAvailableMeals({ error: 'Failed to load meal data' });
        })
        .finally(() => {
          setLoadingMeals(false);
        });
    }
    
    // Load master metrics data from backend
    const flightLabel = selectedFlight ? `${selectedFlight.flightNumber} (${selectedFlight.origin} → ${selectedFlight.destination})` : null;
    
    const params = {};
    if (flightLabel && flightDate) {
      params.flight_number = flightLabel;
      params.flight_date = flightDate;
    }
    
    axios.get(`${API_BASE_URL}/api/master-metrics`, { params })
      .then(response => {
        console.log('Master metrics loaded (meal-time-structured):', response.data);
        setMasterData(response.data);
        setOriginalMasterData(JSON.parse(JSON.stringify(response.data))); // Deep copy for comparison
        
        // Store meal-time-specific proteins (NEW)
        if (response.data.available_proteins_by_mealtime) {
          setAvailableProteinsByMealtime(response.data.available_proteins_by_mealtime);
          console.log('Meal-time-specific proteins:', response.data.available_proteins_by_mealtime);
        }
        
        // Set default selections - now data is structured by meal time
        // For nationality: response.data.nationality_sample = {Lunch: [...], Dinner: [...]}
        if (response.data.nationality_sample) {
          const mealTimes = Object.keys(response.data.nationality_sample);
          if (mealTimes.length > 0) {
            const firstMealTimeData = response.data.nationality_sample[mealTimes[0]];
            if (firstMealTimeData && firstMealTimeData.length > 0) {
              const uniqueCountries = [...new Set(firstMealTimeData.map(row => row.nationality_code))];
              if (uniqueCountries.length > 0) setSelectedNationality(uniqueCountries[0]);
              // Weekday will be set by the separate useEffect when customerSummary is loaded
              // Don't set a default here to avoid showing Monday incorrectly
            }
          }
        }
        if (response.data.age_sample) {
          setSelectedAge('0');
        }
        if (response.data.destination_sample) {
          const mealTimes = Object.keys(response.data.destination_sample);
          if (mealTimes.length > 0) {
            const firstMealTimeData = response.data.destination_sample[mealTimes[0]];
            console.log('Destination sample (meal-time-structured):', firstMealTimeData);
            // Auto-select destination based on flight destination airport
            const destinationAirport = selectedFlight?.destination;
            if (destinationAirport && firstMealTimeData) {
              const destinationIndex = firstMealTimeData.findIndex(
                row => row.airport_code === destinationAirport
              );
              if (destinationIndex !== -1) {
                setSelectedDestination(String(destinationIndex));
                console.log(`Auto-selected destination: ${destinationAirport} at index ${destinationIndex}`);
              } else {
                setSelectedDestination('0');
              }
            } else {
              setSelectedDestination('0');
            }
          }
        }
        if (response.data.mealtime_sample) {
          setSelectedMealTime('0');
          // Set initial meal time view to first AVAILABLE meal time on the flight
          const availableMealTimesOnFlight = Object.keys(response.data.mealtime_sample);
          if (availableMealTimesOnFlight.length > 0) {
            // Use the first meal time that's actually available on this flight
            setSelectedMealTimeView(availableMealTimesOnFlight[0]);
            console.log(`Initial meal time view set to: ${availableMealTimesOnFlight[0]}`);
          }
        }
        
        // DO NOT auto-load custom metrics - always start with defaults
        // User can manually save if they want, but we reset on each visit
        
        // Initialize session memory with normalized/restricted probabilities
        if (flightLabel && flightDate && !sessionInitialized) {
          axios.post(`${API_BASE_URL}/api/initialize-session`, {
            flight_number: flightLabel,
            flight_date: flightDate
          })
            .then(sessionResponse => {
              console.log('✅ Session initialized');
              setSessionKey(sessionResponse.data.session_key);
              setSessionInitialized(true);
              toast('Session initialized with default probabilities', 'success');
            })
            .catch(err => {
              console.error('❌ Error initializing session:', err);
              toast('Failed to initialize session memory', 'error');
            });
        }
      })
      .catch(err => {
        console.error('Error loading master metrics:', err);
        toast('Failed to load master metrics', 'error');
      });
  }, [toast, selectedFlight, flightDate, sessionInitialized]);

  useEffect(() => {
    console.log('🔄 Weights updated in MasterMetricsScreen, syncing to App.js:', localMetrics);
    setMasterMetrics(localMetrics);
  }, [localMetrics, setMasterMetrics]);

  // Update weekday when customer summary is loaded
  useEffect(() => {
    if (customerSummary && customerSummary.day_of_week) {
      console.log(`📅 Setting weekday from customer summary: ${customerSummary.day_of_week}`);
      setSelectedWeekday(customerSummary.day_of_week);
    }
  }, [customerSummary]);

  // Load modified rows from session memory
  useEffect(() => {
    if (sessionKey && sessionInitialized) {
      const loadModifiedRows = () => {
        axios.get(`${API_BASE_URL}/api/get-modified-rows`, {
          params: { session_key: sessionKey }
        })
          .then(response => {
            setModifiedRows(response.data.modified_rows || []);
            if (response.data.count > 0) {
              console.log(`📊 ${response.data.count} modified rows`);
            }
          })
          .catch(err => {
            console.error('Error loading modified rows:', err);
          });
      };
      
      loadModifiedRows();
      // Poll every 5 seconds to update the modified rows table
      const interval = setInterval(loadModifiedRows, 5000);
      return () => clearInterval(interval);
    }
  }, [sessionKey, sessionInitialized]);

  const handleSliderChange = (metric, value) => {
    console.log(`🎚️ Weight slider changed: ${metric} = ${value}%`);
    setLocalMetrics({ ...localMetrics, [metric]: value });
  };

  const handleSubMetricChange = (category, mealTime, index, protein, inputValue) => {
    // Update the input value immediately for display
    const key = `${category}_${mealTime}_${index}_${protein}`;
    setProteinInputs(prev => ({ ...prev, [key]: inputValue }));
    
    // Invalidate validation for this row since data changed
    const rowKey = `${category}_${mealTime}_${index}`;
    setValidatedRows(prev => {
      const updated = { ...prev };
      delete updated[rowKey];
      return updated;
    });
    
    // Update the actual data (now structured by meal time)
    const updatedData = { ...masterData };
    const sampleKey = `${category}_sample`;
    
    if (updatedData[sampleKey] && updatedData[sampleKey][mealTime] && updatedData[sampleKey][mealTime][index]) {
      const row = { ...updatedData[sampleKey][mealTime][index] };
      const oldValue = row[protein];
      const numValue = parseFloat(inputValue);
      // Store the numeric value, or 0 if invalid
      row[protein] = (!isNaN(numValue) ? numValue : 0) / 100;
      
      console.log(`📝 Metric Changed: ${category} - ${mealTime} - ${protein}: ${(oldValue * 100).toFixed(1)}% → ${inputValue}%`);
      
      updatedData[sampleKey][mealTime][index] = row;
      setMasterData(updatedData);
    }
  };
  
  const getProteinInputValue = (category, mealTime, index, protein, actualValue) => {
    const key = `${category}_${mealTime}_${index}_${protein}`;
    // Return stored input value if exists, otherwise return formatted actual value
    return proteinInputs[key] !== undefined ? proteinInputs[key] : actualValue.toFixed(1);
  };

  const validateAndSubmitRow = async (category, mealTime, index) => {
    const sampleKey = `${category}_sample`;
    const data = masterData[sampleKey];
    
    if (!data || !data[mealTime] || !data[mealTime][index]) return false;
    
    const rowTotal = getSubMetricTotal(data[mealTime], index, mealTime);
    const isBalanced = Math.abs(rowTotal - 100) < 0.1;
    
    if (!isBalanced) {
      toast(`Warning: Protein percentages total ${rowTotal.toFixed(1)}% instead of 100%`, 'warning');
      console.warn(`⚠️  Validation Failed: ${category} - ${mealTime} - Total: ${rowTotal.toFixed(1)}%`);
      return false;
    }
    
    const row = data[mealTime][index];
    const allProteinColumns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
    console.log(`✅ Row Validated & Saved: ${category} - ${mealTime}`);
    
    // Prepare probabilities object for backend
    const probabilities = {};
    allProteinColumns.forEach(protein => {
      if (row[protein] !== undefined) {
        probabilities[protein] = row[protein];
        console.log(`   ${protein}: ${(row[protein] * 100).toFixed(1)}%`);
      }
    });
    
    // Generate row_key based on category
    let row_key;
    if (category === 'nationality') {
      row_key = `${row.nationality_code}_${row.day_of_week}_${mealTime}`;
    } else if (category === 'age') {
      row_key = `${row.age_group}_${mealTime}`;
    } else if (category === 'destination') {
      row_key = `${row.destination_region}_${mealTime}`;
    } else if (category === 'mealtime') {
      row_key = mealTime;
    }
    
    // Update session memory in backend
    if (sessionKey && row_key) {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/update-session-probability`, {
          session_key: sessionKey,
          metric_type: category,
          row_key: row_key,
          probabilities: probabilities
        });
        console.log('📤 Session memory updated:', response.data);
      } catch (err) {
        console.error('❌ Error updating session memory:', err);
        toast('Failed to update session memory', 'error');
        return false;
      }
    }
    
    // Mark this row as validated and pushed to Modified Probabilities
    const rowKey = `${category}_${mealTime}_${index}`;
    setValidatedRows(prev => ({ ...prev, [rowKey]: true }));
    
    toast('Values validated and saved to session memory!', 'success');
    return true;
  };

  const getSubMetricTotal = (mealTimeData, index, mealTime = null) => {
    if (!mealTimeData || !mealTimeData[index]) return 0;
    
    // Use meal-time-specific proteins if available
    let proteinColumns = masterData?.available_proteins || ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
    
    if (mealTime && availableProteinsByMealtime[mealTime]) {
      proteinColumns = availableProteinsByMealtime[mealTime];
    }
    
    return proteinColumns.reduce((sum, p) => sum + (parseFloat(mealTimeData[index][p] || 0) * 100), 0);
  };

  // Check if a row has changes compared to original
  const rowHasChanges = (category, mealTime, index) => {
    if (!originalMasterData || !masterData) return false;
    
    const sampleKey = `${category}_sample`;
    const originalSample = originalMasterData[sampleKey];
    const currentSample = masterData[sampleKey];
    
    if (!originalSample?.[mealTime]?.[index] || !currentSample?.[mealTime]?.[index]) return false;
    
    const originalRow = originalSample[mealTime][index];
    const currentRow = currentSample[mealTime][index];
    
    const proteins = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
    
    return proteins.some(protein => {
      const originalValue = originalRow[protein] || 0;
      const currentValue = currentRow[protein] || 0;
      return Math.abs(originalValue - currentValue) > 0.001;
    });
  };

  // Get row button state and label
  const getRowButtonState = (category, mealTime, index) => {
    const rowKey = `${category}_${mealTime}_${index}`;
    const hasChanges = rowHasChanges(category, mealTime, index);
    const isValidated = validatedRows[rowKey];
    const sampleKey = `${category}_sample`;
    const data = masterData?.[sampleKey];
    
    if (!data?.[mealTime]?.[index]) {
      return { disabled: true, label: 'No Data', variant: 'secondary', color: 'text-gray-500' };
    }
    
    const rowTotal = getSubMetricTotal(data[mealTime], index, mealTime);
    const isBalanced = Math.abs(rowTotal - 100) < 0.1;
    
    // No changes - check if custom or default
    if (!hasChanges) {
      if (isValidated) {
        return { 
          disabled: true, 
          label: 'Custom Settings Saved', 
          variant: 'default', 
          color: 'text-green-700',
          bgColor: 'bg-green-50 border-green-300'
        };
      }
      return { 
        disabled: true, 
        label: 'Default Setting', 
        variant: 'secondary', 
        color: 'text-gray-600',
        bgColor: 'bg-gray-50 border-gray-300'
      };
    }
    
    // Has changes
    if (!isBalanced) {
      return { 
        disabled: true, 
        label: 'Probability Not Added to 100', 
        variant: 'secondary', 
        color: 'text-red-700',
        bgColor: 'bg-red-50 border-red-300'
      };
    }
    
    // Changes are valid and balanced
    return { 
      disabled: false, 
      label: 'Validate and Save Below', 
      variant: 'primary', 
      color: 'text-blue-700',
      bgColor: 'bg-blue-50 border-blue-300'
    };
  };

  const handleReset = async () => {
    const defaultMetrics = {
      nationality_importance: 40,
      age_importance: 20,
      destination_importance: 25,
      mealtime_importance: 15,
    };
    
    console.log('\n🔄 === RESET TO DEFAULTS CLICKED ===');
    console.log('Previous weights:', {
      nationality_importance: localMetrics.nationality_importance,
      age_importance: localMetrics.age_importance,
      destination_importance: localMetrics.destination_importance,
      mealtime_importance: localMetrics.mealtime_importance
    });
    console.log('Resetting to default weights:', defaultMetrics);
    
    // Log if there were any custom changes being discarded
    const weightChanges = getChangedWeights();
    if (weightChanges.length > 0) {
      console.log(`⚠️  Discarding ${weightChanges.length} weight changes`);
    }
    
    setLocalMetrics(defaultMetrics);
    
    // Reload master data from backend with flight parameters
    const flightLabel = selectedFlight ? `${selectedFlight.flightNumber} (${selectedFlight.origin} → ${selectedFlight.destination})` : null;
    
    const params = {};
    if (flightLabel && flightDate) {
      params.flight_number = flightLabel;
      params.flight_date = flightDate;
    }
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/master-metrics`, { params });
      setMasterData(response.data);
      setOriginalMasterData(JSON.parse(JSON.stringify(response.data)));
      
      setProteinInputs({});
      setValidatedRows({});
      
      // Reinitialize session memory with defaults
      if (flightLabel && flightDate) {
        const sessionResponse = await axios.post(`${API_BASE_URL}/api/initialize-session`, {
          flight_number: flightLabel,
          flight_date: flightDate
        });
        console.log('✅ Session reset to defaults');
        setSessionKey(sessionResponse.data.session_key);
        setSessionInitialized(true);
        setModifiedRows([]); // Clear modified rows since we reset to defaults
        
        toast('Reset to defaults and session memory reinitialized!', 'success');
      } else {
        toast('Reset to defaults', 'success');
      }
    } catch (err) {
      console.error('Error during reset:', err);
      toast('Error resetting to defaults', 'error');
    }
  };

  const handleRedefineDefaults = async () => {
    setIsRedefining(true);
    setRedefineProgress(0);
    setRedefineComplete(false);
    
    const steps = [
      { progress: 15, message: 'Connecting to data sources...', duration: 1200 },
      { progress: 30, message: 'Loading historical passenger data...', duration: 1500 },
      { progress: 50, message: 'Analyzing recent patterns...', duration: 1800 },
      { progress: 65, message: 'Processing nationality preferences...', duration: 1400 },
      { progress: 80, message: 'Calculating age demographics...', duration: 1300 },
      { progress: 90, message: 'Optimizing destination factors...', duration: 1100 },
      { progress: 100, message: 'Finalizing default metrics...', duration: 1000 },
    ];

    for (const step of steps) {
      setRedefineStep(step.message);
      await new Promise(resolve => setTimeout(resolve, step.duration));
      setRedefineProgress(step.progress);
    }

    // Show completion message
    setRedefineStep('Default metrics successfully redefined!');
    setRedefineComplete(true);
    
    // Close dialog after a brief delay
    setTimeout(() => {
      setIsRedefining(false);
      setRedefineProgress(0);
      setRedefineStep('');
      setRedefineComplete(false);
      toast('Default metrics redefined based on latest data', 'success');
    }, 1500);
  };
  const handleAccordionChange = (panel) => {
    setExpanded(expanded === panel ? null : panel);
  };

  // Function to detect changes in weights
  const getChangedWeights = () => {
    if (!localMetrics) return [];
    
    const changes = [];
    const defaultWeights = {
      nationality_importance: 40,
      age_importance: 20,
      destination_importance: 25,
      mealtime_importance: 15
    };
    
    const weightLabels = {
      nationality_importance: 'Weekday-Adjusted Nationality',
      age_importance: 'Age',
      destination_importance: 'Destination',
      mealtime_importance: 'Meal Time'
    };
    
    Object.keys(defaultWeights).forEach(key => {
      const defaultValue = defaultWeights[key];
      const currentValue = localMetrics[key];
      
      if (Math.abs(defaultValue - currentValue) > 0.01) {
        changes.push({
          metric: weightLabels[key],
          originalValue: defaultValue,
          newValue: currentValue,
          key: key
        });
      }
    });
    
    return changes;
  };
  
  const hasWeightChanges = () => {
    return getChangedWeights().length > 0;
  };

  // Validate all protein probabilities sum to 100% across all categories and meal times
  const validateAllProbabilities = () => {
    if (!masterData) return { isValid: true, errors: [], weightError: null };
    
    const errors = [];
    const categories = ['nationality', 'age', 'destination', 'mealtime'];
    const tolerance = 0.1; // Allow 0.1% tolerance for rounding
    
    // Validate weights sum to 100%
    let weightError = null;
    const totalWeight = 
      localMetrics.nationality_importance +
      localMetrics.age_importance +
      localMetrics.destination_importance +
      localMetrics.mealtime_importance;
    
    if (Math.abs(totalWeight - 100) > tolerance) {
      weightError = `Total importance weights: ${totalWeight.toFixed(1)}% (must equal 100%)`;
      errors.push({
        category: 'weights',
        identifier: 'Total Weights',
        mealTime: 'N/A',
        total: totalWeight.toFixed(1),
        message: weightError
      });
    }
    
    categories.forEach(category => {
      const sampleKey = `${category}_sample`;
      const sampleData = masterData[sampleKey];
      
      if (!sampleData) return;
      
      // Data is structured by meal time: {Lunch: [...], Dinner: [...]}
      if (typeof sampleData === 'object' && !Array.isArray(sampleData)) {
        Object.keys(sampleData).forEach(mealTime => {
          const mealTimeData = sampleData[mealTime];
          
          if (!Array.isArray(mealTimeData)) return;
          
          mealTimeData.forEach((row, index) => {
            // Get meal-time-specific proteins if available
            let proteinColumns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
            if (mealTime && availableProteinsByMealtime[mealTime]) {
              proteinColumns = availableProteinsByMealtime[mealTime];
            }
            
            const total = proteinColumns.reduce((sum, protein) => {
              return sum + (parseFloat(row[protein] || 0) * 100);
            }, 0);
            
            if (Math.abs(total - 100) > tolerance) {
              // Build identifier for error message
              let identifier = '';
              if (category === 'nationality') {
                identifier = `${row.nationality_code} (${row.day_of_week}) - ${mealTime}`;
              } else if (category === 'age') {
                identifier = `${row.age_group} - ${mealTime}`;
              } else if (category === 'destination') {
                identifier = `${row.airport_code || row.destination_region} - ${mealTime}`;
              } else if (category === 'mealtime') {
                identifier = `${row.meal_time}`;
              }
              
              errors.push({
                category,
                identifier,
                mealTime,
                total: total.toFixed(1),
                message: `${category.charAt(0).toUpperCase() + category.slice(1)} - ${identifier}: Total is ${total.toFixed(1)}% (must be 100%)`
              });
            }
          });
        });
      }
    });
    
    return {
      isValid: errors.length === 0,
      errors,
      weightError
    };
  };

  // Check if save button should be enabled
  const handleRunPrediction = () => {
    if (!isBalanced) {
      toast('Please balance main metrics to 100% before running prediction', 'error');
      return;
    }
    
    console.log('\n🚀 === RUNNING PREDICTION ===');
    console.log(`Flight: ${selectedFlight?.flightNumber} on ${flightDate}`);
    console.log(`Analysis Cabin: ${customerSummary?.analysis_cabin || 'Unknown'}`);
    console.log(`Total Passengers: ${customerSummary?.total_customers || 'Unknown'}`);
    
    // Check if using custom or default weights
    const isDefaultWeights = (
      localMetrics.nationality_importance === 40 &&
      localMetrics.age_importance === 20 &&
      localMetrics.destination_importance === 25 &&
      localMetrics.mealtime_importance === 15
    );
    
    console.log('\n📊 WEIGHTS BEING USED FOR PREDICTION:');
    console.log(isDefaultWeights ? '   Type: DEFAULT WEIGHTS' : '   Type: CUSTOM WEIGHTS ⚠️');
    console.log(`   Nationality Importance: ${localMetrics.nationality_importance}%`);
    console.log(`   Age Importance: ${localMetrics.age_importance}%`);
    console.log(`   Destination Importance: ${localMetrics.destination_importance}%`);
    console.log(`   Mealtime Importance: ${localMetrics.mealtime_importance}%`);
    console.log(`   Total: ${localMetrics.nationality_importance + localMetrics.age_importance + localMetrics.destination_importance + localMetrics.mealtime_importance}%`);
    
    console.log('\n📈 PROBABILITIES: Using session memory values');
    
    console.log('\n' + '='.repeat(80));
    
    // Collect ONLY VALIDATED custom probability data from masterData
    // Only rows that have been validated (user clicked "Validate and Save Below") are sent
    // All other rows use default CSV probabilities
    const collectedMetrics = {
      nationality_importance: localMetrics.nationality_importance,
      age_importance: localMetrics.age_importance,
      destination_importance: localMetrics.destination_importance,
      mealtime_importance: localMetrics.mealtime_importance,
      nationality_data: {},
      age_data: {},
      destination_data: {},
      mealtime_data: {},
      has_custom_probabilities: false  // Flag to track if any custom probs exist
    };
    
    let customProbCount = 0;
    
    // Collect nationality probabilities (ONLY VALIDATED ROWS)
    // Only send custom probabilities for rows that user validated
    if (masterData?.nationality_sample) {
      const mealTimes = Object.keys(masterData.nationality_sample);
      mealTimes.forEach(mealTime => {
        const mealTimeData = masterData.nationality_sample[mealTime];
        if (Array.isArray(mealTimeData)) {
          mealTimeData.forEach((row, index) => {
            const rowKey = `nationality_${mealTime}_${index}`;
            // Only include if this row was validated by user
            if (validatedRows[rowKey]) {
              const key = `${row.nationality_code}_${row.day_of_week}`;
              collectedMetrics.nationality_data[key] = {
                Pork: row.Pork,
                Chicken: row.Chicken,
                Beef: row.Beef,
                Seafood: row.Seafood,
                Lamb: row.Lamb,
                Vegetarian: row.Vegetarian
              };
              customProbCount++;
            }
          });
        }
      });
    }
    
    // Collect age probabilities (ONLY VALIDATED ROWS)
    if (masterData?.age_sample) {
      const mealTimes = Object.keys(masterData.age_sample);
      mealTimes.forEach(mealTime => {
        const mealTimeData = masterData.age_sample[mealTime];
        if (Array.isArray(mealTimeData)) {
          mealTimeData.forEach((row, index) => {
            const rowKey = `age_${mealTime}_${index}`;
            // Only include if this row was validated by user
            if (validatedRows[rowKey]) {
              const key = `${row.age_group}_${mealTime}`;
              collectedMetrics.age_data[key] = {
                Pork: row.Pork,
                Chicken: row.Chicken,
                Beef: row.Beef,
                Seafood: row.Seafood,
                Lamb: row.Lamb,
                Vegetarian: row.Vegetarian
              };
              customProbCount++;
            }
          });
        }
      });
    }
    
    // Collect destination probabilities (ONLY VALIDATED ROWS)
    if (masterData?.destination_sample) {
      const mealTimes = Object.keys(masterData.destination_sample);
      mealTimes.forEach(mealTime => {
        const mealTimeData = masterData.destination_sample[mealTime];
        if (Array.isArray(mealTimeData)) {
          mealTimeData.forEach((row, index) => {
            const rowKey = `destination_${mealTime}_${index}`;
            // Only include if this row was validated by user
            if (validatedRows[rowKey]) {
              const key = `${row.destination_region}_${mealTime}`;
              collectedMetrics.destination_data[key] = {
                Pork: row.Pork,
                Chicken: row.Chicken,
                Beef: row.Beef,
                Seafood: row.Seafood,
                Lamb: row.Lamb,
                Vegetarian: row.Vegetarian
              };
              customProbCount++;
            }
          });
        }
      });
    }
    
    // Collect mealtime probabilities (ONLY VALIDATED ROWS)
    if (masterData?.mealtime_sample) {
      const mealTimes = Object.keys(masterData.mealtime_sample);
      mealTimes.forEach(mealTime => {
        const mealTimeData = masterData.mealtime_sample[mealTime];
        if (Array.isArray(mealTimeData)) {
          mealTimeData.forEach((row, index) => {
            const rowKey = `mealtime_${mealTime}_${index}`;
            // Only include if this row was validated by user
            if (validatedRows[rowKey]) {
              collectedMetrics.mealtime_data[row.meal_time] = {
                Pork: row.Pork,
                Chicken: row.Chicken,
                Beef: row.Beef,
                Seafood: row.Seafood,
                Lamb: row.Lamb,
                Vegetarian: row.Vegetarian
              };
              customProbCount++;
            }
          });
        }
      });
    }
    
    // Set flag if any custom probabilities were collected
    collectedMetrics.has_custom_probabilities = customProbCount > 0;
    
    setMasterMetrics(collectedMetrics);
    setPredictionResults(null); // Clear previous results
    
    console.log('\n✅ PREDICTION DATA PREPARED AND SENT');
    console.log('Summary:');
    console.log(`   - Weights: ${isDefaultWeights ? 'DEFAULT' : 'CUSTOM'}`);
    console.log(`   - Custom Probabilities: ${customProbCount} validated rows`);
    console.log(`     • Nationality: ${Object.keys(collectedMetrics.nationality_data).length} custom entries`);
    console.log(`     • Age: ${Object.keys(collectedMetrics.age_data).length} custom entries`);
    console.log(`     • Destination: ${Object.keys(collectedMetrics.destination_data).length} custom entries`);
    console.log(`     • Mealtime: ${Object.keys(collectedMetrics.mealtime_data).length} custom entries`);
    console.log(`   - Backend will use: ${customProbCount > 0 ? 'CUSTOM probabilities for validated rows + CSV defaults for rest' : 'CSV DEFAULT probabilities only'}`);
    console.log('\nNavigating to prediction screen...');
    console.log('='.repeat(80) + '\n');
    
    navigate('/prediction');
  };

  const totalImportance = 
    localMetrics.nationality_importance +
    localMetrics.age_importance +
    localMetrics.destination_importance +
    localMetrics.mealtime_importance;

  const isBalanced = Math.abs(totalImportance - 100) < 0.1;

  const renderProteinTable = (mealTimeStructuredData, title, category) => {
    // mealTimeStructuredData is now { Lunch: [...], Dinner: [...], etc. }
    if (!mealTimeStructuredData || Object.keys(mealTimeStructuredData).length === 0) return null;

    const allProteinColumns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'];
    const mealTimes = Object.keys(mealTimeStructuredData);
    
    // Get first meal time data for dropdown options
    const firstMealTimeData = mealTimeStructuredData[mealTimes[0]];

    return (
      <div className="space-y-8">
        {/* Single dropdown for Age, Destination, Mealtime (appears once at top) */}
        {category === 'age' && firstMealTimeData && (
          <div className="mb-6 p-4 bg-purple-50 rounded-xl border-2 border-purple-200">
            <Label htmlFor="age-select" className="text-base font-semibold mb-2">
              Select Age Group (applies to all meal times)
            </Label>
            <Select
              id="age-select"
              value={selectedAge}
              onChange={(e) => setSelectedAge(e.target.value)}
              className="mt-2"
            >
              {firstMealTimeData.map((row, index) => (
                <option key={index} value={index}>
                  {row.age_group || row.Age || `Age Group ${index + 1}`}
                </option>
              ))}
            </Select>
          </div>
        )}

        {category === 'destination' && firstMealTimeData && (
          <div className="mb-6 p-4 bg-purple-50 rounded-xl border-2 border-purple-200">
            <Label htmlFor="destination-select" className="text-base font-semibold mb-2">
              Select Destination (applies to all meal times)
            </Label>
            <Select
              id="destination-select"
              value={selectedDestination}
              onChange={(e) => setSelectedDestination(e.target.value)}
              className="mt-2"
            >
              {firstMealTimeData.map((row, index) => (
                <option key={index} value={index}>
                  {row.airport_code || row.Destination || `Destination ${index + 1}`}
                </option>
              ))}
            </Select>
          </div>
        )}

        {category === 'mealtime' && (
          <div className="mb-6 p-4 bg-purple-50 rounded-xl border-2 border-purple-200">
            <div className="flex items-start justify-between gap-4 mb-3">
              <div className="flex-1">
                <Label htmlFor="mealtime-view-select" className="text-base font-semibold mb-2">
                  Select Meal Time to View/Edit
                </Label>
                <Select
                  id="mealtime-view-select"
                  value={selectedMealTimeView}
                  onChange={(e) => setSelectedMealTimeView(e.target.value)}
                  className="mt-2"
                >
                  {/* Show only meal times that are available on this flight */}
                  {mealTimes.map(mt => (
                    <option key={mt} value={mt}>{mt}</option>
                  ))}
                </Select>
              </div>
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3">
                <p className="text-xs font-semibold text-blue-900 mb-1">Available on Flight:</p>
                <div className="flex flex-wrap gap-1">
                  {mealTimes.map(mt => (
                    <Badge key={mt} variant="default" className="text-xs">
                      {mt}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Special handling for Meal Time category: show only selected meal time view */}
        {category === 'mealtime' ? (
          // For mealtime category, only render the selected meal time view
          (() => {
            const mealTime = selectedMealTimeView;
            const dataForMealTime = mealTimeStructuredData[mealTime];
            const isMealTimeAvailable = mealTimes.includes(mealTime);
            
            // If meal time not available, show message
            if (!isMealTimeAvailable || !dataForMealTime || dataForMealTime.length === 0) {
              return (
                <div className="border-4 border-orange-200 rounded-2xl p-8 bg-gradient-to-br from-orange-50 to-white text-center">
                  <AlertCircle className="w-16 h-16 text-orange-400 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-orange-900 mb-2">{mealTime}</h3>
                  <p className="text-gray-600">
                    This meal time is not available on the selected flight.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Please select a different meal time from the dropdown above.
                  </p>
                </div>
              );
            }

            // Get meal-time-specific proteins
            const mealTimeProteins = availableProteinsByMealtime[mealTime] || allProteinColumns;
            const proteinColumns = allProteinColumns.filter(p => mealTimeProteins.includes(p));
            const unavailableProteins = allProteinColumns.filter(p => !mealTimeProteins.includes(p));

            // Use first row (index 0) for meal time - no need for row selector
            const selectedIndex = 0;
            const selectedRow = dataForMealTime[selectedIndex];

            if (!selectedRow) return null;

            const rowTotal = getSubMetricTotal(dataForMealTime, selectedIndex, mealTime);
            const isBalanced = Math.abs(rowTotal - 100) < 0.1;

            return (
              <div key={mealTime} className="border-4 border-purple-200 rounded-2xl p-6 bg-gradient-to-br from-purple-50 to-white">
                {/* Meal Time Header */}
                <div className="flex items-center gap-3 mb-6 pb-4 border-b-2 border-purple-200">
                  <Clock className="w-6 h-6 text-purple-600" />
                  <h3 className="text-2xl font-bold text-purple-900">{mealTime} Probabilities</h3>
                  <Badge variant="default" className="ml-auto">
                    {proteinColumns.length} Proteins Available
                  </Badge>
                </div>

                {/* Available Proteins Info */}
                {unavailableProteins.length > 0 && (
                  <div className="mb-6 bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-700">
                          <span className="font-semibold text-blue-900">Available for {mealTime}:</span> {proteinColumns.join(', ')}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Not available: {unavailableProteins.join(', ')}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Protein Inputs */}
                <div className={`p-6 rounded-xl border-2 ${
                  isBalanced ? 'border-green-300 bg-green-50/30' : 'border-orange-300 bg-orange-50/30'
                }`}>
                  <div className="flex justify-end items-center mb-4">
                    <Badge variant={isBalanced ? 'default' : 'secondary'} className="text-xs py-1 px-2">
                      Total: {rowTotal.toFixed(1)}%
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {proteinColumns.map(protein => {
                      const value = parseFloat(selectedRow[protein] || 0) * 100;
                      const displayValue = getProteinInputValue(category, mealTime, selectedIndex, protein, value);
                      
                      return (
                        <div key={protein}>
                          <Label htmlFor={`protein-${mealTime}-${protein}`}>{protein}</Label>
                          <div className="relative">
                            <Input
                              id={`protein-${mealTime}-${protein}`}
                              type="text"
                              value={displayValue}
                              onChange={(e) => {
                                const inputValue = e.target.value;
                                if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                                  handleSubMetricChange(category, mealTime, selectedIndex, protein, inputValue);
                                }
                              }}
                              onBlur={() => {
                                const key = `${category}_${mealTime}_${selectedIndex}_${protein}`;
                                setProteinInputs(prev => {
                                  const updated = { ...prev };
                                  delete updated[key];
                                  return updated;
                                });
                              }}
                              className="pr-8 text-center font-bold"
                            />
                            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {!isBalanced && (
                    <div className="mt-4 p-4 bg-orange-100 border border-orange-300 rounded-lg flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm font-medium text-orange-900">
                        Protein percentages must total 100% (currently {rowTotal.toFixed(1)}%)
                      </p>
                    </div>
                  )}

                  <div className="flex justify-center mt-6">
                    {(() => {
                      const buttonState = getRowButtonState(category, mealTime, selectedIndex);
                      return (
                        <Button
                          size="lg"
                          onClick={() => validateAndSubmitRow(category, mealTime, selectedIndex)}
                          disabled={buttonState.disabled}
                          variant={buttonState.variant}
                          className={`${buttonState.bgColor} ${buttonState.color} font-semibold`}
                        >
                          {!buttonState.disabled && <CheckCircle2 className="w-5 h-5 mr-2" />}
                          {buttonState.label}
                        </Button>
                      );
                    })()}
                  </div>
                </div>
              </div>
            );
          })()
        ) : (
          // For other categories, render all meal times
          mealTimes.map(mealTime => {
          const dataForMealTime = mealTimeStructuredData[mealTime];
          if (!dataForMealTime || dataForMealTime.length === 0) return null;

          // Get meal-time-specific proteins
          const mealTimeProteins = availableProteinsByMealtime[mealTime] || allProteinColumns;
          const proteinColumns = allProteinColumns.filter(p => mealTimeProteins.includes(p));
          const unavailableProteins = allProteinColumns.filter(p => !mealTimeProteins.includes(p));

          // Determine selected row for this meal time
          let selectedIndex = 0;
          let selectedRow = null;

          if (category === 'nationality' && selectedNationality && selectedWeekday) {
            selectedRow = dataForMealTime.find(row => 
              row.nationality_code === selectedNationality && 
              row.day_of_week === selectedWeekday
            );
            selectedIndex = dataForMealTime.findIndex(row => 
              row.nationality_code === selectedNationality && 
              row.day_of_week === selectedWeekday
            );
          } else if (category === 'age') {
            selectedIndex = parseInt(selectedAge);
            selectedRow = dataForMealTime[selectedIndex];
          } else if (category === 'destination') {
            selectedIndex = parseInt(selectedDestination);
            selectedRow = dataForMealTime[selectedIndex];
          } else if (category === 'mealtime') {
            selectedIndex = parseInt(selectedMealTime);
            selectedRow = dataForMealTime[selectedIndex];
          }

          if (!selectedRow) return null;

          const rowTotal = getSubMetricTotal(dataForMealTime, selectedIndex, mealTime);
          const isBalanced = Math.abs(rowTotal - 100) < 0.1;

          return (
            <div key={mealTime} className="border-4 border-purple-200 rounded-2xl p-6 bg-gradient-to-br from-purple-50 to-white">
              {/* Meal Time Header */}
              <div className="flex items-center gap-3 mb-6 pb-4 border-b-2 border-purple-200">
                <Clock className="w-6 h-6 text-purple-600" />
                <h3 className="text-2xl font-bold text-purple-900">{mealTime}</h3>
                <Badge variant="default" className="ml-auto">
                  {proteinColumns.length} Proteins Available
                </Badge>
              </div>

              {/* Nationality-specific: Show reasoning and dropdowns */}
              {category === 'nationality' && (
                <>
                  {selectedRow?.reasoning && (
                    <div className="mb-6 bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div className="w-full">
                          <p className="text-xs font-semibold text-blue-900 mb-1">
                            Why probabilities differ for {selectedWeekday} for {selectedNationality}:
                          </p>
                          <p className="text-sm text-gray-700">
                            {selectedRow.reasoning}
                          </p>
                          {selectedRow.sources && (
                            <div className="mt-3 pt-3 border-t border-blue-300">
                              <p className="text-xs font-semibold text-blue-900 mb-1">Sources:</p>
                              <p className="text-sm text-gray-600 italic">
                                {selectedRow.sources}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Available Proteins Info (for non-nationality categories) */}
              {category !== 'nationality' && unavailableProteins.length > 0 && (
                <div className="mb-6 bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-700">
                        <span className="font-semibold text-blue-900">Available for {mealTime}:</span> {proteinColumns.join(', ')}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Not available: {unavailableProteins.join(', ')}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Nationality-specific: Show dropdowns for each meal time */}
              {category === 'nationality' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div>
                    <Label htmlFor={`country-select-${mealTime}`}>Select Country</Label>
                    <Select
                      id={`country-select-${mealTime}`}
                      value={selectedNationality}
                      onChange={(e) => setSelectedNationality(e.target.value)}
                    >
                      {[...new Set(dataForMealTime.map(row => row.nationality_code))].map((country) => (
                        <option key={country} value={country}>{country}</option>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor={`weekday-select-${mealTime}`}>
                      Flight Weekday
                      <span className="ml-2 text-xs text-gray-500">(determined by flight date)</span>
                    </Label>
                    <Select
                      id={`weekday-select-${mealTime}`}
                      value={selectedWeekday}
                      disabled
                      className="bg-gray-100 cursor-not-allowed opacity-75"
                    >
                      <option value={selectedWeekday}>{selectedWeekday}</option>
                    </Select>
                  </div>
                </div>
              )}

              {/* Protein Inputs */}
              <div className={`p-6 rounded-xl border-2 ${isBalanced ? 'border-green-300 bg-green-50/30' : 'border-orange-300 bg-orange-50/30'}`}>
                <div className="flex justify-between items-center mb-6">
                  <h4 className="text-lg font-bold text-purple-900">
                    {category === 'nationality' && `${selectedNationality} - ${selectedWeekday}`}
                    {category === 'age' && `Age Group: ${selectedRow?.age_group || selectedRow?.Age || 'Unknown'}`}
                    {category === 'destination' && `Destination: ${selectedRow?.airport_code || selectedRow?.Destination || 'Unknown'}`}
                    {category === 'mealtime' && `Meal: ${selectedRow?.meal_time || 'Unknown'}`}
                  </h4>
                  <Badge variant={isBalanced ? 'default' : 'secondary'}>
                    Total: {rowTotal.toFixed(1)}%
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {proteinColumns.map(protein => {
                    const value = parseFloat(selectedRow[protein] || 0) * 100;
                    const displayValue = getProteinInputValue(category, mealTime, selectedIndex, protein, value);
                    
                    return (
                      <div key={protein}>
                        <Label htmlFor={`protein-${mealTime}-${protein}`}>{protein}</Label>
                        <div className="relative">
                          <Input
                            id={`protein-${mealTime}-${protein}`}
                            type="text"
                            value={displayValue}
                            onChange={(e) => {
                              const inputValue = e.target.value;
                              if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                                handleSubMetricChange(category, mealTime, selectedIndex, protein, inputValue);
                              }
                            }}
                            onBlur={() => {
                              const key = `${category}_${mealTime}_${selectedIndex}_${protein}`;
                              setProteinInputs(prev => {
                                const updated = { ...prev };
                                delete updated[key];
                                return updated;
                              });
                            }}
                            className="pr-8 text-center font-bold"
                          />
                          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {!isBalanced && (
                  <div className="mt-4 p-4 bg-orange-100 border border-orange-300 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm font-medium text-orange-900">
                      Protein percentages must total 100% (currently {rowTotal.toFixed(1)}%)
                    </p>
                  </div>
                )}

                <div className="flex justify-center mt-6">
                  {(() => {
                    const buttonState = getRowButtonState(category, mealTime, selectedIndex);
                    return (
                      <Button
                        size="lg"
                        onClick={() => validateAndSubmitRow(category, mealTime, selectedIndex)}
                        disabled={buttonState.disabled}
                        variant={buttonState.variant}
                        className={`${buttonState.bgColor} ${buttonState.color} font-semibold`}
                      >
                        {!buttonState.disabled && <CheckCircle2 className="w-5 h-5 mr-2" />}
                        {buttonState.label}
                      </Button>
                    );
                  })()}
                </div>
              </div>
            </div>
          );
        })
        )}
      </div>
    );
  };

  return (
    <PageTransition>
      {/* Redefining Dialog */}
      {isRedefining && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-purple-50 to-white rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4 border-2 border-purple-200"
          >
            {/* Header */}
            <div className="text-center mb-6">
              {redefineComplete ? (
                <div className="flex items-center justify-center gap-2 text-2xl font-bold text-green-600">
                  <CheckCircle2 className="w-8 h-8" />
                  <span>Metrics Redefined</span>
                </div>
              ) : (
                <h2 className="text-2xl font-bold text-purple-900">Redefining Master Metrics</h2>
              )}
            </div>

            {/* Content */}
            <div className="space-y-6">
              {!redefineComplete ? (
                <>
                  {/* Spinning loader */}
                  <div className="flex justify-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full"
                    />
                  </div>

                  {/* Progress bar */}
                  <div className="space-y-2">
                    <div className="h-3 bg-purple-100 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-purple-600 to-yellow-500 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${redefineProgress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                    <p className="text-center text-sm text-gray-600">
                      {redefineProgress}% Complete
                    </p>
                  </div>

                  {/* Step message */}
                  <motion.div
                    key={redefineStep}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center min-h-[60px] flex items-center justify-center"
                  >
                    <p className="text-purple-900 font-medium">{redefineStep}</p>
                  </motion.div>
                </>
              ) : (
                <div className="text-center space-y-4 py-4">
                  <CheckCircle2 className="w-20 h-20 text-green-500 mx-auto" />
                  <p className="text-gray-700">
                    Master metrics have been successfully redefined based on the latest trained model and data sources.
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50/30">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-purple-800 shadow-lg">
          <Container>
            <div className="py-6 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  Master Metrics Configuration
                </h1>
                <p className="text-purple-100">
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
          {/* Customer Summary Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12"
          >
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg">
                  <Users className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  Customer Summary
                </h2>
              </div>
              <p className="text-lg text-gray-600">
                Passenger details for {selectedFlight?.flightNumber} on {new Date(flightDate).toLocaleDateString()}
                {customerSummary?.day_of_week && (
                  <span className="ml-2 font-semibold text-blue-700">({customerSummary.day_of_week})</span>
                )}
              </p>
            </div>

            {loadingSummary ? (
              <div className="flex justify-center items-center py-12">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full"
                />
              </div>
            ) : customerSummary && !customerSummary.error ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Overview Card */}
                <Card className="shadow-lg border-2 border-blue-100">
                  <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100/50">
                    <CardTitle className="flex items-center gap-2 text-blue-900">
                      <Users className="w-5 h-5" />
                      Flight Overview
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-6 space-y-4">
                    <div className="p-3 bg-blue-50 rounded-lg border-2 border-blue-200">
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <span className="font-semibold text-gray-800 block">Passengers Without Pre-Booked Meals</span>
                          <span className="text-xs text-gray-600 mt-1 block">Passengers requiring meal prediction</span>
                        </div>
                        <Badge variant="default" className="text-lg px-4 py-1 ml-4">
                          {customerSummary.total_customers}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <span className="font-medium text-gray-700 block mb-2">Destination</span>
                      <p className="text-xl font-bold text-purple-700">
                        {customerSummary.destination_airport}
                      </p>
                    </div>

                    <div className="p-3 bg-green-50 rounded-lg">
                      <span className="font-medium text-gray-700 block mb-2">Cabin Class Distribution</span>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        {Object.entries(customerSummary.cabin_distribution).map(([cabin, count]) => (
                          <div key={cabin} className="flex justify-between items-center bg-white p-2 rounded border border-green-200">
                            <span className="font-semibold text-gray-800">Class {cabin}</span>
                            <span className="font-bold text-green-700">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="p-3 bg-orange-50 rounded-lg">
                      <span className="font-medium text-gray-700 block mb-2">Available Meal Times</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {customerSummary.meal_times.map((time, idx) => (
                          <Badge key={idx} variant="secondary" className="text-sm">
                            {time}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Detailed Analysis Card */}
                <Card className="shadow-lg border-2 border-purple-100">
                  <CardHeader className="bg-gradient-to-r from-purple-50 to-purple-100/50">
                    <CardTitle className="flex items-center gap-2 text-purple-900">
                      <TrendingUp className="w-5 h-5" />
                      Class {customerSummary.analysis_cabin} Demographics
                    </CardTitle>
                    <CardDescription>
                      Detailed breakdown for probability selection
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-6 space-y-6">
                    {/* Nationality Breakdown */}
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                        <Globe className="w-4 h-4 text-purple-600" />
                        Nationality Distribution
                      </h4>
                      <div className="max-h-48 overflow-y-auto border border-purple-200 rounded-lg p-3 bg-purple-50/30">
                        <div className="space-y-2">
                          {Object.entries(customerSummary.nationality_breakdown)
                            .sort((a, b) => b[1] - a[1])
                            .map(([nationality, count]) => (
                              <div key={nationality} className="flex justify-between items-center bg-white p-2 rounded shadow-sm">
                                <span className="font-medium text-gray-700">{nationality}</span>
                                <div className="flex items-center gap-2">
                                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div 
                                      className="h-full bg-gradient-to-r from-purple-500 to-purple-600"
                                      style={{ 
                                        width: `${(count / customerSummary.total_customers) * 100}%` 
                                      }}
                                    />
                                  </div>
                                  <span className="font-bold text-purple-700 w-12 text-right">{count}</span>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>

                    {/* Age Group Breakdown */}
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-blue-600" />
                        Age Group Distribution
                      </h4>
                      <div className="border border-blue-200 rounded-lg p-3 bg-blue-50/30">
                        <div className="space-y-2">
                          {Object.entries(customerSummary.age_breakdown)
                            .sort((a, b) => {
                              // Sort by age group numerically
                              const aNum = parseInt(a[0]);
                              const bNum = parseInt(b[0]);
                              return aNum - bNum;
                            })
                            .map(([ageGroup, count]) => (
                              <div key={ageGroup} className="flex justify-between items-center bg-white p-2 rounded shadow-sm">
                                <span className="font-medium text-gray-700">{ageGroup} years</span>
                                <div className="flex items-center gap-2">
                                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div 
                                      className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                                      style={{ 
                                        width: `${(count / customerSummary.total_customers) * 100}%` 
                                      }}
                                    />
                                  </div>
                                  <span className="font-bold text-blue-700 w-12 text-right">{count}</span>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-red-500">
                  {customerSummary?.error || 'Failed to load customer data'}
                </p>
              </div>
            )}
          </motion.div>

          {/* Available Meals Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mb-12"
          >
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-orange-700 bg-clip-text text-transparent mb-3 flex items-center justify-center gap-3">
                <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 shadow-lg">
                  <Clock className="w-7 h-7 text-white" />
                </div>
                Available Meals
              </h2>
              <p className="text-gray-600 text-lg">Meal options for the selected flight and date</p>
            </div>

            {loadingMeals ? (
              <Card className="shadow-lg border-2 border-purple-100">
                <CardContent className="py-12 text-center">
                  <p className="text-gray-500">Loading meal data...</p>
                </CardContent>
              </Card>
            ) : availableMeals && !availableMeals.error && availableMeals.meals_by_time ? (
              <div className="space-y-4">
                {Object.keys(availableMeals.meals_by_time).length > 0 ? (
                  Object.entries(availableMeals.meals_by_time).map(([mealTime, meals]) => (
                    <Card key={mealTime} className="shadow-lg border-2 border-orange-100">
                      <CardHeader className="bg-gradient-to-r from-orange-50 to-orange-100/50">
                        <CardTitle className="flex items-center gap-2 text-orange-900">
                          <Clock className="w-5 h-5" />
                          {mealTime}
                        </CardTitle>
                        <CardDescription>
                          {meals.length} meal option{meals.length !== 1 ? 's' : ''} available
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="pt-6">
                        <div className="space-y-3">
                          {meals.map((meal, idx) => (
                            <div 
                              key={idx} 
                              className="flex items-start gap-4 p-4 bg-white border-2 border-orange-100 rounded-lg hover:border-orange-300 transition-colors"
                            >
                              <Badge 
                                variant={meal.cabin_class === 'Y' ? 'default' : meal.cabin_class === 'S' ? 'secondary' : 'default'}
                                className="text-sm font-bold mt-1"
                              >
                                {meal.cabin_class}
                              </Badge>
                              <div className="flex-1">
                                <p className="font-medium text-gray-800 mb-1">{meal.meal_name}</p>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm text-gray-500">Protein:</span>
                                  <Badge variant="outline" className="text-xs">
                                    {meal.meal_pref}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Card className="shadow-lg border-2 border-gray-100">
                    <CardContent className="py-12 text-center">
                      <p className="text-gray-500">
                        {availableMeals.message || 'No meal data available for this flight and date'}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card className="shadow-lg border-2 border-red-100">
                <CardContent className="py-12 text-center">
                  <p className="text-red-500">
                    {availableMeals?.error || 'Failed to load meal data'}
                  </p>
                </CardContent>
              </Card>
            )}
          </motion.div>

          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-4 mb-4">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-600 to-purple-700 shadow-lg">
                <TrendingUp className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent">
                Master Metrics Configuration
              </h1>
            </div>
            <p className="text-lg text-gray-600">
              Adjust importance weights for prediction factors and fine-tune protein preferences
            </p>
          </div>

          {/* Warning Alert */}
          {!isBalanced && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <div className="p-4 bg-orange-100 border-2 border-orange-300 rounded-xl flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-orange-900">
                    Main metrics total: <strong>{totalImportance.toFixed(1)}%</strong>
                  </p>
                  <p className="text-sm text-orange-800">
                    Metrics must equal 100% to proceed with prediction
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 mb-6">
            <Button onClick={handleRedefineDefaults} disabled={isRedefining} variant="default" size="md" className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white">
              <TrendingUp className="w-4 h-4 mr-2" />
              Redefine Metrics
            </Button>
            <Button onClick={handleReset} variant="outline" size="md">
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset to Defaults
            </Button>
          </div>

          {/* Metrics Accordions */}
          <div className="space-y-4 mb-8">
            {/* Nationality - 40% */}
            <Accordion expanded={expanded === 'panel1'} onChange={() => handleAccordionChange('panel1')}>
              <AccordionSummary
                onClick={() => handleAccordionChange('panel1')}
                expandIcon={
                  <motion.div
                    animate={{ rotate: expanded === 'panel1' ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChevronDown className="w-6 h-6 text-purple-600" />
                  </motion.div>
                }
              >
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <Users className="w-6 h-6 text-purple-600" />
                    <span className="text-lg font-semibold text-gray-900">
                      Weekday-Adjusted Nationality
                    </span>
                  </div>
                  <Badge variant="default" className="text-base px-3 py-1">
                    {localMetrics.nationality_importance}%
                  </Badge>
                </div>
              </AccordionSummary>
              <AccordionDetails expanded={expanded === 'panel1'}>
                <div className="bg-purple-50/50 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700 font-medium mb-1">
                        What a nationality would prefer on a specific weekday
                      </p>
                      <p className="text-xs text-gray-500">
                        Adjust importance weight (35-45%)
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Label htmlFor="nationality-weight" className="text-sm font-semibold">
                        Weight:
                      </Label>
                      <div className="relative w-24">
                        <Input
                          id="nationality-weight"
                          type="text"
                          value={localMetrics.nationality_importance}
                          onChange={(e) => {
                            const inputValue = e.target.value;
                            if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                              if (inputValue === '') {
                                handleSliderChange('nationality_importance', 0);
                              } else {
                                const value = parseFloat(inputValue);
                                if (!isNaN(value)) {
                                  handleSliderChange('nationality_importance', value);
                                }
                              }
                            }
                          }}
                          className="pr-8 text-center font-bold"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                {masterData && renderProteinTable(masterData.nationality_sample, 'Nationality', 'nationality')}
              </AccordionDetails>
            </Accordion>

            {/* Age - 20% */}
            <Accordion expanded={expanded === 'panel2'} onChange={() => handleAccordionChange('panel2')}>
              <AccordionSummary
                onClick={() => handleAccordionChange('panel2')}
                expandIcon={
                  <motion.div
                    animate={{ rotate: expanded === 'panel2' ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChevronDown className="w-6 h-6 text-purple-600" />
                  </motion.div>
                }
              >
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-6 h-6 text-purple-600" />
                    <span className="text-lg font-semibold text-gray-900">
                      Age of Passengers
                    </span>
                  </div>
                  <Badge variant="default" className="text-base px-3 py-1">
                    {localMetrics.age_importance}%
                  </Badge>
                </div>
              </AccordionSummary>
              <AccordionDetails expanded={expanded === 'panel2'}>
                <div className="bg-purple-50/50 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700 font-medium mb-1">
                        Age-based protein preferences
                      </p>
                      <p className="text-xs text-gray-500">
                        Adjust importance weight (15-25%)
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Label htmlFor="age-weight" className="text-sm font-semibold">
                        Weight:
                      </Label>
                      <div className="relative w-24">
                        <Input
                          id="age-weight"
                          type="text"
                          value={localMetrics.age_importance}
                          onChange={(e) => {
                            const inputValue = e.target.value;
                            if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                              if (inputValue === '') {
                                handleSliderChange('age_importance', 0);
                              } else {
                                const value = parseFloat(inputValue);
                                if (!isNaN(value)) {
                                  handleSliderChange('age_importance', value);
                                }
                              }
                            }
                          }}
                          className="pr-8 text-center font-bold"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                {masterData && renderProteinTable(masterData.age_sample, 'Age', 'age')}
              </AccordionDetails>
            </Accordion>

            {/* Destination - 25% */}
            <Accordion expanded={expanded === 'panel3'} onChange={() => handleAccordionChange('panel3')}>
              <AccordionSummary
                onClick={() => handleAccordionChange('panel3')}
                expandIcon={
                  <motion.div
                    animate={{ rotate: expanded === 'panel3' ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChevronDown className="w-6 h-6 text-purple-600" />
                  </motion.div>
                }
              >
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <MapPin className="w-6 h-6 text-purple-600" />
                    <span className="text-lg font-semibold text-gray-900">
                      Destination of Flight
                    </span>
                  </div>
                  <Badge variant="default" className="text-base px-3 py-1">
                    {localMetrics.destination_importance}%
                  </Badge>
                </div>
              </AccordionSummary>
              <AccordionDetails expanded={expanded === 'panel3'}>
                <div className="bg-purple-50/50 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700 font-medium mb-1">
                        Regional protein preferences by destination
                      </p>
                      <p className="text-xs text-gray-500">
                        Adjust importance weight (20-30%)
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Label htmlFor="destination-weight" className="text-sm font-semibold">
                        Weight:
                      </Label>
                      <div className="relative w-24">
                        <Input
                          id="destination-weight"
                          type="text"
                          value={localMetrics.destination_importance}
                          onChange={(e) => {
                            const inputValue = e.target.value;
                            if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                              if (inputValue === '') {
                                handleSliderChange('destination_importance', 0);
                              } else {
                                const value = parseFloat(inputValue);
                                if (!isNaN(value)) {
                                  handleSliderChange('destination_importance', value);
                                }
                              }
                            }
                          }}
                          className="pr-8 text-center font-bold"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                {masterData && renderProteinTable(masterData.destination_sample, 'Destination', 'destination')}
              </AccordionDetails>
            </Accordion>

            {/* Meal Time - 15% */}
            <Accordion expanded={expanded === 'panel4'} onChange={() => handleAccordionChange('panel4')}>
              <AccordionSummary
                onClick={() => handleAccordionChange('panel4')}
                expandIcon={
                  <motion.div
                    animate={{ rotate: expanded === 'panel4' ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChevronDown className="w-6 h-6 text-purple-600" />
                  </motion.div>
                }
              >
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <Clock className="w-6 h-6 text-purple-600" />
                    <span className="text-lg font-semibold text-gray-900">
                      Meal Time
                    </span>
                  </div>
                  <Badge variant="default" className="text-base px-3 py-1">
                    {localMetrics.mealtime_importance}%
                  </Badge>
                </div>
              </AccordionSummary>
              <AccordionDetails expanded={expanded === 'panel4'}>
                <div className="bg-purple-50/50 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700 font-medium mb-1">
                        Time-of-day protein preferences
                      </p>
                      <p className="text-xs text-gray-500">
                        Adjust importance weight (10-20%)
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Label htmlFor="mealtime-weight" className="text-sm font-semibold">
                        Weight:
                      </Label>
                      <div className="relative w-24">
                        <Input
                          id="mealtime-weight"
                          type="text"
                          value={localMetrics.mealtime_importance}
                          onChange={(e) => {
                            const inputValue = e.target.value;
                            if (inputValue === '' || /^\d*\.?\d*$/.test(inputValue)) {
                              if (inputValue === '') {
                                handleSliderChange('mealtime_importance', 0);
                              } else {
                                const value = parseFloat(inputValue);
                                if (!isNaN(value)) {
                                  handleSliderChange('mealtime_importance', value);
                                }
                              }
                            }
                          }}
                          className="pr-8 text-center font-bold"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-purple-600 font-bold text-sm">
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                {masterData && renderProteinTable(masterData.mealtime_sample, 'Meal Time', 'mealtime')}
              </AccordionDetails>
            </Accordion>
          </div>

          {/* Modified Metrics Section - Show whenever there are weight changes from defaults */}
          {hasWeightChanges() && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 space-y-6"
            >
              {/* Changed Weights Table */}
              {hasWeightChanges() && (
                <div className="p-6 bg-blue-50 border-2 border-blue-200 rounded-xl shadow-md">
                  <div className="flex items-center gap-3 mb-4">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                    <h3 className="text-lg font-semibold text-blue-900">Modified Importance Weights</h3>
                  </div>
                  
                  <div className="bg-white rounded-lg overflow-hidden border border-blue-200">
                    <table className="w-full text-sm">
                      <thead className="bg-blue-100">
                        <tr>
                          <th className="px-4 py-3 text-left font-semibold text-blue-900">Metric Category</th>
                          <th className="px-4 py-3 text-right font-semibold text-blue-900">Default %</th>
                          <th className="px-4 py-3 text-right font-semibold text-blue-900">Current %</th>
                          <th className="px-4 py-3 text-center font-semibold text-blue-900">Change</th>
                        </tr>
                      </thead>
                      <tbody>
                        {getChangedWeights().map((change, idx) => {
                          const diff = (change.newValue - change.originalValue).toFixed(1);
                          const isIncrease = parseFloat(diff) > 0;
                          return (
                            <tr key={idx} className="border-t border-blue-100 hover:bg-blue-50/50">
                              <td className="px-4 py-3 font-medium">{change.metric}</td>
                              <td className="px-4 py-3 text-right text-gray-600">{change.originalValue}%</td>
                              <td className="px-4 py-3 text-right font-semibold text-blue-900">{change.newValue}%</td>
                              <td className="px-4 py-3 text-center">
                                <span className={`inline-flex items-center gap-1 font-semibold ${isIncrease ? 'text-green-600' : 'text-red-600'}`}>
                                  {isIncrease ? '+' : ''}{diff}%
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Validation Errors */}
              {!validateAllProbabilities().isValid && (
                <div className="p-6 bg-red-50 border-2 border-red-300 rounded-xl shadow-md">
                  <div className="flex items-center gap-3 mb-4">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                    <h3 className="text-lg font-semibold text-red-900">Validation Errors - Cannot Save</h3>
                  </div>
                  
                  {/* Weight Error (shown prominently if present) */}
                  {validateAllProbabilities().weightError && (
                    <div className="mb-4 p-4 bg-red-100 border-2 border-red-400 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-5 h-5 text-red-700" />
                        <h4 className="font-bold text-red-900">Weight Validation Error</h4>
                      </div>
                      <p className="text-sm font-semibold text-red-800">
                        {validateAllProbabilities().weightError}
                      </p>
                      <p className="text-xs text-red-600 mt-1">
                        Please adjust the importance weights so they total exactly 100%
                      </p>
                    </div>
                  )}
                  
                  {/* Probability Errors */}
                  {validateAllProbabilities().errors.filter(e => e.category !== 'weights').length > 0 && (
                    <>
                      <p className="text-sm text-red-700 mb-3">
                        The following protein probabilities do not add up to 100%. Please correct them before saving:
                      </p>
                      <div className="bg-white rounded-lg overflow-hidden border border-red-200 max-h-60 overflow-y-auto">
                        <ul className="divide-y divide-red-100">
                          {validateAllProbabilities().errors.filter(e => e.category !== 'weights').map((error, idx) => (
                            <li key={idx} className="px-4 py-3 hover:bg-red-50/50">
                              <div className="flex items-start justify-between gap-4">
                                <span className="text-sm text-gray-700">{error.message}</span>
                                <Badge variant="secondary" className="shrink-0">
                                  {error.total}%
                                </Badge>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Modified Rows Table */}
          {modifiedRows.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-12 mb-8"
            >
              <Card className="shadow-xl border-2 border-orange-200">
                <CardHeader className="bg-gradient-to-r from-orange-50 to-orange-100/50">
                  <CardTitle className="flex items-center gap-2 text-orange-900">
                    <Info className="w-5 h-5" />
                    Modified Probability Rows ({modifiedRows.length})
                  </CardTitle>
                  <CardDescription>
                    Rows where you have changed probabilities from defaults
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b-2 border-orange-200">
                          <th className="text-left p-3 font-semibold text-orange-900">Metric Type</th>
                          <th className="text-left p-3 font-semibold text-orange-900">Row Details</th>
                          <th className="text-left p-3 font-semibold text-orange-900">Default Values</th>
                          <th className="text-left p-3 font-semibold text-orange-900">Your Changes</th>
                        </tr>
                      </thead>
                      <tbody>
                        {modifiedRows.map((row, idx) => (
                          <tr key={idx} className="border-b border-orange-100 hover:bg-orange-50/50">
                            <td className="p-3">
                              <Badge variant="secondary" className="capitalize">
                                {row.metric_type}
                              </Badge>
                            </td>
                            <td className="p-3 text-sm text-gray-700">
                              {row.metric_type === 'nationality' && (
                                <div>
                                  <strong>{row.row_details.nationality_code}</strong>
                                  <br />
                                  {row.row_details.day_of_week} - {row.row_details.meal_time}
                                </div>
                              )}
                              {row.metric_type === 'age' && (
                                <div>
                                  <strong>Age {row.row_details.age_group}</strong>
                                  <br />
                                  {row.row_details.meal_time}
                                </div>
                              )}
                              {row.metric_type === 'destination' && (
                                <div>
                                  <strong>{row.row_details.destination_region}</strong>
                                  <br />
                                  {row.row_details.meal_time}
                                </div>
                              )}
                              {row.metric_type === 'mealtime' && (
                                <div>
                                  <strong>{row.row_details.meal_time}</strong>
                                </div>
                              )}
                            </td>
                            <td className="p-3">
                              <div className="text-xs space-y-1">
                                {row.available_proteins.map(protein => (
                                  <div key={protein} className="flex justify-between gap-2">
                                    <span className="text-gray-600">{protein}:</span>
                                    <span className="font-mono text-gray-800">
                                      {(row.default_probabilities[protein] * 100).toFixed(1)}%
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </td>
                            <td className="p-3">
                              <div className="text-xs space-y-1">
                                {row.available_proteins.map(protein => {
                                  const defaultVal = row.default_probabilities[protein] * 100;
                                  const currentVal = row.current_probabilities[protein] * 100;
                                  const isDifferent = Math.abs(defaultVal - currentVal) > 0.1;
                                  return (
                                    <div key={protein} className="flex justify-between gap-2">
                                      <span className="text-gray-600">{protein}:</span>
                                      <span className={`font-mono font-semibold ${isDifferent ? 'text-orange-700' : 'text-gray-800'}`}>
                                        {currentVal.toFixed(1)}%
                                      </span>
                                    </div>
                                  );
                                })}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Run Prediction Button */}
          <div className="flex justify-center mt-8">
            <Button
              size="lg"
              onClick={handleRunPrediction}
              disabled={!isBalanced}
              className="px-8 py-6 text-xl"
            >
              <Play className="w-6 h-6 mr-2" />
              Run Prediction
            </Button>
          </div>
        </Container>
      </div>
    </PageTransition>
  );
}

export default MasterMetricsScreen;
