"""
Session service for managing conversation sessions with live audio transcription.
"""
import asyncio
import json
import logging
import re
import time
import pyaudio
import websockets
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Callable
from collections import deque
from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message
from app.models.conversation_partner import ConversationPartner
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.profile_service import ProfileBuilder
from app.utils.db_helpers import get_next_id

logger = logging.getLogger(__name__)

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

NAME_PATTERNS = [
    re.compile(r"\bmy name is\s+(?P<name>[a-zA-Z][a-zA-Z\s'-]{1,40})", re.IGNORECASE),
    re.compile(r"\bcall me\s+(?P<name>[a-zA-Z][a-zA-Z\s'-]{1,40})", re.IGNORECASE),
]
MAX_NAME_WORDS = 3
MIN_NAME_WORD_LENGTH = 2


class ConversationSession:
    """Manages a single conversation session with live transcription."""

    def __init__(
        self,
        session_id: str,
        user_id: int,
        partner_id: int,
        conversation_id: int,
        deepgram_api_key: str,
        db_factory: Callable[[], Session]
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.partner_id = partner_id
        self.conversation_id = conversation_id
        self.deepgram_api_key = deepgram_api_key
        self.db_factory = db_factory
        self.db: Session = self.db_factory()

        self.is_running = False
        self.session_start = None
        self.audio_queue = None
        self.transcripts = deque(maxlen=100)
        self.transcript_lines: List[str] = []
        self.transcript_char_count = 0
        self.detected_partner_name: Optional[str] = None
        self.last_name_detection_at: Optional[datetime] = None
        self.input_device_index: Optional[int] = None
        self.audio_chunks_enqueued = 0
        self.audio_chunks_sent = 0
        self.debug_messages_logged = 0

        # Audio components
        self.audio = None
        self.stream = None
        self.loop = None
        self.ws = None
        self.thread = None

        # Statistics
        self.message_count = 0
        self.total_duration = 0

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS format."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def mic_callback(self, input_data, frame_count, time_info, status_flag):
        """Callback for PyAudio to capture microphone data."""
        if self.is_running and self.loop and self.audio_queue:
            asyncio.run_coroutine_threadsafe(
                self.audio_queue.put(input_data), self.loop
            )
            self.audio_chunks_enqueued += 1
            if self.audio_chunks_enqueued <= 3:
                logger.info(
                    f"[Session {self.session_id}] Enqueued audio chunk {self.audio_chunks_enqueued} "
                    f"(bytes={len(input_data)})"
                )
        return (input_data, pyaudio.paContinue)

    async def send_audio(self):
        """Send audio data to Deepgram."""
        try:
            while self.is_running and self.ws:
                audio_data = await self.audio_queue.get()
                await self.ws.send(audio_data)
                self.audio_chunks_sent += 1
                if self.audio_chunks_sent <= 3:
                    logger.info(
                        f"[Session {self.session_id}] Sent audio chunk {self.audio_chunks_sent} "
                        f"(bytes={len(audio_data)}) to Deepgram"
                    )
        except Exception as e:
            logger.error(f"Error sending audio: {e}")

    async def receive_transcripts(self):
        """Receive transcripts from Deepgram and save to database."""
        try:
            async for msg in self.ws:
                if not self.is_running:
                    break

                res = json.loads(msg)
                event_type = res.get("type")
                if event_type and event_type != "Results" and self.debug_messages_logged < 5:
                    logger.debug(f"[Session {self.session_id}] Deepgram event ({event_type}): {res}")
                    self.debug_messages_logged += 1

                is_final = res.get("is_final")
                is_result_event = event_type == "Results"

                if is_final or is_result_event:
                    transcript_text = (
                        res.get("channel", {})
                        .get("alternatives", [{}])[0]
                        .get("transcript", "")
                    )

                    if transcript_text.strip():
                        # Calculate elapsed time
                        elapsed = time.time() - self.session_start
                        timestamp = self.format_timestamp(elapsed)

                        transcript_entry = {
                            'timestamp': timestamp,
                            'text': transcript_text,
                            'elapsed': elapsed,
                            'datetime': datetime.now(timezone.utc).isoformat()
                        }

                        self.transcripts.append(transcript_entry)
                        pretty_line = f"[{timestamp}] {transcript_text.strip()}"
                        self.transcript_lines.append(pretty_line)
                        self.transcript_char_count += len(pretty_line) + 1
                        if self.transcript_char_count > 20000 and len(self.transcript_lines) > 50:
                            removed = self.transcript_lines.pop(0)
                            self.transcript_char_count -= len(removed) + 1
                        logger.info(f"[Session {self.session_id}] [{timestamp}] {transcript_text}")
                        print(f"[Session {self.session_id}] {transcript_text}", flush=True)

                        # Save to database as a message
                        self.save_message(transcript_text)
                        self.detect_partner_name(transcript_text)
                    elif self.debug_messages_logged < 5:
                        logger.debug(f"[Session {self.session_id}] Empty transcript payload: {res}")
                        self.debug_messages_logged += 1

        except Exception as e:
            logger.error(f"Error receiving transcripts: {e}")

    def save_message(self, content: str, sender: str = "user"):
        """
        Save a transcript message to the database.

        Args:
            content: Message content
            sender: 'user' or 'partner' (default: 'user')
        """
        try:
            message = Message(
                conversation_id=self.conversation_id,
                sender=sender,
                content=content,
                timestamp=datetime.now(timezone.utc)
            )

            self.db.add(message)
            self.db.commit()
            self.message_count += 1

            logger.info(f"Message saved to conversation {self.conversation_id}")

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            self.db.rollback()

    def _log_microphone_devices(self):
        """Log detected input devices to help debug audio issues."""
        if not self.audio:
            return

        try:
            device_count = self.audio.get_device_count()
            logger.info(f"PyAudio detected {device_count} audio devices")

            for idx in range(device_count):
                info = self.audio.get_device_info_by_index(idx)
                if info.get("maxInputChannels", 0) > 0:
                    logger.info(
                        f"[Audio Device] index={idx} name='{info.get('name')}' "
                        f"inputs={info.get('maxInputChannels')} defaultSampleRate={info.get('defaultSampleRate')}"
                    )
        except Exception as e:
            logger.warning(f"Unable to enumerate audio devices: {e}")

    def _ensure_microphone_ready(self):
        """Ensure a microphone input is available before recording."""
        if not self.audio:
            raise RuntimeError("PyAudio not initialized")

        try:
            default_device = self.audio.get_default_input_device_info()
            logger.info(
                "Using default input device '%s' (index %s)",
                default_device.get("name"),
                default_device.get("index"),
            )
        except Exception as e:
            logger.error(f"No default microphone available: {e}")
            raise RuntimeError("No default microphone input available") from e

    def _compile_full_transcript(self) -> str:
        """Compile the entire conversation transcript from stored messages."""
        if self.transcript_lines:
            return "\n".join(self.transcript_lines)

        try:
            messages = (
                self.db.query(Message)
                .filter(Message.conversation_id == self.conversation_id)
                .order_by(Message.timestamp.asc())
                .all()
            )
        except Exception as e:
            logger.error(f"Error loading messages for transcript: {e}")
            return ""

        if not messages:
            return ""

        lines = []
        for message in messages:
            timestamp = (
                message.timestamp.isoformat()
                if getattr(message, "timestamp", None)
                else ""
            )
            sender = message.sender.capitalize() if message.sender else "Speaker"
            content = message.content or ""
            if timestamp:
                lines.append(f"{timestamp} [{sender}]: {content}")
            else:
                lines.append(f"[{sender}]: {content}")

        return "\n".join(lines)

    def _run_conversation_analysis(self):
        """Trigger Gemini-powered analysis for the completed conversation."""
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            logger.warning("Gemini API key not configured; skipping conversation analysis")
            return

        try:
            builder = ProfileBuilder(gemini_api_key=api_key)
            builder.analyze_conversation(self.conversation_id, self.db)
            logger.info(f"Completed AI analysis for conversation {self.conversation_id}")
        except Exception as e:
            logger.error(f"Failed to analyze conversation {self.conversation_id}: {e}")

    def _extract_name_from_transcript(self, text: str) -> Optional[str]:
        """Try to extract a likely name from transcript text."""
        if not text:
            return None

        normalized = text.strip()
        for pattern in NAME_PATTERNS:
            match = pattern.search(normalized)
            if not match:
                continue

            raw_candidate = match.group("name")
            # Stop at obvious sentence terminators
            candidate = re.split(r"[.!?,;]", raw_candidate)[0].strip()
            # Remove trailing filler words
            candidate = re.sub(r"\b(and|but|so)\b.*", "", candidate, flags=re.IGNORECASE).strip()
            words = [w for w in re.split(r"[\s\-]+", candidate) if w]

            if not words or len(words) > MAX_NAME_WORDS:
                continue

            if any(len(word) < MIN_NAME_WORD_LENGTH for word in words):
                continue

            if any(not word.isalpha() for word in words):
                continue

            formatted = " ".join(word.capitalize() for word in words)

            if len(formatted) < MIN_NAME_WORD_LENGTH + 1:  # Too short overall
                continue

            return formatted

        return None

    def detect_partner_name(self, transcript_text: str):
        """Detect and update partner name once per session."""
        if self.detected_partner_name:
            return

        candidate = self._extract_name_from_transcript(transcript_text)
        if not candidate:
            return

        self._update_partner_name(candidate)

    def _update_partner_name(self, new_name: str):
        """Persist detected partner name."""
        try:
            partner = self.db.query(ConversationPartner).filter(
                ConversationPartner.id == self.partner_id
            ).first()

            if not partner:
                logger.warning(f"Partner {self.partner_id} not found for name update")
                return

            current_name = (partner.name or "").strip()
            if current_name.lower() == new_name.lower():
                self.detected_partner_name = new_name
                self.last_name_detection_at = datetime.now(timezone.utc)
                return

            partner.name = new_name
            self.db.commit()
            self.detected_partner_name = new_name
            self.last_name_detection_at = datetime.now(timezone.utc)
            logger.info(f"Updated partner {partner.id} name to '{new_name}' based on transcript")

        except Exception as e:
            logger.error(f"Error updating partner name: {e}")
            self.db.rollback()

    async def run_transcription(self):
        """Main async function to handle transcription."""
        deepgram_url = (
            f"wss://api.deepgram.com/v1/listen?"
            f"punctuate=true&encoding=linear16&sample_rate={RATE}&channels={CHANNELS}"
        )

        try:
            logger.info(f"Attempting Deepgram connection for session {self.session_id}")
            print(f"[Session {self.session_id}] Connecting to Deepgram...", flush=True)
            async with websockets.connect(
                deepgram_url,
                extra_headers={"Authorization": f"Token {self.deepgram_api_key}"},
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10
            ) as ws:
                self.ws = ws
                logger.info(f"Connected to Deepgram for session {self.session_id}")
                print(f"[Session {self.session_id}] Connected to Deepgram", flush=True)

                # Run sender and receiver concurrently
                await asyncio.gather(
                    self.send_audio(),
                    self.receive_transcripts()
                )

        except Exception as e:
            logger.error(f"Transcription error: {e}")
        finally:
            self.is_running = False
            self.ws = None

    async def start_async(self):
        """Start the transcription service asynchronously."""
        self.session_start = time.time()
        self.is_running = True
        self.audio_queue = asyncio.Queue()

        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            self._log_microphone_devices()
            self._ensure_microphone_ready()
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=self.mic_callback,
            )

            self.stream.start_stream()
            logger.info(f"Microphone started for session {self.session_id}")
            if not self.stream.is_active():
                logger.warning("Microphone stream is not active immediately after start")
            else:
                logger.info("Microphone stream active and capturing audio")

            # Start transcription
            await self.run_transcription()

        except Exception as e:
            logger.error(f"Error starting session: {e}")
            self.is_running = False

    def stop(self):
        """Stop the session and cleanup."""
        logger.info(f"Stopping session {self.session_id}")
        self.is_running = False

        # Stop audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.audio:
            self.audio.terminate()

        # Unblock async tasks so event loop can finish cleanly
        if self.loop and self.audio_queue:
            try:
                self.loop.call_soon_threadsafe(self.audio_queue.put_nowait, b"")
            except Exception as e:
                logger.debug(f"Failed to flush audio queue: {e}")

        if self.ws and self.loop:
            try:
                asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            except Exception as e:
                logger.debug(f"Failed to close websocket gracefully: {e}")

        # Update conversation end time
        try:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == self.conversation_id
            ).first()

            if conversation:
                conversation.ended_at = datetime.now(timezone.utc)
                conversation.full_transcript = self._compile_full_transcript()
                self.total_duration = (conversation.ended_at - conversation.started_at).total_seconds()
                self.db.commit()

                logger.info(f"Conversation {self.conversation_id} ended. Duration: {self.total_duration}s")
                if conversation.full_transcript:
                    line_count = len(conversation.full_transcript.splitlines())
                    logger.info(
                        f"Stored {line_count} transcript lines for conversation {self.conversation_id}"
                    )
                    preview = conversation.full_transcript
                    # Print in red for visibility
                    print(
                        f"\033[91m[Session {self.session_id}] Transcript saved ({line_count} lines):\n{preview}\033[0m",
                        flush=True
                    )
                self._run_conversation_analysis()

        except Exception as e:
            logger.error(f"Error updating conversation end time: {e}")
            self.db.rollback()
        finally:
            try:
                self.db.close()
            except Exception:
                pass

    def get_recent_transcripts(self, max_lines: int = 10) -> List[Dict]:
        """Get the most recent transcripts."""
        return list(self.transcripts)[-max_lines:]

    def get_statistics(self) -> Dict:
        """Get session statistics."""
        elapsed = 0
        if self.session_start:
            elapsed = time.time() - self.session_start

        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'partner_id': self.partner_id,
            'conversation_id': self.conversation_id,
            'is_running': self.is_running,
            'elapsed_seconds': elapsed,
            'elapsed_formatted': self.format_timestamp(elapsed),
            'message_count': self.message_count,
            'transcript_count': len(self.transcripts)
        }


class SessionManager:
    """Manages multiple conversation sessions."""

    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.loops: Dict[str, asyncio.AbstractEventLoop] = {}
        self.threads: Dict[str, threading.Thread] = {}

    def create_session(
        self,
        session_id: str,
        user_id: int,
        partner_id: int,
        deepgram_api_key: str,
        db: Session
    ) -> Optional[ConversationSession]:
        """
        Create and start a new conversation session.

        Args:
            session_id: Unique session identifier
            user_id: User ID
            partner_id: Conversation partner ID
            deepgram_api_key: Deepgram API key for transcription
            db: Database session

        Returns:
            ConversationSession instance or None if failed
        """
        if session_id in self.sessions:
            logger.warning(f"Session {session_id} already exists")
            return None

        try:
            # Create new conversation in database
            conversation = Conversation(
                id=get_next_id(db, Conversation),
                user_id=user_id,
                partner_id=partner_id,
                title=f"Session {session_id}",
                started_at=datetime.now(timezone.utc),
                is_analyzed=False
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            logger.info(f"Created conversation {conversation.id} for session {session_id}")

            # Create session
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id,
                partner_id=partner_id,
                conversation_id=conversation.id,
                deepgram_api_key=deepgram_api_key,
                db_factory=SessionLocal
            )

            session.loop = asyncio.new_event_loop()

            # Start session in background
            def run_loop():
                asyncio.set_event_loop(session.loop)
                try:
                    session.loop.run_until_complete(session.start_async())
                finally:
                    session.loop.close()

            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()
            session.thread = thread

            # Give it a moment to start
            time.sleep(1)

            self.sessions[session_id] = session
            self.loops[session_id] = session.loop
            self.threads[session_id] = thread

            logger.info(f"Session {session_id} started successfully")

            return session

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            db.rollback()
            return None

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get an existing session."""
        return self.sessions.get(session_id)

    def stop_session(self, session_id: str) -> bool:
        """
        Stop a session.

        Args:
            session_id: Session ID to stop

        Returns:
            True if stopped successfully, False otherwise
        """
        session = self.sessions.get(session_id)

        if not session:
            logger.warning(f"Session {session_id} not found")
            return False

        try:
            session.stop()

            thread = self.threads.get(session_id)
            if thread and thread.is_alive():
                thread.join(timeout=5)

            # Remove from tracking
            del self.sessions[session_id]
            if session_id in self.loops:
                del self.loops[session_id]
            if session_id in self.threads:
                del self.threads[session_id]

            logger.info(f"Session {session_id} stopped and removed")
            return True

        except Exception as e:
            logger.error(f"Error stopping session {session_id}: {e}")
            return False

    def get_all_sessions(self) -> List[Dict]:
        """Get statistics for all active sessions."""
        return [session.get_statistics() for session in self.sessions.values()]

    def stop_all_sessions(self):
        """Stop all active sessions."""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            self.stop_session(session_id)


# Global session manager instance
session_manager = SessionManager()
