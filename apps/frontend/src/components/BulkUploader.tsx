"use client";

import { useState, useRef, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, CheckCircle, XCircle, Loader2 } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { API_BASE_URL } from "@/lib/constants";
import { cn } from "@/lib/utils";

const MAX_SIZE_MB = 10;
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ACCEPT = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

type FileStatus = "pending" | "processing" | "complete" | "failed";

interface BatchResultItem {
  image_id: string;
  status: FileStatus;
  image_url?: string;
  error?: string;
}

interface BatchState {
  total: number;
  completed: number;
  results: BatchResultItem[];
  status: "processing" | "complete";
}

const POLL_INTERVAL_MS = 2000;

export function BulkUploader() {
  const [files, setFiles] = useState<File[]>([]);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [batchState, setBatchState] = useState<BatchState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (accepted) => setFiles((prev) => [...prev, ...accepted]),
    accept: ACCEPT,
    maxSize: MAX_BYTES,
    maxFiles: 20,
    disabled: !!batchId && (batchState?.status ?? "") !== "complete",
    onDropRejected: (rejections) => {
      const first = rejections[0];
      if (first?.errors[0]?.code === "file-too-large") {
        setError(`Files must be under ${MAX_SIZE_MB}MB`);
      } else {
        setError("Please use JPG, PNG, or WEBP images.");
      }
    },
  });

  useEffect(() => {
    if (!batchId || batchState?.status === "complete") return;
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/bulk-status/${batchId}`);
        if (!res.ok) return;
        const data = await res.json();
        setBatchState(data);
        if (data.status === "complete") {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
        }
      } catch {
        // keep polling
      }
    };
    poll();
    pollRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [batchId, batchState?.status]);

  async function startBulkAnalysis() {
    if (files.length === 0) return;
    setError(null);
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    try {
      const res = await fetch(`${API_BASE_URL}/api/bulk-upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Bulk upload failed");
      }
      const data = await res.json();
      setBatchId(data.batch_id);
      setBatchState({
        total: data.total,
        completed: 0,
        results: Array.from({ length: data.total }, () => ({ image_id: "", status: "pending" })),
        status: "processing",
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Bulk upload failed");
    }
  }

  function reset() {
    setFiles([]);
    setBatchId(null);
    setBatchState(null);
    setError(null);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  const completed = batchState?.completed ?? 0;
  const total = batchState?.total ?? 0;
  const isComplete = batchState?.status === "complete";

  return (
    <Card className="overflow-hidden border-border/60 bg-card/80">
      <CardContent className="p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Bulk Upload
        </h3>
        <div
          {...getRootProps()}
          className={cn(
            "flex min-h-[120px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-4 transition",
            isDragActive ? "border-primary/50 bg-primary/5" : "border-border/60 hover:border-border"
          )}
        >
          <input {...getInputProps()} />
          <Upload className="h-8 w-8 text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">
            {isDragActive ? "Drop images here" : "Drag & drop multiple images, or click to select"}
          </p>
        </div>
        {files.length > 0 && !batchId && (
          <div className="mt-3 flex flex-wrap gap-2">
            {files.map((f, i) => (
              <div key={i} className="relative h-14 w-14 overflow-hidden rounded border border-border/60">
                <Image
                  src={URL.createObjectURL(f)}
                  alt=""
                  width={56}
                  height={56}
                  className="h-full w-full object-cover"
                  unoptimized
                />
              </div>
            ))}
          </div>
        )}
        {files.length > 0 && !batchId && (
          <Button className="mt-3 w-full" onClick={startBulkAnalysis}>
            Start Bulk Analysis ({files.length} {files.length === 1 ? "image" : "images"})
          </Button>
        )}
        {batchState && (
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span>{completed} / {total} complete</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: total ? `${(completed / total) * 100}%` : "0%" }}
              />
            </div>
            <div className="max-h-40 space-y-1 overflow-y-auto">
              {(batchState.results ?? []).map((item, i) => (
                <div
                  key={item.image_id || i}
                  className="flex items-center gap-2 rounded border border-border/60 px-2 py-1 text-xs"
                >
                  {item.status === "complete" && <CheckCircle className="h-4 w-4 shrink-0 text-emerald-500" />}
                  {item.status === "failed" && <XCircle className="h-4 w-4 shrink-0 text-destructive" />}
                  {(item.status === "pending" || item.status === "processing") && (
                    <Loader2 className="h-4 w-4 shrink-0 animate-spin text-muted-foreground" />
                  )}
                  <span className="truncate font-mono">{item.image_id || `File ${i + 1}`}</span>
                  <span className={cn(
                    "ml-auto shrink-0",
                    item.status === "complete" && "text-emerald-500",
                    item.status === "failed" && "text-destructive"
                  )}>
                    {item.status}
                  </span>
                  {item.error && <span className="truncate text-destructive" title={item.error}>{item.error}</span>}
                </div>
              ))}
            </div>
            {isComplete && (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={reset}>
                  Upload more
                </Button>
                <Link href="/">
                  <Button size="sm">View in history</Button>
                </Link>
              </div>
            )}
          </div>
        )}
        {error && (
          <p className="mt-2 text-sm text-destructive">{error}</p>
        )}
      </CardContent>
    </Card>
  );
}
