/**
 * Modern Flight Selection Screen
 * Redesigned with new component library and purple theme
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plane, Calendar, ArrowRight, Globe } from 'lucide-react';
import axios from 'axios';
import { Header, Container, PageTransition } from '../components/layout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, Button, Label, Select, Input } from '../components/ui';
import { API_BASE_URL } from '../config';

function FlightSelectionScreen({ selectedFlight, setSelectedFlight, flightDate, setFlightDate }) {
  const navigate = useNavigate();
  const [flights, setFlights] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [availableDates, setAvailableDates] = useState([]);

  // Clear session memory when returning to flight selection
  useEffect(() => {
    console.log('🗑️  Clearing session memory (returned to flight selection)');
    axios.post(`${API_BASE_URL}/api/clear-session`)
      .then(response => {
        console.log('✅ Session cleared:', response.data);
      })
      .catch(err => {
        console.error('Error clearing session:', err);
      });
  }, []);

  useEffect(() => {
    // Fetch flights from API (from customers.csv)
    const fetchFlights = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/flights`);
        const data = await response.json();
        
        console.log('Fetched flight data:', data);
        
        if (data.flights && data.flights.length > 0) {
          setFlights(data.flights);
          setCategories(['all', ...data.categories]);
          
          // Set default flight if none selected
          if (!selectedFlight) {
            const defaultFlight = data.flights[0];
            setSelectedFlight(defaultFlight);
            if (defaultFlight.availableDates && defaultFlight.availableDates.length > 0) {
              setAvailableDates(defaultFlight.availableDates);
              setFlightDate(defaultFlight.availableDates[0]);
            }
          } else {
            // If a flight is already selected, update available dates
            const existingFlight = data.flights.find(
              f => f.flightNumber === selectedFlight.flightNumber
            );
            if (existingFlight && existingFlight.availableDates) {
              setAvailableDates(existingFlight.availableDates);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching flights:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFlights();
  }, []);

  const handleNext = () => {
    if (selectedFlight && flightDate) {
      // Validate that the selected date is in available dates
      if (!availableDates.includes(flightDate)) {
        alert('Please select a valid departure date from the available dates.');
        return;
      }
      navigate('/metrics');
    }
  };

  // Check if a date is available for the selected flight
  const isDateAvailable = (date) => {
    return availableDates.includes(date);
  };

  // Filter flights by category
  const displayFlights = selectedCategory === 'all' 
    ? flights 
    : flights.filter(f => f.category === selectedCategory);

  console.log('Current state:', {
    loading,
    categoriesCount: categories.length,
    flightsCount: flights.length,
    displayFlightsCount: displayFlights.length,
    selectedCategory,
    selectedFlight,
    availableDates: availableDates.length
  });

  if (loading) {
    return (
      <PageTransition>
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-purple-300">Loading flights from the system...</p>
        </div>
      </PageTransition>
    );
  }

  if (!loading && flights.length === 0) {
    return (
      <PageTransition>
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-red-500">No flights found. Please check if customers.csv is loaded.</p>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen pb-12">
        <Header 
          title="Meal Prediction System"
          subtitle="AI-Powered In-Flight Meal Analytics & Optimization"
        />

        <Container className="mt-8">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-600 to-pink-500 mb-6 shadow-lg shadow-purple-500/30">
              <Plane className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-4xl font-bold gradient-text mb-4">
              Flight Selection
            </h2>
          </motion.div>

          {/* Main Selection Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="max-w-4xl mx-auto"
          >
            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle>Flight Information</CardTitle>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Category Filter */}
                <div className="space-y-2">
                  <Label htmlFor="category">Destination Region</Label>
                  <Select
                    id="category"
                    value={selectedCategory}
                    onChange={(e) => {
                      console.log('Category changed to:', e.target.value);
                      setSelectedCategory(e.target.value);
                    }}
                  >
                    {categories.length === 0 ? (
                      <option value="">Loading categories...</option>
                    ) : (
                      categories.map((category) => (
                        <option key={category} value={category}>
                          {category === 'all' ? 'All Destination Regions' : category}
                        </option>
                      ))
                    )}
                  </Select>
                </div>

                {/* Flight Selection */}
                <div className="space-y-2">
                  <Label htmlFor="flight">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4" />
                      Flight Route
                    </div>
                  </Label>
                  <Select
                    id="flight"
                    value={selectedFlight ? selectedFlight.flightNumber : ''}
                    onChange={(e) => {
                      console.log('Flight changed to:', e.target.value);
                      const flight = displayFlights.find(
                        f => f.flightNumber === e.target.value
                      );
                      console.log('Found flight:', flight);
                      setSelectedFlight(flight);
                      // Update available dates for this flight
                      if (flight && flight.availableDates) {
                        setAvailableDates(flight.availableDates);
                        // Set first available date as default
                        if (flight.availableDates.length > 0) {
                          setFlightDate(flight.availableDates[0]);
                        }
                      } else {
                        setAvailableDates([]);
                        setFlightDate('');
                      }
                    }}
                  >
                    {displayFlights.length === 0 ? (
                      <option value="">No flights available for this region</option>
                    ) : (
                      <>
                        <option value="">Select a flight</option>
                        {displayFlights.map((flight, index) => (
                          <option
                            key={index}
                            value={flight.flightNumber}
                          >
                            {flight.flightNumber} - {flight.origin} → {flight.destination}
                          </option>
                        ))}
                      </>
                    )}
                  </Select>
                </div>

                {/* Date Selection */}
                <div className="space-y-2">
                  <Label htmlFor="date">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Departure Date
                    </div>
                  </Label>
                  <input
                    id="date"
                    type="date"
                    value={flightDate || ''}
                    onChange={(e) => {
                      const selectedDate = e.target.value;
                      console.log('Date selected:', selectedDate);
                      console.log('Available dates:', availableDates);
                      
                      // Validate if the selected date is in available dates
                      if (availableDates.includes(selectedDate)) {
                        setFlightDate(selectedDate);
                        console.log('Date accepted:', selectedDate);
                      } else {
                        // Show a user-friendly error
                        alert(`The date you selected is not available for this flight.\n\nPlease choose from one of the ${availableDates.length} available dates shown below.`);
                        // Reset to current valid date
                        e.target.value = flightDate;
                      }
                    }}
                    disabled={!selectedFlight || availableDates.length === 0}
                    min={availableDates.length > 0 ? availableDates[0] : ''}
                    max={availableDates.length > 0 ? availableDates[availableDates.length - 1] : ''}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
                    style={{ colorScheme: 'light' }}
                  />
                  {/* {availableDates.length > 0 && (
                    <div className="text-xs text-muted-foreground space-y-1">
                      <p className="font-medium">
                        {availableDates.length} available date{availableDates.length !== 1 ? 's' : ''} for this flight:
                      </p>
                      <p className="max-h-20 overflow-y-auto border rounded p-2 bg-muted/30">
                        {availableDates.slice(0, 10).map(date => {
                          const d = new Date(date + 'T00:00:00');
                          return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
                        }).join(', ')}
                        {availableDates.length > 10 && ` ... and ${availableDates.length - 10} more`}
                      </p>
                    </div>
                  )}
                  {!selectedFlight && (
                    <p className="text-xs text-yellow-600 dark:text-yellow-500">
                      Please select a flight first to see available dates
                    </p>
                  )} */}
                </div>

                {/* Selected Flight Details */}
                {selectedFlight && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-6 p-4 rounded-lg bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800"
                  >
                    <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">
                      Selected Flight Details
                    </h4>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-muted-foreground">Flight Number:</span>
                        <p className="font-medium">{selectedFlight.flightNumber}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Route:</span>
                        <p className="font-medium">
                          {selectedFlight.origin} → {selectedFlight.destination}
                        </p>
                      </div>
                      {selectedFlight.category && (
                        <div>
                          <span className="text-muted-foreground">Category:</span>
                          <p className="font-medium">{selectedFlight.category}</p>
                        </div>
                      )}
                      <div>
                        <span className="text-muted-foreground">Date:</span>
                        <p className="font-medium">
                          {new Date(flightDate).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </CardContent>

              <CardFooter className="flex justify-between">
                <p className="text-sm text-muted-foreground">
                  {displayFlights.length} flight{displayFlights.length !== 1 ? 's' : ''} available
                </p>
                <Button
                  onClick={handleNext}
                  disabled={!selectedFlight || !flightDate}
                  size="lg"
                  className="gap-2"
                >
                  Continue to Metrics
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </CardFooter>
            </Card>
          </motion.div>

          {/* Info Cards */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid md:grid-cols-3 gap-6 mt-8 max-w-4xl mx-auto"
          >
            {[
              {
                title: 'Smart Analytics',
                description: 'Advanced ML models analyze passenger demographics and preferences',
                icon: '🧠'
              },
              {
                title: 'Real-time Insights',
                description: 'Get instant predictions and recommendations for meal planning',
                icon: '⚡'
              },
              {
                title: 'Optimized Planning',
                description: 'Reduce waste and improve customer satisfaction',
                icon: '🎯'
              }
            ].map((item, index) => (
              <Card key={index} className="text-center hover:shadow-xl transition-shadow">
                <CardContent className="pt-6">
                  <div className="text-4xl mb-3">{item.icon}</div>
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        </Container>
      </div>
    </PageTransition>
  );
}

export default FlightSelectionScreen;
