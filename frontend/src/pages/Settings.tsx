import { Settings as SettingsIcon, Database, Mic, Brain, Phone } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function Settings() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight" data-testid="text-title">
          Settings
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Configure your conversation memory assistant
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Database className="w-5 h-5" />
            API Integrations
          </CardTitle>
          <CardDescription>
            Connected services and API status
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-3 border rounded-md">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <div>
                <p className="font-medium text-sm">Face Recognition</p>
                <p className="text-xs text-muted-foreground">Client-side face matching</p>
              </div>
            </div>
            <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:bg-green-500/20 dark:text-green-400">
              Active
            </Badge>
          </div>

          <div className="flex items-center justify-between p-3 border rounded-md">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <div>
                <p className="font-medium text-sm">NLP Summary (Gemini)</p>
                <p className="text-xs text-muted-foreground">AI-powered conversation analysis</p>
              </div>
            </div>
            <Badge variant="outline" className="bg-green-500/10 text-green-700 dark:bg-green-500/20 dark:text-green-400">
              Active
            </Badge>
          </div>

          <div className="flex items-center justify-between p-3 border rounded-md">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              <div>
                <p className="font-medium text-sm">Voice Feedback (ElevenLabs)</p>
                <p className="text-xs text-muted-foreground">Text-to-speech synthesis</p>
              </div>
            </div>
            <Badge variant="outline" className="bg-yellow-500/10 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400">
              Configured
            </Badge>
          </div>

          <div className="flex items-center justify-between p-3 border rounded-md">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              <div>
                <p className="font-medium text-sm">Call System (Vapi)</p>
                <p className="text-xs text-muted-foreground">Outbound voice calls</p>
              </div>
            </div>
            <Badge variant="outline" className="bg-yellow-500/10 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400">
              Future
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Features
          </CardTitle>
          <CardDescription>
            Enable or disable conversation features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="live-transcription" className="font-medium">
                Live Transcription
              </Label>
              <p className="text-sm text-muted-foreground">
                Enable real-time speech-to-text during conversations
              </p>
            </div>
            <Switch id="live-transcription" defaultChecked data-testid="switch-transcription" />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-followup" className="font-medium">
                Auto LinkedIn Follow-up
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically suggest LinkedIn connections after meetings
              </p>
            </div>
            <Switch id="auto-followup" data-testid="switch-followup" />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="voice-debrief" className="font-medium">
                Voice Debrief Calls
              </Label>
              <p className="text-sm text-muted-foreground">
                Receive AI-generated voice feedback after conversations
              </p>
            </div>
            <Switch id="voice-debrief" defaultChecked data-testid="switch-debrief" />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="sentiment-analysis" className="font-medium">
                Sentiment Analysis
              </Label>
              <p className="text-sm text-muted-foreground">
                Analyze emotional tone of conversations
              </p>
            </div>
            <Switch id="sentiment-analysis" defaultChecked data-testid="switch-sentiment" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Database Schema
          </CardTitle>
          <CardDescription>
            Data model structure for conversation memory
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm font-mono bg-muted/50 p-4 rounded-md">
            <div>
              <span className="text-primary font-semibold">Person</span> → Conversation → Summary
            </div>
            <div className="pl-4 text-muted-foreground">
              ├─ id, name, photo, company, school
            </div>
            <div className="pl-4 text-muted-foreground">
              ├─ experiences, hobbies, contacts
            </div>
            <div className="pl-4 text-muted-foreground">
              └─ lastLocation, lastMeetingDate
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
