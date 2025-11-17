import { useState, useEffect } from "react";
import { KnowledgeBaseInfo } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useKnowledgeBase() {
  const [info, setInfo] = useState<KnowledgeBaseInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchInfo = async () => {
    try {
      const response = await fetch(`${API_BASE}/info`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setInfo(data);
      }
    } catch (error) {
      console.error("Error fetching KB info:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInfo();
    const interval = setInterval(fetchInfo, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return { info, loading, refresh: fetchInfo };
}
