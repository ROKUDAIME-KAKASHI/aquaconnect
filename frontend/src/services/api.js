import axios from 'axios';

import { Preferences } from '@capacitor/preferences';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add JWT token to headers
api.interceptors.request.use(async (config) => {
  const { value: token } = await Preferences.get({ key: 'token' });
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await Preferences.remove({ key: 'token' });
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/profile'),
};

export const farmService = {
  getFarms: () => api.get('/farms'),
  getFarm: (id) => api.get(`/farms/${id}`),
  createFarm: (data) => api.post('/farms', data),
  updateFarm: (id, data) => api.put(`/farms/${id}`, data),
  deleteFarm: (id) => api.delete(`/farms/${id}`),
};

export const waterService = {
  analyze: (data) => api.post('/water-quality', data),
  getHistory: (farmId) => api.get(`/water-quality/${farmId}`),
};

export const financeService = {
  getSummary: (farmId) => api.get(`/financial/summary/${farmId}`),
  getTransactions: (farmId) => api.get(`/financial/transactions/${farmId}`),
  createTransaction: (data) => api.post('/financial/transactions', data),
};

export const forumService = {
  getPosts: () => api.get('/forum/posts'),
  getPost: (id) => api.get(`/forum/posts/${id}`),
  createPost: (data) => api.post('/forum/posts', data),
  addReply: (postId, data) => api.post(`/forum/posts/${postId}/replies`, data),
};

export default api;
