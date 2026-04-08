"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Tag, Search } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between gap-4">
        <Link href="/" className="flex shrink-0 items-center gap-2 font-semibold">
          <Tag className="h-6 w-6" />
          <span>Image Tagger</span>
        </Link>

        <nav className="flex flex-1 items-center justify-center gap-2 max-w-md w-full">
          <Link
            href="/"
            className={cn(
              "flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
              pathname === "/" ? "bg-accent text-accent-foreground" : "text-muted-foreground"
            )}
          >
            <Tag className="h-4 w-4" />
            Tag Image
          </Link>
          <button
            type="button"
            onClick={() => router.push("/search")}
            className="flex flex-1 items-center gap-2 rounded-md border border-input bg-muted/30 px-3 py-2 text-sm text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors"
          >
            <Search className="h-4 w-4 shrink-0" />
            <span className="truncate">Search</span>
          </button>
        </nav>

        <div className="shrink-0">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
