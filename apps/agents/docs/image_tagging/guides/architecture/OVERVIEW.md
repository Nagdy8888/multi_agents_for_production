# System architecture

High-level flow: browser → Next.js → FastAPI → LangGraph agent → (optional) Supabase.

## Diagram

```mermaid
flowchart TD
    subgraph FE ["Frontend - Next.js + shadcn/ui"]
        Upload["Image Upload"]
        Dashboard["Dashboard"]
        SearchPage["Search Page"]
        BulkPage["Bulk Upload"]
    end

    subgraph BE ["Backend - FastAPI"]
        Server["server.py Routes"]
        StaticFiles["Static /uploads"]
    end

    subgraph Agent ["LangGraph Agent"]
        Preprocess["image_preprocessor"]
        Vision["vision_analyzer GPT-4o"]
        subgraph Taggers ["Parallel Taggers x8"]
            T1["season"]
            T2["theme"]
            T3["objects"]
            T4["colors"]
            T5["design"]
            T6["occasion"]
            T7["mood"]
            T8["product"]
        end
        Validator["tag_validator"]
        ConfFilter["confidence_filter"]
        Aggregator["tag_aggregator"]
    end

    subgraph DB ["Supabase PostgreSQL"]
        ImageTags["image_tags table"]
        SearchIndex["GIN search_index"]
    end

    Upload -->|"POST /api/analyze-image"| Server
    SearchPage -->|"GET /api/search-images"| Server
    BulkPage -->|"POST /api/bulk-upload"| Server
    Dashboard -->|"GET /api/tag-images"| Server

    Server --> Preprocess
    Preprocess --> Vision
    Vision --> T1 & T2 & T3 & T4 & T5 & T6 & T7 & T8
    T1 & T2 & T3 & T4 & T5 & T6 & T7 & T8 --> Validator
    Validator --> ConfFilter --> Aggregator

    Aggregator -->|"upsert TagRecord"| ImageTags
    ImageTags --> SearchIndex
    Server --> StaticFiles
```

## Tech stack

- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind v4, shadcn/ui, Framer Motion, Lucide, react-dropzone.
- **Backend:** Python 3.11, FastAPI, LangGraph, langchain-openai (GPT-4o vision), Pillow, python-dotenv, psycopg2.
- **Database:** Supabase (PostgreSQL); JSONB `tag_record`, GIN-indexed `search_index` array for filtered search.
- **Tracing:** LangSmith optional via `LANGCHAIN_API_KEY` / `LANGCHAIN_TRACING_V2`.

## Rationale

- **LangGraph:** Structured pipeline (preprocess → vision → parallel taggers → validate → filter → aggregate) with clear state and fan-out.
- **GPT-4o:** Strong vision and JSON output for product-image tagging.
- **Supabase:** Managed Postgres, simple connection string, GIN indexes for array containment search.
- **Next.js + shadcn:** Fast UI, accessible components, dark theme, good DX.
