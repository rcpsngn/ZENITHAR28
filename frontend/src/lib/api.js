import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getProfile: () => api.get('/auth/profile/'),
  getSubscription: () => api.get('/auth/subscription/'),
};

export const personnelAPI = {
  getEmployees: (params) => api.get('/personnel/employees/', { params }),
  getEmployee: (id) => api.get(`/personnel/employees/${id}/`),
  createEmployee: (data) => api.post('/personnel/employees/', data),
  updateEmployee: (id, data) => api.put(`/personnel/employees/${id}/`, data),
  deleteEmployee: (id) => api.delete(`/personnel/employees/${id}/`),
  toggleActive: (id) => api.post(`/personnel/employees/${id}/toggle_active/`),
  
  getAttendance: (params) => api.get('/personnel/attendance/', { params }),
  createAttendance: (data) => api.post('/personnel/attendance/', data),
  quickEntry: (data) => api.post('/personnel/attendance/quick_entry/', data),
  
  getSalaries: (params) => api.get('/personnel/salaries/', { params }),
  createSalary: (data) => api.post('/personnel/salaries/', data),
  updateSalary: (id, data) => api.put(`/personnel/salaries/${id}/`, data),
  markPaid: (id) => api.post(`/personnel/salaries/${id}/mark_paid/`),
  
  getLeaves: (params) => api.get('/personnel/leaves/', { params }),
  createLeave: (data) => api.post('/personnel/leaves/', data),
  updateLeave: (id, data) => api.put(`/personnel/leaves/${id}/`, data),
  approveLeave: (id) => api.post(`/personnel/leaves/${id}/approve/`),
  rejectLeave: (id, notes) => api.post(`/personnel/leaves/${id}/reject/`, { notes }),
};
