"""Minimalist Web Dashboard for Regress Engine with Light & Dark Modes."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Regress Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #ffffff;
      --bg-card: #ffffff;
      --bg-subtle: #f9fafb;
      --border-color: #e5e7eb;
      --border-focus: #111827;
      --text-main: #111827;
      --text-muted: #6b7280;
      --accent: #dc2626;
      --accent-hover: #b91c1c;
      --btn-bg: #dc2626;
      --btn-text: #ffffff;
      --btn-sec-bg: #f3f4f6;
      --btn-sec-text: #111827;
      --console-bg: #09090b;
      --console-text: #f9fafb;
      --console-border: #27272a;
      --toggle-bg: #e5e7eb;
      --toggle-knob: #111827;
      --input-bg: #ffffff;
      --input-border: #d1d5db;
      --status-idle: #6b7280;
      --status-active: #dc2626;
      --status-success: #16a34a;
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    [data-theme="dark"] {
      --bg-primary: #000000;
      --bg-card: #09090b;
      --bg-subtle: #111217;
      --border-color: #27272a;
      --border-focus: #ffffff;
      --text-main: #ffffff;
      --text-muted: #a1a1aa;
      --accent: #faeed9;
      --accent-hover: #f5f0e6;
      --btn-bg: #faeed9;
      --btn-text: #000000;
      --btn-sec-bg: #18181b;
      --btn-sec-text: #ffffff;
      --console-bg: #050505;
      --console-text: #faeed9;
      --console-border: #27272a;
      --toggle-bg: #27272a;
      --toggle-knob: #faeed9;
      --input-bg: #09090b;
      --input-border: #27272a;
      --status-idle: #71717a;
      --status-active: #faeed9;
      --status-success: #4ade80;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-primary);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }

    /* Minimal Header */
    header {
      background: var(--bg-primary);
      border-bottom: 1px solid var(--border-color);
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
      transition: color 0.15s ease;
    }
    .nav-link:hover {
      color: var(--text-main);
    }

    /* Minimal Toggle Switch */
    .theme-toggle {
      width: 40px;
      height: 22px;
      background: var(--toggle-bg);
      border-radius: 9999px;
      position: relative;
      cursor: pointer;
      display: inline-block;
      transition: background 0.2s ease;
    }

    .theme-toggle-knob {
      width: 16px;
      height: 16px;
      background: var(--toggle-knob);
      border-radius: 50%;
      position: absolute;
      top: 3px;
      left: 3px;
      transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    [data-theme="dark"] .theme-toggle-knob {
      transform: translateX(18px);
    }

    /* Workspace */
    main {
      flex: 1;
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
      padding: 2.5rem 2rem;
    }

    .workspace-grid {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 2.5rem;
      align-items: start;
    }

    @media (max-width: 960px) {
      .workspace-grid {
        grid-template-columns: 1fr;
      }
    }

    /* Section Cards */
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.75rem;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }

    .card-title {
      font-size: 1rem;
      font-weight: 600;
      letter-spacing: -0.01em;
    }

    .card-status {
      font-size: 0.75rem;
      font-weight: 600;
      font-family: var(--font-mono);
      color: var(--status-idle);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Forms & Inputs */
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }

    label {
      font-size: 0.8125rem;
      font-weight: 500;
      color: var(--text-main);
    }

    input[type="text"], input[type="number"], select {
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      border-radius: 6px;
      padding: 0.65rem 0.8rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.875rem;
      outline: none;
      transition: border-color 0.15s ease;
    }

    input:focus, select:focus {
      border-color: var(--border-focus);
    }

    .checkbox-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-top: 0.5rem;
      margin-bottom: 1.5rem;
      cursor: pointer;
    }

    .checkbox-row input {
      accent-color: var(--accent);
      cursor: pointer;
    }

    .checkbox-label {
      font-size: 0.8125rem;
      color: var(--text-muted);
      cursor: pointer;
    }

    /* Primary Hero Button */
    .btn-primary {
      width: 100%;
      background: var(--btn-bg);
      color: var(--btn-text);
      font-weight: 600;
      border: none;
      border-radius: 6px;
      padding: 0.8rem 1rem;
      font-size: 0.875rem;
      cursor: pointer;
      transition: opacity 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }

    .btn-primary:hover {
      opacity: 0.9;
    }

    .btn-primary:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: var(--btn-sec-bg);
      color: var(--btn-sec-text);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 0.65rem 0.9rem;
      font-size: 0.8125rem;
      font-weight: 500;
      cursor: pointer;
      transition: opacity 0.15s ease;
      white-space: nowrap;
    }
    .btn-secondary:hover {
      opacity: 0.8;
    }

    /* Inspect Section (Minimal) */
    .lookup-section {
      margin-top: 1.75rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border-color);
    }

    .lookup-title {
      font-size: 0.8125rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }

    .lookup-row {
      display: flex;
      gap: 0.5rem;
    }

    #job-detail-card {
      display: none;
      margin-top: 0.75rem;
      padding: 0.75rem;
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      max-height: 180px;
      overflow-y: auto;
    }

    /* Clean Console */
    .console-box {
      background: var(--console-bg);
      border: 1px solid var(--console-border);
      border-radius: 6px;
      padding: 1.25rem;
      font-family: var(--font-mono);
      font-size: 0.8125rem;
      color: var(--console-text);
      min-height: 480px;
      max-height: 600px;
      overflow-y: auto;
      white-space: pre-wrap;
      line-height: 1.6;
    }

    .spinner {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: currentColor;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
      display: inline-block;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <header>
    <div class="brand-title">Regress Engine</div>
    <div class="nav-actions">
      <a href="/docs" target="_blank" class="nav-link">Docs</a>
      <a href="https://github.com/prasoon-21/llm-regression-engine" target="_blank" class="nav-link">GitHub</a>
      <div class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme" id="theme-toggle">
        <div class="theme-toggle-knob" id="theme-knob"></div>
      </div>
    </div>
  </header>

  <main>
    <div class="workspace-grid">
      <!-- Left: Dispatch Form -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Run Evaluation</div>
        </div>

        <form id="trigger-form" onsubmit="handleTrigger(event)">
          <div class="form-group">
            <label for="repo">Repository</label>
            <input type="text" id="repo" value="prasoon-21/llm-regression-engine" required>
          </div>

          <div class="form-group">
            <label for="commit">Commit SHA</label>
            <input type="text" id="commit" value="3de3eea" required>
          </div>

          <div class="form-group">
            <label for="pr_num">Pull Request Number (Optional)</label>
            <input type="number" id="pr_num" value="1" placeholder="e.g. 42">
          </div>

          <div class="form-group">
            <label for="model">Evaluation Model</label>
            <select id="model">
              <option value="gemini-1.5-flash">Google Gemini 1.5 Flash</option>
              <option value="groq/llama-3.3-70b">Groq Llama 3.3 70B</option>
              <option value="gpt-4o">OpenAI GPT-4o</option>
            </select>
          </div>

          <label class="checkbox-row" for="adversarial">
            <input type="checkbox" id="adversarial" checked>
            <span class="checkbox-label">Include adversarial red-teaming checks</span>
          </label>

          <button type="submit" id="submit-btn" class="btn-primary">
            <span>Run Evaluation</span>
          </button>
        </form>

        <!-- Compact Prior Run Lookup -->
        <div class="lookup-section">
          <div class="lookup-title">Lookup Prior Job</div>
          <div class="lookup-row">
            <input type="text" id="inspect-job-id" placeholder="Job ID (e.g. manual-abc12345)" style="flex: 1;">
            <button type="button" class="btn-secondary" onclick="inspectJob()">Inspect</button>
          </div>
          <div id="job-detail-card"></div>
        </div>
      </div>

      <!-- Right: Live Output -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Execution Feed</div>
          <span class="card-status" id="active-job-badge">IDLE</span>
        </div>
        <div class="console-box" id="console-output">Ready. Waiting for incoming GitHub webhook or manual dispatch...</div>
      </div>
    </div>
  </main>

  <script>
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

    async function handleTrigger(e) {
      e.preventDefault();
      const btn = document.getElementById('submit-btn');
      const consoleBox = document.getElementById('console-output');
      const badge = document.getElementById('active-job-badge');

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span><span>Dispatching...</span>';

      const payload = {
        repository: document.getElementById('repo').value,
        commit_sha: document.getElementById('commit').value,
        pull_request_number: document.getElementById('pr_num').value ? parseInt(document.getElementById('pr_num').value) : null,
        model_override: document.getElementById('model').value,
        enable_adversarial: document.getElementById('adversarial').checked,
        langsmith_project: "llm-ci-cd-regression-engine"
      };

      try {
        consoleBox.innerText = `[DISPATCH] Dispatching evaluation for ${payload.repository} @ ${payload.commit_sha}...\\n`;
        const res = await fetch('/api/v1/jobs/trigger', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.status === 202) {
          consoleBox.innerText += `[QUEUED] Job enqueued: ${data.job_id}\\n\\n[TASK] Background worker processing:\\n - Harvesting golden traces from LangSmith\\n - Mutating adversarial prompt injections\\n - Auditing schema conformance & LLM-as-a-Judge\\n - Synthesizing regression report...\\n`;
          badge.innerText = 'RUNNING';
          badge.style.color = 'var(--status-active)';
          pollJob(data.job_id);
        } else {
          consoleBox.innerText += `[ERROR] Failed to enqueue: ${JSON.stringify(data)}\\n`;
        }
      } catch (err) {
        consoleBox.innerText += `[ERROR] Connection failed: ${err.message}\\n`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Run Evaluation</span>';
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
              const passed = job.status === 'completed';
              badge.innerText = passed ? 'PASSED' : 'REGRESSION DETECTED';
              badge.style.color = passed ? 'var(--status-success)' : 'var(--status-active)';
              consoleBox.innerText += `\\n[COMPLETED] Status: ${job.status.toUpperCase()}\\n`;
              if (job.result && job.result.markdown_report) {
                consoleBox.innerText += `\\n=== REPORT ===\\n\\n${job.result.markdown_report}`;
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
        detailCard.innerHTML = `<pre style="font-family: var(--font-mono); font-size: 0.75rem; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>`;
      } catch (e) {
        detailCard.innerText = `Error: ${e.message}`;
      }
    }
  </script>
</body>
</html>
"""
