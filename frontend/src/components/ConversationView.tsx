import React, { useState, useEffect } from 'react';
import './ConversationView.css';
import { apiService, Conversation } from '../services/api';

interface Props {
  partnerId: number;
}

const ConversationView: React.FC<Props> = ({ partnerId }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: string; content: string }>>([
    { sender: 'user', content: '' },
  ]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadConversations();
  }, [partnerId]);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const data = await apiService.getConversations(partnerId);
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    const validMessages = messages.filter(m => m.content.trim());
    if (validMessages.length === 0) return;

    setCreating(true);
    try {
      const newConv = await apiService.createConversation({
        partner_id: partnerId,
        messages: validMessages,
      });

      // Analyze the conversation
      await apiService.analyzeConversation(newConv.id);

      // Reload conversations
      await loadConversations();

      // Reset form
      setMessages([{ sender: 'user', content: '' }]);
      setShowNewConversation(false);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      alert('Failed to create conversation');
    } finally {
      setCreating(false);
    }
  };

  const addMessage = () => {
    const lastSender = messages[messages.length - 1]?.sender || 'user';
    const newSender = lastSender === 'user' ? 'partner' : 'user';
    setMessages([...messages, { sender: newSender, content: '' }]);
  };

  const updateMessage = (index: number, content: string) => {
    const updated = [...messages];
    updated[index].content = content;
    setMessages(updated);
  };

  return (
    <div className="conversation-view">
      <div className="conversation-header">
        <h2>Conversations</h2>
        <button onClick={() => setShowNewConversation(!showNewConversation)}>
          {showNewConversation ? 'Cancel' : 'New Conversation'}
        </button>
      </div>

      {showNewConversation && (
        <div className="new-conversation-form">
          <h3>Add New Conversation</h3>
          <div className="messages-input">
            {messages.map((msg, index) => (
              <div key={index} className={`message-input ${msg.sender}`}>
                <label>{msg.sender === 'user' ? 'You' : 'Partner'}:</label>
                <textarea
                  value={msg.content}
                  onChange={(e) => updateMessage(index, e.target.value)}
                  placeholder={`Message from ${msg.sender === 'user' ? 'you' : 'partner'}...`}
                  rows={3}
                />
              </div>
            ))}
          </div>
          <div className="form-actions">
            <button onClick={addMessage} className="secondary">
              Add Message
            </button>
            <button onClick={handleCreateConversation} disabled={creating}>
              {creating ? 'Saving & Analyzing...' : 'Save & Analyze'}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading conversations...</div>
      ) : conversations.length === 0 ? (
        <div className="empty-state">
          <p>No conversations yet.</p>
          <p>Click "New Conversation" to add your first conversation.</p>
        </div>
      ) : (
        <div className="conversation-list">
          {conversations.map((conv) => (
            <div key={conv.id} className="conversation-card">
              <div className="conversation-date">
                {new Date(conv.started_at).toLocaleDateString()}
              </div>
              {conv.summary && (
                <div className="conversation-summary">{conv.summary}</div>
              )}
              {conv.topics && conv.topics.length > 0 && (
                <div className="conversation-topics">
                  {conv.topics.map((topic, i) => (
                    <span key={i} className="topic-tag">
                      {topic}
                    </span>
                  ))}
                </div>
              )}
              <div className="conversation-status">
                {conv.is_analyzed ? '✓ Analyzed' : 'Not analyzed'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationView;
