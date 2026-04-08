# Lab 01 — User Clicks Analyze

**Estimated time:** 25 min  
**Difficulty:** Beginner

When the user selects an image and clicks "Analyze," two things happen: the **ImageUploader** component calls a function passed from the parent, and the **Home** page sends that file to the backend via HTTP. This lab traces that flow with exact line numbers.

---

## Learning objectives

- See how a React component receives a callback (props) and calls it with user data (the file).
- See how the page builds a `FormData` and sends a `POST` request with `fetch`.
- Understand the frontend state (e.g. `isProcessing`, `analysisResult`) at this stage.

---

## Prerequisites

- [00-prerequisites.md](00-prerequisites.md) — especially React (components, props, state) and HTTP (request/response).

---

## Step 1 — ImageUploader: user clicks "Analyze"

The user has already dropped or selected a file. The dropzone shows a preview and an "Analyze" button. When they click it, the component calls `onAnalyze(file)`.

> **File Type — .tsx:** A TypeScript file that also contains JSX (HTML-like markup). Used for React components.

**Snippet (lines 75–84 in ImageUploader.tsx)**

```tsx
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
```

**What is happening**

- `onClick` runs when the user clicks the button.
- `e.stopPropagation()` prevents the click from bubbling to the parent dropzone (so the dropzone does not think you clicked to open the file picker again).
- `onAnalyze(file)` calls the function that the parent (Home page) passed in as the `onAnalyze` prop. The argument is the single `File` object from `acceptedFiles[0]` (line 46).
- `disabled={disabled}` grays out the button when the parent says processing is in progress.

**Source:** [frontend/src/components/ImageUploader.tsx](../../frontend/src/components/ImageUploader.tsx) (lines 75–84)

> **Glossary:** **props** — Inputs passed to a component by its parent. Here, `onAnalyze` and `disabled` are props of `ImageUploader`.

> **State Tracker (ImageUploader):** `error` is the only local state; it may be set if the user dropped an invalid file. `file` is the selected file from the dropzone. The parent’s state (`analysisResult`, `isProcessing`) is not in this component.

> **I/O Snapshot:** **Input:** User click event. **Output:** Call to `onAnalyze(file)` where `file` is a browser `File` (e.g. `{ name: "photo.jpg", size: 102400, type: "image/jpeg" }`).

> **Error Path:** If the user never selected a file, `file` would be `undefined` and the Analyze button would not be shown (the UI only shows it when `file` is truthy). So at click time we always have a valid `File`.

> **Next:** Execution continues in the parent: `handleAnalyze(file)` in [Lab 01 — Step 2](#step-2--home-page-handleanalyze-receives-the-file).

---

## Step 2 — Home page: handleAnalyze receives the file

The Home page defined `handleAnalyze` and passed it to ImageUploader as `onAnalyze={handleAnalyze}`. So when the user clicked "Analyze," that function is now invoked with the `File` object.

**Snippet (lines 31–39 in page.tsx)**

```tsx
async function handleAnalyze(file: File) {
  setError(null);
  setIsProcessing(true);
  setCurrentStep(1);

  const formData = new FormData();
  formData.append("file", file);
  setCurrentStep(2);
```

**What is happening**

- `setError(null)` clears any previous error message.
- `setIsProcessing(true)` tells React that we are now in “processing” mode; the UI will show the processing overlay and can disable the uploader.
- `setCurrentStep(1)` resets the step indicator (used by the overlay).
- `new FormData()` creates an empty form payload. We use FormData because we are sending a file (multipart request).
- `formData.append("file", file)` adds the image under the key `"file"`. The backend expects a field named `file` (see Lab 02).
- `setCurrentStep(2)` advances the visible step before the network call.

> **Glossary:** **FormData** — A web API object that holds key-value pairs (and files) to send in an HTTP request body. Used for `multipart/form-data` uploads.

> **State Tracker (Home page):** At this point: `isProcessing === true`, `currentStep === 2`, `error === null`, `analysisResult` unchanged (still null or previous result). The request has not been sent yet.

> **Why This Way?** We use FormData instead of JSON because the body is a binary file. JSON cannot represent raw binary efficiently; multipart/form-data is the standard way to upload files in browsers.

> **Next:** Execution continues at [Lab 01 — Step 3](#step-3--fetch-post-to-the-api).

---

## Step 3 — fetch POST to the API

The same function now sends the request and waits for the response.

**Snippet (lines 40–55 in page.tsx)**

```tsx
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
```

**What is happening**

- `fetch(url, { method: "POST", body: formData })` sends an HTTP POST to the backend. The browser sets the `Content-Type` header to `multipart/form-data` with a boundary when the body is FormData. No need to set it manually.
- `API_BASE_URL` comes from `@/lib/constants` (e.g. `http://localhost:8000`). So the full URL is `http://localhost:8000/api/analyze-image`.
- `await` pauses until the server responds. The server will run the full pipeline (Labs 02–11) before responding.
- `res.ok` is false when status is not 2xx. We then try to parse the body as JSON (the backend returns `{ "detail": "..." }` on error) and throw an Error with that message so the catch block can set `error` state.
- `res.json()` parses the response body as JSON. The type is `AnalyzeImageResponse` (image_url, tag_record, tags_by_category, etc.).
- `setCurrentStep(MAX_STEP)` and the short delay are for the UI (overlay shows “complete” briefly).
- `setAnalysisResult(data)` stores the result so the next render shows `DashboardResult` instead of the upload form (see Lab 12).

**Source:** [frontend/src/app/page.tsx](../../frontend/src/app/page.tsx) (lines 40–55)

> **State Tracker (after success):** `isProcessing` will be set to `false` in `finally` (below). `analysisResult` is now the full API response object. `error` is still null.

> **I/O Snapshot:** **Request:** `POST /api/analyze-image`, body = FormData with one field `file` (the image file). **Response (200):** JSON like `{ "image_id": "...", "image_url": "...", "tag_record": { ... }, "tags_by_category": { ... }, "processing_status": "complete", "saved_to_db": true, ... }`.

> **Error Path:** If the server returns 400 (e.g. invalid file type), 500 (e.g. graph error), or the network fails, we jump to the `catch` block: `setError(message)` and `setIsProcessing(false)`. The user sees the error message and can try again. The `finally` block always runs and sets `isProcessing` to false.

> **Next:** Execution continues on the **server**: the request has been received by FastAPI. See [02-server-receives-image.md](02-server-receives-image.md) Step 1.

---

## Lab summary

1. User clicks "Analyze" in **ImageUploader** → `onAnalyze(file)` is called with the selected file.
2. **Home**’s `handleAnalyze(file)` runs: it clears error, sets processing state, builds **FormData** with the file, and sends **POST** to `/api/analyze-image` with **fetch**.
3. When the response comes back, the frontend parses JSON and calls **setAnalysisResult(data)**. The UI then re-renders and shows the result (Lab 12).

---

## Exercises

1. In ImageUploader, why is `onAnalyze` passed as a prop instead of being defined inside the component?
2. What would happen if we sent the file as `formData.append("image", file)` instead of `"file"`? (Hint: check the backend parameter name in Lab 02.)
3. If the server takes 30 seconds to respond, what does the user see during that time (state and UI)?

---

## Next lab

Go to [02-server-receives-image.md](02-server-receives-image.md) to see how the FastAPI server receives the request, validates the file, saves it to disk, and prepares the initial state for the graph.
