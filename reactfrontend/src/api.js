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

getSummary: async (params) => {
  try {
    const response = await apiClient.get(`/get_summary`, {
      params,
      headers: {
        'Accept': 'application/json' // Explicitly request JSON
      },
      timeout: 45000
    });
    console.log('API Response:', response.data);
    return response.data;
  } catch (error) {
    console.error("API Error:", {
      message: error.message,
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    });
    throw error;
  }
},

getData: async (params = {}) => {
  try {
    // Filter and transform sources for URL params
    const filteredParams = {
      ...params,
      // Remove the sources array from main params (we'll handle it manually)
      sources: undefined
    };

    // Create URLSearchParams to handle multiple values properly
    const urlParams = new URLSearchParams();

    // Add keyword and other params
    Object.entries(filteredParams).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => urlParams.append(key, v));
      } else if (value !== undefined && value !== null) {
        urlParams.append(key, value);
      }
    });

    // Handle `sources` array separately with correct naming
    if (params.sources) {
      params.sources
        .filter(source => source !== null && source !== undefined && source !== '')
        .forEach(source => urlParams.append('source', source));
    }

    useSearchStore.getState().setLoading(true);

    const response = await apiClient.get('/get_data', {
      params: urlParams,
      paramsSerializer: params => params.toString() // Prevent default serialization
    });

    if (response.data) {

    const data = response.data
  
    console.log('api testing top pubs', data.top_publications)

    useSearchStore.setState({
        articles: data.articles || [],
        top_publications: data.top_publications || [],
        top_countries: data.top_countries || [],
        wordcloud_data: data.wordcloud_data || [],
        trend_data: data.trend_data || { labels: [], data: [] },
        total_articles: data.total_articles || 0,
        isLoading: false,
        error: null
      });

      console.log('api', useSearchStore.getState().top_publications)

    } else {
      console.error('[API] No data received in response');
      throw new Error('No data received from API');
    }

    return response.data;
    
  } catch (error) {
    useSearchStore.setState({
      isLoading: false,
      error: error.message
    });

    // Optionally: fallback to mock data
    getStoreState().setArticles(getMockArticles());

    throw error;
  }
}

};

// export const api = {
//   getSummary: async (params = {}) => {
//     try {
//       const response = await apiClient.get('/get_summary', { params });
//       getStoreState().setSummary(response.data);
//       return response.data;
//     } catch (error) {
//       console.error("Summary error:", error);
//       getStoreState().setError(error.message);
//       throw error;
//     }
//   },

//   getData: async (params = {}) => {
//     try {
//       // console.log('Fetching from:', `${API_BASE}/get_data`);
//       const response = await apiClient.get('/get_data', { params });
//       getStoreState().setArticles(response.data);
//       return response.data;
//     } catch (error) {
//       console.error("Data error:", error);
//       getStoreState().setArticles(getMockArticles());
//       getStoreState().setError(error.message);
//       throw error;
//     }
//   },


// };