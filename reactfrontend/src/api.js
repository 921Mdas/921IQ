import axios from 'axios';
import { useSearchStore } from './store';
import qs from 'qs';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';


const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: params => {
    return qs.stringify(params, { arrayFormat: 'repeat' });
  }
});

// Add interceptors for debugging
apiClient.interceptors.request.use(config => {
  return config;
});

const getStoreState = () => useSearchStore.getState();

const getMockArticles = () => [{
  id: 'mock-1',
  title: 'Service Unavailable',
  content: 'Please check your connection and try again.',
  isMock: true
}];

export const api = {
  getSummary: async (params = {}) => {
    try {
      const response = await apiClient.get('/get_summary', { params });
      getStoreState().setSummary(response.data);
      return response.data;
    } catch (error) {
      console.error("Summary error:", error);
      getStoreState().setError(error.message);
      throw error;
    }
  },

  getData: async (params = {}) => {
    try {
      // console.log('Fetching from:', `${API_BASE}/get_data`);
      const response = await apiClient.get('/get_data', { params });
      getStoreState().setArticles(response.data);
      return response.data;
    } catch (error) {
      console.error("Data error:", error);
      getStoreState().setArticles(getMockArticles());
      getStoreState().setError(error.message);
      throw error;
    }
  }
};