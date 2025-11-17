"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Header } from "@/components/Header";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { ChatInput } from "@/components/chat/ChatInput";
import { UploadPanel } from "@/components/upload/UploadPanel";
import { WorkflowVisualization } from "@/components/workflow/WorkflowVisualization";
import { useChat } from "@/lib/hooks/useChat";
import { useKnowledgeBase } from "@/lib/hooks/useKnowledgeBase";
import { useAuth } from "@/lib/contexts/AuthContext";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageSquare, Workflow } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, hasCredentials, isLoading } = useAuth();
  const [showUpload, setShowUpload] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "workflow">("chat");
  const { messages, loading, sendMessage } = useChat();
  const { info: kbInfo, refresh: refreshKB } = useKnowledgeBase();

  // Check authentication and credentials
  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push('/login');
      } else if (!hasCredentials) {
        router.push('/settings');
      }
    }
  }, [isAuthenticated, hasCredentials, isLoading, router]);

  const handleUploadComplete = () => {
    refreshKB();
  };

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-linear-to-br from-background via-background to-muted/20">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full"
        />
      </div>
    );
  }

  // Don't render if not authenticated or no credentials
  if (!isAuthenticated || !hasCredentials) {
    return null;
  }

  return (
    <div className="flex flex-col h-screen bg-linear-to-br from-background via-background to-muted/20">
      <Header
        kbInfo={kbInfo}
        showUpload={showUpload}
        onToggleUpload={() => setShowUpload(!showUpload)}
        onToggleWorkflow={() => setActiveTab(activeTab === "chat" ? "workflow" : "chat")}
      />

      <UploadPanel
        show={showUpload}
        onClose={() => setShowUpload(false)}
        onUploadComplete={handleUploadComplete}
      />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex-1 container mx-auto max-w-6xl px-4 py-6 flex flex-col overflow-hidden"
      >
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "chat" | "workflow")} className="flex-1 flex flex-col">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-4">
            <TabsTrigger value="chat" className="gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="workflow" className="gap-2">
              <Workflow className="w-4 h-4" />
              Workflow
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="flex-1 flex flex-col mt-0 space-y-4">
            <ChatContainer messages={messages} loading={loading} />
            <ChatInput onSend={sendMessage} loading={loading} />
          </TabsContent>

          <TabsContent value="workflow" className="flex-1 mt-0">
            <Card className="h-full p-6">
              <div className="space-y-4">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Agent Workflow</h2>
                  <p className="text-muted-foreground">
                    Visualize how the orchestrator agent processes queries through knowledge base search and web fallback.
                  </p>
                </div>
                <WorkflowVisualization />
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
}
