// api.js – Client wrapper for communicating with the FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json'
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = getHeaders();
  
  const config = {
    ...options,
    headers: {
      ...headers,
      ...options.headers
    }
  };
  
  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Request failed on ${endpoint}:`, error);
    throw error;
  }
};

export const authApi = {
  login: async (email, password) => {
    // Bridges to Supabase Auth via FastAPI /login
    const data = await request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.success && data.token) {
      localStorage.setItem('token', data.token);
    }
    return data;
  },
  
  register: async (name, email, password) => {
    return await request('/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
  },
  
  logout: () => {
    localStorage.removeItem('token');
  },
  
  getProfile: async () => {
    return await request('/profile');
  }
};

export const homeApi = {
  getHomes: async () => {
    return await request('/homes');
  },
  
  createHome: async (homeData) => {
    return await request('/homes', {
      method: 'POST',
      body: JSON.stringify(homeData)
    });
  },
  
  getHomeDetails: async (homeId) => {
    return await request(`/homes/${homeId}`);
  },
  
  updateHome: async (homeId, homeData) => {
    return await request(`/homes/${homeId}`, {
      method: 'PUT',
      body: JSON.stringify(homeData)
    });
  },
  
  deleteHome: async (homeId) => {
    return await request(`/homes/${homeId}`, {
      method: 'DELETE'
    });
  },
  
  selectHome: async (homeId) => {
    return await request('/sessions/select', {
      method: 'POST',
      body: JSON.stringify({ home_id: homeId })
    });
  }
};

export const deviceApi = {
  getDevices: async (homeId) => {
    return await request(`/devices?home_id=${homeId}`);
  },
  
  addDevice: async (deviceData) => {
    return await request('/devices', {
      method: 'POST',
      body: JSON.stringify(deviceData)
    });
  },
  
  updateDevice: async (deviceId, deviceData) => {
    return await request(`/devices/${deviceId}`, {
      method: 'PUT',
      body: JSON.stringify(deviceData)
    });
  },
  
  deleteDevice: async (deviceId) => {
    return await request(`/devices/${deviceId}`, {
      method: 'DELETE'
    });
  },
  
  toggleDevice: async (deviceId, status = null) => {
    const url = `/devices/${deviceId}/toggle` + (status ? `?status=${status}` : '');
    return await request(url, {
      method: 'POST'
    });
  }
};

export const energyApi = {
  getEnergyData: async (homeId) => {
    return await request(`/energy/data?home_id=${homeId}`);
  },
  
  getEnergySummary: async (homeId) => {
    return await request(`/energy/summary?home_id=${homeId}`);
  },
  
  getHourlyUsage: async (homeId) => {
    return await request(`/energy/hourly?home_id=${homeId}`);
  },
  
  getPredictions: async (homeId) => {
    return await request(`/energy/prediction?home_id=${homeId}`);
  },
  
  getRecommendations: async (homeId) => {
    return await request(`/energy/recommendations?home_id=${homeId}`);
  },
  
  trainModel: async (homeId) => {
    return await request(`/energy/train?home_id=${homeId}`, {
      method: 'POST'
    });
  }
};

export const reportApi = {
  getReports: async (homeId) => {
    return await request(`/reports?home_id=${homeId}`);
  },
  
  generateReport: async (homeId, type, dateStr = null) => {
    return await request('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ home_id: homeId, type, date_str: dateStr })
    });
  },
  
  getCSVUrl: (reportId) => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/reports/${reportId}/csv` + (token ? `?token=${token}` : '');
  },
  
  getPDFUrl: (reportId) => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/reports/${reportId}/pdf` + (token ? `?token=${token}` : '');
  }
};

export const chatbotApi = {
  getHistory: async (homeId) => {
    return await request(`/chatbot/history?home_id=${homeId}`);
  },
  
  query: async (homeId, message) => {
    return await request('/chatbot/query', {
      method: 'POST',
      body: JSON.stringify({ home_id: homeId, message })
    });
  }
};

export const voiceApi = {
  sendCommand: async (homeId, command) => {
    return await request('/voice/command', {
      method: 'POST',
      body: JSON.stringify({ home_id: homeId, command })
    });
  }
};
