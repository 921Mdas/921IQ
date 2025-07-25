

import axios from 'axios';
import { useSearchStore } from './store';
import qs from 'qs';

// Environment Configuration
const API_BASE = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com'
  : 'http://localhost:5000';

export const API_AUTH_URL = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com/auth'
  : 'http://127.0.0.1:8000/auth';

console.log('xxxx', API_AUTH_URL, API_BASE  )

// Axios Client Configuration
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
});

// Request Interceptor for logging/debugging
apiClient.interceptors.request.use(config => {
  if (import.meta.env.MODE === 'development') {
    console.log('Request:', config.method?.toUpperCase(), config.url);
    if (config.params) console.log('Params:', config.params);
    if (config.data) console.log('Data:', config.data);
  }
  return config;
});

// Response Interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (import.meta.env.MODE === 'development') {
      console.error('API Error:', {
        message: error.message,
        url: error.config?.url,
        status: error.response?.status,
        data: error.response?.data
      });
    }
    return Promise.reject(error);
  }
);

// Mock Data for fallback
const getMockArticles = () => [{
  id: 'mock-1',
  title: 'Service Unavailable',
  content: 'Please check your connection and try again.',
  isMock: true
}];

// API Service Methods
export const api = {
  /**
   * Fetch summary data from API
   * @param {Object} params - Search parameters
   */
  getSummary: async (params) => {
    const store = useSearchStore.getState();
    store.setIsLoadingSummary(true);

    try {
      const response = await apiClient.get('/get_summary', {
        params,
        headers: { 'Accept': 'application/json' },
        timeout: 45000
      });

      if (response.data?.summary) {
        store.setSummary(response.data.summary);
      }

      return response.data;
    } catch (error) {
      store.setSummary(null);
      if (import.meta.env.MODE === 'development') {
        console.error('Summary Error:', error);
      }
      throw error;
    } finally {
      store.setIsLoadingSummary(false);
    }
  },

  /**
   * Fetch article data with filters
   * @param {Object} params - Filter parameters
   */
  getData: async (params = {}) => {
    const store = useSearchStore.getState();
    store.setLoading(true);

    try {
      // Prepare URL parameters
      const urlParams = new URLSearchParams();

      // Add all parameters except sources
      Object.entries(params).forEach(([key, value]) => {
        if (key !== 'sources' && value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => urlParams.append(key, v));
          } else {
            urlParams.append(key, value);
          }
        }
      });

      // Handle sources separately
      if (params.sources?.length) {
        params.sources
          .filter(source => source)
          .forEach(source => urlParams.append('source', source));
      }

      const response = await apiClient.get('/get_data', {
        params: urlParams,
        paramsSerializer: params => params.toString()
      });

      const data = response.data


      if (data) {
        console.log('let verify ', data.top_publications )
        store.setArticles(data.articles || []);
        store.setTopPublications(data.top_publications || []);
        store.setLoading(false);
      }

      return response.data;
    } catch (error) {
      store.setLoading(false),
      store.setError(error)
      // store.setState({
      //   isLoading: false,
      //   error: error.message
      // });

      // Fallback to mock data in development
      if (import.meta.env.MODE === 'development') {
        store.setArticles(getMockArticles());
      }

      throw error;
    }
  },

  /**
   * Fetch entity data
   * @param {Object} params - Entity search parameters
   */
// getEntity: async (params = {}) => {
//   const store = useSearchStore.getState();
//   store.setEntities([]);
//   store.setIsLoadingEntity(true);

//   try {
//     const urlParams = new URLSearchParams();

//     Object.entries(params).forEach(([key, value]) => {
//       if (Array.isArray(value)) {
//         value.forEach(v => urlParams.append(key, v));
//       } else if (value !== undefined && value !== null) {
//         urlParams.append(key, value);
//       }
//     });

//     // Append query string to URL directly
//     const queryString = urlParams.toString();
//     const url = queryString ? `/get_entities?${queryString}` : '/get_entities';

//     const response = await apiClient.get(url);

//     return response.data;
//   } catch (error) {
//     store.setEntities([]);
//     throw error;
//   } finally {
//     store.setIsLoadingEntity(false);
//   }
// },


  /**
   * Health check endpoint
   */
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      if (import.meta.env.MODE === 'development') {
        console.error('Health check failed:', error);
      }
      throw error;
    }
  },


};

// import axios from 'axios';
// import { useSearchStore } from './store';
// import qs from 'qs';

// // Environment Configuration
// const API_BASE = import.meta.env.MODE === 'production'
//   ? 'https://nine21iq.onrender.com'
//   : 'http://localhost:5000';

// export const API_AUTH_URL = import.meta.env.MODE === 'production'
//   ? 'https://nine21iq.onrender.com/auth'
//   : 'http://127.0.0.1:8000/auth';

// const apiClient = axios.create({
//   baseURL: API_BASE,
//   timeout: 30000,
//   headers: { 'Content-Type': 'application/json' },
//   paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
// });

// // Request Interceptor
// apiClient.interceptors.request.use(config => {
//   if (import.meta.env.MODE === 'development') {
//     console.log('Request:', config.method?.toUpperCase(), config.url);
//     if (config.params) console.log('Params:', config.params);
//     if (config.data) console.log('Data:', config.data);
//   }
//   return config;
// });

// // Response Interceptor
// apiClient.interceptors.response.use(
//   response => response,
//   error => {
//     if (import.meta.env.MODE === 'development') {
//       console.error('API Error:', {
//         message: error.message,
//         url: error.config?.url,
//         status: error.response?.status,
//         data: error.response?.data
//       });
//     }
//     return Promise.reject(error);
//   }
// );

// export const api = {
//   getSummary: async (params) => {
//     const store = useSearchStore.getState();
//     store.setIsLoadingSummary(true);

//     try {
//       const response = await apiClient.get('/get_summary', { 
//         params,
//         timeout: 45000
//       });

//       if (response.data?.summary) {
//         store.setSummary(response.data.summary);
//       }
//       return response.data;
//     } catch (error) {
//       store.setSummary(null);
//       store.setError(error.message);
//       throw error;
//     } finally {
//       store.setIsLoadingSummary(false);
//     }
//   },

//   getData: async (params = {}) => {
//     const store = useSearchStore.getState();
//     store.setLoading(true);
//     store.setError(null);

//     try {
//       const urlParams = new URLSearchParams();
      
//       // Add all parameters
//       Object.entries(params).forEach(([key, value]) => {
//         if (Array.isArray(value)) {
//           value.forEach(v => urlParams.append(key, v));
//         } else if (value !== undefined && value !== null) {
//           urlParams.append(key, value);
//         }
//       });

//       const response = await apiClient.get('/get_data', { params: urlParams });
//       const data = response.data;

//       if (data) {
//         // Using individual setters with proper fallbacks
//         store.setArticles(data.articles || []);
//         store.setTopPublications({
//           labels: data.top_publications?.labels || [],
//           data: data.top_publications?.data || []
//         });
//         store.setTopCountries(data.top_countries || []);
//         store.setWordcloudData(data.wordcloud_data || []);
//         store.setTotalArticles(data.total_articles || 0);
//         store.setTrendData({
//           labels: data.trend_data?.labels || [],
//           data: data.trend_data?.data || []
//         });
//       }

//       return data;
//     } catch (error) {
//       store.setLoading(false);
//       store.setError(error.message);
//       throw error;
//     }
//   },

//   getEntity: async (params = {}) => {
//     const store = useSearchStore.getState();
//     store.setEntities([]);
//     store.setIsLoadingEntity(true);

//     try {
//       const response = await apiClient.get('/get_entities', { params });
//       store.setEntities(response.data?.entities || response.data?.top_people || []);
//       return response.data;
//     } catch (error) {
//       store.setError(error.message);
//       throw error;
//     } finally {
//       store.setIsLoadingEntity(false);
//     }
//   },

//   checkHealth: async () => {
//     try {
//       const response = await apiClient.get('/health');
//       return response.data;
//     } catch (error) {
//       console.error('Health check failed:', error);
//       throw error;
//     }
//   }
// };