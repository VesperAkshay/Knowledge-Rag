"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, File, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FileUploadProps {
  onUploadComplete: () => void;
}

export function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setStatus("idle");
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/upload-file`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setStatus("success");
        setMessage(`Uploaded ${file.name} - ${data.chunks} chunks indexed`);
        onUploadComplete();
        setTimeout(() => {
          setStatus("idle");
          setMessage("");
        }, 3000);
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      setStatus("error");
      setMessage("Failed to upload file");
      setTimeout(() => {
        setStatus("idle");
        setMessage("");
      }, 3000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <label
        className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-lg cursor-pointer transition-all ${
          uploading
            ? "border-primary bg-primary/5"
            : status === "success"
            ? "border-green-500 bg-green-500/5"
            : status === "error"
            ? "border-red-500 bg-red-500/5"
            : "border-border hover:border-primary/50 hover:bg-accent/50"
        }`}
      >
        <div className="flex flex-col items-center justify-center py-6">
          <motion.div
            animate={uploading ? { rotate: 360 } : {}}
            transition={uploading ? { duration: 2, repeat: Infinity, ease: "linear" } : {}}
          >
            {uploading ? (
              <Loader2 className="w-10 h-10 text-primary" />
            ) : status === "success" ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <CheckCircle2 className="w-10 h-10 text-green-500" />
              </motion.div>
            ) : status === "error" ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                <XCircle className="w-10 h-10 text-red-500" />
              </motion.div>
            ) : (
              <Upload className="w-10 h-10 text-muted-foreground" />
            )}
          </motion.div>

          <p className="mt-2 text-sm text-center text-muted-foreground">
            {uploading
              ? "Uploading..."
              : status === "success"
              ? message
              : status === "error"
              ? message
              : "Click to upload file"}
          </p>

          {status === "idle" && (
            <p className="mt-1 text-xs text-muted-foreground">
              PDF, DOCX, TXT (Max 10MB)
            </p>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.doc,.docx,.txt"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              handleFileUpload(e.target.files[0]);
            }
          }}
          disabled={uploading}
        />
      </label>
    </motion.div>
  );
}
