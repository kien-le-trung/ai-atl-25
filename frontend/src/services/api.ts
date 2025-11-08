import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Partner {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  notes?: string;
  relationship?: string;
  image_path?: string;
  image_url?: string;
}

export interface Message {
  sender: string;
  content: string;
  timestamp?: string;
}

export interface Conversation {
  id: number;
  partner_id: number;
  title?: string;
  summary?: string;
  is_analyzed: boolean;
  started_at: string;
  messages?: Message[];
  topics?: string[];
}

export interface Suggestions {
  partner_name: string;
  known_facts_count: number;
  recent_topics: string[];
  conversation_starters: string[];
  follow_up_questions: string[];
  new_topic_suggestions: string[];
}

export interface Fact {
  id: number;
  category: string;
  fact_key: string;
  fact_value: string;
  confidence: number;
  extracted_at: string;
}

export const apiService = {
  // Partners
  async getPartners(): Promise<Partner[]> {
    const response = await apiClient.get('/partners');
    return response.data;
  },

  async createPartner(data: { name: string; email?: string; phone?: string }): Promise<Partner> {
    const response = await apiClient.post('/partners', data);
    return response.data;
  },

  async createPartnerWithImage(data: {
    name: string;
    email?: string;
    relationship?: string;
    notes?: string;
    image?: File;
  }): Promise<Partner> {
    const formData = new FormData();
    formData.append('name', data.name);
    if (data.email) formData.append('email', data.email);
    if (data.relationship) formData.append('relationship', data.relationship);
    if (data.notes) formData.append('notes', data.notes);
    if (data.image) formData.append('image', data.image);

    const response = await apiClient.post('/partners/create-with-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadPartnerImage(partnerId: number, image: File): Promise<Partner> {
    const formData = new FormData();
    formData.append('image', image);

    const response = await apiClient.post(`/partners/${partnerId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async searchPartnersByFace(image: File, threshold?: number, topK?: number): Promise<any> {
    const formData = new FormData();
    formData.append('image', image);
    if (threshold !== undefined) formData.append('threshold', threshold.toString());
    if (topK !== undefined) formData.append('top_k', topK.toString());

    const response = await apiClient.post('/partners/search-by-face', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getPartner(id: number): Promise<Partner> {
    const response = await apiClient.get(`/partners/${id}`);
    return response.data;
  },

  // Conversations
  async getConversations(partnerId?: number): Promise<Conversation[]> {
    const params = partnerId ? { partner_id: partnerId } : {};
    const response = await apiClient.get('/conversations', { params });
    return response.data;
  },

  async createConversation(data: {
    partner_id: number;
    title?: string;
    messages: Message[];
  }): Promise<Conversation> {
    const response = await apiClient.post('/conversations', data);
    return response.data;
  },

  async getConversation(id: number): Promise<Conversation> {
    const response = await apiClient.get(`/conversations/${id}`);
    return response.data;
  },

  async analyzeConversation(id: number): Promise<any> {
    const response = await apiClient.post(`/conversations/${id}/analyze`);
    return response.data;
  },

  // Suggestions
  async getSuggestions(partnerId: number): Promise<Suggestions> {
    const response = await apiClient.get(`/suggestions/${partnerId}`);
    return response.data;
  },

  async getPartnerFacts(partnerId: number): Promise<Fact[]> {
    const response = await apiClient.get(`/suggestions/${partnerId}/facts`);
    return response.data;
  },
};
