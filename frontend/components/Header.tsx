"use client";

import { motion } from "framer-motion";
import { Database, Upload, FileText, Activity, Workflow, Settings as SettingsIcon, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { KnowledgeBaseInfo } from "@/lib/types";
import { useAuth } from "@/lib/contexts/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface HeaderProps {
  kbInfo: KnowledgeBaseInfo | null;
  showUpload: boolean;
  onToggleUpload: () => void;
  onToggleWorkflow?: () => void;
}

export function Header({ kbInfo, showUpload, onToggleUpload, onToggleWorkflow }: HeaderProps) {
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-50"
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center gap-3"
          >
            <motion.div
              whileHover={{ scale: 1.1, rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 rounded-lg bg-linear-to-tr from-primary/20 to-primary/5 flex items-center justify-center border border-primary/20"
            >
              <Database className="w-6 h-6 text-primary" />
            </motion.div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-linear-to-r from-primary to-primary/50 bg-clip-text text-transparent">
                Orchestrator RAG
              </h1>
              <p className="text-sm text-muted-foreground">
                Intelligent Knowledge Base with Web Search
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-3"
          >
            {/* User Info */}
            {user && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.35 }}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-lg border border-primary/20"
              >
                <User className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">{user.username}</span>
              </motion.div>
            )}

            {kbInfo && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.4 }}
              >
                <Badge variant="secondary" className="gap-2">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <FileText className="w-4 h-4" />
                  </motion.div>
                  {kbInfo.document_count} documents
                </Badge>
              </motion.div>
            )}

            {onToggleWorkflow && (
              <Button
                variant="outline"
                size="sm"
                onClick={onToggleWorkflow}
                className="gap-2"
              >
                <Workflow className="w-4 h-4" />
                <span className="hidden sm:inline">Workflow</span>
              </Button>
            )}

            <Button
              variant={showUpload ? "default" : "outline"}
              size="sm"
              onClick={onToggleUpload}
              className="gap-2"
            >
              <motion.div
                animate={showUpload ? { rotate: 180 } : { rotate: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Upload className="w-4 h-4" />
              </motion.div>
              <span className="hidden sm:inline">Upload</span>
            </Button>

            <Link href="/settings">
              <Button
                variant="ghost"
                size="sm"
                className="gap-2"
              >
                <SettingsIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Settings</span>
              </Button>
            </Link>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="gap-2 text-red-500 hover:text-red-600 hover:bg-red-500/10"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
}
