import { useState, useRef, useEffect } from "react";
import { Camera, Mic, MicOff, StopCircle, User, MapPin } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { queryClient } from "@/lib/queryClient";

interface LiveSessionProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSessionComplete: (conversationId: string) => void;
}

export function LiveSession({ open, onOpenChange, onSessionComplete }: LiveSessionProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [location, setLocation] = useState("");
  const [name, setName] = useState("");
  const [photoBlob, setPhotoBlob] = useState<Blob | null>(null);
  const [hasPermissions, setHasPermissions] = useState(false);
  const [detectedLocation, setDetectedLocation] = useState("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);
  const isMutedRef = useRef(false);
  const isRecordingRef = useRef(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open && !hasPermissions) {
      startCamera();
      getLocation();
    }
    
    return () => {
      stopCamera();
      stopRecording();
    };
  }, [open]);

  // Extract names from transcript
  useEffect(() => {
    if (transcript) {
      // Simple name extraction - look for common patterns
      const namePatterns = [
        /(?:my name is|i'm|i am|this is|name's)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/gi,
        /(?:call me|they call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/gi,
        /^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:here|speaking)/gi
      ];
      
      for (const pattern of namePatterns) {
        const match = transcript.match(pattern);
        if (match) {
          const extractedName = match[1] || match[0].replace(pattern, '$1');
          if (extractedName && !name) {
            setName(extractedName.trim());
            break;
          }
        }
      }
    }
  }, [transcript]);

  const getLocation = async () => {
    if ("geolocation" in navigator) {
      try {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject);
        });
        
        // Try to get city name from coordinates using reverse geocoding
        const { latitude, longitude } = position.coords;
        
        // For now, just set a general location based on coordinates
        // In production, you'd use a geocoding API
        setLocation("Current Location");
        setDetectedLocation(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
        
        toast({
          title: "Location Detected",
          description: "Using your current location for this session",
        });
      } catch (error) {
        console.error("Error getting location:", error);
        setLocation("Meeting Location");
      }
    } else {
      setLocation("Meeting Location");
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: true,
      });
      
      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setHasPermissions(true);
      
      toast({
        title: "Camera & Microphone Active",
        description: "Ready to start recording conversation",
      });
    } catch (error) {
      console.error("Error accessing camera/microphone:", error);
      toast({
        title: "Permission Denied",
        description: "Please allow camera and microphone access to use live session",
        variant: "destructive",
      });
    }
  };

  const stopCamera = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          setPhotoBlob(blob);
          toast({
            title: "Face Captured",
            description: "Photo saved for person identification",
          });
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast({
        title: "Speech Recognition Not Supported",
        description: "Please use Chrome or Edge browser for live transcription",
        variant: "destructive",
      });
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsRecording(true);
      isRecordingRef.current = true;
      if (!isMutedRef.current) {
        toast({
          title: "Recording Started",
          description: "Speak naturally - conversation is being transcribed",
        });
      }
    };

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcriptPiece + ' ';
        } else {
          interim += transcriptPiece;
        }
      }

      if (final) {
        setTranscript(prev => prev + final);
        setInterimTranscript('');
      } else {
        setInterimTranscript(interim);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      if (event.error !== 'no-speech') {
        toast({
          title: "Transcription Error",
          description: "Speech recognition encountered an issue",
          variant: "destructive",
        });
      }
    };

    recognition.onend = () => {
      // Only auto-restart if we're still recording and not muted
      if (isRecordingRef.current && !isMutedRef.current) {
        recognition.start();
      }
    };

    recognitionRef.current = recognition;
    recognition.start();

    // Auto-capture photo after 2 seconds
    setTimeout(() => {
      if (!photoBlob) {
        capturePhoto();
      }
    }, 2000);
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      isRecordingRef.current = false;
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsRecording(false);
    setIsMuted(false);
    isMutedRef.current = false;
    setInterimTranscript('');
  };

  const toggleMute = () => {
    if (!isRecording) return;

    if (!isMuted) {
      // Mute: stop speech recognition
      isMutedRef.current = true;
      setIsMuted(true);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      toast({
        title: "Transcription Paused",
        description: "Speech recognition is now paused",
      });
    } else {
      // Unmute: restart speech recognition
      isMutedRef.current = false;
      setIsMuted(false);
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
      toast({
        title: "Transcription Resumed",
        description: "Speech recognition is active again",
      });
    }
  };

  const completeMutation = useMutation({
    mutationFn: async () => {
      if (!photoBlob) {
        throw new Error("No photo captured");
      }

      // Upload photo and create conversation
      const formData = new FormData();
      formData.append("photo", photoBlob, "face-capture.jpg");
      formData.append("name", name || `Person ${Date.now()}`);
      formData.append("location", location || "Live Session");

      const uploadResponse = await fetch("/api/photo-upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error("Failed to upload photo");
      }

      const uploadData = await uploadResponse.json();
      const conversationId = uploadData.conversation.id;

      // Analyze conversation with transcript
      if (transcript.trim()) {
        const analyzeResponse = await fetch(`/api/conversations/${conversationId}/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ transcript: transcript.trim() }),
        });

        if (!analyzeResponse.ok) {
          console.error("Failed to analyze conversation");
        }
      }

      // Initiate Vapi phone call
      try {
        const vapiResponse = await fetch("/api/vapi/call", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            conversationId,
            phoneNumberId: "5153ba09-d91b-446d-a1c8-b1db58439387",
            assistantId: "dced8a66-0b31-4e92-b41a-25ff274e32a8",
            customerNumber: "+14436367028", // 443-636-7028
          }),
        });

        if (vapiResponse.ok) {
          const vapiData = await vapiResponse.json();
          console.log("Vapi call initiated:", vapiData.callId);
          toast({
            title: "Phone Call Initiated",
            description: "Calling your phone with conversation debrief...",
          });
        } else {
          const errorData = await vapiResponse.json();
          console.error("Failed to initiate Vapi call:", errorData);
          toast({
            title: "Phone Call Failed",
            description: "Could not initiate follow-up call. Session still saved.",
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error("Vapi call error:", error);
        toast({
          title: "Phone Call Error",
          description: "Could not initiate follow-up call. Session still saved.",
          variant: "destructive",
        });
      }

      return conversationId;
    },
    onSuccess: (conversationId) => {
      queryClient.invalidateQueries({ queryKey: ["/api/conversations"] });
      queryClient.invalidateQueries({ queryKey: ["/api/stats"] });
      queryClient.invalidateQueries({ queryKey: ["/api/insights"] });

      toast({
        title: "Session Saved",
        description: "Conversation analyzed and saved successfully",
      });

      handleClose();
      onSessionComplete(conversationId);
    },
    onError: (error) => {
      toast({
        title: "Failed to Save Session",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    },
  });

  const handleComplete = () => {
    stopRecording();
    completeMutation.mutate();
  };

  const handleClose = () => {
    stopCamera();
    stopRecording();
    setTranscript("");
    setInterimTranscript("");
    setLocation("");
    setName("");
    setPhotoBlob(null);
    setHasPermissions(false);
    onOpenChange(false);
  };

  const canComplete = photoBlob && (transcript.trim().length > 0 || name.trim().length > 0);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto" data-testid="dialog-live-session">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">Live Conversation Session</DialogTitle>
          <DialogDescription>
            Camera and microphone are active - speak naturally while we transcribe and identify
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Video Preview */}
          <div className="relative bg-muted rounded-md overflow-hidden" style={{ aspectRatio: '16/9' }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
              data-testid="video-preview"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {photoBlob && (
              <Badge className="absolute top-2 right-2 bg-green-500/90 text-white">
                Face Captured
              </Badge>
            )}

            {isRecording && (
              <Badge className="absolute top-2 left-2 bg-red-500/90 text-white animate-pulse">
                Recording
              </Badge>
            )}
          </div>

          {/* Controls */}
          <div className="flex justify-center gap-3">
            {!isRecording ? (
              <Button
                onClick={startRecording}
                disabled={!hasPermissions}
                data-testid="button-start-recording"
                size="lg"
              >
                <Mic className="w-5 h-5 mr-2" />
                Start Recording
              </Button>
            ) : (
              <>
                <Button
                  onClick={toggleMute}
                  variant="outline"
                  data-testid="button-toggle-mute"
                >
                  {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </Button>
                <Button
                  onClick={stopRecording}
                  variant="destructive"
                  data-testid="button-stop-recording"
                >
                  <StopCircle className="w-5 h-5 mr-2" />
                  Stop Recording
                </Button>
              </>
            )}
          </div>

          {/* Transcript Display */}
          <Card className="p-4 min-h-[150px] max-h-[200px] overflow-y-auto">
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Live Transcript</Label>
              {transcript || interimTranscript ? (
                <div className="text-sm leading-relaxed space-y-1">
                  <p className="text-foreground" data-testid="text-transcript">
                    {transcript}
                  </p>
                  {interimTranscript && (
                    <p className="text-muted-foreground italic" data-testid="text-interim-transcript">
                      {interimTranscript}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground italic">
                  Start recording to see live transcription...
                </p>
              )}
            </div>
          </Card>

          {/* Auto-detected Information */}
          {(name || location) && (
            <Card className="p-3 bg-muted/50">
              <div className="flex items-center gap-4 text-sm">
                {name && (
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="font-medium">Person: {name}</span>
                  </div>
                )}
                {location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-muted-foreground" />
                    <span className="font-medium">{location}</span>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={handleClose} data-testid="button-cancel-session">
              Cancel
            </Button>
            <Button
              onClick={handleComplete}
              disabled={!canComplete || completeMutation.isPending}
              data-testid="button-complete-session"
            >
              {completeMutation.isPending ? "Saving..." : "Complete & Analyze"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
