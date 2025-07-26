import { useSearchStore } from './store';
import {createApiClient,withRetry, prepareSearchParams, normalizeParam } from './Utils/apiHelper'

const API_BASE = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com'
  : 'http://localhost:8000';

export const API_AUTH_URL = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com/auth'
  : 'http://127.0.0.1:8000/auth';

const apiClient = createApiClient(API_BASE);

export const api = {

getData: async (params = {}) => {
  const store = useSearchStore.getState();
  store.setLoading(true);
  store.setError(null);

  const exposedParam = Object.fromEntries(params);

  try {
    // Normalize parameters
    const normalizedParams = {
      and: normalizeParam(exposedParam.and), // Directly use the key you have
      or: normalizeParam(exposedParam.or),
      not: normalizeParam(exposedParam.not),
      sources: normalizeParam(exposedParam.sources)
    };


    // Simple API GET request
    const response = await apiClient.get('/get_data', { params: normalizedParams });
    const data = response.data;

    return data;

    
  } catch (error) {
    store.setError(error.message);
    throw error;
  } finally {
    store.setLoading(false);
  }
},




  getSummary: async (params) => {
    console.log('RAW PARAMS RECEIVED:', params);
    const queryParams = prepareSearchParams(params);

    try {
      const response = await apiClient.get('/get_summary', {
        params: queryParams,
        paramsSerializer: params => params.toString(),
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('API CALL FAILED:', error);
      throw error;
    }
  },



  checkHealth: async (options = {}) => {
    try {
      return await withRetry(async (attempt) => {
        const response = await apiClient.get('/health', {
          timeout: options.timeout || 5000,
          headers: { 'X-Attempt': attempt }
        });
        return response.data;
      }, options);
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};