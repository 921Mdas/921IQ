import axios from 'axios';
import { useSearchStore } from './store';
import qs from 'qs';

const API_BASE = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com'
  : 'http://localhost:5000';

export const API_AUTH_URL = import.meta.env.MODE === 'production'
  ? 'https://nine21iq.onrender.com/auth'
  : 'http://127.0.0.1:8000/auth';

const generateRequestId = () => Math.random().toString(36).substring(2, 15) + 
                             Math.random().toString(36).substring(2, 15);

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
});

apiClient.interceptors.request.use(config => {
  const requestId = generateRequestId();
  config.headers['X-Request-Id'] = requestId;

  if (import.meta.env.MODE === 'development') {
    console.log('API Request:', {
      requestId,
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data
    });
  }

  performance.mark(`api-request-start-${requestId}`);
  return config;
});

apiClient.interceptors.response.use(
  response => {
    const requestId = response.config.headers['X-Request-Id'];
    const duration = performance.measure(
      `api-request-duration-${requestId}`,
      `api-request-start-${requestId}`
    ).duration;

    if (import.meta.env.MODE === 'development') {
      console.log('API Response:', {
        requestId,
        status: response.status,
        duration: `${duration.toFixed(2)}ms`,
        data: response.data
      });
    }
    return response;
  },
  error => {
    const errorData = {
      message: error.message,
      code: error.code,
      url: error.config?.url,
      method: error.config?.method,
      params: error.config?.params,
      status: error.response?.status,
      data: error.response?.data,
      stack: error.stack
    };

    if (import.meta.env.MODE === 'development') {
      console.error('API Error:', errorData);
    }
    return Promise.reject(error);
  }
);

const normalizeError = (error) => {
  if (error.response) {
    return {
      status: error.response.status,
      message: error.response.data?.message || 'API request failed',
      details: error.response.data?.details,
      isApiError: true
    };
  } else if (error.request) {
    return {
      message: 'Network error - no response received',
      isNetworkError: true
    };
  }
  return {
    message: error.message || 'Unknown API error',
    isClientError: true
  };
};

const withRetry = async (requestFn, options = {}) => {
  const { retries = 2, retryDelay = 1000 } = options;
  let lastError = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await requestFn(attempt);
    } catch (error) {
      lastError = error;
      if (error.response?.status === 404 || error.response?.status === 401) {
        break;
      }
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        continue;
      }
      throw normalizeError(error);
    }
  }
  throw normalizeError(lastError);
};

export const api = {
// getSummary: async (params, options = {}) => {
//     const store = useSearchStore.getState();
//     store.setIsLoadingSummary(true);
//     store.setError(null);

//     try {
//       const data = await withRetry(async (attempt) => {
//         const response = await apiClient.get('/get_summary', {
//           params,
//           headers: { 
//             'Accept': 'application/json',
//             'X-Attempt': attempt 
//           },
//           timeout: options.timeout || 45000
//         });
//         return response.data;
//       }, options);

//       if (data?.summary) {
//         store.setSummary(data.summary);
//       }
//       return data;
//     } catch (error) {
//       store.setSummary(null);
//       store.setSummaryError(error.message);
//       throw error;
//     } finally {
//       store.setIsLoadingSummary(false);
//     }
//   },

getData: async (params = {}, options = {}) => {
    const store = useSearchStore.getState();
    store.setLoading(true);
    store.setError(null);

    try {
      const urlParams = new URLSearchParams();

      Object.entries(params).forEach(([key, value]) => {
        if (key !== 'sources' && value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => urlParams.append(key, v));
          } else {
            urlParams.append(key, value);
          }
        }
      });

      if (params.sources?.length) {
        params.sources
          .filter(source => source)
          .forEach(source => urlParams.append('source', source));
      }

      const data = await withRetry(async (attempt) => {
        const response = await apiClient.get('/get_data', {
          params: urlParams,
          paramsSerializer: params => params.toString(),
          timeout: options.timeout || 90000,
          headers: { 'X-Attempt': attempt }
        });
        return response.data;
      }, options);

      if (data) {
        store.setArticles(data.articles || []);
        store.setTopPublications(data.top_publications || []);
      }
      return data;
    } catch (error) {
      store.setError(error.message);
      if (import.meta.env.MODE === 'development') {
        store.setArticles([{
          id: 'mock-1',
          title: 'Service Unavailable',
          content: 'Please check your connection and try again.',
          isMock: true
        }]);
      }
      throw error;
    } finally {
      store.setLoading(false);
    }
  },

  // getEntity: async (params = {}, options = {}) => {
  //   const store = useSearchStore.getState();
  //   store.setEntities([]);
  //   store.setIsLoadingEntity(true);
  //   store.setError(null);

  //   try {
  //     const urlParams = new URLSearchParams();

  //     Object.entries(params).forEach(([key, value]) => {
  //       if (Array.isArray(value)) {
  //         value.forEach(v => urlParams.append(key, v));
  //       } else if (value !== undefined && value !== null) {
  //         urlParams.append(key, value);
  //       }
  //     });

  //     const queryString = urlParams.toString();
  //     const url = queryString ? `/get_entities?${queryString}` : '/get_entities';

  //     const data = await withRetry(async (attempt) => {
  //       const response = await apiClient.get(url, {
  //         timeout: options.timeout || 30000,
  //         headers: { 'X-Attempt': attempt }
  //       });
  //       return response.data;
  //     }, options);

  //     store.setEntities(data?.entities || data || []);
  //     return data;
  //   } catch (error) {
  //     store.setError(error.message);
  //     store.setEntities([]);
  //     throw error;
  //   } finally {
  //     store.setIsLoadingEntity(false);
  //   }
  // },

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