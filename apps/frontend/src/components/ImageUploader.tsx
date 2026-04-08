"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload } from "lucide-react";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const MAX_SIZE_MB = 10;
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ACCEPT = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

interface ImageUploaderProps {
  onAnalyze: (file: File) => void;
  disabled?: boolean;
}

export function ImageUploader({ onAnalyze, disabled }: ImageUploaderProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
  }, []);

  const { getRootProps, getInputProps, acceptedFiles, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPT,
    maxSize: MAX_BYTES,
    maxFiles: 1,
    disabled,
    onDropRejected: (rejections) => {
      const first = rejections[0];
      if (first?.errors[0]?.code === "file-too-large") {
        setError(`File must be under ${MAX_SIZE_MB}MB`);
      } else {
        setError("Please use a JPG, PNG, or WEBP image.");
      }
    },
  });

  const file = acceptedFiles[0];

  return (
    <Card className="overflow-hidden border-border/60 bg-card/80">
      <CardContent className="p-0">
        <div
          {...getRootProps()}
          className={cn(
            "flex min-h-[280px] cursor-pointer flex-col items-center justify-center gap-3 border-2 border-dashed p-6 transition-colors",
            isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50",
            file && "min-h-0 justify-start"
          )}
        >
          <input {...getInputProps()} />
          {file ? (
            <>
              <div className="relative h-48 w-full max-w-sm overflow-hidden rounded-lg bg-muted">
                <Image
                  src={URL.createObjectURL(file)}
                  alt="Preview"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
              <p className="text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024).toFixed(1)} KB
              </p>
              <Button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onAnalyze(file);
                }}
                disabled={disabled}
                className="mt-2"
              >
                Analyze
              </Button>
            </>
          ) : (
            <>
              <Upload className="h-12 w-12 text-muted-foreground" />
              <p className="text-center text-sm text-muted-foreground">
                Drag & drop an image here, or click to browse
              </p>
              <p className="text-xs text-muted-foreground">
                Supports JPG, PNG, WEBP (max {MAX_SIZE_MB}MB)
              </p>
            </>
          )}
        </div>
        {error && (
          <p className="px-6 pb-4 text-sm text-destructive">{error}</p>
        )}
      </CardContent>
    </Card>
  );
}
