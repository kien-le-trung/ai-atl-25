import React, { useState, useEffect } from 'react';
import './App.css';
import { apiService } from './services/api';
import PartnerList from './components/PartnerList';
import ConversationView from './components/ConversationView';
import SuggestionsPanel from './components/SuggestionsPanel';

interface Partner {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  relationship?: string;
  image_path?: string;
}

function App() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [selectedPartnerId, setSelectedPartnerId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPartners();
  }, []);

  const loadPartners = async () => {
    try {
      const data = await apiService.getPartners();
      setPartners(data);
    } catch (error) {
      console.error('Failed to load partners:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePartner = async (
    name: string,
    email?: string,
    relationship?: string,
    image?: File
  ) => {
    try {
      const newPartner = await apiService.createPartnerWithImage({
        name,
        email,
        relationship,
        image,
      });
      setPartners([...partners, newPartner]);
      return newPartner;
    } catch (error) {
      console.error('Failed to create partner:', error);
      throw error;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Conversation Assistant</h1>
        <p>Enhance your conversations with intelligent insights</p>
      </header>

      <div className="App-container">
        <div className="sidebar">
          <PartnerList
            partners={partners}
            selectedPartnerId={selectedPartnerId}
            onSelectPartner={setSelectedPartnerId}
            onCreatePartner={handleCreatePartner}
            loading={loading}
          />
        </div>

        <div className="main-content">
          {selectedPartnerId ? (
            <>
              <ConversationView partnerId={selectedPartnerId} />
              <SuggestionsPanel partnerId={selectedPartnerId} />
            </>
          ) : (
            <div className="welcome">
              <h2>Welcome to AI Conversation Assistant</h2>
              <p>Select a conversation partner from the sidebar to get started.</p>
              <p>Or create a new partner to begin tracking conversations.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
