import React, { useState, useEffect } from 'react';
import './SuggestionsPanel.css';
import { apiService, Suggestions, Fact } from '../services/api';

interface Props {
  partnerId: number;
}

const SuggestionsPanel: React.FC<Props> = ({ partnerId }) => {
  const [suggestions, setSuggestions] = useState<Suggestions | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'facts'>('suggestions');

  useEffect(() => {
    loadData();
  }, [partnerId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [suggestionsData, factsData] = await Promise.all([
        apiService.getSuggestions(partnerId),
        apiService.getPartnerFacts(partnerId),
      ]);
      setSuggestions(suggestionsData);
      setFacts(factsData);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="suggestions-panel">
        <div className="loading">Loading suggestions...</div>
      </div>
    );
  }

  return (
    <div className="suggestions-panel">
      <div className="panel-tabs">
        <button
          className={activeTab === 'suggestions' ? 'active' : ''}
          onClick={() => setActiveTab('suggestions')}
        >
          Suggestions
        </button>
        <button
          className={activeTab === 'facts' ? 'active' : ''}
          onClick={() => setActiveTab('facts')}
        >
          Known Facts ({facts.length})
        </button>
      </div>

      {activeTab === 'suggestions' && suggestions && (
        <div className="suggestions-content">
          <section className="suggestion-section">
            <h3>Conversation Starters</h3>
            <ul>
              {suggestions.conversation_starters.map((starter, i) => (
                <li key={i}>{starter}</li>
              ))}
            </ul>
          </section>

          <section className="suggestion-section">
            <h3>Follow-up Questions</h3>
            <ul>
              {suggestions.follow_up_questions.map((question, i) => (
                <li key={i}>{question}</li>
              ))}
            </ul>
          </section>

          <section className="suggestion-section">
            <h3>New Topic Ideas</h3>
            <ul>
              {suggestions.new_topic_suggestions.map((topic, i) => (
                <li key={i}>{topic}</li>
              ))}
            </ul>
          </section>

          {suggestions.recent_topics.length > 0 && (
            <section className="suggestion-section">
              <h3>Recent Topics</h3>
              <div className="topic-tags">
                {suggestions.recent_topics.map((topic, i) => (
                  <span key={i} className="topic-tag">
                    {topic}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {activeTab === 'facts' && (
        <div className="facts-content">
          {facts.length === 0 ? (
            <div className="empty-state">
              <p>No facts extracted yet.</p>
              <p>Add and analyze conversations to build knowledge.</p>
            </div>
          ) : (
            <div className="facts-list">
              {facts.map((fact) => (
                <div key={fact.id} className="fact-card">
                  <div className="fact-header">
                    <span className="fact-category">{fact.category}</span>
                    <span className="fact-confidence">
                      {Math.round(fact.confidence * 100)}% confident
                    </span>
                  </div>
                  <div className="fact-content">
                    <strong>{fact.fact_key}:</strong> {fact.fact_value}
                  </div>
                  <div className="fact-date">
                    Extracted {new Date(fact.extracted_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SuggestionsPanel;
