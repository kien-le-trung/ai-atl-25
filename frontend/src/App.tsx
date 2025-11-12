import { Switch, Route, Link, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { LayoutDashboard, Clock, Lightbulb, Settings as SettingsIcon } from "lucide-react";
import NotFound from "@/pages/not-found";
import Dashboard from "@/pages/Dashboard";
import ConversationDetail from "@/pages/ConversationDetail";
import Timeline from "@/pages/Timeline";
import Insights from "@/pages/Insights";
import Settings from "@/pages/Settings";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/conversation/:id" component={ConversationDetail} />
      <Route path="/timeline" component={Timeline} />
      <Route path="/insights" component={Insights} />
      <Route path="/settings" component={Settings} />
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  const [location] = useLocation();
  
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="min-h-screen bg-gray-100 dark:bg-gray-950 p-4">
          <div className="w-full max-w-[1600px] mx-auto h-[calc(100vh-32px)] bg-white dark:bg-black border-4 border-black dark:border-white rounded-2xl shadow-brutal-xl overflow-hidden">
            <div className="flex h-full">
              {/* Integrated Sidebar */}
              <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r-4 border-black dark:border-white flex flex-col">
                <div className="p-4 border-b-4 border-black dark:border-white">
                  <h2 className="text-sm font-bold uppercase text-muted-foreground">Conversation Memory</h2>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                  <Link href="/">
                    <a className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-colors ${
                      location === "/" || location.startsWith("/conversation") 
                        ? "bg-black dark:bg-white text-white dark:text-black" 
                        : "hover:bg-gray-200 dark:hover:bg-gray-800"
                    }`}>
                      <LayoutDashboard className="w-5 h-5" />
                      <span>Dashboard</span>
                    </a>
                  </Link>
                  <Link href="/timeline">
                    <a className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-colors ${
                      location === "/timeline" 
                        ? "bg-black dark:bg-white text-white dark:text-black" 
                        : "hover:bg-gray-200 dark:hover:bg-gray-800"
                    }`}>
                      <Clock className="w-5 h-5" />
                      <span>Timeline</span>
                    </a>
                  </Link>
                  <Link href="/insights">
                    <a className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-colors ${
                      location === "/insights" 
                        ? "bg-black dark:bg-white text-white dark:text-black" 
                        : "hover:bg-gray-200 dark:hover:bg-gray-800"
                    }`}>
                      <Lightbulb className="w-5 h-5" />
                      <span>Insights</span>
                    </a>
                  </Link>
                  <Link href="/settings">
                    <a className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-colors ${
                      location === "/settings" 
                        ? "bg-black dark:bg-white text-white dark:text-black" 
                        : "hover:bg-gray-200 dark:hover:bg-gray-800"
                    }`}>
                      <SettingsIcon className="w-5 h-5" />
                      <span>Settings</span>
                    </a>
                  </Link>
                </nav>
              </div>
              
              {/* Main Content Area */}
              <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-black">
                <header className="flex items-center justify-between px-6 py-4 border-b-4 border-black dark:border-white bg-white dark:bg-black flex-shrink-0">
                  <h1 className="text-2xl font-black uppercase">Project Memory</h1>
                  <div className="flex items-center gap-3">
                    <Button 
                      className="rounded-full bg-white dark:bg-black text-black dark:text-white border-2 border-black dark:border-white font-bold px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-900"
                      data-testid="button-connect-account"
                    >
                      Connect Account
                    </Button>
                    <Button 
                      className="rounded-full bg-white dark:bg-black text-black dark:text-white border-2 border-black dark:border-white font-bold px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-900"
                      data-testid="button-settings"
                    >
                      Settings
                    </Button>
                  </div>
                </header>
                <main className="flex-1 overflow-y-auto p-6 min-h-0 bg-white dark:bg-black">
                  <Router />
                </main>
              </div>
            </div>
          </div>
        </div>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
