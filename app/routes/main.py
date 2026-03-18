from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.services.leetcode_fetcher import get_leetcode_stats
from app.services.card_generator import card_generator
from app.services.heatmap_generator import heatmap_generator
from app.schemas import StatsResponse


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <head>
        <title>LeetCard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cg transform='translate(4 3) scale(0.22)'%3E%3Cpath d='M67.506 83.066C70 80.576 74.037 80.582 76.522 83.08C79.008 85.578 79.002 89.622 76.508 92.112L65.435 103.169C55.219 113.37 38.56 113.518 28.172 103.513C28.112 103.455 23.486 98.92 8.227 83.957C-1.924 74.002 -2.936 58.074 6.616 47.846L24.428 28.774C33.91 18.621 51.387 17.512 62.227 26.278L78.405 39.362C81.144 41.577 81.572 45.598 79.361 48.342C77.149 51.087 73.135 51.515 70.395 49.3L54.218 36.217C48.549 31.632 38.631 32.262 33.739 37.5L15.927 56.572C11.277 61.552 11.786 69.574 17.146 74.829C28.351 85.816 36.987 94.284 36.997 94.294C42.398 99.495 51.13 99.418 56.433 94.123L67.506 83.066Z' fill='%23FFA116'/%3E%3Cpath d='M49.412 2.023C51.817 -0.552 55.852 -0.686 58.423 1.722C60.994 4.132 61.128 8.173 58.723 10.749L15.928 56.572C11.277 61.551 11.786 69.573 17.145 74.829L36.909 94.209C39.425 96.676 39.468 100.719 37.005 103.24C34.542 105.76 30.506 105.804 27.99 103.336L8.226 83.956C-1.924 74.002 -2.936 58.074 6.617 47.846L49.412 2.023Z' fill='%23F5F5F5'/%3E%3Cpath d='M40.606 72.001C37.086 72.001 34.231 69.142 34.231 65.614C34.231 62.087 37.086 59.228 40.606 59.228H87.624C91.145 59.228 94 62.087 94 65.614C94 69.142 91.145 72.001 87.624 72.001H40.606Z' fill='%238E8E8E'/%3E%3C/g%3E%3C/svg%3E" />
        <style>
          :root {
            --bg: #0f1115;
            --panel: #1a1d24;
            --panel-2: #20242d;
            --border: #2b313d;
            --text: #f5f7fb;
            --muted: #9aa4b2;
            --accent: #ffa116;
            --accent-soft: rgba(255, 161, 22, 0.18);
            --easy: #2ec866;
            --medium: #f7b84b;
            --hard: #ff5c5c;
          }

          * {
            box-sizing: border-box;
          }

          body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background:
              radial-gradient(circle at top left, rgba(255, 161, 22, 0.12), transparent 28%),
              radial-gradient(circle at 85% 15%, rgba(46, 200, 102, 0.08), transparent 24%),
              linear-gradient(180deg, #0d0f14 0%, #10131a 100%);
          }

          .shell {
            width: min(1120px, calc(100% - 32px));
            margin: 0 auto;
            padding: 32px 0 48px;
          }

          .hero {
            display: grid;
            grid-template-columns: 1fr;
            gap: 22px;
            align-items: stretch;
          }

          .panel {
            background: linear-gradient(180deg, rgba(33, 37, 46, 0.96), rgba(24, 27, 34, 0.96));
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28);
          }

          .intro {
            padding: 22px 24px 0;
            background: transparent;
            border: 0;
            box-shadow: none;
          }

          .brand {
            display: inline-flex;
            align-items: center;
            gap: 12px;
          }

          .brand svg {
            width: 24px;
            height: 24px;
            flex: 0 0 auto;
          }

          h1 {
            margin: 22px 0 14px;
            font-size: clamp(2.1rem, 4vw, 3.2rem);
            line-height: 1;
            letter-spacing: -0.05em;
          }

          .lead {
            margin: 0;
            color: var(--muted);
            font-size: 16px;
            line-height: 1.6;
          }

          .builder {
            padding: 28px;
            display: flex;
            flex-direction: column;
            gap: 20px;
          }

          .builder h2 {
            margin: 0;
            font-size: 24px;
            letter-spacing: -0.03em;
          }

          .builder p {
            margin: 0;
            color: var(--muted);
            line-height: 1.65;
            font-size: 15px;
          }

          .visual-flow {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 24px;
          }

          .visual-card {
            padding: 16px;
            border: 1px solid #313847;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.025);
          }

          .visual-card strong {
            display: block;
            margin-bottom: 12px;
            font-size: 14px;
            color: #f5f7fb;
          }

          .visual-box {
            border: 1px dashed #3a4456;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.02);
          }

          .visual-input {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 14px;
          }

          .visual-input .dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: var(--accent);
          }

          .visual-line {
            height: 10px;
            border-radius: 999px;
            background: #5d6677;
            opacity: 0.55;
          }

          .visual-line.short {
            width: 42%;
          }

          .visual-line.mid {
            width: 66%;
          }

          .visual-line.long {
            width: 88%;
          }

          .visual-options {
            display: grid;
            gap: 10px;
          }

          .visual-option {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid #2f3643;
          }

          .visual-option.active {
            border-color: rgba(255, 161, 22, 0.6);
            background: rgba(255, 161, 22, 0.08);
          }

          .radio {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            border: 2px solid #778093;
          }

          .visual-option.active .radio {
            border-color: var(--accent);
            background: var(--accent);
          }

          .visual-arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #687282;
            font-size: 24px;
            font-weight: 800;
          }

          .visual-copy {
            display: grid;
            gap: 10px;
          }

          .copy-chip {
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid #2f3643;
            color: #d8dfeb;
            font-size: 13px;
            font-weight: 700;
          }

          .places {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }

          .place {
            padding: 8px 10px;
            border-radius: 999px;
            background: #161b24;
            border: 1px solid #2c3341;
            color: #c9d0dc;
            font-size: 12px;
            font-weight: 700;
          }

          .field-label {
            display: block;
            margin-bottom: 10px;
            color: #dfe5ef;
            font-size: 14px;
            font-weight: 700;
          }

          .input-wrap {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 16px;
            border: 1px solid #333949;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.03);
          }

          .input-wrap:focus-within {
            border-color: rgba(255, 161, 22, 0.65);
            box-shadow: 0 0 0 4px rgba(255, 161, 22, 0.12);
          }

          .input-icon {
            width: 24px;
            height: 24px;
            flex: 0 0 auto;
          }

          input[type="text"] {
            width: 100%;
            border: 0;
            outline: none;
            background: transparent;
            color: var(--text);
            padding: 16px 0;
            font-size: 16px;
          }

          input[type="text"]::placeholder {
            color: #6f7886;
          }

          .modes {
            display: grid;
            gap: 12px;
          }

          .mode-card {
            position: relative;
            display: block;
            padding: 16px 18px;
            border: 1px solid #333949;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.025);
            cursor: pointer;
            transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
          }

          .mode-card:hover {
            transform: translateY(-1px);
            border-color: #444d60;
            background: rgba(255, 255, 255, 0.04);
          }

          .mode-card input {
            position: absolute;
            opacity: 0;
            pointer-events: none;
          }

          .mode-card:has(input:checked) {
            border-color: rgba(255, 161, 22, 0.72);
            background: linear-gradient(180deg, rgba(255, 161, 22, 0.12), rgba(255, 161, 22, 0.05));
            box-shadow: inset 0 0 0 1px rgba(255, 161, 22, 0.28);
          }

          .mode-title {
            display: block;
            margin-bottom: 6px;
            font-size: 16px;
            font-weight: 700;
            color: var(--text);
          }

          .mode-desc {
            display: block;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.5;
          }

          .actions {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
          }

          .button {
            border: 0;
            border-radius: 14px;
            padding: 14px 18px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            transition: transform 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
          }

          .button:hover {
            transform: translateY(-1px);
          }

          .button-primary {
            color: #161616;
            background: linear-gradient(180deg, #ffb84c 0%, #ffa116 100%);
            box-shadow: 0 16px 30px rgba(255, 161, 22, 0.22);
          }

          .button-secondary {
            color: #dfe5ef;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid #333949;
          }

          .footer-note {
            margin-top: 14px;
            color: #7e8897;
            font-size: 13px;
          }

          .sample {
            margin-top: 8px;
            padding: 22px 24px;
          }

          .sample h3 {
            margin: 0 0 14px;
            font-size: 18px;
          }

          .sample-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
          }

          .sample-card {
            padding: 14px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid #313847;
          }

          .sample-card strong {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
          }

          .sample-card span {
            display: block;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.5;
          }

          .sample-preview {
            margin-top: 12px;
            padding: 10px;
            border-radius: 14px;
            background: #12161d;
            border: 1px solid #2c3341;
          }

          .sample-preview img {
            display: block;
            width: 100%;
            height: auto;
            border-radius: 10px;
          }

          .next-panel {
            margin-top: 18px;
            padding: 16px 18px;
            border-radius: 18px;
            border: 1px solid #313847;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
          }

          .next-panel strong {
            display: block;
            margin-bottom: 8px;
            color: #f4f6fb;
            font-size: 14px;
          }

          .next-panel p {
            margin: 0;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.7;
          }

          .example-url {
            margin-top: 12px;
            padding: 12px 14px;
            border-radius: 14px;
            background: #141821;
            border: 1px solid #2a3040;
            color: #dbe4f0;
            font-size: 13px;
            overflow-wrap: anywhere;
          }

          @media (max-width: 900px) {
            .visual-flow {
              grid-template-columns: 1fr;
            }

            .sample-grid {
              grid-template-columns: 1fr;
            }
          }
        </style>
      </head>
      <body>
        <main class="shell">
          <section class="hero">
            <article class="intro">
              <div class="brand">
                <svg viewBox="0 0 94 105" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M67.506,83.066 C70.000,80.576 74.037,80.582 76.522,83.080 C79.008,85.578 79.002,89.622 76.508,92.112 L65.435,103.169 C55.219,113.370 38.560,113.518 28.172,103.513 C28.112,103.455 23.486,98.920 8.227,83.957 C-1.924,74.002 -2.936,58.074 6.616,47.846 L24.428,28.774 C33.910,18.621 51.387,17.512 62.227,26.278 L78.405,39.362 C81.144,41.577 81.572,45.598 79.361,48.342 C77.149,51.087 73.135,51.515 70.395,49.300 L54.218,36.217 C48.549,31.632 38.631,32.262 33.739,37.500 L15.927,56.572 C11.277,61.552 11.786,69.574 17.146,74.829 C28.351,85.816 36.987,94.284 36.997,94.294 C42.398,99.495 51.130,99.418 56.433,94.123 L67.506,83.066 Z" fill="#FFA116"/>
                  <path d="M49.412,2.023 C51.817,-0.552 55.852,-0.686 58.423,1.722 C60.994,4.132 61.128,8.173 58.723,10.749 L15.928,56.572 C11.277,61.551 11.786,69.573 17.145,74.829 L36.909,94.209 C39.425,96.676 39.468,100.719 37.005,103.240 C34.542,105.760 30.506,105.804 27.990,103.336 L8.226,83.956 C-1.924,74.002 -2.936,58.074 6.617,47.846 L49.412,2.023 Z" fill="#F5F5F5"/>
                  <path d="M40.606,72.001 C37.086,72.001 34.231,69.142 34.231,65.614 C34.231,62.087 37.086,59.228 40.606,59.228 L87.624,59.228 C91.145,59.228 94,62.087 94,65.614 C94,69.142 91.145,72.001 87.624,72.001 L40.606,72.001 Z" fill="#8E8E8E"/>
                </svg>
                <h1>LeetCard</h1>
              </div>
              <p class="lead">
                Enter a LeetCode username, choose an output, and copy the generated SVG link.
              </p>
              <div class="visual-flow">
                <div class="visual-card">
                  <strong>1. Put your name here</strong>
                  <div class="visual-box visual-input">
                    <div class="dot"></div>
                    <div class="visual-line long"></div>
                  </div>
                </div>
                <div class="visual-card">
                  <strong>2. Click what you want</strong>
                  <div class="visual-options">
                    <div class="visual-option active">
                      <div class="radio"></div>
                      <div class="visual-line short"></div>
                    </div>
                    <div class="visual-option">
                      <div class="radio"></div>
                      <div class="visual-line mid"></div>
                    </div>
                    <div class="visual-option">
                      <div class="radio"></div>
                      <div class="visual-line short"></div>
                    </div>
                  </div>
                </div>
                <div class="visual-card">
                  <strong>3. Copy and paste it in</strong>
                  <div class="visual-copy">
                    <div class="visual-box" style="padding: 12px 14px;">
                      <div class="visual-line long"></div>
                    </div>
                    <div class="places">
                      <span class="place">README</span>
                      <span class="place">Portfolio</span>
                      <span class="place">Website</span>
                    </div>
                  </div>
                </div>
              </div>
            </article>

            <section class="panel builder">
              <div>
                <h2>Build Your Card</h2>
                <p>Generate an SVG.</p>
              </div>

              <form id="card-form">
                <label class="field-label" for="username">LeetCode Username</label>
                <div class="input-wrap">
                  <svg class="input-icon" viewBox="0 0 94 105" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M67.506,83.066 C70.000,80.576 74.037,80.582 76.522,83.080 C79.008,85.578 79.002,89.622 76.508,92.112 L65.435,103.169 C55.219,113.370 38.560,113.518 28.172,103.513 C28.112,103.455 23.486,98.920 8.227,83.957 C-1.924,74.002 -2.936,58.074 6.616,47.846 L24.428,28.774 C33.910,18.621 51.387,17.512 62.227,26.278 L78.405,39.362 C81.144,41.577 81.572,45.598 79.361,48.342 C77.149,51.087 73.135,51.515 70.395,49.300 L54.218,36.217 C48.549,31.632 38.631,32.262 33.739,37.500 L15.927,56.572 C11.277,61.552 11.786,69.574 17.146,74.829 C28.351,85.816 36.987,94.284 36.997,94.294 C42.398,99.495 51.130,99.418 56.433,94.123 L67.506,83.066 Z" fill="#FFA116"/>
                    <path d="M49.412,2.023 C51.817,-0.552 55.852,-0.686 58.423,1.722 C60.994,4.132 61.128,8.173 58.723,10.749 L15.928,56.572 C11.277,61.551 11.786,69.573 17.145,74.829 L36.909,94.209 C39.425,96.676 39.468,100.719 37.005,103.240 C34.542,105.760 30.506,105.804 27.990,103.336 L8.226,83.956 C-1.924,74.002 -2.936,58.074 6.617,47.846 L49.412,2.023 Z" fill="#F5F5F5"/>
                    <path d="M40.606,72.001 C37.086,72.001 34.231,69.142 34.231,65.614 C34.231,62.087 37.086,59.228 40.606,59.228 L87.624,59.228 C91.145,59.228 94,62.087 94,65.614 C94,69.142 91.145,72.001 87.624,72.001 L40.606,72.001 Z" fill="#8E8E8E"/>
                  </svg>
                  <input type="text" id="username" name="username" placeholder="e.g. abdulsamad" required />
                </div>

                <div style="height: 18px;"></div>

                <label class="field-label">Output Mode</label>
                <div class="modes">
                  <label class="mode-card">
                    <input type="radio" id="mode_card" name="mode" value="card" checked />
                    <span class="mode-title">Stats Card</span>
                    <span class="mode-desc">A sleek LeetCode-style card with the segmented progress arc and difficulty breakdown.</span>
                  </label>

                  <label class="mode-card">
                    <input type="radio" id="mode_card_heatmap" name="mode" value="card_heatmap" />
                    <span class="mode-title">Stats Card + Heatmap</span>
                    <span class="mode-desc">Shows the full stats card with the month-grouped heatmap rendered underneath.</span>
                  </label>

                  <label class="mode-card">
                    <input type="radio" id="mode_heatmap" name="mode" value="heatmap" />
                    <span class="mode-title">Heatmap Only</span>
                    <span class="mode-desc">Outputs the contribution-style submission heatmap by itself for standalone embedding.</span>
                  </label>
                </div>

                <div style="height: 20px;"></div>

                <div class="actions">
                  <button class="button button-primary" type="submit">Generate SVG</button>
                  <button class="button button-secondary" type="button" id="preview-demo">Try Demo User</button>
                </div>

                <p class="footer-note">Generate, then copy the link.</p>
                <div class="next-panel">
                  <strong>Your SVG Link</strong>
                  <p id="next-copy">Copy this link.</p>
                  <div class="example-url" id="example-url">Example output: /card/cpcs.svg</div>
                  <button class="button button-secondary" type="button" id="copy-link" style="margin-top: 12px;">Copy Generated Link</button>
                </div>
              </form>
            </section>
          </section>

          <section class="panel sample">
            <h3>Sample Outputs</h3>
            <div class="sample-grid">
              <div class="sample-card">
                <strong>Stats Card</strong>
                <span>Default LeetCode-style stats card.</span>
                <div class="sample-preview">
                  <img src="/card/cpcs.svg" alt="Sample stats card preview" />
                </div>
              </div>
              <div class="sample-card">
                <strong>Stats + Heatmap</strong>
                <span>Stats card with the activity heatmap attached below.</span>
                <div class="sample-preview">
                  <img src="/card/cpcs.svg?show_heatmap=true" alt="Sample stats card with heatmap preview" />
                </div>
              </div>
              <div class="sample-card">
                <strong>Heatmap Only</strong>
                <span>Standalone submission heatmap.</span>
                <div class="sample-preview">
                  <img src="/heatmap/cpcs.svg" alt="Sample standalone heatmap preview" />
                </div>
              </div>
            </div>
          </section>
        </main>

        <script>
          const form = document.getElementById("card-form");
          const demoButton = document.getElementById("preview-demo");
          const usernameInput = document.getElementById("username");
          const nextCopy = document.getElementById("next-copy");
          const exampleUrl = document.getElementById("example-url");
          const copyLinkButton = document.getElementById("copy-link");

          function updateGuidance() {
            const username = usernameInput.value.trim() || "cpcs";
            const mode = document.querySelector('input[name="mode"]:checked').value;

            let url = `/card/${username}.svg`;
            let message = "Copy this link.";

            if (mode === "card_heatmap") {
              url = `/card/${username}.svg?show_heatmap=true`;
              message = "Copy this card + heatmap link.";
            }

            if (mode === "heatmap") {
              url = `/heatmap/${username}.svg`;
              message = "Copy this heatmap link.";
            }

            nextCopy.textContent = message;
            exampleUrl.textContent = `${window.location.origin}${url}`;
          }

          form.addEventListener("submit", function (event) {
            event.preventDefault();

            const username = usernameInput.value.trim();
            if (!username) {
              usernameInput.focus();
              return;
            }

            const mode = document.querySelector('input[name="mode"]:checked').value;

            let url = `/card/${username}.svg`;
            if (mode === "card_heatmap") {
              url = `/card/${username}.svg?show_heatmap=true`;
            }
            if (mode === "heatmap") {
              url = `/heatmap/${username}.svg`;
            }

            window.location.href = url;
          });

          demoButton.addEventListener("click", function () {
            usernameInput.value = "cpcs";
            usernameInput.focus();
            updateGuidance();
          });

          copyLinkButton.addEventListener("click", async function () {
            const link = exampleUrl.textContent;
            try {
              await navigator.clipboard.writeText(link);
              copyLinkButton.textContent = "Copied";
              setTimeout(function () {
                copyLinkButton.textContent = "Copy Generated Link";
              }, 1400);
            } catch (error) {
              copyLinkButton.textContent = "Copy failed";
              setTimeout(function () {
                copyLinkButton.textContent = "Copy Generated Link";
              }, 1400);
            }
          });

          usernameInput.addEventListener("input", updateGuidance);
          document.querySelectorAll('input[name="mode"]').forEach(function (input) {
            input.addEventListener("change", updateGuidance);
          });

          updateGuidance();
        </script>
      </body>
    </html>
    """

@router.get("/stats/{username}", response_model=StatsResponse)
def fetch_stats(username: str):
    try:
        return get_leetcode_stats(username)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.get("/card/{username}.svg")
def make_card(username: str, show_heatmap: bool = False):
    try:
        stats = get_leetcode_stats(username)
        return card_generator(stats, show_heatmap=show_heatmap)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/heatmap/{username}.svg")
def make_heatmap(username: str):
    try:
        stats = get_leetcode_stats(username)
        return heatmap_generator(stats)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
