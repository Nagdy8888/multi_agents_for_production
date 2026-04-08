# Multi-Agent Platform -- Architecture Overview

This document provides a comprehensive visual guide to the entire platform: how both AI agents share a single backend, how GAS triggers and callbacks flow, and the internal LangGraph pipeline of each agent.

---

## 1. System-Level Architecture

The platform has three deployment units: a unified Python backend, a Next.js frontend, and a Google Apps Script project (separate repo). All communication between GAS and Python is via HTTP webhooks.

```mermaid
flowchart TD
    subgraph google ["Google Workspace"]
        Gmail["Gmail Inbox"]
        Drive["Google Drive\n(Product Images Folder)"]
        POSheets["PO Google Sheet\n(PO Data, PO Items,\nMonitoring Logs)"]
        IMGSheets["Image Google Sheet\n(Image Tags,\nImage Monitoring)"]
    end

    subgraph gasRepo ["GAS Repo (Git Submodule)"]
        EmailTrigger["EmailTrigger.gs\n(every 5min)"]
        DriveTrigger["DriveTrigger.gs\n(every 5min)"]
        WebAppGS["WebApp.gs\n(doPost callback router)"]
        SheetsWriterPO["SheetsWriter.gs\n(PO data)"]
        SheetsWriterImg["SheetsWriter.gs\n(Image data)"]
        Notifier["Notifier.gs\n(Email alerts)"]
        LabelMgr["LabelManager.gs\n(Gmail labels)"]
    end

    subgraph pythonBackend ["Python Backend -- apps/agents/ (port 8000)"]
        FastAPIApp["Unified FastAPI\n(src/api/main.py)"]

        subgraph poAgent ["PO Parser Agent"]
            POGraph["LangGraph: po_parser"]
        end

        subgraph imgAgent ["Image Tagging Agent"]
            IMGGraph["LangGraph: image_tagging"]
        end

        subgraph sharedServices ["Shared Services (src/services/)"]
            OpenAISvc["openai/\n(GPT-4o, GPT-4o-mini)"]
            AirtableSvc["airtable/\n(pyairtable)"]
            SupabaseSvc["supabase/\n(psycopg2)"]
            GASCallbackSvc["gas_callback/\n(httpx)"]
        end
    end

    subgraph frontend ["Next.js Frontend -- apps/frontend/ (port 3000)"]
        Dashboard["Image Tagging Dashboard\n(Upload, Search, History)"]
    end

    subgraph externalAPIs ["External APIs"]
        OpenAI["OpenAI API"]
        Airtable["Airtable"]
        Supabase["Supabase PostgreSQL"]
    end

    subgraph tunnel ["Public URL (ngrok / production)"]
        Ngrok["ngrok tunnel\n(tunnels to port 8000)"]
    end

    Gmail -->|"new PO emails"| EmailTrigger
    Drive -->|"new image files"| DriveTrigger
    EmailTrigger -->|"POST /webhook/email\n+ x-webhook-secret header"| Ngrok
    DriveTrigger -->|"POST /webhook/drive-image\n+ x-webhook-secret header\n(base64 image payload)"| Ngrok
    Ngrok --> FastAPIApp

    FastAPIApp -->|"PO email payload"| POGraph
    FastAPIApp -->|"image payload"| IMGGraph

    POGraph --> OpenAISvc
    POGraph --> AirtableSvc
    POGraph --> GASCallbackSvc
    IMGGraph --> OpenAISvc
    IMGGraph --> SupabaseSvc

    OpenAISvc --> OpenAI
    AirtableSvc --> Airtable
    SupabaseSvc --> Supabase

    GASCallbackSvc -->|"POST callback\n(JSON + secret + type)"| WebAppGS

    WebAppGS -->|"type=po_result"| SheetsWriterPO
    WebAppGS -->|"type=po_result"| Notifier
    WebAppGS -->|"type=po_result"| LabelMgr
    WebAppGS -->|"type=image_result"| SheetsWriterImg
    SheetsWriterPO --> POSheets
    SheetsWriterImg --> IMGSheets
    LabelMgr --> Gmail

    Dashboard -->|"REST API calls\n(analyze, search, history,\ntaxonomy, bulk-upload)"| FastAPIApp
```

---

## 2. Port and URL Map

```mermaid
flowchart LR
    subgraph ports ["Network Layout"]
        P8000["Port 8000\nUnified FastAPI Backend\n(PO webhooks + Image API)"]
        P3000["Port 3000\nNext.js Frontend\n(Image Tagging Dashboard)"]
        NgrokURL["ngrok public URL\n(tunnels to 8000)"]
    end

    GAS_Triggers["GAS Triggers\n(EmailTrigger + DriveTrigger)"] -->|"WEBHOOK_URL\nIMAGE_WEBHOOK_URL"| NgrokURL
    NgrokURL --> P8000
    P3000 -->|"NEXT_PUBLIC_API_URL"| P8000
    Browser["Browser"] --> P3000
```

Both GAS triggers use the **same ngrok tunnel** (port 8000) with **different paths**:
- PO Parser: `https://<ngrok>/webhook/email`
- Image Tagger: `https://<ngrok>/webhook/drive-image`

---

## 3. API Endpoint Map

```mermaid
flowchart TD
    subgraph endpoints ["Unified FastAPI -- All Endpoints"]
        subgraph poEndpoints ["PO Parser Endpoints"]
            Health["GET /health"]
            WebhookEmail["POST /webhook/email\n(GAS email trigger)"]
        end

        subgraph imgEndpoints ["Image Tagger Endpoints"]
            Taxonomy["GET /api/taxonomy"]
            Analyze["POST /api/analyze-image\n(file upload)"]
            TagImage["GET /api/tag-image/{id}"]
            TagImages["GET /api/tag-images"]
            Search["GET /api/search-images"]
            Filters["GET /api/available-filters"]
            BulkUpload["POST /api/bulk-upload"]
            BulkStatus["GET /api/bulk-status/{id}"]
        end

        subgraph gasEndpoints ["GAS Integration Endpoints"]
            DriveImage["POST /webhook/drive-image\n(GAS Drive trigger)"]
        end
    end

    WebhookEmail -->|"runs in background"| POGraph2["po_parser graph"]
    Analyze --> IMGGraph2["image_tagging graph"]
    DriveImage -->|"runs in background"| IMGGraph2
    BulkUpload -->|"background per file"| IMGGraph2
```

---

## 4. PO Parser Agent -- Full Pipeline

### 4a. End-to-End Sequence

```mermaid
sequenceDiagram
    participant Gmail
    participant GAS as GAS EmailTrigger
    participant API as FastAPI :8000
    participant Graph as LangGraph po_parser
    participant OAI as OpenAI API
    participant AT as Airtable API
    participant GASWeb as GAS WebApp.gs
    participant Sheets as Google Sheets

    GAS->>Gmail: GmailApp.search (PO emails, every 5min)
    Gmail-->>GAS: Matching unread emails
    GAS->>API: POST /webhook/email (JSON + x-webhook-secret)
    API-->>GAS: 202 Accepted (immediate)

    Note over API,Graph: Background task starts

    API->>Graph: graph.invoke(initial_state)
    Graph->>OAI: Classify email (GPT-4o-mini, JSON mode)
    OAI-->>Graph: {is_po: true, confidence: 0.92}

    Note over Graph: route_after_classify: confidence >= 0.7 --> parse

    Graph->>Graph: parse_body (strip HTML, clean whitespace)
    Graph->>Graph: parse_pdf (pdfplumber -> PyMuPDF -> OCR fallback)
    Graph->>OAI: Vision OCR if text extraction fails
    OAI-->>Graph: OCR text
    Graph->>Graph: parse_excel (openpyxl / pandas)
    Graph->>Graph: consolidate (merge all text sections)
    Graph->>OAI: Extract structured PO (GPT-4o-mini, JSON mode)
    OAI-->>Graph: ExtractedPO JSON
    Graph->>Graph: normalize (dates, money, SKUs)
    Graph->>Graph: validate (required fields + Airtable duplicate check)
    Graph->>AT: find_po_by_number (duplicate check)
    AT-->>Graph: existing record or null
    Graph->>AT: create_po_record + create_po_items
    AT-->>Graph: record IDs + URLs
    Graph->>GASWeb: POST callback (JSON + secret + type=po_result)
    GASWeb->>Sheets: Write PO Data + PO Items + Monitoring
    GASWeb->>Gmail: Send notification + label PO-Processed
    GASWeb-->>Graph: {status: ok}
```

### 4b. LangGraph Node Flow

```mermaid
flowchart TD
    START(["START"]) --> classify["classify\n(OpenAI GPT-4o-mini)"]
    classify --> route{"route_after_classify"}
    route -->|"is_po=false OR\nconfidence < 0.7"| END1(["END\n(skip non-PO)"])
    route -->|"is_po=true AND\nconfidence >= 0.7"| parse_body["parse_body\n(clean email text)"]
    parse_body --> parse_pdf["parse_pdf\n(pdfplumber -> PyMuPDF -> OCR)"]
    parse_pdf --> parse_excel["parse_excel\n(openpyxl / pandas)"]
    parse_excel --> consolidate["consolidate\n(merge all text sections)"]
    consolidate --> extract["extract\n(OpenAI GPT-4o-mini JSON mode)"]
    extract --> normalize["normalize\n(dates, money, SKUs, customer names)"]
    normalize --> validate["validate\n(required fields + Airtable duplicate)"]
    validate --> write_airtable["write_airtable\n(create/update PO + line items)"]
    write_airtable --> callback_gas["callback_gas\n(POST to GAS WebApp.gs)"]
    callback_gas --> END2(["END"])
```

### 4c. PO Parser State Fields

```mermaid
flowchart LR
    subgraph stateFields ["AgentState (po_parser)"]
        email["email: IncomingEmail"]
        classification["classification: ClassificationResult\n{is_po, confidence, type}"]
        body_text["body_text: str"]
        pdf_texts["pdf_texts: list of str"]
        excel_data["excel_data: list of dicts"]
        consolidated_text["consolidated_text: str"]
        extracted_po["extracted_po: ExtractedPO"]
        normalized_po["normalized_po: ExtractedPO"]
        validation["validation: ValidationResult\n{status, issues, is_duplicate, is_revised}"]
        airtable_id["airtable_record_id: str"]
        airtable_url["airtable_url: str"]
        gas_status["gas_callback_status: str"]
        errors["errors: list of str"]
    end

    classify2["classify"] -->|writes| classification
    parse_body2["parse_body"] -->|writes| body_text
    parse_pdf2["parse_pdf"] -->|writes| pdf_texts
    parse_excel2["parse_excel"] -->|writes| excel_data
    consolidate2["consolidate"] -->|reads body_text, pdf_texts, excel_data\nwrites| consolidated_text
    extract2["extract"] -->|reads consolidated_text\nwrites| extracted_po
    normalize2["normalize"] -->|reads extracted_po\nwrites| normalized_po
    validate2["validate"] -->|reads normalized_po\nwrites| validation
    write_airtable2["write_airtable"] -->|reads normalized_po, validation\nwrites| airtable_id
    callback_gas2["callback_gas"] -->|reads all\nwrites| gas_status
```

---

## 5. Image Tagging Agent -- Full Pipeline

### 5a. End-to-End Sequence (Browser Upload)

```mermaid
sequenceDiagram
    participant User
    participant NextJS as Next.js :3000
    participant API as FastAPI :8000
    participant Graph as LangGraph image_tagging
    participant OAI as OpenAI API
    participant DB as Supabase PostgreSQL

    User->>NextJS: Upload image file
    NextJS->>API: POST /api/analyze-image (multipart)
    API->>API: Validate type, save to uploads/, base64 encode
    API->>Graph: graph.ainvoke(initial_state)

    Graph->>Graph: image_preprocessor (resize, validate)
    Graph->>OAI: vision_analyzer (GPT-4o describe image)
    OAI-->>Graph: vision_description + vision_raw_tags

    par 8 parallel taggers via Send API
        Graph->>OAI: season_tagger
        Graph->>OAI: theme_tagger
        Graph->>OAI: objects_tagger
        Graph->>OAI: color_tagger
        Graph->>OAI: design_tagger
        Graph->>OAI: occasion_tagger
        Graph->>OAI: mood_tagger
        Graph->>OAI: product_tagger
    end
    OAI-->>Graph: 8 TagResult items (merged via operator.add reducer)

    Graph->>Graph: tag_validator (validate against taxonomy)
    Graph->>Graph: confidence_filter (flag low-confidence tags)
    Graph->>Graph: tag_aggregator (build final tag_record)
    Graph-->>API: result (tag_record, flagged_tags, processing_status)

    opt Supabase enabled
        API->>DB: upsert_tag_record
    end

    API-->>NextJS: JSON response
    NextJS-->>User: Display tags, confidence, flagged items
```

### 5b. End-to-End Sequence (GAS Drive Trigger)

```mermaid
sequenceDiagram
    participant Drive as Google Drive
    participant GAS as GAS DriveTrigger
    participant API as FastAPI :8000
    participant Graph as LangGraph image_tagging
    participant OAI as OpenAI API
    participant DB as Supabase PostgreSQL
    participant GASWeb as GAS WebApp.gs
    participant Sheets as Google Sheets

    GAS->>Drive: Check folder for new images (every 5min)
    Drive-->>GAS: New image files since last check
    GAS->>GAS: Base64 encode image bytes
    GAS->>API: POST /webhook/drive-image (JSON + x-webhook-secret)
    API-->>GAS: 202 Accepted (immediate)

    Note over API,Graph: Background task starts

    API->>API: Decode base64, save to uploads/
    API->>Graph: graph.ainvoke(initial_state)
    Graph->>Graph: preprocessor -> vision -> 8 taggers -> validator -> confidence -> aggregator
    Graph-->>API: result

    opt Supabase enabled
        API->>DB: upsert_tag_record
    end

    API->>GASWeb: POST callback (JSON + secret + type=image_result)
    GASWeb->>Sheets: Write to Image Tags + Image Monitoring tabs
    GASWeb-->>API: {status: ok}
```

### 5c. LangGraph Node Flow

```mermaid
flowchart TD
    START2(["START"]) --> preprocessor["image_preprocessor\n(resize, validate format)"]
    preprocessor --> vision["vision_analyzer\n(GPT-4o describe image)"]
    vision -->|"fan_out_to_taggers\n(Send API, all 8 run in parallel)"| parallel

    subgraph parallel ["8 Parallel Taggers"]
        season["season_tagger"]
        theme["theme_tagger"]
        objects["objects_tagger"]
        color["color_tagger"]
        design["design_tagger"]
        occasion["occasion_tagger"]
        mood["mood_tagger"]
        product["product_tagger"]
    end

    parallel --> validator2["tag_validator\n(check against taxonomy)"]
    validator2 --> confidence["confidence_filter\n(flag low-confidence tags)"]
    confidence --> aggregator["tag_aggregator\n(build final tag_record)"]
    aggregator --> END3(["END"])
```

### 5d. Image Tagging State Fields

```mermaid
flowchart LR
    subgraph imgState ["ImageTaggingState"]
        img_id["image_id: str"]
        img_url["image_url: str"]
        img_b64["image_base64: str"]
        vision_desc["vision_description: str"]
        vision_raw["vision_raw_tags: dict"]
        partial["partial_tags: list\n(Annotated with operator.add\nfor parallel merge)"]
        validated["validated_tags: dict"]
        flagged["flagged_tags: list"]
        tag_rec["tag_record: dict"]
        proc_status["processing_status: str"]
        needs_rev["needs_review: bool"]
    end

    preprocessor2["preprocessor"] -->|writes| img_b64
    vision2["vision_analyzer"] -->|writes| vision_desc
    vision2 -->|writes| vision_raw
    taggers["8 taggers\n(parallel)"] -->|"each appends via\noperator.add reducer"| partial
    validator3["tag_validator"] -->|"reads partial\nwrites"| validated
    validator3 -->|writes| flagged
    confidence2["confidence_filter"] -->|"filters validated\nupdates"| flagged
    confidence2 -->|writes| needs_rev
    aggregator2["tag_aggregator"] -->|"reads validated\nwrites"| tag_rec
    aggregator2 -->|writes| proc_status
```

---

## 6. Shared Services Detail

```mermaid
flowchart TD
    subgraph services ["src/services/ -- Shared Across Agents"]
        subgraph openaiSvc ["openai/"]
            OAISettings["settings.py\n(OpenAISettings)"]
            OAIClient["client.py\n(chat_completion,\nvision_completion)"]
        end

        subgraph supabaseSvc ["supabase/"]
            SUPSettings["settings.py\n(DATABASE_URI)"]
            SUPClient["client.py\n(upsert_tag_record,\nlist_tag_images,\nsearch_images_filtered,\nget_available_filter_values)"]
        end

        subgraph airtableSvc ["airtable/"]
            ATSettings["settings.py\n(AIRTABLE_API_KEY,\nBASE_ID, tables)"]
            ATClient["client.py\n(create_po_record,\ncreate_po_items,\nfind_po_by_number,\nupload_file_to_field)"]
        end

        subgraph gasCallbackSvc ["gas_callback/"]
            GASSettings["settings.py\n(GAS_WEBAPP_URL,\nGAS_WEBAPP_SECRET)"]
            GASClient["client.py\n(send_results,\nsend_results_async)"]
        end
    end

    POGraph3["po_parser graph"] --> OAIClient
    POGraph3 --> ATClient
    POGraph3 --> GASClient
    IMGGraph3["image_tagging graph"] --> OAIClient
    IMGGraph3 --> SUPClient
    FastAPI3["main.py\n/webhook/drive-image"] --> GASClient
    FastAPI3 --> SUPClient
```

---

## 7. GAS Callback Routing

```mermaid
flowchart TD
    PythonCallback["Python gas_callback.send_results()"] -->|"POST JSON to GAS_WEBAPP_URL\n(secret in body)"| doPost["doPost(e)"]
    doPost --> authCheck{"payload.secret\n== GAS_WEBAPP_SECRET?"}
    authCheck -->|No| reject["Return error: Invalid secret"]
    authCheck -->|Yes| typeCheck{"payload.type?"}

    typeCheck -->|"po_result\n(default if missing)"| handlePO["handlePOResult()"]
    typeCheck -->|"image_result"| handleImg["handleImageResult()"]
    typeCheck -->|"unknown"| unknownErr["Return error: Unknown type"]

    handlePO --> writePOData["writePOData() -> PO Data tab"]
    handlePO --> writePOItems["writePOItems() -> PO Items tab"]
    handlePO --> writeMonLog["writeMonitoringLog() -> Monitoring tab"]
    handlePO --> sendNotif["sendPONotification()"]
    handlePO --> labelMsg["labelMessage() -> PO-Processed"]

    handleImg --> writeImgData["writeImageData() -> Image Tags tab"]
    handleImg --> writeImgMon["writeImageMonitoringLog() -> Image Monitoring tab"]
```

---

## 8. Data Persistence Map

```mermaid
flowchart LR
    subgraph poData ["PO Parser Data Stores"]
        AT_PO["Airtable: Customer POs\n(PO Number, Customer, dates,\nStatus, Raw Extract JSON)"]
        AT_Items["Airtable: PO Items\n(SKU, Description, Qty,\nUnit Price, Total, DC)"]
        GS_PO["Google Sheets: PO Data tab"]
        GS_Items["Google Sheets: PO Items tab"]
        GS_Mon["Google Sheets: Monitoring Logs tab"]
    end

    subgraph imgData ["Image Tagger Data Stores"]
        SUP_Tags["Supabase: image_tags table\n(image_id, tag_record,\nsearch_index, image_url,\nneeds_review, processing_status)"]
        GS_Img["Google Sheets: Image Tags tab"]
        GS_ImgMon["Google Sheets: Image Monitoring tab"]
        Uploads["Local filesystem:\napps/agents/uploads/"]
    end

    POGraph4["po_parser"] -->|"pyairtable"| AT_PO
    POGraph4 -->|"pyairtable"| AT_Items
    GASCallback1["GAS callback\ntype=po_result"] --> GS_PO
    GASCallback1 --> GS_Items
    GASCallback1 --> GS_Mon

    IMGGraph4["image_tagging"] -->|"psycopg2"| SUP_Tags
    FastAPI4["main.py"] -->|"write_bytes"| Uploads
    GASCallback2["GAS callback\ntype=image_result"] --> GS_Img
    GASCallback2 --> GS_ImgMon
```

---

## 9. Security and Authentication

```mermaid
flowchart TD
    subgraph secrets ["Secrets Flow"]
        subgraph gasToP ["GAS --> Python"]
            GAS1["GAS trigger"] -->|"x-webhook-secret header\n= WEBHOOK_SECRET"| FastAPI5["FastAPI middleware\nverify_webhook_secret()"]
        end

        subgraph pToGAS ["Python --> GAS"]
            GASCb["GASCallbackClient"] -->|"secret field in JSON body\n= GAS_WEBAPP_SECRET"| doPost2["GAS doPost()\nvalidates payload.secret"]
        end

        subgraph apiKeys ["API Keys"]
            OpenAIKey["OPENAI_API_KEY\n(env var)"]
            AirtableKey["AIRTABLE_API_KEY\n(env var)"]
            DBUri["DATABASE_URI\n(env var)"]
            LangSmithKey["LANGCHAIN_API_KEY\n(env var, optional)"]
        end
    end

    subgraph storage ["Where Secrets Live"]
        EnvFile[".env at repo root\n(gitignored)"]
        ScriptProps["GAS Script Properties\n(in Apps Script editor)"]
    end

    EnvFile -->|"docker-compose\nenv_file: .env"| FastAPI5
    EnvFile -->|"docker-compose\nenv_file: .env"| GASCb
    EnvFile --> OpenAIKey
    EnvFile --> AirtableKey
    EnvFile --> DBUri
    ScriptProps -->|"getConfig()"| GAS1
    ScriptProps -->|"getConfig()"| doPost2
```

---

## 10. Deployment Architecture

```mermaid
flowchart TB
    subgraph local ["Local Development"]
        IDE["Cursor IDE"]
        Clasp["clasp CLI"]
        DockerDesktop["Docker Desktop"]
    end

    subgraph containers ["Docker Compose"]
        AgentsContainer["agents service\n(Python :8000)"]
        FrontendContainer["frontend service\n(Next.js :3000)"]
    end

    subgraph googlePlatform ["Google Platform"]
        GASRuntime["Apps Script Runtime"]
        GmailSvc["Gmail"]
        DriveSvc["Google Drive"]
        SheetsSvc["Google Sheets"]
    end

    subgraph external2 ["External"]
        OpenAI2["OpenAI API"]
        Airtable2["Airtable"]
        Supabase2["Supabase"]
        NgrokTunnel["ngrok tunnel"]
    end

    subgraph observability2 ["Observability"]
        LangSmith2["LangSmith"]
        Studio2["LangGraph Studio"]
    end

    IDE -->|"clasp push"| GASRuntime
    IDE -->|"docker compose up"| DockerDesktop
    DockerDesktop --> containers
    AgentsContainer --> OpenAI2
    AgentsContainer --> Airtable2
    AgentsContainer --> Supabase2
    AgentsContainer -.->|"traces"| LangSmith2
    AgentsContainer -.->|"visualize"| Studio2
    NgrokTunnel --> AgentsContainer
    GASRuntime -->|"webhooks via ngrok"| NgrokTunnel
    GASRuntime --> GmailSvc
    GASRuntime --> DriveSvc
    GASRuntime --> SheetsSvc
    FrontendContainer -->|"API calls"| AgentsContainer
```