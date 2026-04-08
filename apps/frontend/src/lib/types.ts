/** Single category output from a tagger node (e.g. season). */
export interface PartialTagResult {
  category: string;
  tags: string[];
  confidence_scores: Record<string, number>;
}

/** Tag with confidence (from tags_by_category). */
export interface TagWithConfidence {
  value: string;
  confidence: number;
}

/** Hierarchical tag (parent/child). */
export interface HierarchicalTag {
  parent: string;
  child: string;
}

/** Final tag record from aggregator. */
export interface TagRecord {
  image_id: string;
  season: string[];
  theme: string[];
  objects: HierarchicalTag[];
  dominant_colors: HierarchicalTag[];
  design_elements: string[];
  occasion: string[];
  mood: string[];
  product_type: HierarchicalTag | null;
  needs_review: boolean;
  processed_at: string;
}

/** Flagged tag (low confidence or invalid). */
export interface FlaggedTag {
  category: string;
  value: string;
  confidence: number;
  reason: string;
}

export interface AnalyzeImageResponse {
  image_url: string;
  image_id: string;
  vision_description: string;
  vision_raw_tags: Record<string, unknown>;
  partial_tags?: PartialTagResult[];
  /** Category -> list of { value, confidence } (from validated tags). */
  tags_by_category?: Record<string, TagWithConfidence[]>;
  tag_record?: TagRecord | null;
  flagged_tags?: FlaggedTag[];
  processing_status?: "complete" | "needs_review" | "failed";
  saved_to_db?: boolean;
}

/** Stored row from GET /api/tag-images */
export interface TagImageRow {
  image_id: string;
  tag_record: TagRecord | Record<string, unknown>;
  search_index?: string[];
  image_url?: string | null;
  needs_review: boolean;
  processing_status: string;
  created_at: string;
  updated_at: string;
}

export interface TagImagesListResponse {
  items: TagImageRow[];
  limit: number;
  offset: number;
}
