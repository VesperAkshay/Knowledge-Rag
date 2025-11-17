"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Upload, X } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileUpload } from "./FileUpload";
import { URLUpload } from "./URLUpload";
import { Button } from "@/components/ui/button";

interface UploadPanelProps {
  show: boolean;
  onClose: () => void;
  onUploadComplete: () => void;
}

export function UploadPanel({ show, onClose, onUploadComplete }: UploadPanelProps) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="border-b bg-card/50 backdrop-blur-sm overflow-hidden"
        >
          <div className="container mx-auto max-w-4xl p-4">
            <Card className="border-primary/20">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Upload className="w-5 h-5" />
                    Upload Documents
                  </CardTitle>
                  <CardDescription>
                    Add documents to your knowledge base via file upload or URL
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="h-8 w-8 p-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FileUpload onUploadComplete={onUploadComplete} />
                  <URLUpload onUploadComplete={onUploadComplete} />
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
