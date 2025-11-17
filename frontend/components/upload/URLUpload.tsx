"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link as LinkIcon, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api";

interface URLUploadProps {
  onUploadComplete: () => void;
}

export function URLUpload({ onUploadComplete }: URLUploadProps) {
  const [url, setUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleUrlUpload = async () => {
    if (!url.trim()) return;

    setUploading(true);
    setStatus("idle");
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/upload-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setStatus("success");
        setMessage(`Scraped URL - ${data.chunks} chunks indexed`);
        onUploadComplete();
        setUrl("");
        setTimeout(() => {
          setStatus("idle");
          setMessage("");
        }, 3000);
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      setStatus("error");
      setMessage("Failed to scrape URL");
      setTimeout(() => {
        setStatus("idle");
        setMessage("");
      }, 3000);
    } finally {
      setUploading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="space-y-3"
    >
      <div className="relative">
        <Input
          placeholder="https://example.com/article"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleUrlUpload();
          }}
          disabled={uploading}
          className="pr-10"
        />
        <LinkIcon className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
      </div>

      <Button
        onClick={handleUrlUpload}
        disabled={uploading || !url.trim()}
        className="w-full relative overflow-hidden group"
      >
        <motion.div
          className="absolute inset-0 bg-primary/20"
          initial={false}
          animate={{
            scale: uploading ? [1, 1.5, 1] : 1,
            opacity: uploading ? [0.5, 0.2, 0.5] : 0,
          }}
          transition={{
            duration: 1.5,
            repeat: uploading ? Infinity : 0,
          }}
        />

        <span className="relative flex items-center gap-2">
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Scraping...
            </>
          ) : status === "success" ? (
            <>
              <CheckCircle2 className="w-4 h-4" />
              Success!
            </>
          ) : status === "error" ? (
            <>
              <XCircle className="w-4 h-4" />
              Failed
            </>
          ) : (
            <>
              <LinkIcon className="w-4 h-4" />
              Upload URL
            </>
          )}
        </span>
      </Button>

      <AnimatePresence>
        {message && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`text-sm text-center ${
              status === "success"
                ? "text-green-500"
                : status === "error"
                ? "text-red-500"
                : ""
            }`}
          >
            {message}
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
