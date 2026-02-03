// API Configuration
// For Docker: Use window.location.hostname to dynamically get the host
// This way it works whether accessing via localhost, IP, or domain name

const getApiBaseUrl = () => {
  // Check if running in development mode
  if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // In production or Docker, use the same host as the frontend
  // This works for localhost, VM IP, or any hostname
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  // Backend runs on port 8001
  return `${protocol}//${hostname}:8001`;
};

export const API_BASE_URL = getApiBaseUrl();

console.log('🔧 API Configuration:', API_BASE_URL);
