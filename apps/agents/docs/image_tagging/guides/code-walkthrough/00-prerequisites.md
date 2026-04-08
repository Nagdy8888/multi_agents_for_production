# Lab 0 — Before You Start

**Estimated time:** 30–45 min  
**Difficulty:** Foundation

This lab gives you just enough background so the rest of the walkthrough makes sense. You do not need to be an expert in any of these; you only need to recognize the ideas when they appear in the code.

---

## Learning objectives

- Recognize what Python, JavaScript/TypeScript, HTTP, JSON, async/await, React, API, database, and Docker are and why they appear in this project.
- Know what a request/response and status code are.
- Know what a component, props, and state are in React terms.

---

## Prerequisites

None — this is the starting point.

---

## 1. Python

**What it is:** A programming language. This project’s **backend** (the server that receives uploads and runs the AI pipeline) is written in Python.

**You’ll see:** Files ending in `.py`. Functions defined with `def`, async functions with `async def`. Imports at the top (`from fastapi import ...`). No need to write Python to follow the labs; we explain each snippet.

---

## 2. JavaScript and TypeScript

**What they are:** Languages that run in the **browser** and (with Node.js) on the server. **TypeScript** is JavaScript with types (e.g. “this variable is a string”). This project’s **frontend** (the web UI) is written in TypeScript/React.

**You’ll see:** Files ending in `.ts` or `.tsx`. `.tsx` = TypeScript + JSX (HTML-like syntax inside the file). Example:

```ts
const [count, setCount] = useState(0);  // state: a value that can change and trigger re-render
```

---

## 3. HTTP — request and response

**What it is:** The protocol the browser uses to talk to the server. The browser sends a **request** (URL, method like GET or POST, sometimes a body). The server sends back a **response** (status code, body, headers).

**Terms:**

- **Request:** “Get this URL” (GET) or “Here is data, process it” (POST).
- **Response:** What the server returns (often JSON in the body).
- **Status code:** Number indicating outcome, e.g. 200 = OK, 400 = bad request, 404 = not found, 500 = server error.

**In this project:** The frontend sends `POST /api/analyze-image` with the image file; the backend returns 200 and a JSON object with tags and status.

---

## 4. JSON

**What it is:** A text format for data: key–value pairs and lists. Both frontend and backend use it to send structured data.

**Example:**

```json
{
  "image_id": "abc-123",
  "processing_status": "complete",
  "tags_by_category": { "season": ["christmas"], "mood": ["joyful_fun"] }
}
```

**In this project:** The API response is JSON; the graph state is merged like a dict; the database stores a “tag record” as JSON.

---

## 5. Async / await

**What it is:** Code that can “wait” for slow operations (network, disk, AI API) without blocking. `async` marks a function that can wait; `await` waits for a result.

**Python example:**

```python
async def analyze_image(...):
    result = await graph.ainvoke(initial_state)  # wait for pipeline to finish
    return result
```

**JavaScript example:**

```ts
const res = await fetch(url);  // wait for server response
const data = await res.json(); // wait for body to be parsed
```

---

## 6. React — components, props, state, hooks

**What it is:** A library for building the UI. The screen is built from **components** (reusable pieces). Each component can have **props** (inputs passed from the parent) and **state** (data it owns that can change). **Hooks** (e.g. `useState`, `useEffect`) let components use state and run logic when things change.

**Terms:**

- **Component:** A function that returns JSX (the HTML-like UI). Example: `ImageUploader`, `DashboardResult`.
- **Props:** Arguments passed to the component, e.g. `onAnalyze={handleAnalyze}`, `data={analysisResult}`.
- **State:** Data held inside the component that, when updated, causes a re-render. Example: `analysisResult`, `filters`.
- **Hook:** A function like `useState` or `useEffect` used inside a component to manage state or side effects.

**In this project:** The home page has state `analysisResult`; when the server responds, we call `setAnalysisResult(data)` and the UI re-renders to show `DashboardResult`.

---

## 7. API

**What it is:** An **Application Programming Interface** — in web terms, a set of **endpoints** (URLs + methods) the server exposes so the client can request or send data.

**Endpoint:** One URL + method, e.g. `POST /api/analyze-image` (upload and analyze), `GET /api/search-images?season=christmas` (search by tags).

**In this project:** The backend is the “API server”; the frontend calls it with `fetch()` to analyze images, search, or get bulk status.

---

## 8. Database

**What it is:** Persistent storage. The server can save results so they survive restarts and can be searched later.

**In this project:** We use **PostgreSQL** (via Supabase). The backend saves each analysis as a row (e.g. `image_id`, `tag_record`, `search_index`). Search is implemented by querying that table with filters.

---

## 9. Docker

**What it is:** A way to run the app in **containers** — isolated environments with the right Python/Node versions and dependencies. **Docker Compose** runs both backend and frontend containers together.

**In this project:** You can run `docker compose up --build` and get the backend on port 8000 and the frontend on port 3000 without installing Python or Node locally. The labs refer to “the server” and “the frontend” whether you run them via Docker or directly.

---

## Summary

- **Backend (Python):** Receives requests, runs the AI pipeline (LangGraph), talks to the database, returns JSON.
- **Frontend (TypeScript/React):** Renders the UI, sends HTTP requests to the API, updates state when responses arrive, shows results.
- **HTTP/JSON:** The language they use to communicate.
- **Async:** Used whenever we wait for the network or the AI.
- **Database:** Where we store and search tag results.
- **Docker:** One way to run both backend and frontend.

---

## Next

Go to [01-user-clicks-analyze.md](01-user-clicks-analyze.md) to see what happens when the user selects an image and clicks "Analyze" — from the first React component to the `fetch` call.
