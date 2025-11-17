export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
  isStreaming?: boolean;
}

export interface KnowledgeBaseInfo {
  document_count: number;
  last_updated?: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  chunks?: number;
}

export interface WorkflowStep {
  id: string;
  label: string;
  status: "idle" | "active" | "completed" | "error";
  timestamp?: Date;
}

export interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

export interface UploadState {
  uploads: UploadProgress[];
  uploading: boolean;
}
