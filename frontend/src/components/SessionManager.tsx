import React, { useState, useEffect } from 'react';
import './SessionManager.css';
import { API_BASE_ORIGIN } from '../services/api';

interface Camera {
  index: number;
  width: number;
  height: number;
  fps: number;
  backend: string;
  name: string;
}

interface Partner {
  id: number;
  name: string;
  email?: string;
  relationship?: string;
}

interface Session {
  session_id: string;
  user_id: number;
  partner_id: number;
  conversation_id: number;
  is_running: boolean;
  elapsed_seconds: number;
  elapsed_formatted: string;
  message_count: number;
}

interface Transcript {
  timestamp: string;
  text: string;
  elapsed: number;
}

const API_BASE = API_BASE_ORIGIN;
const DEEPGRAM_API_KEY = process.env.REACT_APP_DEEPGRAM_API_KEY || '';

const SessionManager: React.FC = () => {
  // Camera state
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<number | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraLoading, setCameraLoading] = useState(false);

  // Partner state
  const [partners, setPartners] = useState<Partner[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<number | null>(null);

  // Session state
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [transcripts, setTranscripts] = useState<Transcript[]>([]);
  const [detectedPartnerName, setDetectedPartnerName] = useState<string | null>(null);
  const [sessionLoading, setSessionLoading] = useState(false);

  // Face capture state
  const [capturingFace, setCapturingFace] = useState(false);

  // Load cameras on mount
  useEffect(() => {
    loadCameras();
    loadPartners();
    checkCameraStatus();
  }, []);

  // Poll for transcripts when session is active
  useEffect(() => {
    if (!activeSession) {
      return;
    }

    loadTranscripts(activeSession.session_id, activeSession.partner_id);

    const interval = setInterval(() => {
      loadTranscripts(activeSession.session_id, activeSession.partner_id);
    }, 2000);

    return () => clearInterval(interval);
  }, [activeSession]);

  const loadCameras = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/sessions/camera/list`);
      const data = await response.json();
      setCameras(data.cameras);

      // Auto-select last camera (usually OBS Virtual Camera)
      if (data.cameras.length > 0) {
        setSelectedCamera(data.cameras[data.cameras.length - 1].index);
      }
    } catch (error) {
      console.error('Failed to load cameras:', error);
    }
  };

  const loadPartners = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/partners`);
      const data = await response.json();
      setPartners(data);
    } catch (error) {
      console.error('Failed to load partners:', error);
    }
  };

  const checkCameraStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/sessions/camera/status`);
      const data = await response.json();
      setCameraActive(data.is_active);
      if (data.is_active && data.camera_index !== null) {
        setSelectedCamera(data.camera_index);
      }
    } catch (error) {
      console.error('Failed to check camera status:', error);
    }
  };

  const startCamera = async () => {
    if (selectedCamera === null) {
      alert('Please select a camera first');
      return;
    }

    setCameraLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/sessions/camera/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camera_index: selectedCamera })
      });

      const data = await response.json();

      if (data.is_active) {
        setCameraActive(true);
        alert(`Camera ${data.camera_index} started successfully!`);
      } else {
        alert('Failed to start camera');
      }
    } catch (error) {
      console.error('Failed to start camera:', error);
      alert('Error starting camera');
    } finally {
      setCameraLoading(false);
    }
  };

  const stopCamera = async () => {
    setCameraLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/sessions/camera/stop`, {
        method: 'POST'
      });

      const data = await response.json();
      setCameraActive(false);
      alert('Camera stopped');
    } catch (error) {
      console.error('Failed to stop camera:', error);
      alert('Error stopping camera');
    } finally {
      setCameraLoading(false);
    }
  };

  const captureFace = async () => {
    if (!cameraActive) {
      alert('Please start the camera first');
      return;
    }

    setCapturingFace(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/sessions/camera/capture-face?user_id=1`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (data.success) {
        if (data.is_new_partner) {
          alert(`New partner created: ${data.partner_name} (ID: ${data.partner_id})`);
        } else {
          alert(`Identified: ${data.partner_name} (Similarity: ${(data.similarity_score * 100).toFixed(1)}%)`);
        }

        // Reload partners and select the captured one
        await loadPartners();
        setSelectedPartner(data.partner_id);
      } else {
        alert(data.message || 'Failed to capture face');
      }
    } catch (error) {
      console.error('Failed to capture face:', error);
      alert('Error capturing face');
    } finally {
      setCapturingFace(false);
    }
  };

  const startSession = async () => {
    if (selectedPartner === null) {
      alert('Please select or capture a partner first');
      return;
    }

    // Use frontend key or prompt user to enter
    let apiKey = DEEPGRAM_API_KEY;
    if (!apiKey) {
      const enteredKey = prompt('Enter your Deepgram API key:')?.trim();
      if (!enteredKey) {
        alert('Deepgram API key is required to start a session');
        return;
      }
      apiKey = enteredKey;
    }

    setDetectedPartnerName(null);
    setSessionLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/sessions/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          partner_id: selectedPartner,
          deepgram_api_key: apiKey
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start session');
      }

      const data = await response.json();
      setActiveSession(data);
      setTranscripts([]);
      alert('Session started! Speak into your microphone.');
    } catch (error) {
      console.error('Failed to start session:', error);
      const message = error instanceof Error ? error.message : String(error);
      alert(`Error starting session: ${message}`);
    } finally {
      setSessionLoading(false);
    }
  };

  const stopSession = async () => {
    if (!activeSession) return;

    setSessionLoading(true);
    try {
      await fetch(`${API_BASE}/api/sessions/stop/${activeSession.session_id}`, {
        method: 'POST'
      });

      alert(`Session ended. ${activeSession.message_count} messages recorded.`);
      setActiveSession(null);
      setTranscripts([]);
      setDetectedPartnerName(null);
    } catch (error) {
      console.error('Failed to stop session:', error);
      alert('Error stopping session');
    } finally {
      setSessionLoading(false);
    }
  };

  const loadTranscripts = async (sessionId: string, partnerId?: number) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/sessions/${sessionId}/transcripts?max_lines=10`
      );
      const data = await response.json();
      setTranscripts(data.transcripts);
      if (data.detected_partner_name) {
        setDetectedPartnerName(data.detected_partner_name);
      }

      if (data.partner_name) {
        const targetPartnerId = partnerId ?? selectedPartner;
        if (targetPartnerId !== null) {
          setPartners(prev =>
            prev.map(partner =>
              partner.id === targetPartnerId
                ? { ...partner, name: data.partner_name }
                : partner
            )
          );
        }
      }
    } catch (error) {
      console.error('Failed to load transcripts:', error);
    }
  };

  const getPartnerName = (partnerId: number) => {
    const partner = partners.find(p => p.id === partnerId);
    return partner ? partner.name : `Partner ${partnerId}`;
  };

  return (
    <div className="session-manager">
      <h2>🎥 Session Manager</h2>

      {/* Camera Selection */}
      <section className="camera-section">
        <h3>1. Camera Setup</h3>

        <div className="camera-controls">
          <div className="form-group">
            <label>Select Camera:</label>
            <select
              value={selectedCamera ?? ''}
              onChange={(e) => setSelectedCamera(Number(e.target.value))}
              disabled={cameraActive}
            >
              <option value="">-- Select Camera --</option>
              {cameras.map(camera => (
                <option key={camera.index} value={camera.index}>
                  {camera.name} - {camera.fps}fps ({camera.backend})
                </option>
              ))}
            </select>
          </div>

          <div className="button-group">
            {!cameraActive ? (
              <button
                onClick={startCamera}
                disabled={cameraLoading || selectedCamera === null}
                className="btn-primary"
              >
                {cameraLoading ? 'Starting...' : '▶ Start Camera'}
              </button>
            ) : (
              <button
                onClick={stopCamera}
                disabled={cameraLoading}
                className="btn-danger"
              >
                {cameraLoading ? 'Stopping...' : '⏹ Stop Camera'}
              </button>
            )}

            <button onClick={loadCameras} className="btn-secondary">
              🔄 Refresh Cameras
            </button>
          </div>

          {cameraActive && (
            <div className="status-badge success">
              ✓ Camera Active (Index: {selectedCamera})
            </div>
          )}
        </div>

        {/* Camera Preview */}
        {cameraActive && (
          <div className="camera-preview">
            <img
              src={`${API_BASE}/api/sessions/camera/frame?t=${Date.now()}`}
              alt="Camera feed"
              style={{ maxWidth: '100%', height: 'auto', border: '2px solid #4CAF50' }}
              onError={(e) => {
                // Refresh image every 500ms
                setTimeout(() => {
                  (e.target as HTMLImageElement).src =
                    `${API_BASE}/api/sessions/camera/frame?t=${Date.now()}`;
                }, 500);
              }}
            />
          </div>
        )}
      </section>

      {/* Face Capture */}
      <section className="face-section">
        <h3>2. Identify Person</h3>

        <button
          onClick={captureFace}
          disabled={!cameraActive || capturingFace}
          className="btn-primary btn-large"
        >
          {capturingFace ? '📸 Capturing...' : '📸 Capture Face'}
        </button>

        {selectedPartner && (
          <div className="status-badge info">
            Selected: {getPartnerName(selectedPartner)}
          </div>
        )}
      </section>

      {/* Session Controls */}
      <section className="session-section">
        <h3>3. Conversation Session</h3>

        <div className="form-group">
          <label>Partner:</label>
          <select
            value={selectedPartner ?? ''}
            onChange={(e) => setSelectedPartner(Number(e.target.value))}
            disabled={!!activeSession}
          >
            <option value="">-- Select Partner --</option>
            {partners.map(partner => (
              <option key={partner.id} value={partner.id}>
                {partner.name} {partner.relationship ? `(${partner.relationship})` : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="button-group">
          {!activeSession ? (
            <button
              onClick={startSession}
              disabled={sessionLoading || selectedPartner === null}
              className="btn-success btn-large"
            >
              {sessionLoading ? 'Starting...' : '🎙️ Start Session'}
            </button>
          ) : (
            <button
              onClick={stopSession}
              disabled={sessionLoading}
              className="btn-danger btn-large"
            >
              {sessionLoading ? 'Stopping...' : '⏹ Stop Session'}
            </button>
          )}
        </div>

        {/* Active Session Info */}
        {activeSession && (
          <div className="active-session">
            <div className="status-badge success pulse">
              🔴 Recording
            </div>

            <div className="session-info">
              <div>Partner: {getPartnerName(activeSession.partner_id)}</div>
              <div>Duration: {activeSession.elapsed_formatted}</div>
              <div>Messages: {activeSession.message_count}</div>
              <div>Conversation ID: {activeSession.conversation_id}</div>
            </div>
            {detectedPartnerName && (
              <div className="status-badge info">
                Identified name detected: {detectedPartnerName}
              </div>
            )}

            {/* Live Transcripts */}
            <div className="transcripts">
              <h4>Live Transcription:</h4>
              <div className="transcript-list">
                {transcripts.length === 0 ? (
                  <div className="transcript-placeholder">
                    Speak into your microphone to see transcripts...
                  </div>
                ) : (
                  transcripts.map((t, idx) => (
                    <div key={idx} className="transcript-item">
                      <span className="transcript-time">[{t.timestamp}]</span>
                      <span className="transcript-text">{t.text}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Help */}
      <section className="help-section">
        <h4>ℹ️ Instructions</h4>
        <ol>
          <li>Select your camera (OBS Virtual Camera for Meta glasses)</li>
          <li>Start the camera to see the live feed</li>
          <li>Capture a face to identify or create a new partner</li>
          <li>Start a conversation session to begin recording with transcription</li>
          <li>Speak normally - everything will be transcribed in real-time</li>
          <li>Stop the session when done</li>
        </ol>
      </section>
    </div>
  );
};

export default SessionManager;
