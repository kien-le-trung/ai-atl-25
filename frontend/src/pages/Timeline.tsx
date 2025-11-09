import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Calendar, User, Filter } from "lucide-react";
import { useLocation } from "wouter";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { ConversationWithPerson } from "@shared/schema";
import { formatDistanceToNow } from "date-fns";

export default function Timeline() {
  const [, setLocation] = useLocation();
  const [filterTopic, setFilterTopic] = useState<string>("all");
  const [filterMonth, setFilterMonth] = useState<string>("all");

  const { data: conversations, isLoading } = useQuery<ConversationWithPerson[]>({
    queryKey: ["/api/conversations"],
  });

  const filteredConversations = conversations?.filter((conv) => {
    if (filterTopic !== "all" && (!conv.topics || !conv.topics.includes(filterTopic))) {
      return false;
    }
    if (filterMonth !== "all") {
      const convMonth = new Date(conv.createdAt).getMonth();
      if (convMonth !== parseInt(filterMonth)) {
        return false;
      }
    }
    return true;
  });

  const allTopics = conversations?.reduce((acc, conv) => {
    if (conv.topics) {
      conv.topics.forEach((topic) => {
        if (!acc.includes(topic)) {
          acc.push(topic);
        }
      });
    }
    return acc;
  }, [] as string[]) || [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight" data-testid="text-title">
          Memory Timeline
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          View and explore your conversation history
        </p>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Filter by:</span>
          </div>
          
          <Select value={filterTopic} onValueChange={setFilterTopic}>
            <SelectTrigger className="w-[180px]" data-testid="select-topic-filter">
              <SelectValue placeholder="All Topics" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Topics</SelectItem>
              {allTopics.map((topic) => (
                <SelectItem key={topic} value={topic}>
                  {topic}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filterMonth} onValueChange={setFilterMonth}>
            <SelectTrigger className="w-[180px]" data-testid="select-month-filter">
              <SelectValue placeholder="All Months" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Months</SelectItem>
              <SelectItem value="0">January</SelectItem>
              <SelectItem value="1">February</SelectItem>
              <SelectItem value="2">March</SelectItem>
              <SelectItem value="3">April</SelectItem>
              <SelectItem value="4">May</SelectItem>
              <SelectItem value="5">June</SelectItem>
              <SelectItem value="6">July</SelectItem>
              <SelectItem value="7">August</SelectItem>
              <SelectItem value="8">September</SelectItem>
              <SelectItem value="9">October</SelectItem>
              <SelectItem value="10">November</SelectItem>
              <SelectItem value="11">December</SelectItem>
            </SelectContent>
          </Select>

          {(filterTopic !== "all" || filterMonth !== "all") && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setFilterTopic("all");
                setFilterMonth("all");
              }}
              data-testid="button-clear-filters"
            >
              Clear Filters
            </Button>
          )}
        </div>
      </Card>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex gap-4">
              <div className="flex flex-col items-center">
                <Skeleton className="w-8 h-8 rounded-full" />
                <Skeleton className="w-0.5 h-24 mt-2" />
              </div>
              <Card className="flex-1 p-4">
                <Skeleton className="h-5 w-1/3 mb-2" />
                <Skeleton className="h-4 w-1/2 mb-4" />
                <Skeleton className="h-16 w-full" />
              </Card>
            </div>
          ))}
        </div>
      ) : filteredConversations && filteredConversations.length > 0 ? (
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />
          <div className="space-y-6">
            {filteredConversations.map((conversation, index) => (
              <div key={conversation.id} className="flex gap-4 relative" data-testid={`timeline-item-${conversation.id}`}>
                <div className="flex-shrink-0 relative z-10">
                  <Avatar className="w-12 h-12 border-2 border-black dark:border-white bg-white dark:bg-gray-900" data-testid={`avatar-${conversation.id}`}>
                    <AvatarImage 
                      src={conversation.person.photoUrl || undefined} 
                      className="object-cover object-center"
                      alt={conversation.person.name} 
                    />
                    <AvatarFallback className="bg-gray-200 dark:bg-gray-700 text-black dark:text-white font-bold">
                      <User className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                </div>
                
                <Card
                  className="flex-1 p-4 border-4 border-black dark:border-white rounded-2xl shadow-brutal hover-elevate active-elevate-2 transition-all cursor-pointer bg-white dark:bg-gray-900"
                  onClick={() => setLocation(`/conversation/${conversation.id}`)}
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2 flex-wrap">
                      <div className="flex-1">
                        <h3 className="font-semibold text-base" data-testid={`text-name-${conversation.id}`}>
                          {conversation.person.name}
                        </h3>
                        <p className="text-sm text-muted-foreground" data-testid={`text-affiliation-${conversation.id}`}>
                          {conversation.person.company || conversation.person.school || "No affiliation"}
                        </p>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        <span data-testid={`text-date-${conversation.id}`}>
                          {formatDistanceToNow(new Date(conversation.createdAt), { addSuffix: true })}
                        </span>
                      </div>
                    </div>

                    <p className="text-sm line-clamp-2" data-testid={`text-summary-${conversation.id}`}>
                      {conversation.summary || "Met and discussed various topics."}
                    </p>

                    {conversation.topics && conversation.topics.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {conversation.topics.map((topic, i) => (
                          <Badge key={i} variant="outline" className="text-xs" data-testid={`badge-topic-${i}`}>
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <Card className="p-12">
          <div className="text-center space-y-3">
            <Calendar className="w-12 h-12 mx-auto text-muted-foreground" />
            <h3 className="text-lg font-semibold">No conversations found</h3>
            <p className="text-sm text-muted-foreground max-w-sm mx-auto">
              {filterTopic !== "all" || filterMonth !== "all"
                ? "Try adjusting your filters to see more results"
                : "Start tracking conversations to build your memory timeline"}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
