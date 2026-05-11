// API Configuration
// Automatically detects the hostname from browser URL and constructs backend API URL

const getApiBaseUrl = () => {
  // This code runs in the browser
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  // Backend always runs on port 8001
  const apiUrl = `${protocol}//${hostname}:8001/api/v1`;
  
  return apiUrl;
};

export const API_BASE_URL = getApiBaseUrl();
