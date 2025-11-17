"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion } from "framer-motion";
import { Database, Globe, Save, CheckCircle2 } from "lucide-react";

const initialNodes: Node[] = [
  {
    id: "1",
    type: "input",
    data: { label: "User Query" },
    position: { x: 250, y: 0 },
    style: { background: "#6366f1", color: "white", border: "2px solid #4f46e5" },
  },
  {
    id: "2",
    data: { label: "Orchestrator Agent" },
    position: { x: 250, y: 100 },
    style: { background: "#8b5cf6", color: "white", border: "2px solid #7c3aed" },
  },
  {
    id: "3",
    data: { label: "Knowledge Base Search" },
    position: { x: 100, y: 220 },
    style: { background: "#10b981", color: "white", border: "2px solid #059669" },
  },
  {
    id: "4",
    data: { label: "Web Search (DuckDuckGo)" },
    position: { x: 400, y: 220 },
    style: { background: "#f59e0b", color: "white", border: "2px solid #d97706" },
  },
  {
    id: "5",
    data: { label: "Index New Knowledge" },
    position: { x: 400, y: 340 },
    style: { background: "#3b82f6", color: "white", border: "2px solid #2563eb" },
  },
  {
    id: "6",
    type: "output",
    data: { label: "Response to User" },
    position: { x: 250, y: 460 },
    style: { background: "#22c55e", color: "white", border: "2px solid #16a34a" },
  },
];

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e2-3", source: "2", target: "3", label: "Try KB first", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e2-4", source: "2", target: "4", label: "If not found", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e3-6", source: "3", target: "6", label: "Found", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e4-5", source: "4", target: "5", label: "Save findings", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: "e5-6", source: "5", target: "6", animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
];

export function WorkflowVisualization() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="w-full h-[500px] border rounded-lg overflow-hidden bg-background"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.style?.background) return node.style.background as string;
            return "#ddd";
          }}
          maskColor="rgba(0, 0, 0, 0.2)"
        />
      </ReactFlow>
    </motion.div>
  );
}
