import { formatDistanceToNow } from "date-fns";
import { User, Calendar, MapPin, Volume2, Linkedin, Mail } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { ConversationWithPerson } from "@shared/schema";
import { useLocation } from "wouter";

interface ConversationCardProps {
  conversation: ConversationWithPerson;
  onViewDetail?: (id: string) => void;
}

export function ConversationCard({ conversation, onViewDetail }: ConversationCardProps) {
  const [, setLocation] = useLocation();
  const { person } = conversation;
  const statusColor = conversation.status === "matched" ? "bg-green-500/10 text-green-700 dark:bg-green-500/20 dark:text-green-400" : "bg-orange-500/10 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400";
  const statusText = conversation.status === "matched" ? "Match Found" : "New Contact";
  
  const hasFollowUps = conversation.vapiCallStatus === "ended" && conversation.vapiCallEndedAt;
  
  const handleViewDetail = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLocation(`/conversation/${conversation.id}`);
  };

  return (
    <Card className="p-4 border-4 border-black dark:border-white rounded-2xl shadow-brutal hover-elevate active-elevate-2 transition-all cursor-pointer bg-white dark:bg-gray-900 w-full" onClick={() => onViewDetail?.(conversation.id)} data-testid={`card-conversation-${conversation.id}`}>
      <div className="flex gap-4">
        <Avatar className="w-14 h-14 flex-shrink-0 border-2 border-black dark:border-white bg-white dark:bg-gray-900" data-testid={`avatar-${person.id}`}>
          <AvatarImage 
            src={person.photoUrl || undefined} 
            className="object-cover object-center"
            alt={person.name}
          />
          <AvatarFallback className="bg-gray-200 dark:bg-gray-700 text-black dark:text-white font-bold">
            <User className="w-6 h-6" />
          </AvatarFallback>
        </Avatar>

        <div className="flex-1 min-w-0 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0 pr-2">
              <h3 className="font-black text-lg truncate" data-testid={`text-name-${conversation.id}`}>
                {person.name}
              </h3>
              <p className="text-sm font-semibold text-muted-foreground truncate" data-testid={`text-company-${conversation.id}`}>
                {person.company || person.school || "No affiliation"}
              </p>
            </div>
            <Badge className={`${statusColor} flex-shrink-0 text-xs px-3 py-1 border-2 border-black dark:border-white font-bold rounded-full`} data-testid={`badge-status-${conversation.id}`}>
              {statusText}
            </Badge>
          </div>

          <p className="text-sm text-foreground/80 line-clamp-2 break-words" data-testid={`text-summary-${conversation.id}`}>
            {conversation.summary || "No summary available yet"}
          </p>

          <div className="flex items-center gap-4 text-xs font-semibold text-muted-foreground flex-wrap">
            <div className="flex items-center gap-1 flex-shrink-0">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              <span data-testid={`text-date-${conversation.id}`} className="whitespace-nowrap">
                {formatDistanceToNow(new Date(conversation.createdAt), { addSuffix: true })}
              </span>
            </div>
            {conversation.location && (
              <div className="flex items-center gap-1 flex-shrink-0">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span className="truncate max-w-[150px]">{conversation.location}</span>
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-2 flex-wrap">
            <Button size="sm" onClick={handleViewDetail} data-testid={`button-detail-${conversation.id}`} className="text-xs rounded-xl bg-black dark:bg-white text-white dark:text-black border-4 border-black dark:border-white font-bold shadow-brutal-xs">
              View Detail
            </Button>
            {hasFollowUps && (
              <>
                <Button size="sm" onClick={handleViewDetail} data-testid={`button-linkedin-${conversation.id}`} className="text-xs rounded-xl bg-white dark:bg-black text-black dark:text-white border-4 border-black dark:border-white font-bold shadow-brutal-xs">
                  <Linkedin className="w-3 h-3 mr-1" />
                  <span className="hidden sm:inline">LinkedIn</span>
                </Button>
                <Button size="sm" onClick={handleViewDetail} data-testid={`button-followup-${conversation.id}`} className="text-xs rounded-xl bg-white dark:bg-black text-black dark:text-white border-4 border-black dark:border-white font-bold shadow-brutal-xs">
                  <Mail className="w-3 h-3 mr-1" />
                  <span className="hidden sm:inline">Follow-up</span>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
