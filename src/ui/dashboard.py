"""Modern, interactive Web Dashboard for the LLM CI/CD Regression & Red-Teaming Engine with Light & Dark Modes."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Regress Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    /* ========================================================
       Theme Variables: Light Mode (Default) & Dark Mode
       Light Mode: White Primary with Black & Red Accents
       Dark Mode:  Black Primary with White & Cream Accents
       ======================================================== */
    :root {
      --bg-primary: #ffffff;
      --bg-secondary: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-hover: #fbfcfd;
      --border-color: rgba(9, 9, 11, 0.12);
      --border-focus: #dc2626;
      --border-strong: #09090b;
      --text-main: #09090b;
      --text-muted: #52525b;
      --accent-red: #dc2626;
      --accent-red-hover: #b91c1c;
      --accent-black: #09090b;
      --accent-black-hover: #27272a;
      --btn-bg: #09090b;
      --btn-text: #ffffff;
      --btn-highlight: #dc2626;
      --btn-highlight-text: #ffffff;
      --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
      --card-shadow-hover: 0 10px 30px rgba(0, 0, 0, 0.1);
      --console-bg: #09090b;
      --console-text: #f8fafc;
      --console-border: #18181b;
      --badge-bg: #fee2e2;
      --badge-text: #991b1b;
      --badge-border: #fca5a5;
      --pulse-color: #dc2626;
      --toggle-bg: #e4e4e7;
      --toggle-circle: #09090b;
      --input-bg: #ffffff;
      --input-border: #d4d4d8;
      --topo-bg: #f8fafc;
      --topo-border: #e4e4e7;
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    [data-theme="dark"] {
      --bg-primary: #050508;
      --bg-secondary: #0c0d12;
      --bg-card: #0e1017;
      --bg-card-hover: #141722;
      --border-color: rgba(255, 255, 255, 0.1);
      --border-focus: #faeed9;
      --border-strong: #ffffff;
      --text-main: #ffffff;
      --text-muted: #a1a1aa;
      --accent-red: #faeed9; /* Cream highlight */
      --accent-red-hover: #f3dfbf;
      --accent-black: #ffffff;
      --accent-black-hover: #f4f4f5;
      --btn-bg: #faeed9; /* Cream button */
      --btn-text: #050508;
      --btn-highlight: #ffffff;
      --btn-highlight-text: #050508;
      --card-shadow: 0 4px 25px rgba(0, 0, 0, 0.8);
      --card-shadow-hover: 0 12px 36px rgba(0, 0, 0, 0.95);
      --console-bg: #000000;
      --console-text: #faeed9; /* Cream console font */
      --console-border: rgba(250, 238, 217, 0.2);
      --badge-bg: rgba(250, 238, 217, 0.15);
      --badge-text: #faeed9;
      --badge-border: rgba(250, 238, 217, 0.35);
      --pulse-color: #faeed9;
      --toggle-bg: #27272a;
      --toggle-circle: #faeed9;
      --input-bg: #07080c;
      --input-border: rgba(255, 255, 255, 0.15);
      --topo-bg: #0c0d14;
      --topo-border: rgba(255, 255, 255, 0.08);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.25s ease, border-color 0.25s ease, color 0.2s ease; }

    body {
      background-color: var(--bg-primary);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* Header */
    header {
      backdrop-filter: blur(16px);
      background: var(--bg-primary);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 1.1rem 2.25rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .brand-title {
      font-weight: 800;
      font-size: 1.35rem;
      letter-spacing: -0.03em;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    /* Dark Mode Switcher */
    .theme-switch-container {
      display: flex;
      align-items: center;
      padding: 0.25rem 0.35rem;
      background: var(--topo-bg);
      border: 1px solid var(--border-color);
      border-radius: 9999px;
      cursor: pointer;
      user-select: none;
    }

    .theme-toggle {
      width: 44px;
      height: 24px;
      background: var(--toggle-bg);
      border-radius: 9999px;
      position: relative;
      cursor: pointer;
      transition: background 0.3s ease;
    }

    .theme-toggle-knob {
      width: 18px;
      height: 18px;
      background: var(--toggle-circle);
      border-radius: 50%;
      position: absolute;
      top: 3px;
      left: 3px;
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    [data-theme="dark"] .theme-toggle-knob {
      transform: translateX(20px);
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
    }

    .status-pulse {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--pulse-color);
      box-shadow: 0 0 10px var(--pulse-color);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.3); }
      100% { opacity: 1; transform: scale(1); }
    }

    .btn-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.825rem;
      font-weight: 500;
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      transition: all 0.2s ease;
    }
    .btn-link:hover {
      color: var(--text-main);
      border-color: var(--border-strong);
    }

    /* Main Container */
    main {
      flex: 1;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
      padding: 2.25rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    /* Topology Strip */
    .topo-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
    }
    @media (max-width: 768px) {
      .topo-grid { grid-template-columns: repeat(2, 1fr); }
    }

    .topo-item {
      background: var(--topo-bg);
      border: 1px solid var(--topo-border);
      border-radius: 12px;
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
    }

    .topo-name {
      font-size: 0.725rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-weight: 600;
    }

    .topo-val {
      font-size: 0.95rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    /* Grid Layout */
    .dashboard-grid {
      display: grid;
      grid-template-columns: 1fr 1.55fr;
      gap: 2rem;
    }

    @media (max-width: 1024px) {
      .dashboard-grid { grid-template-columns: 1fr; }
    }

    /* Cards */
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.85rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      box-shadow: var(--card-shadow);
      transition: all 0.25s ease;
    }
    .card:hover {
      box-shadow: var(--card-shadow-hover);
      border-color: var(--border-strong);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 0.6rem;
      border-bottom: 1px solid var(--border-color);
    }

    .card-title {
      font-size: 1.125rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      letter-spacing: -0.01em;
    }

    /* Form Fields */
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.45rem;
    }

    label {
      font-size: 0.825rem;
      font-weight: 600;
      color: var(--text-main);
    }

    input, select {
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 8px;
      padding: 0.75rem 0.95rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: all 0.2s ease;
    }

    input:focus, select:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15);
    }

    [data-theme="dark"] input:focus, [data-theme="dark"] select:focus {
      box-shadow: 0 0 0 3px rgba(250, 238, 217, 0.25);
    }

    .checkbox-container {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.65rem 0.85rem;
      background: var(--topo-bg);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      cursor: pointer;
    }

    .checkbox-container input[type="checkbox"] {
      width: 16px;
      height: 16px;
      accent-color: var(--accent-red);
      cursor: pointer;
    }

    .btn-submit {
      background: var(--btn-highlight);
      color: var(--btn-highlight-text);
      font-weight: 700;
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 0.95rem 1.5rem;
      font-size: 0.95rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      letter-spacing: -0.01em;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    }

    .btn-submit:hover {
      background: var(--accent-red-hover);
      transform: translateY(-1px);
    }

    [data-theme="dark"] .btn-submit {
      background: var(--btn-bg);
      color: var(--btn-text);
      box-shadow: 0 4px 16px rgba(250, 238, 217, 0.2);
    }

    [data-theme="dark"] .btn-submit:hover {
      background: #ffffff;
    }

    .btn-submit:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    /* Output Console */
    .console-box {
      background: var(--console-bg);
      border: 1px solid var(--console-border);
      border-radius: 12px;
      padding: 1.35rem;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--console-text);
      min-height: 320px;
      max-height: 520px;
      overflow-y: auto;
      white-space: pre-wrap;
      line-height: 1.65;
      box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
    }

    /* Spinner */
    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    [data-theme="dark"] .spinner {
      border: 2px solid rgba(5, 5, 8, 0.3);
      border-top-color: #050508;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-title">Regress Engine</div>
    </div>
    <div class="nav-actions">
      <!-- Theme Switcher -->
      <div class="theme-switch-container" onclick="toggleTheme()" title="Toggle Light / Dark Mode">
        <div class="theme-toggle">
          <div class="theme-toggle-knob" id="theme-knob"></div>
        </div>
      </div>

      <div class="status-badge">
        <div class="status-pulse"></div>
        <span id="sys-status">Live & Guarding</span>
      </div>
      <a href="/docs" target="_blank" class="btn-link">OpenAPI Docs</a>
      <a href="https://github.com/prasoon-21/llm-regression-engine" target="_blank" class="btn-link">GitHub Repo</a>
      <a href="https://smith.langchain.com" target="_blank" class="btn-link">LangSmith</a>
    </div>
  </header>

  <main>
    <!-- System Topology Summary -->
    <div class="topo-grid">
      <div class="topo-item">
        <span class="topo-name">Task Broker</span>
        <span class="topo-val">Upstash Redis (Live)</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Trace Harvester</span>
        <span class="topo-val">LangSmith Traces</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Storage</span>
        <span class="topo-val">Supabase Postgres</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Telemetry</span>
        <span class="topo-val">PostHog Analytics</span>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="dashboard-grid">
      <!-- Left Panel: Trigger Form -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Dispatch Evaluation Run</div>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5;">
          Trigger an on-demand regression check or adversarial red-teaming sweep against candidate LLM traces.
        </p>

        <form id="trigger-form" onsubmit="handleTrigger(event)">
          <div class="form-group">
            <label for="repo">GitHub Repository</label>
            <input type="text" id="repo" value="prasoon-21/llm-regression-engine" required>
          </div>

          <div class="form-group" style="margin-top: 0.85rem;">
            <label for="commit">Commit SHA</label>
            <input type="text" id="commit" value="3de3eea" required>
          </div>

          <div class="form-group" style="margin-top: 0.85rem;">
            <label for="pr_num">Pull Request # (Optional)</label>
            <input type="number" id="pr_num" value="1" placeholder="e.g. 42">
          </div>

          <div class="form-group" style="margin-top: 0.85rem;">
            <label for="model">Target Evaluation Model</label>
            <select id="model">
              <option value="gemini-1.5-flash">Google Gemini 1.5 Flash</option>
              <option value="groq/llama-3.3-70b">Groq Llama 3.3 70B</option>
              <option value="gpt-4o">OpenAI GPT-4o</option>
            </select>
          </div>

          <div class="form-group" style="margin-top: 1rem;">
            <label class="checkbox-container">
              <input type="checkbox" id="adversarial" checked>
              <span style="font-size: 0.825rem; font-weight: 500;">Include Adversarial Red-Teaming (Prompt Injections & Jailbreaks)</span>
            </label>
          </div>

          <button type="submit" id="submit-btn" class="btn-submit" style="margin-top: 1.5rem; width: 100%;">
            <span>Run Regression & Red-Team Audit</span>
          </button>
        </form>
      </div>

      <!-- Right Panel: Live Execution Console -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Execution Console & Audit Feed</div>
          <span id="active-job-badge" style="font-size: 0.75rem; font-weight: 600; font-family: var(--font-mono);">IDLE</span>
        </div>
        <div class="console-box" id="console-output">Ready. Waiting for incoming GitHub Webhook or manual dispatch...</div>
      </div>
    </div>

    <!-- Live Status Checker Card -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">Inspect Job Status by ID</div>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <input type="text" id="inspect-job-id" placeholder="Enter Job ID (e.g. manual-abc12345)" style="flex: 1;">
        <button class="btn-submit" onclick="inspectJob()" style="padding: 0.75rem 1.35rem; width: auto;">Query Status</button>
      </div>
      <div id="job-detail-card" style="display: none; margin-top: 1rem; padding: 1.15rem; background: var(--topo-bg); border: 1px solid var(--border-color); border-radius: 8px;"></div>
    </div>
  </main>

  <script>
    // Theme Management: Light Mode (Default) & Dark Mode
    function initTheme() {
      const savedTheme = localStorage.getItem('theme') || 'light';
      applyTheme(savedTheme);
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem('theme', next);
    }

    function applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
    }

    initTheme();

    // Trigger Handling
    async function handleTrigger(e) {
      e.preventDefault();
      const btn = document.getElementById('submit-btn');
      const consoleBox = document.getElementById('console-output');
      const badge = document.getElementById('active-job-badge');

      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div><span>Dispatching to Redis Broker...</span>';

      const payload = {
        repository: document.getElementById('repo').value,
        commit_sha: document.getElementById('commit').value,
        pull_request_number: document.getElementById('pr_num').value ? parseInt(document.getElementById('pr_num').value) : null,
        model_override: document.getElementById('model').value,
        enable_adversarial: document.getElementById('adversarial').checked,
        langsmith_project: "llm-ci-cd-regression-engine"
      };

      try {
        consoleBox.innerText = `[INFO] Sending dispatch payload for ${payload.repository} @ ${payload.commit_sha}...\n`;
        const res = await fetch('/api/v1/jobs/trigger', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.status === 202) {
          consoleBox.innerText += `[SUCCESS] Job enqueued into Upstash Redis Task Broker!\n[JOB ID]: ${data.job_id}\n\n[INFO] Background Worker is now processing:\n - Harvesting golden traces from LangSmith\n - Mutating adversarial prompt injections\n - Auditing schema conformance & LLM-as-a-Judge\n - Generating Markdown regression report...\n`;
          badge.innerText = `RUNNING: ${data.job_id}`;
          badge.style.color = '#dc2626';
          pollJob(data.job_id);
        } else {
          consoleBox.innerText += `[ERROR] Failed to enqueue: ${JSON.stringify(data)}\n`;
        }
      } catch (err) {
        consoleBox.innerText += `[ERROR] Connection failed: ${err.message}\n`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Run Regression & Red-Team Audit</span>';
      }
    }

    async function pollJob(jobId) {
      const consoleBox = document.getElementById('console-output');
      const badge = document.getElementById('active-job-badge');

      for (let i = 0; i < 25; i++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          const res = await fetch(`/api/v1/jobs/${jobId}`);
          if (res.ok) {
            const job = await res.json();
            if (job.status === 'completed' || job.status === 'regression_detected') {
              badge.innerText = `DONE: ${job.status.toUpperCase()}`;
              badge.style.color = job.status === 'completed' ? '#16a34a' : '#dc2626';
              consoleBox.innerText += `\n[COMPLETED] Status: ${job.status.toUpperCase()}\n`;
              if (job.result && job.result.markdown_report) {
                consoleBox.innerText += `\n=== MARKDOWN PR COMMENT REPORT ===\n\n${job.result.markdown_report}`;
              }
              return;
            }
          }
        } catch (e) {}
      }
    }

    async function inspectJob() {
      const id = document.getElementById('inspect-job-id').value.trim();
      if (!id) return;
      const detailCard = document.getElementById('job-detail-card');
      detailCard.style.display = 'block';
      detailCard.innerText = 'Fetching job details...';
      try {
        const res = await fetch(`/api/v1/jobs/${id}`);
        if (!res.ok) {
          detailCard.innerText = 'Job not found.';
          return;
        }
        const data = await res.json();
        detailCard.innerHTML = `<pre style="font-family: var(--font-mono); font-size: 0.8rem; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>`;
      } catch (e) {
        detailCard.innerText = `Error: ${e.message}`;
      }
    }
  </script>
</body>
</html>
"""
