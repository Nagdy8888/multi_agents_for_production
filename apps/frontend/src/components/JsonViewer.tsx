"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface JsonViewerProps {
  data?: Record<string, unknown> | object | null;
}

export function JsonViewer({ data }: JsonViewerProps) {
  const obj = data != null && typeof data === "object" ? data : {};
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="w-full rounded-lg border bg-card">
      <Button
        variant="ghost"
        className="w-full justify-start gap-2 rounded-b-none rounded-t-lg"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
        View Raw JSON
      </Button>
      {expanded && (
        <pre className="max-h-[400px] overflow-auto rounded-b-lg border-t bg-zinc-950 p-4 text-xs text-zinc-100">
          <code>{JSON.stringify(obj, null, 2)}</code>
        </pre>
      )}
    </div>
  );
}
