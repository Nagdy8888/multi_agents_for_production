"use client";

import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { ImageUploader } from "@/components/ImageUploader";
import { BulkUploader } from "@/components/BulkUploader";
import { ProcessingOverlay } from "@/components/ProcessingOverlay";
import { DashboardResult } from "@/components/DashboardResult";
import { HistoryGrid } from "@/components/HistoryGrid";
import { API_BASE_URL } from "@/lib/constants";
import type { AnalyzeImageResponse } from "@/lib/types";

const MAX_STEP = 6;

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeImageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!isProcessing) return;
    stepTimerRef.current = setInterval(() => {
      setCurrentStep((s) => (s < MAX_STEP - 1 ? s + 1 : s));
    }, 3500);
    return () => {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    };
  }, [isProcessing]);

  async function handleAnalyze(file: File) {
    setError(null);
    setIsProcessing(true);
    setCurrentStep(1);

    const formData = new FormData();
    formData.append("file", file);
    setCurrentStep(2);

    try {
      const res = await fetch(`${API_BASE_URL}/api/analyze-image`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Analysis failed");
      }

      const data: AnalyzeImageResponse = await res.json();
      setCurrentStep(MAX_STEP);
      await new Promise((r) => setTimeout(r, 500));
      setAnalysisResult(data);
      if (data.saved_to_db) {
        toast.success("Analysis saved to database");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setIsProcessing(false);
    }
  }

  function handleReplaceImage() {
    setAnalysisResult(null);
    setError(null);
    setCurrentStep(1);
  }

  return (
    <main className="min-h-[calc(100vh-3.5rem)] bg-background">
      <div className="container mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        {!analysisResult ? (
          <div className="mx-auto max-w-2xl space-y-6">
            <div className="text-center">
              <h1 className="text-xl font-semibold tracking-tight text-foreground">
                Tag Image
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Upload an image to analyze and tag with AI.
              </p>
            </div>

            <ImageUploader onAnalyze={handleAnalyze} disabled={isProcessing} />

            <div className="mt-8">
              <BulkUploader />
            </div>

            {error && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}
          </div>
        ) : (
          <div className="mx-auto w-full max-w-6xl">
            <DashboardResult data={analysisResult} onReplaceImage={handleReplaceImage} />
          </div>
        )}

        <HistoryGrid />
      </div>

      <ProcessingOverlay isVisible={isProcessing} currentStep={currentStep} />
    </main>
  );
}
