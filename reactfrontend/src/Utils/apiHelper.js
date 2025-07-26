import axios from 'axios';
import qs from 'qs';

export const generateRequestId = () => Math.random().toString(36).substring(2, 15) + 
                             Math.random().toString(36).substring(2, 15);

// Helper function to ensure array format
export function normalizeParam(param) {
  if (!param) return [];
  if (Array.isArray(param)) return param;
  return [String(param)]; // Convert numbers/objects if needed
}

export const normalizeError = (error) => {
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

export const withRetry = async (requestFn, options = {}) => {
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

export const createApiClient = (baseURL) => {
  const apiClient = axios.create({
    baseURL,
    timeout: 60000,
    withCredentials: false,
    headers: {
      'Content-Type': 'application/json',
    },
    paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' }),
    crossdomain: true
  });

  apiClient.interceptors.request.use(config => {
    console.log('FULL REQUEST CONFIG:', config);
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

  return apiClient;
};

export const prepareSearchParams = (params) => {
  // Convert params to URLSearchParams format
  const queryParams = new URLSearchParams();
  
  // Handle AND terms
  if (params.and?.length) {
    params.and.forEach(term => queryParams.append('and', term));
  }
  
  // Handle OR terms (if needed)
  if (params.or?.length) {
    params.or.forEach(term => queryParams.append('or', term));
  }
  
  // Handle NOT terms (if needed)
  if (params.not?.length) {
    params.not.forEach(term => queryParams.append('not', term));
  }
  
  // Handle sources
  if (params.sources) {
    if (Array.isArray(params.sources)) {
      params.sources.forEach(source => queryParams.append('source', source));
    } else {
      queryParams.append('source', params.sources);
    }
  }

  return queryParams;
};

