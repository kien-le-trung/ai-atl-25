#!/usr/bin/env python3
"""
Meta Glasses CLI - Command-line interface for Meta glasses integration
with conversation tracking and face recognition.

This tool allows you to:
1. Start OBS Virtual Camera (Meta glasses feed)
2. Capture faces and identify/create partners
3. Start conversation sessions with live transcription
4. Analyze conversations and build profiles
"""
import sys
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.camera_service import CameraService
from app.services.session_service import session_manager
from app.services.profile_service import ProfileBuilder
from app.models.user import User
from app.models.conversation_partner import ConversationPartner
from app.models.conversation import Conversation


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def list_cameras():
    """List available cameras."""
    print_header("Available Cameras")

    camera = CameraService()

    for i in range(10):
        import cv2
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                print(f"  [{i}] Camera {i} - {width}x{height} @ {fps}fps")
            cap.release()


def start_camera_interactive():
    """Start camera with interactive selection."""
    print_header("Start Camera")

    # List cameras
    list_cameras()

    # Get user input
    camera_index = input("\nEnter camera index (or press Enter for auto-detect): ").strip()

    if camera_index:
        camera_index = int(camera_index)
    else:
        camera_index = None

    # Start camera
    camera = CameraService()
    success = camera.start_camera(camera_index)

    if success:
        print(f"\n✅ Camera {camera.camera_index} started successfully!")
        print("Press 'q' to stop the camera preview")

        # Show preview
        import cv2
        while True:
            frame = camera.capture_frame()
            if frame is not None:
                cv2.imshow("Camera Preview", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        cv2.destroyAllWindows()
        camera.stop_camera()
    else:
        print("\n❌ Failed to start camera")


def capture_face_interactive(user_id: int):
    """Capture and identify face interactively."""
    print_header("Capture Face")

    db = SessionLocal()

    try:
        # Start camera
        camera = CameraService()
        if not camera.start_camera():
            print("❌ Failed to start camera")
            return

        print("\n✅ Camera started")
        print("Press SPACE to capture face, or 'q' to cancel")

        # Show preview
        import cv2
        while True:
            frame = camera.capture_frame()
            if frame is not None:
                # Add instruction overlay
                cv2.putText(frame, "Press SPACE to capture face", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Face Capture", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):  # Space bar
                print("\n📸 Capturing face...")

                result = camera.capture_and_identify_face()

                if result is None:
                    print("❌ No face detected")
                    continue

                face_img, embedding, face_info = result

                # Save face
                import uuid
                filename = f"captured_face_{uuid.uuid4()}.jpg"
                face_path = camera.save_face_image(face_img, filename)

                print(f"✅ Face detected: {face_info['w']}x{face_info['h']}")

                # Search for similar faces
                from app.services.face_service import find_similar_faces
                similar_faces = find_similar_faces(
                    image_path=face_path,
                    db=db,
                    threshold=0.6,
                    top_k=1
                )

                if similar_faces and len(similar_faces) > 0:
                    partner, similarity = similar_faces[0]
                    print(f"\n✅ Identified existing partner:")
                    print(f"   Name: {partner.name}")
                    print(f"   ID: {partner.id}")
                    print(f"   Similarity: {similarity:.2%}")

                    # Update partner's image
                    partner.image_path = face_path
                    partner.image_embedding = embedding
                    db.commit()

                    break
                else:
                    # Create new partner
                    name = input("\n👤 Enter partner name: ").strip()
                    if not name:
                        name = f"Unknown Person {uuid.uuid4().hex[:8]}"

                    new_partner = ConversationPartner(
                        user_id=user_id,
                        name=name,
                        image_path=face_path,
                        image_embedding=embedding
                    )

                    db.add(new_partner)
                    db.commit()
                    db.refresh(new_partner)

                    print(f"\n✅ Created new partner:")
                    print(f"   Name: {new_partner.name}")
                    print(f"   ID: {new_partner.id}")

                    break

            elif key == ord('q'):
                print("\n❌ Cancelled")
                break

        cv2.destroyAllWindows()
        camera.stop_camera()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def start_session_interactive(user_id: int):
    """Start a conversation session interactively."""
    print_header("Start Conversation Session")

    db = SessionLocal()

    try:
        # List partners
        partners = db.query(ConversationPartner).filter(
            ConversationPartner.user_id == user_id
        ).all()

        if not partners:
            print("\n❌ No partners found. Create a partner first.")
            return

        print("\nAvailable partners:")
        for i, partner in enumerate(partners, 1):
            print(f"  [{i}] {partner.name} (ID: {partner.id})")

        # Select partner
        choice = int(input("\nSelect partner number: ")) - 1
        partner = partners[choice]

        # Get Deepgram API key
        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        if not deepgram_key:
            deepgram_key = input("\nEnter Deepgram API key: ").strip()

        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())

        # Create session
        print(f"\n🎙️ Starting session with {partner.name}...")

        session = session_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            partner_id=partner.id,
            deepgram_api_key=deepgram_key,
            db=db
        )

        if session is None:
            print("❌ Failed to create session")
            return

        print(f"✅ Session started (ID: {session_id})")
        print(f"📊 Conversation ID: {session.conversation_id}")
        print("\n🎤 Speak into your microphone...")
        print("Press Enter to stop the session")

        # Wait for user to stop
        input()

        # Stop session
        print("\n⏹️ Stopping session...")
        session_manager.stop_session(session_id)

        stats = session.get_statistics()
        print(f"\n✅ Session ended")
        print(f"   Duration: {stats['elapsed_formatted']}")
        print(f"   Messages: {stats['message_count']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def analyze_conversation_interactive():
    """Analyze a conversation interactively."""
    print_header("Analyze Conversation")

    db = SessionLocal()

    try:
        # List unanalyzed conversations
        conversations = db.query(Conversation).filter(
            Conversation.is_analyzed == False
        ).order_by(Conversation.started_at.desc()).limit(10).all()

        if not conversations:
            print("\n❌ No unanalyzed conversations found")
            return

        print("\nUnanalyzed conversations:")
        for i, conv in enumerate(conversations, 1):
            partner = db.query(ConversationPartner).filter(
                ConversationPartner.id == conv.partner_id
            ).first()
            print(f"  [{i}] ID {conv.id} - {partner.name if partner else 'Unknown'} - {conv.started_at}")

        # Select conversation
        choice = int(input("\nSelect conversation number: ")) - 1
        conversation = conversations[choice]

        # Get Gemini API key
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            gemini_key = input("\nEnter Gemini API key: ").strip()

        # Analyze
        print(f"\n🔍 Analyzing conversation {conversation.id}...")

        builder = ProfileBuilder(gemini_api_key=gemini_key)
        result = builder.analyze_conversation(conversation.id, db)

        print(f"\n✅ Analysis complete!")
        print(f"   Facts extracted: {result['facts_extracted']}")
        print(f"   Topics identified: {result['topics_identified']}")
        print(f"\n📝 Summary:")
        print(f"   {result['summary']}")

        if result['topics']:
            print(f"\n🏷️ Topics: {', '.join(result['topics'])}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def view_profile_interactive():
    """View partner profile interactively."""
    print_header("View Partner Profile")

    db = SessionLocal()

    try:
        # List partners
        partners = db.query(ConversationPartner).all()

        if not partners:
            print("\n❌ No partners found")
            return

        print("\nPartners:")
        for i, partner in enumerate(partners, 1):
            convs = db.query(Conversation).filter(
                Conversation.partner_id == partner.id,
                Conversation.is_analyzed == True
            ).count()
            print(f"  [{i}] {partner.name} - {convs} analyzed conversations")

        # Select partner
        choice = int(input("\nSelect partner number: ")) - 1
        partner = partners[choice]

        # Get Gemini API key
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            gemini_key = input("\nEnter Gemini API key: ").strip()

        # Build profile
        print(f"\n📊 Building profile for {partner.name}...")

        builder = ProfileBuilder(gemini_api_key=gemini_key)
        profile = builder.build_partner_profile(partner.id, db)

        print(f"\n✅ Profile for {profile['partner_name']}")
        print(f"\n📈 Statistics:")
        print(f"   Conversations: {profile['statistics']['total_conversations']}")
        print(f"   Messages: {profile['statistics']['total_messages']}")
        print(f"   Facts: {profile['statistics']['total_facts']}")
        print(f"   Topics: {profile['statistics']['topics_count']}")

        print(f"\n💡 Facts by Category:")
        for category, facts in profile['facts'].items():
            print(f"\n   {category.replace('_', ' ').title()}: ({len(facts)} facts)")
            for fact in facts[:3]:  # Show first 3
                print(f"      • {fact['key']}: {fact['value']}")

        if profile['topics']:
            print(f"\n🏷️ Topics: {', '.join(profile['topics'][:10])}")

        # Get insights
        print(f"\n🤖 Generating conversation suggestions...")
        insights = builder.get_conversation_insights(partner.id, db)

        if insights['suggestions']:
            print(f"\n💬 Suggested Topics:")
            for i, suggestion in enumerate(insights['suggestions'], 1):
                print(f"   {i}. {suggestion}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Meta Glasses CLI - Conversation tracking with face recognition"
    )

    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="User ID (default: 1)"
    )

    args = parser.parse_args()

    print_header("Meta Glasses CLI")
    print(f"User ID: {args.user_id}")

    while True:
        print("\n" + "-" * 70)
        print("Options:")
        print("  [1] List cameras")
        print("  [2] Start camera preview")
        print("  [3] Capture and identify face")
        print("  [4] Start conversation session")
        print("  [5] Analyze conversation")
        print("  [6] View partner profile")
        print("  [q] Quit")
        print("-" * 70)

        choice = input("\nSelect option: ").strip().lower()

        if choice == '1':
            list_cameras()
        elif choice == '2':
            start_camera_interactive()
        elif choice == '3':
            capture_face_interactive(args.user_id)
        elif choice == '4':
            start_session_interactive(args.user_id)
        elif choice == '5':
            analyze_conversation_interactive()
        elif choice == '6':
            view_profile_interactive()
        elif choice == 'q':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option")


if __name__ == "__main__":
    main()
