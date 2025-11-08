import React, { useState, useEffect } from 'react';
import './ConversationView.css';
import { apiService, Conversation, ConversationDetail } from '../services/api';

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
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null);
  const [conversationDetail, setConversationDetail] = useState<ConversationDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

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

  useEffect(() => {
    if (conversations.length === 0) {
      setSelectedConversationId(null);
      setConversationDetail(null);
      return;
    }

    if (!selectedConversationId || !conversations.find(conv => conv.id === selectedConversationId)) {
      const first = conversations[0];
      setSelectedConversationId(first.id);
      loadConversationDetail(first.id);
    }
  }, [conversations]);

  const loadConversationDetail = async (conversationId: number) => {
    setDetailLoading(true);
    try {
      const detail = await apiService.getConversation(conversationId);
      setConversationDetail(detail);
    } catch (error) {
      console.error('Failed to load conversation detail:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSelectConversation = (conversationId: number) => {
    setSelectedConversationId(conversationId);
    loadConversationDetail(conversationId);
  };

  const handleAnalyzeConversation = async () => {
    if (!selectedConversationId) return;
    setAnalyzing(true);
    try {
      await apiService.analyzeConversation(selectedConversationId);
      await loadConversations();
      await loadConversationDetail(selectedConversationId);
    } catch (error) {
      console.error('Failed to analyze conversation:', error);
      alert('Analysis failed');
    } finally {
      setAnalyzing(false);
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
        <div className="conversation-content">
          <div className="conversation-list">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                className={`conversation-card ${selectedConversationId === conv.id ? 'active' : ''}`}
                onClick={() => handleSelectConversation(conv.id)}
              >
                <div className="conversation-date">
                  {new Date(conv.started_at).toLocaleDateString()}
                </div>
                {conv.summary && (
                  <div className="conversation-summary">{conv.summary}</div>
                )}
                <div className="conversation-status">
                  {conv.is_analyzed ? '✓ Analyzed' : 'Not analyzed'}
                </div>
              </button>
            ))}
          </div>

          <div className="conversation-detail-panel">
            {detailLoading ? (
              <div className="loading">Loading conversation...</div>
            ) : !conversationDetail ? (
              <div className="detail-placeholder">
                Select a conversation to view transcript and analysis.
              </div>
            ) : (
              <div className="conversation-detail">
                <div className="detail-header">
                  <div>
                    <div className="conversation-date">
                      {new Date(conversationDetail.started_at).toLocaleString()}
                    </div>
                    <div className="conversation-status">
                      {conversationDetail.is_analyzed ? '✓ Analyzed' : 'Not analyzed'}
                    </div>
                  </div>
                  {!conversationDetail.is_analyzed && (
                    <button onClick={handleAnalyzeConversation} disabled={analyzing}>
                      {analyzing ? 'Analyzing...' : 'Analyze Conversation'}
                    </button>
                  )}
                </div>

                {conversationDetail.summary && (
                  <section>
                    <h4>Summary</h4>
                    <p>{conversationDetail.summary}</p>
                  </section>
                )}

                <section>
                  <h4>Transcript</h4>
                  {conversationDetail.full_transcript ? (
                    <pre className="transcript-block">
                      {conversationDetail.full_transcript}
                    </pre>
                  ) : (
                    <div className="empty-state">No transcript captured.</div>
                  )}
                </section>

                {conversationDetail.extracted_facts && conversationDetail.extracted_facts.length > 0 && (
                  <section>
                    <h4>Extracted Facts</h4>
                    <ul className="fact-list">
                      {conversationDetail.extracted_facts.map((fact) => (
                        <li key={fact.id}>
                          <span className="fact-key">{fact.fact_key}:</span>
                          <span>{fact.fact_value}</span>
                        </li>
                      ))}
                    </ul>
                  </section>
                )}

                {conversationDetail.topics && conversationDetail.topics.length > 0 && (
                  <section>
                    <h4>Topics</h4>
                    <div className="conversation-topics">
                      {conversationDetail.topics.map((topic, index) => (
                        <span key={index} className="topic-tag">{topic}</span>
                      ))}
                    </div>
                  </section>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversationView;
