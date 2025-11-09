import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Plus, Users, TrendingUp, Target, Video } from "lucide-react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PhotoCaptureModal } from "@/components/PhotoCaptureModal";
import { LiveSession } from "@/components/LiveSession";
import { ConversationCard } from "@/components/ConversationCard";
import { useToast } from "@/hooks/use-toast";
import { queryClient, apiRequest } from "@/lib/queryClient";
import type { ConversationWithPerson } from "@shared/schema";

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const [photoModalOpen, setPhotoModalOpen] = useState(false);
  const [liveSessionOpen, setLiveSessionOpen] = useState(false);
  const { toast } = useToast();

  const { data: conversations, isLoading } = useQuery<ConversationWithPerson[]>({
    queryKey: ["/api/conversations"],
  });

  const { data: stats } = useQuery<{
    total: number;
    thisWeek: number;
    recognitionAccuracy: number;
  }>({
    queryKey: ["/api/stats"],
  });

  const photoUploadMutation = useMutation({
    mutationFn: async ({ file, name, location }: { file: File; name: string; location: string }) => {
      const formData = new FormData();
      formData.append("photo", file);
      formData.append("name", name || `Person ${Date.now()}`);
      formData.append("location", location || "Unknown");

      const response = await fetch("/api/photo-upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload photo");
      }

      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["/api/conversations"] });
      queryClient.invalidateQueries({ queryKey: ["/api/stats"] });
      
      toast({
        title: data.isMatch ? "Match Found!" : "New Contact Created",
        description: data.message,
      });

      if (data.conversation) {
        setLocation(`/conversation/${data.conversation.id}`);
      }
    },
    onError: (error) => {
      toast({
        title: "Upload Failed",
        description: "Failed to process photo. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handlePhotoCapture = async (file: File, name: string, location: string) => {
    photoUploadMutation.mutate({ file, name, location });
  };

  const createDemoConversation = useMutation({
    mutationFn: async () => {
      // Create a sample person
      const personResponse = await apiRequest("POST", "/api/persons", {
        name: "Sarah Johnson",
        company: "TechCorp",
        school: "Stanford University",
        email: "sarah.j@techcorp.com",
      });

      const person = await personResponse.json();

      // Create a conversation
      const conversationResponse = await apiRequest("POST", "/api/conversations", {
        personId: person.id,
        location: "Tech Conference 2025",
      });

      const conversation = await conversationResponse.json();

      // Analyze the conversation with a sample transcript
      const transcript = `We discussed the future of AI in education and how machine learning can personalize learning experiences. Sarah mentioned her work at TechCorp on adaptive learning platforms and shared her passion for making education more accessible. She talked about her time at Stanford studying computer science and her interest in rock climbing and photography. We exchanged contact information and agreed to collaborate on a potential project.`;

      await apiRequest("POST", `/api/conversations/${conversation.id}/analyze`, {
        transcript,
      });

      return conversation.id;
    },
    onSuccess: (conversationId) => {
      queryClient.invalidateQueries({ queryKey: ["/api/conversations"] });
      queryClient.invalidateQueries({ queryKey: ["/api/stats"] });
      queryClient.invalidateQueries({ queryKey: ["/api/insights"] });
      
      toast({
        title: "Demo Conversation Created",
        description: "AI analysis complete! View the conversation details.",
      });

      setLocation(`/conversation/${conversationId}`);
    },
    onError: () => {
      toast({
        title: "Failed to Create Demo",
        description: "Could not create demo conversation.",
        variant: "destructive",
      });
    },
  });

  return (
    <div className="space-y-8 w-full">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-black tracking-tight" data-testid="text-title">
            DASHBOARD
          </h1>
          <p className="text-muted-foreground text-sm mt-1 font-semibold">
            Manage your conversation memories and insights
          </p>
        </div>
        <div className="flex gap-3 flex-wrap">
          <Button 
            onClick={() => setLiveSessionOpen(true)}
            data-testid="button-live-session"
            size="lg"
            className="rounded-2xl bg-black dark:bg-white text-white dark:text-black border-4 border-black dark:border-white font-bold shadow-brutal hover-elevate active-elevate-2"
          >
            <Video className="w-5 h-5 mr-2" />
            <span className="whitespace-nowrap">Start Live Session</span>
          </Button>
          <Button 
            variant="outline" 
            onClick={() => createDemoConversation.mutate()}
            disabled={createDemoConversation.isPending}
            data-testid="button-demo-conversation"
            className="rounded-2xl border-4 border-black dark:border-white font-bold shadow-brutal hover-elevate active-elevate-2"
          >
            {createDemoConversation.isPending ? "Creating..." : "Demo"}
          </Button>
          <Button variant="outline" onClick={() => setPhotoModalOpen(true)} data-testid="button-new-conversation" className="rounded-2xl border-4 border-black dark:border-white font-bold shadow-brutal hover-elevate active-elevate-2">
            <Plus className="w-4 h-4 mr-2" />
            <span className="whitespace-nowrap">Upload Photo</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-4 border-black dark:border-white rounded-2xl shadow-brutal bg-white dark:bg-gray-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase">Total Conversations</CardTitle>
            <Users className="w-5 h-5" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black" data-testid="text-total-conversations">
              {stats?.total ?? 0}
            </div>
            <p className="text-xs font-semibold text-muted-foreground mt-1">
              All time
            </p>
          </CardContent>
        </Card>

        <Card className="border-4 border-black dark:border-white rounded-2xl shadow-brutal bg-white dark:bg-gray-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase">New This Week</CardTitle>
            <TrendingUp className="w-5 h-5" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black" data-testid="text-week-conversations">
              {stats?.thisWeek ?? 0}
            </div>
            <p className="text-xs font-semibold text-muted-foreground mt-1">
              Last 7 days
            </p>
          </CardContent>
        </Card>

        <Card className="border-4 border-black dark:border-white rounded-2xl shadow-brutal bg-white dark:bg-gray-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-bold uppercase">Recognition Accuracy</CardTitle>
            <Target className="w-5 h-5" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-black" data-testid="text-accuracy">
              {stats?.recognitionAccuracy ?? 0}%
            </div>
            <p className="text-xs font-semibold text-muted-foreground mt-1">
              Face matching rate
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-black uppercase">Recent Conversations</h2>
        
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-4 border-4 border-black dark:border-white rounded-2xl shadow-brutal bg-white dark:bg-gray-900">
                <div className="flex gap-4">
                  <Skeleton className="w-12 h-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-5 w-1/3" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : conversations && conversations.length > 0 ? (
          <div className="space-y-4">
            {conversations.map((conversation) => (
              <ConversationCard
                key={conversation.id}
                conversation={conversation}
                onViewDetail={(id) => setLocation(`/conversation/${id}`)}
              />
            ))}
          </div>
        ) : (
          <Card className="p-12 border-4 border-black dark:border-white rounded-2xl shadow-brutal bg-white dark:bg-gray-900">
            <div className="text-center space-y-4">
              <Users className="w-16 h-16 mx-auto text-muted-foreground" />
              <h3 className="text-2xl font-black uppercase">No Conversations Yet</h3>
              <p className="text-sm font-semibold text-muted-foreground max-w-sm mx-auto">
                Start by capturing a photo to identify someone and begin tracking your conversations
              </p>
              <Button onClick={() => setPhotoModalOpen(true)} data-testid="button-start-conversation" className="rounded-2xl border-4 border-black dark:border-white font-bold shadow-brutal hover-elevate active-elevate-2">
                <Plus className="w-4 h-4 mr-2" />
                Start First Conversation
              </Button>
            </div>
          </Card>
        )}
      </div>

      <PhotoCaptureModal
        open={photoModalOpen}
        onOpenChange={setPhotoModalOpen}
        onPhotoCapture={handlePhotoCapture}
      />

      <LiveSession
        open={liveSessionOpen}
        onOpenChange={setLiveSessionOpen}
        onSessionComplete={(conversationId) => setLocation(`/conversation/${conversationId}`)}
      />
    </div>
  );
}
