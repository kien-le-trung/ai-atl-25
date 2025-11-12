import { useQuery } from "@tanstack/react-query";
import { TrendingUp, MessageCircle, Target, Users, Lightbulb, Volume2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";

interface InsightsData {
  talkTimeRatio: string;
  averageSentiment: number;
  topTopics: string[];
  totalMatches: number;
  totalConversations: number;
  feedbackPoints: string[];
}

export default function Insights() {
  const { data: insights, isLoading } = useQuery<InsightsData>({
    queryKey: ["/api/insights"],
  });

  const sentimentColor = (score: number) => {
    if (score >= 0.7) return "text-green-600 dark:text-green-400";
    if (score >= 0.4) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight" data-testid="text-title">
          Insights & Analytics
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          AI-powered analysis of your conversation patterns
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Talk Time Ratio</CardTitle>
            <MessageCircle className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-3xl font-bold" data-testid="text-talk-ratio">
                  {insights?.talkTimeRatio || "N/A"}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  You / Them
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Sentiment</CardTitle>
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className={`text-3xl font-bold ${sentimentColor(insights?.averageSentiment || 0)}`} data-testid="text-sentiment">
                  +{((insights?.averageSentiment || 0) * 100).toFixed(0)}%
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {insights?.averageSentiment && insights.averageSentiment >= 0.7 ? "Very Positive" : insights?.averageSentiment && insights.averageSentiment >= 0.4 ? "Neutral" : "Needs Improvement"}
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Top Topics</CardTitle>
            <Lightbulb className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-full" />
            ) : (
              <>
                <div className="text-xl font-bold truncate" data-testid="text-top-topics">
                  {insights?.topTopics?.slice(0, 2).join(", ") || "No topics yet"}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Most discussed
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Match Rate</CardTitle>
            <Target className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-3xl font-bold" data-testid="text-matches">
                  {insights?.totalMatches || 0} / {insights?.totalConversations || 0}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Recognized faces
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">AI Feedback Summary</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : insights?.feedbackPoints && insights.feedbackPoints.length > 0 ? (
            <div className="space-y-4">
              {insights.feedbackPoints.map((point, index) => (
                <div key={index} className="flex gap-3 p-4 bg-muted/50 rounded-md" data-testid={`feedback-${index}`}>
                  <Lightbulb className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <p className="text-sm leading-relaxed">{point}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Lightbulb className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">
                No feedback available yet. Complete more conversations to get AI-powered insights.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Voice Debrief</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-md">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Volume2 className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1">AI-Generated Voice Summary</h3>
              <p className="text-sm text-muted-foreground">
                Listen to personalized feedback about your conversation patterns
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <Button data-testid="button-replay-debrief">
              <Volume2 className="w-4 h-4 mr-2" />
              Replay My Debrief
            </Button>
            <Button variant="outline" data-testid="button-schedule-call">
              Call Me for Review
            </Button>
          </div>

          <div className="text-xs text-muted-foreground p-3 bg-muted/30 rounded-md">
            <p>
              <strong>Note:</strong> Voice debrief generation is powered by ElevenLabs AI voice synthesis and Vapi phone calling system.
              This feature analyzes your conversation patterns and provides personalized coaching.
            </p>
          </div>
        </CardContent>
      </Card>

      {insights?.topTopics && insights.topTopics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Topic Distribution</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {insights.topTopics.map((topic, index) => {
              const percentage = Math.max(20, 100 - index * 15);
              return (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium" data-testid={`topic-name-${index}`}>{topic}</span>
                    <span className="text-muted-foreground" data-testid={`topic-percentage-${index}`}>{percentage}%</span>
                  </div>
                  <Progress value={percentage} className="h-2" />
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
