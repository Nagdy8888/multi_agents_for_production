"use client";

import { cn } from "@/lib/utils";

/** Ring showing confidence 0–1; optional center label (e.g. "87%"). */
interface ConfidenceRingProps {
  confidence: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  /** Show percentage in center (for large ring). */
  showValue?: boolean;
}

export function ConfidenceRing({
  confidence,
  size = 32,
  strokeWidth = 3,
  className,
  showValue = false,
}: ConfidenceRingProps) {
  const clamped = Math.min(1, Math.max(0, confidence));
  const pct = Math.round(clamped * 100);
  const r = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped);

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="shrink-0 -rotate-90"
        aria-label={`Confidence ${pct}%`}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted opacity-30"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="text-emerald-500 transition-[stroke-dashoffset] duration-500"
        />
      </svg>
      {showValue && (
        <span className="absolute inset-0 flex items-center justify-center text-sm font-semibold text-foreground">
          {pct}%
        </span>
      )}
    </div>
  );
}
