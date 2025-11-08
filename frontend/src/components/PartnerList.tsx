import React, { useState } from 'react';
import './PartnerList.css';

interface Partner {
  id: number;
  name: string;
  email?: string;
}

interface Props {
  partners: Partner[];
  selectedPartnerId: number | null;
  onSelectPartner: (id: number) => void;
  onCreatePartner: (name: string, email?: string) => Promise<any>;
  loading: boolean;
}

const PartnerList: React.FC<Props> = ({
  partners,
  selectedPartnerId,
  onSelectPartner,
  onCreatePartner,
  loading,
}) => {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setCreating(true);
    try {
      await onCreatePartner(name, email || undefined);
      setName('');
      setEmail('');
      setShowForm(false);
    } catch (error) {
      alert('Failed to create partner');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="partner-list">
      <div className="partner-list-header">
        <h2>Contacts</h2>
        <button onClick={() => setShowForm(!showForm)} className="add-btn">
          {showForm ? '−' : '+'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="partner-form">
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email (optional)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button type="submit" disabled={creating}>
            {creating ? 'Creating...' : 'Create Contact'}
          </button>
        </form>
      )}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : partners.length === 0 ? (
        <div className="empty-state">
          <p>No contacts yet.</p>
          <p>Click + to add your first contact.</p>
        </div>
      ) : (
        <ul className="partner-items">
          {partners.map((partner) => (
            <li
              key={partner.id}
              className={selectedPartnerId === partner.id ? 'active' : ''}
              onClick={() => onSelectPartner(partner.id)}
            >
              <div className="partner-avatar">
                {partner.name.charAt(0).toUpperCase()}
              </div>
              <div className="partner-info">
                <div className="partner-name">{partner.name}</div>
                {partner.email && (
                  <div className="partner-email">{partner.email}</div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PartnerList;
