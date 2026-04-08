"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Sparkles, Check } from "lucide-react";

const STEPS = [
  { label: "Uploading...", icon: Loader2 },
  { label: "Preprocessing...", icon: Loader2 },
  { label: "Analyzing with AI...", icon: Sparkles },
  { label: "Tagging 8 categories...", icon: Sparkles },
  { label: "Validating...", icon: Loader2 },
  { label: "Complete!", icon: Check },
];

interface ProcessingOverlayProps {
  isVisible: boolean;
  currentStep: number;
}

export function ProcessingOverlay({ isVisible, currentStep }: ProcessingOverlayProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm"
        >
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-6 rounded-xl border border-border/60 bg-card/95 p-8 shadow-xl backdrop-blur"
        >
            {STEPS.map((step, index) => {
              const isActive = index + 1 === currentStep;
              const isComplete = index + 1 < currentStep;
              const Icon = step.icon;

              return (
                <motion.div
                  key={step.label}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                      isComplete
                        ? "bg-primary text-primary-foreground"
                        : isActive
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {isComplete ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <Icon
                        className={`h-5 w-5 ${isActive && Icon === Loader2 ? "animate-spin" : ""}`}
                      />
                    )}
                  </div>
                  <span
                    className={
                      isActive ? "font-medium text-foreground" : "text-muted-foreground"
                    }
                  >
                    {step.label}
                  </span>
                </motion.div>
              );
            })}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
