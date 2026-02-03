import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, CheckCircle2, Users, TrendingUp, Lightbulb, Info, Brain, Coffee, Utensils, Moon } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card';
import Badge from './ui/Badge';
import Button from './ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

function ResultsDisplay({ results, selectedFlight, flightDate }) {
  console.log('[ResultsDisplay] Rendering with results:', results);
  
  const [aiSummaries, setAiSummaries] = useState({});
  
  // Extract data before early return
  const meal_times = results?.meal_times || {};
  const mealTimeKeys = Object.keys(meal_times);
  const flight_number = results?.flight_number;
  const flight_date = results?.flight_date;
  const passenger_details = results?.passenger_details;
  const weights_used = results?.weights_used;
  const original_counts = results?.original_counts;
  
  // Use pre-generated AI summaries from results (no need to fetch separately)
  useEffect(() => {
    if (results?.ai_summaries) {
      console.log('[AI Summary] Using pre-generated summaries from results:', results.ai_summaries);
      setAiSummaries(results.ai_summaries);
    } else {
      console.log('[AI Summary] No pre-generated summaries found in results');
    }
  }, [results]);
  
  // Early return AFTER hooks
  if (!results || !results.meal_times) {
    console.log('[ResultsDisplay] No results or meal_times, returning null');
    return null;
  }

  const { cabin_class, total_passengers, cabin_passengers_for_prediction, workflow_time } = results;
  const hasMultipleMealTimes = mealTimeKeys.length > 1;
  
  // Use cabin-specific count for display
  const displayPassengerCount = cabin_passengers_for_prediction || total_passengers;
  
  // Get meal time icon
  const getMealTimeIcon = (mealTime) => {
    const timeStr = mealTime?.toLowerCase() || '';
    if (timeStr.includes('breakfast')) return Coffee;
    if (timeStr.includes('lunch') || timeStr.includes('dinner')) return Utensils;
    if (timeStr.includes('supper')) return Moon;
    return Utensils;
  };
  
  // Get actual/original data from API, return null if not available
  const getActualData = (proteinType, predictedCount, mealTime) => {
    // Check if we have original_counts from the API for this meal time
    if (original_counts && original_counts[mealTime] && original_counts[mealTime][proteinType]) {
      return original_counts[mealTime][proteinType];
    }
    
    // Return null if not available (will show empty bar)
    return null;
  };
  
  // Check if original data is available for a meal time
  const hasOriginalData = (mealTime) => {
    return original_counts && original_counts[mealTime] && Object.keys(original_counts[mealTime]).length > 0;
  };
  
  // Generate AI analysis text
  const generateAIAnalysis = (proteins, mealTime = null) => {
    const sortedProteins = Object.entries(proteins)
      .sort((a, b) => b[1] - a[1])
      .map(([protein, count]) => ({
        protein,
        count,
        percentage: ((count / Object.values(proteins).reduce((a, b) => a + b, 0)) * 100).toFixed(1)
      }));
    
    if (sortedProteins.length === 0) {
      return 'No protein data available for analysis.';
    }
    
    const top = sortedProteins[0];
    const second = sortedProteins.length > 1 ? sortedProteins[1] : null;
    const third = sortedProteins.length > 2 ? sortedProteins[2] : null;
    
    const mealTimePrefix = mealTime ? `For ${mealTime} service, ` : '';
    
    let analysis = `${mealTimePrefix}Our AI model predicts ${top.protein} will be the most preferred option at ${top.percentage}%`;
    
    if (second) {
      analysis += `, followed by ${second.protein} (${second.percentage}%)`;
    }
    
    if (third) {
      analysis += ` and ${third.protein} (${third.percentage}%)`;
    }
    
    analysis += '. This prediction is based on passenger demographics, route characteristics, travel day patterns, and historical meal preferences for this specific flight.';
    
    return analysis;
  };
  
  // Render protein chart for a specific meal time
  const renderMealTimeSection = (mealTime, proteins, index) => {
    const MealIcon = getMealTimeIcon(mealTime);
    
    // Calculate comparison data using real data from API
    const hasData = hasOriginalData(mealTime);
    const comparisonData = Object.entries(proteins).map(([protein, predictedCount]) => {
      const actualCount = getActualData(protein, predictedCount, mealTime);
      const diff = actualCount !== null ? predictedCount - actualCount : 0;
      const diffPercent = actualCount !== null && actualCount > 0 ? Math.abs(diff / actualCount * 100).toFixed(0) : 0;
      
      return {
        protein,
        predicted: predictedCount,
        actual: actualCount,
        diff,
        diffPercent,
        isUnderOrdered: diff > 0,
        hasActualData: actualCount !== null
      };
    });
    
    // Sort by predicted count
    const sortedProteins = Object.entries(proteins)
      .sort((a, b) => b[1] - a[1])
      .map(([protein, count], idx) => ({
        protein,
        count,
        percentage: ((count / Object.values(proteins).reduce((a, b) => a + b, 0)) * 100).toFixed(2),
        rank: idx + 1
      }));
    
    const gradients = [
      'from-purple-600 to-purple-700',
      'from-yellow-500 to-yellow-600',
      'from-blue-500 to-blue-600',
      'from-green-500 to-green-600',
      'from-pink-500 to-pink-600',
      'from-orange-500 to-orange-600',
    ];
    
    const aiAnalysis = generateAIAnalysis(proteins, hasMultipleMealTimes ? mealTime : null);
    
    return (
      <motion.div
        key={mealTime}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 + (index * 0.1) }}
        className="mb-8"
      >
        {/* Meal Time Header */}
        {hasMultipleMealTimes && (
          <div className="flex items-center gap-3 mb-4">
            <MealIcon className="w-8 h-8 text-purple-600" />
            <h2 className="text-3xl font-bold text-purple-900">{mealTime}</h2>
          </div>
        )}
        
        {/* AI Analysis Card */}
        <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50 mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-blue-600" />
              <CardTitle className="text-2xl text-purple-900">
                {hasMultipleMealTimes ? `${mealTime} - AI Prediction Summary` : 'AI Prediction Summary'}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-white rounded-lg p-4 border border-blue-200">
              <h3 className="font-semibold text-lg text-purple-900 mb-3 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                Why This Prediction?
              </h3>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {aiSummaries[mealTime] || aiAnalysis}
              </p>
            </div>
          </CardContent>
        </Card>
        
        {/* Planned vs Predicted Comparison */}
        <Card className="border-2 border-purple-200 bg-gradient-to-br from-white to-purple-50 mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <TrendingUp className="w-6 h-6 text-purple-600" />
              <CardTitle className="text-2xl text-purple-900">
                Planned vs AI Recommended
              </CardTitle>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {hasData 
                ? 'Comparison with historical actual meal orders' 
                : 'AI Recommendations (Historical data not available for this flight/date/meal time)'}
            </p>
            {!hasData && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Original meal counts not available for this flight, date, and meal time combination. Showing AI predictions only.
                </p>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Side - Vertical Bar Chart */}
              <div className="flex flex-col h-full">
                <h3 className="text-lg font-semibold text-purple-900 mb-3">Meal Count Comparison</h3>
                <div className="flex-1 flex flex-col">
                  <div className="relative flex-1" style={{ minHeight: '500px' }}>
                    <div className="absolute inset-x-0 bottom-12 top-8 flex justify-around items-end">
                      {comparisonData.map((data, idx) => {
                        const maxValue = Math.max(...comparisonData.map(d => Math.max(d.predicted, d.actual)));
                        const maxHeight = 400;
                        const predictedHeightPx = (data.predicted / maxValue) * maxHeight;
                        const actualHeightPx = (data.actual / maxValue) * maxHeight;
                        
                        return (
                          <motion.div
                            key={data.protein}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 * idx }}
                            className="flex flex-col items-center flex-1 max-w-[80px]"
                          >
                            <div className="flex gap-1 w-full items-end justify-center" style={{ height: `${maxHeight}px` }}>
                              {/* Planned Bar */}
                              <div className="flex-1 flex flex-col justify-end items-center max-w-[30px]">
                                {data.hasActualData ? (
                                  <motion.div
                                    initial={{ height: 0 }}
                                    animate={{ height: `${actualHeightPx}px` }}
                                    transition={{ duration: 0.8, delay: 0.2 + (0.05 * idx), ease: "easeOut" }}
                                    className="w-full bg-gradient-to-t from-orange-500 to-orange-400 rounded-t-lg relative shadow-md"
                                    style={{ minHeight: '20px' }}
                                  >
                                    <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-sm font-bold text-orange-600">
                                      {data.actual}
                                    </span>
                                  </motion.div>
                                ) : (
                                  <div className="w-full h-5 bg-gray-200 rounded-t-lg relative border-2 border-dashed border-gray-400">
                                    <span className="absolute -top-7 left-1/2 -translate-x-1/2 text-sm font-bold text-gray-400">
                                      N/A
                                    </span>
                                  </div>
                                )}
                              </div>
                              
                              {/* AI Recommended Bar */}
                              <div className="flex-1 flex flex-col justify-end items-center max-w-[30px]">
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${predictedHeightPx}px` }}
                                  transition={{ duration: 0.8, delay: 0.3 + (0.05 * idx), ease: "easeOut" }}
                                  className="w-full bg-gradient-to-t from-green-600 to-green-500 rounded-t-lg relative shadow-md"
                                  style={{ minHeight: '20px' }}
                                >
                                  <span className="absolute -top-7 left-1/2 -translate-x-1/2 text-sm font-bold text-green-600">
                                    {data.predicted}
                                  </span>
                                </motion.div>
                              </div>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                    
                    <div className="absolute inset-x-0 border-b-2 border-gray-300" style={{ bottom: '48px' }}></div>
                    
                    <div className="absolute inset-x-0 bottom-0 flex justify-around" style={{ height: '48px' }}>
                      {comparisonData.map((data, idx) => (
                        <div key={`label-${data.protein}`} className="flex-1 max-w-[80px] text-center">
                          <div className={`
                            w-6 h-6 rounded-full flex items-center justify-center text-white font-bold text-xs mx-auto mb-0.5 shadow-sm
                            bg-gradient-to-br ${gradients[idx % gradients.length]}
                          `}>
                            {idx + 1}
                          </div>
                          <p className="text-xs font-semibold text-gray-800 truncate">{data.protein}</p>
                          <div className="flex gap-1 text-xs justify-center">
                            <span className="text-orange-600 font-medium">Planned:{data.hasActualData ? data.actual : 'N/A'}</span>
                            <span className="text-green-600 font-medium">Rec:{data.predicted}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-4 mt-3 pt-3 border-t border-purple-200">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-gradient-to-r from-orange-400 to-orange-500" />
                      <span className="text-xs font-medium text-gray-700">Planned</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-gradient-to-r from-green-500 to-green-600" />
                      <span className="text-xs font-medium text-gray-700">Recommended</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Side - Accuracy Cards */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-purple-900 mb-4">Ordering Analysis</h3>
                <div className="grid grid-cols-2 gap-4">
                  {comparisonData.map((data, idx) => (
                    <motion.div
                      key={data.protein}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.1 * idx, type: "spring" }}
                      className={`bg-white rounded-xl p-4 shadow-sm border-2 hover:shadow-md transition-all ${
                        !data.hasActualData ? 'border-gray-200 bg-gray-50/30' :
                        data.isUnderOrdered ? 'border-green-200 bg-green-50/30' : 'border-orange-200 bg-orange-50/30'
                      }`}
                    >
                      <div className="flex flex-col items-center">
                        {data.hasActualData ? (
                          <>
                            <div className="w-full mb-3">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs text-orange-600 font-medium">Planned: {data.actual}</span>
                                <span className="text-xs text-green-600 font-medium">Recommended: {data.predicted}</span>
                              </div>
                          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${(data.actual / Math.max(data.predicted, data.actual)) * 100}%` }}
                              transition={{ duration: 0.8, delay: 0.2 + (0.05 * idx) }}
                              className="absolute left-0 h-full bg-orange-500 rounded-full"
                            />
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${(data.predicted / Math.max(data.predicted, data.actual)) * 100}%` }}
                              transition={{ duration: 0.8, delay: 0.3 + (0.05 * idx) }}
                              className="absolute right-0 h-full bg-green-500 rounded-full"
                            />
                          </div>
                        </div>
                        
                        <div className={`w-full px-3 py-2 rounded-lg mb-2 ${
                          data.isUnderOrdered ? 'bg-green-100 border border-green-300' : 'bg-orange-100 border border-orange-300'
                        }`}>
                          <div className="flex items-center justify-center gap-2">
                            {data.isUnderOrdered ? (
                              <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                              </svg>
                            )}
                            <span className={`text-sm font-bold ${data.isUnderOrdered ? 'text-green-700' : 'text-orange-700'}`}>
                              {data.isUnderOrdered ? 'AI Optimized +' : 'AI Reduced -'}
                            </span>
                          </div>
                          <p className={`text-center text-xl font-bold mt-1 ${data.isUnderOrdered ? 'text-green-600' : 'text-orange-600'}`}>
                            {data.diffPercent}%
                          </p>
                        </div>
                        
                            <div className="text-center">
                              <p className="text-base font-semibold text-gray-800">{data.protein}</p>
                              <p className="text-xs text-gray-600 mt-1">
                                {data.isUnderOrdered ? 'Increased from planned' : 'Decreased from planned'}
                              </p>
                            </div>
                          </>
                        ) : (
                          <div className="w-full text-center py-4">
                            <div className="text-gray-400 mb-2">
                              <Info className="w-8 h-8 mx-auto" />
                            </div>
                            <p className="text-base font-semibold text-gray-800 mb-1">{data.protein}</p>
                            <p className="text-sm text-gray-500">Recommended: {data.predicted}</p>
                            <p className="text-xs text-gray-400 mt-2">No historical data</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Results Table */}
        <Card className="border-2 border-purple-200">
          <CardHeader>
            <CardTitle className="text-2xl text-purple-900">
              {hasMultipleMealTimes ? `${mealTime} - Detailed Breakdown` : 'Detailed Meal Breakdown'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-purple-900 font-bold">Rank</TableHead>
                    <TableHead className="text-purple-900 font-bold">Protein Type</TableHead>
                    <TableHead className="text-center text-purple-900 font-bold">Planned</TableHead>
                    <TableHead className="text-center text-purple-900 font-bold">Proportion</TableHead>
                    <TableHead className="text-center text-purple-900 font-bold">Recommended</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedProteins.map((row, idx) => {
                    const compData = comparisonData.find(d => d.protein === row.protein);
                    return (
                      <TableRow key={row.protein} className="hover:bg-purple-50/50">
                        <TableCell>
                          <div className={`
                            inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-white shadow-sm
                            bg-gradient-to-br ${gradients[idx % gradients.length]}
                          `}>
                            {row.rank}
                          </div>
                        </TableCell>
                        <TableCell className={`${idx === 0 ? 'font-bold text-lg' : 'text-base'} text-gray-900`}>
                          {row.protein}
                        </TableCell>
                        <TableCell className="text-center">
                          {compData?.hasActualData ? (
                            <Badge className="bg-orange-100 text-orange-700 border border-orange-300 text-base px-3 py-1">
                              {compData.actual}
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-100 text-gray-500 border border-gray-300 text-base px-3 py-1">
                              N/A
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge 
                            variant={idx === 0 ? 'default' : 'secondary'}
                            className={`
                              text-base px-4 py-1
                              ${idx === 0 ? 'bg-purple-100 text-purple-900 border-2 border-purple-600' : 'bg-yellow-100 text-yellow-800 border border-yellow-300'}
                            `}
                          >
                            {row.percentage}%
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge className="bg-green-100 text-green-700 border border-green-300 text-base px-3 py-1">
                            {row.count}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>

            {/* Visual Distribution Bar */}
            <div className="mt-8">
              <h3 className="text-xl font-semibold text-purple-900 mb-4">Visual Distribution</h3>
              <div className="flex h-16 rounded-lg overflow-hidden border-2 border-purple-300 shadow-md">
                {sortedProteins.map((row, idx) => (
                  <div
                    key={row.protein}
                    style={{ width: `${row.percentage}%` }}
                    className={`
                      bg-gradient-to-br ${gradients[idx % gradients.length]}
                      flex items-center justify-center relative
                      transition-all duration-300 hover:scale-y-110 cursor-pointer
                    `}
                    title={`${row.protein}: ${row.percentage}%`}
                  >
                    {parseFloat(row.percentage) > 5 && (
                      <span className="text-white font-bold text-sm drop-shadow-md">
                        {parseFloat(row.percentage).toFixed(1)}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="flex flex-wrap gap-4 mt-4">
                {sortedProteins.map((row, idx) => (
                  <div key={row.protein} className="flex items-center gap-2">
                    <div className={`w-4 h-4 rounded bg-gradient-to-br ${gradients[idx % gradients.length]}`} />
                    <span className="text-sm text-gray-700 font-medium">{row.protein}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };
  
  const handleExport = () => {
    let csvContent = 'Meal Time,Protein Type,Count,Percentage\n';
    
    Object.entries(meal_times).forEach(([mealTime, proteins]) => {
      const total = Object.values(proteins).reduce((a, b) => a + b, 0);
      Object.entries(proteins).forEach(([protein, count]) => {
        const percentage = ((count / total) * 100).toFixed(2);
        csvContent += `${mealTime},${protein},${count},${percentage}\n`;
      });
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `meal_predictions_${flight_number}_${flight_date}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Success Header */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-8"
      >
        <div className="flex justify-center mb-4">
          <CheckCircle2 className="w-20 h-20 text-purple-600" />
        </div>
        <h2 className="text-4xl font-bold text-purple-900 mb-3">
          Prediction Complete
        </h2>
        <p className="text-xl text-gray-600">
          AI meal predictions for {cabin_class} Class passengers
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Flight {flight_number} • {flight_date}
        </p>
        {workflow_time && (
          <p className="text-sm text-gray-500 mt-2">
            Processing time: {workflow_time.toFixed(1)}s
          </p>
        )}
      </motion.div>

      {/* Flight Info Card */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-8"
      >
        <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50">
          <CardContent className="py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600 mb-1">Cabin Class</div>
                <div className="text-3xl font-bold text-purple-900">{cabin_class} Class</div>
                <div className="text-xs text-gray-500 mt-1">Passenger cabin</div>
              </div>
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600 mb-1">{cabin_class} Class Passengers</div>
                <div className="text-3xl font-bold text-orange-600 flex items-center justify-center gap-2">
                  <Users className="w-8 h-8" />
                  {displayPassengerCount}
                </div>
                <div className="text-xs text-gray-500 mt-1">Prediction for this cabin only</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Export Button */}
      <div className="flex justify-end mb-6">
        <Button onClick={handleExport} size="md" className="bg-purple-600 hover:bg-purple-700">
          <Download className="w-4 h-4 mr-2" />
          Export Results
        </Button>
      </div>

      {/* Render each meal time section */}
      {mealTimeKeys.map((mealTime, index) => 
        renderMealTimeSection(mealTime, meal_times[mealTime], index)
      )}
    </div>
  );
}

export default ResultsDisplay;
