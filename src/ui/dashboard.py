"""Modern, interactive Web Dashboard for the LLM CI/CD Regression & Red-Teaming Engine."""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LLM CI/CD Regression & Red-Teaming Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #0a0d14;
      --bg-card: rgba(18, 24, 38, 0.7);
      --bg-card-hover: rgba(26, 34, 54, 0.85);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(99, 102, 241, 0.3);
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --cyan: #06b6d4;
      --emerald: #10b981;
      --coral: #f43f5e;
      --amber: #f59e0b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(16, 185, 129, 0.05) 0px, transparent 60%);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* Navigation Header */
    header {
      backdrop-filter: blur(16px);
      background: rgba(10, 13, 20, 0.8);
      border-bottom: 1px solid var(--border-subtle);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .brand-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: linear-gradient(135deg, var(--primary), var(--cyan));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
    }

    .brand-title {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .brand-subtitle {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 500;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
    }

    .status-pulse {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 10px #10b981;
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
      font-size: 0.85rem;
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      transition: all 0.2s;
      border: 1px solid var(--border-subtle);
    }
    .btn-link:hover {
      color: var(--text-main);
      border-color: var(--primary);
      background: rgba(99, 102, 241, 0.1);
    }

    /* Main Container */
    main {
      flex: 1;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
      padding: 2.5rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 2.5rem;
    }

    /* Grid Layout */
    .dashboard-grid {
      display: grid;
      grid-template-columns: 1fr 1.6fr;
      gap: 2rem;
    }

    @media (max-width: 1024px) {
      .dashboard-grid { grid-template-columns: 1fr; }
    }

    /* Cards */
    .card {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      transition: border-color 0.3s, transform 0.2s;
    }
    .card:hover {
      border-color: var(--border-glow);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }

    /* Form Styles */
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    label {
      font-size: 0.825rem;
      font-weight: 500;
      color: var(--text-muted);
    }

    input, select {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 0.65rem 0.9rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.9rem;
      outline: none;
      transition: all 0.2s;
    }

    input:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary), #4338ca);
      color: #fff;
      font-weight: 600;
      border: none;
      border-radius: 8px;
      padding: 0.85rem 1.5rem;
      font-size: 0.95rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, var(--primary-hover), #3730a3);
      transform: translateY(-1px);
    }
    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    /* Topology Cards */
    .topo-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
    }
    @media (max-width: 768px) {
      .topo-grid { grid-template-columns: repeat(2, 1fr); }
    }

    .topo-item {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .topo-name {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .topo-val {
      font-size: 0.95rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    /* Output Console */
    .console-box {
      background: #030712;
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 1.25rem;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: #e2e8f0;
      min-height: 280px;
      max-height: 480px;
      overflow-y: auto;
      white-space: pre-wrap;
      line-height: 1.6;
    }

    /* Table */
    .table-container {
      overflow-x: auto;
      border-radius: 10px;
      border: 1px solid var(--border-subtle);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.85rem;
    }

    th {
      background: rgba(15, 23, 42, 0.8);
      color: var(--text-muted);
      padding: 0.75rem 1rem;
      font-weight: 600;
      border-bottom: 1px solid var(--border-subtle);
    }

    td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--border-subtle);
    }

    tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    .badge-pass {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-weight: 600;
    }

    .badge-fail {
      background: rgba(244, 63, 94, 0.15);
      color: #fb7185;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-weight: 600;
    }

    /* Loading Spinner */
    .spinner {
      width: 18px;
      height: 18px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-title">LLM Regression & Red-Teaming Engine</div>
        <div class="brand-subtitle">CI/CD Autonomous Gatekeeper</div>
      </div>
    </div>
    <div class="nav-actions">
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
        <span class="topo-val" style="color: #38bdf8;">⚡ Upstash Redis (Live)</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Trace Harvester</span>
        <span class="topo-val" style="color: #a78bfa;">🦜 LangSmith Traces</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Storage</span>
        <span class="topo-val" style="color: #34d399;">🗄️ Supabase Postgres</span>
      </div>
      <div class="topo-item">
        <span class="topo-name">Telemetry</span>
        <span class="topo-val" style="color: #fbbf24;">🦔 PostHog Analytics</span>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="dashboard-grid">
      <!-- Left Panel: Trigger Form -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">🚀 Dispatch Evaluation Run</div>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Trigger an on-demand regression check or red-teaming sweep against candidate LLM traces.
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

          <div class="form-group" style="margin-top: 0.85rem; flex-direction: row; align-items: center; gap: 0.5rem;">
            <input type="checkbox" id="adversarial" checked style="width: auto;">
            <label for="adversarial" style="margin-bottom: 0;">Include Adversarial Red-Teaming (Prompt Injections & Jailbreaks)</label>
          </div>

          <button type="submit" id="submit-btn" class="btn-primary" style="margin-top: 1.5rem; width: 100%;">
            <span>Run Regression & Red-Team Audit</span>
          </button>
        </form>
      </div>

      <!-- Right Panel: Live Execution Console -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">🖥️ Execution Console & Audit Feed</div>
          <span id="active-job-badge" style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">IDLE</span>
        </div>
        <div class="console-box" id="console-output">Ready. Waiting for incoming GitHub Webhook or manual dispatch...</div>
      </div>
    </div>

    <!-- Live Status Checker Card -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">📋 Inspect Job Status by ID</div>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <input type="text" id="inspect-job-id" placeholder="Enter Job ID (e.g. manual-abc12345)" style="flex: 1;">
        <button class="btn-primary" onclick="inspectJob()" style="padding: 0.65rem 1.25rem;">Query Status</button>
      </div>
      <div id="job-detail-card" style="display: none; margin-top: 1rem; padding: 1rem; background: rgba(15,23,42,0.6); border-radius: 8px;"></div>
    </div>
  </main>

  <script>
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
          badge.style.color = '#38bdf8';
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

      for (let i = 0; i < 20; i++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          const res = await fetch(`/api/v1/jobs/${jobId}`);
          if (res.ok) {
            const job = await res.json();
            if (job.status === 'completed' || job.status === 'regression_detected') {
              badge.innerText = `DONE: ${job.status.toUpperCase()}`;
              badge.style.color = job.status === 'completed' ? '#34d399' : '#fb7185';
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
