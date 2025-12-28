import axios from 'axios';
import { getApiUrl } from './env';

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
});

// Interceptor to add JWT token
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
