import { useQuery } from "@tanstack/react-query";
import { useRoute } from "wouter";
import { ArrowLeft, Linkedin, Mail, Phone, MapPin, Calendar, Briefcase, GraduationCap, Heart, User as UserIcon, ExternalLink, Copy } from "lucide-react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import type { ConversationWithPerson, ConversationDetail, FollowUpAction } from "@shared/schema";

export default function ConversationDetail() {
  const [, params] = useRoute("/conversation/:id");
  const conversationId = params?.id;
  const { toast } = useToast();

  const { data: conversation, isLoading: conversationLoading } = useQuery<ConversationWithPerson>({
    queryKey: ["/api/conversations", conversationId],
    queryFn: async () => {
      const response = await fetch(`/api/conversations/${conversationId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch conversation");
      }
      return response.json();
    },
    enabled: !!conversationId,
  });

  const { data: details } = useQuery<ConversationDetail>({
    queryKey: ["/api/conversation-details", conversationId],
    queryFn: async () => {
      const response = await fetch(`/api/conversation-details/${conversationId}`);
      if (!response.ok) {
        return null; // Details might not exist yet
      }
      return response.json();
    },
    enabled: !!conversationId,
  });

  const { data: followUps } = useQuery<FollowUpAction[]>({
    queryKey: ["/api/conversations", conversationId, "follow-ups"],
    queryFn: async () => {
      const response = await fetch(`/api/conversations/${conversationId}/follow-ups`);
      if (!response.ok) {
        return [];
      }
      return response.json();
    },
    enabled: !!conversationId,
  });

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: `${type} copied successfully`,
    });
  };

  if (conversationLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Card>
          <CardHeader className="flex flex-row items-center gap-4">
            <Skeleton className="w-20 h-20 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-3">
          <p className="text-lg text-muted-foreground">Conversation not found</p>
          <Link href="/">
            <Button variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const { person } = conversation;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" size="icon" data-testid="button-back">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight" data-testid="text-title">
            Conversation Detail
          </h1>
          <p className="text-sm text-muted-foreground">
            View extracted information and conversation history
          </p>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-4">
              <Avatar className="w-20 h-20" data-testid="avatar-person">
                <AvatarImage src={person.photoUrl || undefined} />
                <AvatarFallback className="bg-primary/10 text-primary text-2xl">
                  <UserIcon className="w-8 h-8" />
                </AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <h2 className="text-2xl font-semibold" data-testid="text-person-name">
                  {person.name}
                </h2>
                <p className="text-muted-foreground" data-testid="text-person-affiliation">
                  {person.company || person.school || "No affiliation"}
                </p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="w-4 h-4" />
                  <span data-testid="text-meeting-date">
                    {person.lastMeetingDate
                      ? new Date(person.lastMeetingDate).toLocaleDateString()
                      : new Date(conversation.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
            <Badge
              className={conversation.status === "matched" ? "bg-green-500/10 text-green-700 dark:bg-green-500/20 dark:text-green-400" : "bg-orange-500/10 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400"}
              data-testid="badge-status"
            >
              {conversation.status === "matched" ? "Matched via photo" : "New entry created"}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Extracted Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {details?.school && (
              <div className="flex items-start gap-3">
                <GraduationCap className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">School</p>
                  <p className="text-base" data-testid="text-school">{details.school}</p>
                </div>
              </div>
            )}

            {details?.company && (
              <div className="flex items-start gap-3">
                <Briefcase className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">Company</p>
                  <p className="text-base" data-testid="text-company">{details.company}</p>
                </div>
              </div>
            )}

            {details?.experiences && (
              <div className="flex items-start gap-3">
                <Briefcase className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">Experiences</p>
                  <p className="text-base" data-testid="text-experiences">{details.experiences}</p>
                </div>
              </div>
            )}

            {details?.hobbies && (
              <div className="flex items-start gap-3">
                <Heart className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">Hobbies</p>
                  <p className="text-base" data-testid="text-hobbies">{details.hobbies}</p>
                </div>
              </div>
            )}

            {details?.contacts && (
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">Contacts</p>
                  <p className="text-base" data-testid="text-contacts">{details.contacts}</p>
                </div>
              </div>
            )}

            {conversation.location && (
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted-foreground">Location</p>
                  <p className="text-base" data-testid="text-location">{conversation.location}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">AI Summary & Highlights</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">Summary</p>
              <p className="text-base leading-relaxed" data-testid="text-ai-summary">
                {conversation.summary || "No summary available yet. The AI will analyze the conversation and generate insights."}
              </p>
            </div>

            {conversation.transcript && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Transcript Highlights</p>
                <div className="bg-muted/50 p-4 rounded-md max-h-64 overflow-y-auto">
                  <p className="text-sm font-mono whitespace-pre-wrap" data-testid="text-transcript">
                    {conversation.transcript}
                  </p>
                </div>
              </div>
            )}

            {conversation.topics && conversation.topics.length > 0 && (
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Topics Discussed</p>
                <div className="flex flex-wrap gap-2">
                  {conversation.topics.map((topic: string, i: number) => (
                    <Badge key={i} variant="outline" data-testid={`badge-topic-${i}`}>
                      {topic}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {followUps && followUps.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Drafted Follow-Ups</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              AI-generated messages ready for you to review and send
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {followUps.map((action) => (
              <div key={action.id} className="border rounded-lg p-4 space-y-3" data-testid={`followup-${action.type}`}>
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-2">
                    {action.type === "email" ? (
                      <Mail className="w-5 h-5 text-primary" />
                    ) : (
                      <Linkedin className="w-5 h-5 text-primary" />
                    )}
                    <div>
                      <h3 className="font-semibold" data-testid={`text-followup-${action.type}-subject`}>
                        {action.subject}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {action.type === "email" ? "Follow-up Email" : "LinkedIn Connection"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {action.recipientLinkedIn && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(action.recipientLinkedIn!, "_blank")}
                        data-testid={`button-open-linkedin-${action.type}`}
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        Open LinkedIn
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(action.content, action.type === "email" ? "Email" : "LinkedIn message")}
                      data-testid={`button-copy-${action.type}`}
                    >
                      <Copy className="w-4 h-4 mr-1" />
                      Copy
                    </Button>
                  </div>
                </div>

                {action.recipientEmail && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground" data-testid={`text-email-${action.type}`}>
                      {action.recipientEmail}
                    </span>
                  </div>
                )}

                <div className="bg-muted/50 p-4 rounded-md">
                  <pre className="text-sm whitespace-pre-wrap font-sans" data-testid={`text-followup-${action.type}-content`}>
                    {action.content}
                  </pre>
                </div>

                <Badge variant="outline" className="w-fit">
                  Status: {action.status}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-3">
            <Button data-testid="button-linkedin-action">
              <Linkedin className="w-4 h-4 mr-2" />
              View LinkedIn
            </Button>
            <Button variant="outline" data-testid="button-followup-action">
              <Mail className="w-4 h-4 mr-2" />
              Send Follow-up
            </Button>
            <Button variant="outline" data-testid="button-debrief-action">
              <Phone className="w-4 h-4 mr-2" />
              Voice Debrief Call
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
