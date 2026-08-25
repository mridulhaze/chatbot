/**
 * National University Bangladesh AI Assistant — Embeddable Web Widget
 * Robust standalone floating widget script
 */
(function () {
  "use strict";

  // Prevent multiple injections
  if (window.__NU_AI_WIDGET_LOADED__) return;
  window.__NU_AI_WIDGET_LOADED__ = true;

  // Resolve API Base URL dynamically
  function getApiBase() {
    // 1. Explicit data attribute on script tag
    const scripts = document.querySelectorAll("script[src*='widget.js']");
    for (let s of scripts) {
      const customApi = s.getAttribute("data-api-base");
      if (customApi) return customApi.replace(/\/+$/, "");
    }
    // 2. Script origin
    if (document.currentScript && document.currentScript.src) {
      try {
        const u = new URL(document.currentScript.src);
        return u.origin;
      } catch (e) {}
    }
    for (let s of scripts) {
      if (s.src) {
        try {
          const u = new URL(s.src);
          return u.origin;
        } catch (e) {}
      }
    }
    // 3. Fallback to window.location.origin
    if (window.location && window.location.origin && window.location.origin.startsWith("http")) {
      return window.location.origin;
    }
    return "http://localhost:8000";
  }

  const API_BASE = getApiBase();
  let isOpen = false;
  let conversationHistory = [];
  let pendingMessage = null;

  // Global Controller object defined immediately
  window.NU_AI_WIDGET = {
    open: function () {
      if (window.__NU_TOGGLE__) window.__NU_TOGGLE__(true);
      else isOpen = true;
    },
    close: function () {
      if (window.__NU_TOGGLE__) window.__NU_TOGGLE__(false);
      else isOpen = false;
    },
    toggle: function () {
      if (window.__NU_TOGGLE__) window.__NU_TOGGLE__();
    },
    send: function (msg) {
      if (window.__NU_SEND__) {
        window.__NU_TOGGLE__(true);
        window.__NU_SEND__(msg);
      } else {
        pendingMessage = msg;
        isOpen = true;
      }
    }
  };

  function initWidget() {
    if (document.getElementById("nu-ai-widget-container")) return;

    // Inject Styles
    const styleEl = document.createElement("style");
    styleEl.id = "nu-ai-widget-styles";
    styleEl.textContent = `
      #nu-ai-widget-container * {
        box-sizing: border-box !important;
        font-family: 'Hind Siliguri', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
      }
      #nu-ai-widget-container {
        position: fixed !important;
        z-index: 2147483647 !important;
        right: 20px !important;
        bottom: 20px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-end !important;
        font-size: 14px !important;
      }
      .nu-launcher-btn {
        width: 62px !important;
        height: 62px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #065f46 0%, #047857 50%, #0f766e 100%) !important;
        color: #ffffff !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(6, 95, 70, 0.5), 0 8px 10px -6px rgba(6, 95, 70, 0.4) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        outline: none !important;
        position: relative !important;
      }
      .nu-launcher-btn:hover {
        transform: scale(1.08) translateY(-2px) !important;
        box-shadow: 0 16px 32px -4px rgba(6, 95, 70, 0.6) !important;
      }
      .nu-launcher-btn:active {
        transform: scale(0.95) !important;
      }
      .nu-launcher-pulse {
        position: absolute !important;
        top: 2px !important;
        right: 2px !important;
        width: 14px !important;
        height: 14px !important;
        background: #10b981 !important;
        border: 2px solid #ffffff !important;
        border-radius: 50% !important;
        animation: nuPulse 2s infinite !important;
      }
      @keyframes nuPulse {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
      }
      .nu-launcher-badge {
        position: absolute !important;
        right: 76px !important;
        top: 14px !important;
        background: #ffffff !important;
        color: #065f46 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 6px 14px !important;
        border-radius: 20px !important;
        white-space: nowrap !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.12) !important;
        border: 1px solid #e2e8f0 !important;
        pointer-events: none !important;
        animation: nuFadeSlide 0.4s ease-out !important;
      }
      @keyframes nuFadeSlide {
        from { opacity: 0; transform: translateX(10px); }
        to { opacity: 1; transform: translateX(0); }
      }
      .nu-chat-window {
        position: absolute !important;
        bottom: 78px !important;
        right: 0 !important;
        width: 410px !important;
        max-width: calc(100vw - 28px) !important;
        height: 610px !important;
        max-height: calc(100vh - 100px) !important;
        background: #ffffff !important;
        border-radius: 20px !important;
        box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0,0,0,0.08) !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        transform-origin: bottom right !important;
      }
      .nu-chat-window.nu-hidden {
        opacity: 0 !important;
        transform: scale(0.88) translateY(24px) !important;
        pointer-events: none !important;
      }
      .nu-chat-header {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #0f766e 100%) !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        flex-shrink: 0 !important;
      }
      .nu-header-title {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
      }
      .nu-header-logo {
        width: 36px !important;
        height: 36px !important;
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        color: #ffffff !important;
      }
      .nu-header-actions button {
        background: rgba(255,255,255,0.15) !important;
        border: none !important;
        color: #ffffff !important;
        width: 28px !important;
        height: 28px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 13px !important;
        transition: background 0.2s !important;
        margin-left: 4px !important;
      }
      .nu-header-actions button:hover {
        background: rgba(255,255,255,0.3) !important;
      }
      .nu-chat-body {
        flex: 1 !important;
        overflow-y: auto !important;
        padding: 14px !important;
        background: #f8fafc !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
      }
      .nu-msg {
        display: flex !important;
        gap: 8px !important;
        max-width: 90% !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
      }
      .nu-msg.nu-user {
        align-self: flex-end !important;
        flex-direction: row-reverse !important;
      }
      .nu-msg.nu-bot {
        align-self: flex-start !important;
      }
      .nu-avatar {
        width: 28px !important;
        height: 28px !important;
        border-radius: 50% !important;
        background: #065f46 !important;
        color: #ffffff !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        margin-top: 2px !important;
      }
      .nu-msg-content {
        padding: 10px 14px !important;
        border-radius: 16px !important;
        word-break: break-word !important;
      }
      .nu-user .nu-msg-content {
        background: linear-gradient(135deg, #065f46, #0f766e) !important;
        color: #ffffff !important;
        border-bottom-right-radius: 4px !important;
      }
      .nu-bot .nu-msg-content {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-bottom-left-radius: 4px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
      }
      .nu-chips-container {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        padding: 4px 0 6px 36px !important;
      }
      .nu-chip-btn {
        background: #ecfdf5 !important;
        color: #065f46 !important;
        border: 1px solid #a7f3d0 !important;
        padding: 5px 10px !important;
        border-radius: 12px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
      }
      .nu-chip-btn:hover {
        background: #d1fae5 !important;
        border-color: #6ee7b7 !important;
      }
      .nu-typing {
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
        padding: 6px 12px !important;
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        align-self: flex-start !important;
        margin-left: 36px !important;
        font-size: 11px !important;
        color: #059669 !important;
        font-weight: 600 !important;
      }
      .nu-dot {
        width: 6px !important;
        height: 6px !important;
        background: #10b981 !important;
        border-radius: 50% !important;
        animation: nuBounce 1.2s infinite ease-in-out !important;
      }
      .nu-dot:nth-child(2) { animation-delay: 0.2s !important; }
      .nu-dot:nth-child(3) { animation-delay: 0.4s !important; }
      @keyframes nuBounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1.0); }
      }
      .nu-chat-footer {
        padding: 10px 12px !important;
        background: #ffffff !important;
        border-top: 1px solid #e2e8f0 !important;
        display: flex !important;
        gap: 8px !important;
        align-items: center !important;
        flex-shrink: 0 !important;
      }
      .nu-chat-input {
        flex: 1 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 9px 12px !important;
        font-size: 13px !important;
        outline: none !important;
        transition: border-color 0.2s !important;
      }
      .nu-chat-input:focus {
        border-color: #059669 !important;
      }
      .nu-voice-btn {
        background: #f8fafc !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        flex-shrink: 0 !important;
      }
      .nu-voice-btn:hover {
        background: #ecfdf5 !important;
        color: #047857 !important;
        border-color: #a7f3d0 !important;
      }
      .nu-voice-btn.listening {
        background: #ef4444 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
        animation: nuVoicePulse 1.2s infinite !important;
      }
      @keyframes nuVoicePulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.08); opacity: 0.85; }
      }
      .nu-send-btn {
        background: #065f46 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: background 0.2s !important;
        flex-shrink: 0 !important;
      }
      .nu-send-btn:hover {
        background: #047857 !important;
      }
      .nu-msg-content a {
        color: #2563eb !important;
        text-decoration: underline !important;
        font-weight: 600 !important;
        transition: color 0.15s ease !important;
      }
      .nu-msg-content a:hover {
        color: #1d4ed8 !important;
      }
      .nu-sources {
        margin-top: 8px !important;
        padding-top: 6px !important;
        border-top: 1px dashed #cbd5e1 !important;
        font-size: 11px !important;
        color: #64748b !important;
      }
      .nu-sources a {
        color: #2563eb !important;
        text-decoration: none !important;
        display: inline-block !important;
        margin-right: 6px !important;
        margin-top: 2px !important;
        font-weight: 600 !important;
      }
      .nu-sources a:hover {
        color: #1d4ed8 !important;
        text-decoration: underline !important;
      }
      @media (max-width: 480px) {
        .nu-chat-window {
          bottom: 0 !important;
          right: 0 !important;
          left: 0 !important;
          width: 100vw !important;
          height: 100vh !important;
          max-width: 100vw !important;
          max-height: 100vh !important;
          border-radius: 0 !important;
        }
      }
    `;
    document.head.appendChild(styleEl);

    // Markdown formatter with HTML tag tolerance for bot action links
    function formatMarkdown(text) {
      if (!text) return "";
      return text
        .replace(/^### (.*$)/gim, '<h4 style="font-size:13px;font-weight:700;margin:6px 0 3px 0;color:#065f46;">$1</h4>')
        .replace(/^## (.*$)/gim, '<h3 style="font-size:14px;font-weight:700;margin:8px 0 4px 0;color:#064e3b;">$1</h3>')
        .replace(/^# (.*$)/gim, '<h2 style="font-size:15px;font-weight:800;margin:10px 0 4px 0;color:#064e3b;">$1</h2>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong style="color:#0f172a;">$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank" style="color:#059669;font-weight:600;text-decoration:underline;">$1</a>')
        .replace(/^\s*\*\s+(.*$)/gim, '<li style="margin-left:14px;list-style-type:disc;">$1</li>')
        .replace(/^\s*-\s+(.*$)/gim, '<li style="margin-left:14px;list-style-type:disc;">$1</li>')
        .replace(/\n\n+/g, '<br><br>')
        .replace(/\n/g, '<br>');
    }

    window.openServiceFormPopup = function(serviceCode, serviceName, tokenId) {
      const problem = prompt(`[ ${serviceName} ]\nটোকেন নম্বর: ${tokenId}\n\nঅনুগ্রহ করে আপনার সমস্যার বিবরণ লিখুন:`);
      if (problem && problem.trim().length > 2) {
        fetch(`${resolvedApiBase}/api/token/${tokenId}/submit-details`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            service_type: serviceCode,
            problem: problem.trim()
          })
        }).then(res => res.json()).then(data => {
          appendMessage("bot", `### ✅ আপনার সমস্যাটি সফলভাবে জমা হয়েছে!\n\n* 🎫 **টোকেন নম্বর:** \`${data.token_id}\`\n* 📂 **সেবা:** **${data.service_name}**\n* 📅 **দাখিলের তারিখ:** ${data.created_date}\n* ⏳ **সম্ভাব্য সমাধান তারিখ:** **${data.estimated_solve_date || '২-৩ কার্যদিবস'}**\n* 🟡 **স্ট্যাটাস:** PENDING\n\n📌 *টোকেন নম্বরটি (\`${data.token_id}\`) সংরক্ষণ করে রাখুন।*`);
        }).catch(err => {
          alert("ত্রুটি: " + err.message);
        });
      }
    };

    // Build DOM
    const container = document.createElement("div");
    container.id = "nu-ai-widget-container";
    container.innerHTML = `
      <div id="nu-badge" class="nu-launcher-badge">
        💬 জাতীয় বিশ্ববিদ্যালয় এআই সহকারী
      </div>

      <button id="nu-launcher" class="nu-launcher-btn" aria-label="Open National University AI Assistant">
        <span class="nu-launcher-pulse"></span>
        <svg id="nu-icon-chat" width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <svg id="nu-icon-close" width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="display:none;">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div id="nu-window" class="nu-chat-window nu-hidden">
        <div class="nu-chat-header">
          <div class="nu-header-title">
            <div class="nu-header-logo">NU</div>
            <div>
              <div style="font-size:13px;font-weight:700;line-height:1.2;">জাতীয় বিশ্ববিদ্যালয় AI সহকারী</div>
              <div style="font-size:10px;opacity:0.9;">24/7 Smart Academic Assistant</div>
            </div>
          </div>
          <div class="nu-header-actions">
            <button id="nu-btn-clear" title="Clear Chat">🗑️</button>
            <button id="nu-btn-close" title="Close Window">✕</button>
          </div>
        </div>

        <div id="nu-messages" class="nu-chat-body">
          <div class="nu-msg nu-bot">
            <div class="nu-avatar">NU</div>
            <div class="nu-msg-content">
              <p style="margin:0 0 6px 0;"><strong>স্বাগতম! (National University AI)</strong></p>
              <p style="margin:0;">ভর্তি তথ্য, পরীক্ষার রুটিন, নোটিশ, দপ্তর বা ফলাফল জানতে প্রশ্ন করুন।</p>
              <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; align-items: center; font-size: 10px; color: #94a3b8; user-select: none;">
                <span id="nu-welcome-time">Online</span>
              </div>
            </div>
          </div>

          <div id="nu-chips" class="nu-chips-container">
            <button class="nu-chip-btn" data-query="Token Service">🎫 টোকেন সার্ভিস (Token Service)</button>
            <button class="nu-chip-btn" data-query="Check token status">📋 টোকেন স্ট্যাটাস চেক</button>
            <button class="nu-chip-btn" data-query="আইসিটি দপ্তরের কর্মকর্তা ও কর্মচারীবৃন্দের তালিকা">💻 আইসিটি কর্মকর্তা তালিকা</button>
            <button class="nu-chip-btn" data-query="Honours 4th year exam routine">📅 অনার্স ৪র্থ বর্ষ রুটিন</button>
            <button class="nu-chip-btn" data-query="ফলাফল দেখার ওয়েবসাইট ও SMS নিয়ম">📊 ফলাফল ও SMS নিয়ম</button>
          </div>
        </div>

        <div id="nu-typing" class="nu-typing" style="display:none;">
          <span class="nu-dot"></span>
          <span class="nu-dot"></span>
          <span class="nu-dot"></span>
          <span style="margin-left:4px;">অনুসন্ধান করা হচ্ছে...</span>
        </div>

        <div class="nu-chat-footer">
          <input id="nu-input" type="text" class="nu-chat-input" placeholder="প্রশ্ন লিখুন (যেমন: আইসিটি বিভাগ, নোটিশ, ভর্তি)..." autocomplete="off" />
          <button id="nu-voice" class="nu-voice-btn" aria-label="Voice Search" title="ভয়েস সার্চ">
            <svg id="nu-mic-icon" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
          <button id="nu-send" class="nu-send-btn" aria-label="Send">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(container);

    const launcher = document.getElementById("nu-launcher");
    const badge = document.getElementById("nu-badge");
    const win = document.getElementById("nu-window");
    const iconChat = document.getElementById("nu-icon-chat");
    const iconClose = document.getElementById("nu-icon-close");
    const messagesBox = document.getElementById("nu-messages");
    const inputEl = document.getElementById("nu-input");
    const voiceBtn = document.getElementById("nu-voice");
    const sendBtn = document.getElementById("nu-send");
    const clearBtn = document.getElementById("nu-btn-clear");
    const closeBtn = document.getElementById("nu-btn-close");
    const typingEl = document.getElementById("nu-typing");
    let chipsEl = document.getElementById("nu-chips");
    const welcomeTimeEl = document.getElementById("nu-welcome-time");
    if (welcomeTimeEl) welcomeTimeEl.innerText = formatTime(new Date());

    // --- Voice Recognition for Widget ---
    let widgetSpeechRec = null;
    let isWidgetListening = false;

    function initWidgetVoice() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return null;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;
      rec.lang = "bn-BD";

      rec.onstart = () => {
        isWidgetListening = true;
        if (voiceBtn) {
          voiceBtn.classList.add("listening");
          voiceBtn.title = "🎙️ শুনছি... বলুন";
        }
        if (inputEl) inputEl.placeholder = "🎙️ শুনছি... আপনার প্রশ্নটি বলুন...";
      };

      rec.onresult = (e) => {
        let text = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          text += e.results[i][0].transcript;
        }
        if (inputEl && text) inputEl.value = text;
      };

      rec.onerror = () => stopWidgetVoice();

      rec.onend = () => {
        stopWidgetVoice();
        if (inputEl && inputEl.value.trim().length > 0) {
          sendMessage();
        }
      };

      return rec;
    }

    function toggleWidgetVoice() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("আপনার ব্রাউজারে ভয়েস সার্চ সমর্থন করে না।");
        return;
      }
      if (!widgetSpeechRec) widgetSpeechRec = initWidgetVoice();

      if (isWidgetListening) {
        widgetSpeechRec.stop();
        stopWidgetVoice();
      } else {
        try {
          widgetSpeechRec.start();
        } catch (e) {
          widgetSpeechRec = initWidgetVoice();
          widgetSpeechRec.start();
        }
      }
    }

    function stopWidgetVoice() {
      isWidgetListening = false;
      if (voiceBtn) {
        voiceBtn.classList.remove("listening");
        voiceBtn.title = "ভয়েস সার্চ";
      }
      if (inputEl && !inputEl.value) {
        inputEl.placeholder = "প্রশ্ন লিখুন (যেমন: আইসিটি বিভাগ, নোটিশ, ভর্তি)...";
      }
    }

    if (voiceBtn) {
      voiceBtn.addEventListener("click", () => toggleWidgetVoice());
    }

    function toggleWidget(forceState) {
      isOpen = forceState !== undefined ? forceState : !isOpen;
      if (isOpen) {
        win.classList.remove("nu-hidden");
        iconChat.style.display = "none";
        iconClose.style.display = "block";
        badge.style.display = "none";
        setTimeout(() => inputEl.focus(), 200);
      } else {
        win.classList.add("nu-hidden");
        iconChat.style.display = "block";
        iconClose.style.display = "none";
      }
    }

    window.__NU_TOGGLE__ = toggleWidget;

    launcher.addEventListener("click", () => toggleWidget());
    closeBtn.addEventListener("click", () => toggleWidget(false));

    setTimeout(() => {
      if (badge && !isOpen) {
        badge.style.transition = "opacity 0.5s ease-out";
        badge.style.opacity = "0";
        setTimeout(() => { if (badge) badge.style.display = "none"; }, 500);
      }
    }, 10000);

    function formatTime(d) {
      const date = d || new Date();
      let hours = date.getHours();
      const minutes = date.getMinutes();
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12;
      hours = hours ? hours : 12;
      const minutesStr = minutes < 10 ? '0' + minutes : minutes;
      return `${hours}:${minutesStr} ${ampm}`;
    }

    async function sendMessage(text) {
      const query = (text || inputEl.value || "").trim();
      if (!query) return;

      if (chipsEl) {
        chipsEl.remove();
        chipsEl = null;
      }

      const startTime = performance.now();
      const userTime = formatTime(new Date());

      inputEl.value = "";
      appendMessage("user", query, [], userTime);
      conversationHistory.push({ role: "user", content: query });

      typingEl.style.display = "flex";
      messagesBox.scrollTop = messagesBox.scrollHeight;

      try {
        const response = await fetch(`${API_BASE}/api/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: query,
            history: conversationHistory.slice(-6)
          })
        });

        if (!response.ok || !response.body) {
          throw new Error(`Server returned ${response.status}`);
        }

        typingEl.style.display = "none";

        const msgDiv = document.createElement("div");
        msgDiv.className = `nu-msg nu-bot`;
        const msgId = "widget-stream-" + Date.now();
        msgDiv.innerHTML = `
          <div class="nu-avatar">NU</div>
          <div class="nu-msg-content" style="position: relative;">
            <div id="${msgId}"></div>
            <div id="${msgId}-citations"></div>
            <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; align-items: center; gap: 6px; font-size: 10px; color: #94a3b8; user-select: none;">
              <span id="${msgId}-time">${formatTime(new Date())}</span>
              <span id="${msgId}-badge" style="display: none; background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; padding: 1px 5px; border-radius: 9999px; font-weight: 600; font-size: 9px;"></span>
            </div>
          </div>
        `;
        messagesBox.appendChild(msgDiv);

        const contentEl = document.getElementById(msgId);
        const citationsEl = document.getElementById(msgId + "-citations");
        const badgeEl = document.getElementById(msgId + "-badge");
        const timeEl = document.getElementById(msgId + "-time");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let accumulatedText = "";
        let finalCitations = [];
        let finalChips = [];
        let finalElapsed = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop();

          for (const line of lines) {
            const cleanLine = line.trim();
            if (!cleanLine.startsWith("data:")) continue;
            try {
              const data = JSON.parse(cleanLine.replace(/^data:\s*/, ""));
              if (data.type === "token") {
                accumulatedText += data.content;
                contentEl.innerHTML = formatMarkdown(accumulatedText);
                messagesBox.scrollTop = messagesBox.scrollHeight;
              } else if (data.type === "status") {
                if (!accumulatedText) {
                  contentEl.innerHTML = `<span style="color: #94a3b8; font-style: italic;">${data.content}</span>`;
                }
              } else if (data.type === "citations") {
                finalCitations = data.citations || [];
              } else if (data.type === "chips") {
                finalChips = data.chips || [];
              } else if (data.type === "done") {
                finalElapsed = data.response_time_sec;
              }
            } catch (err) {
              console.warn("SSE parse error", err);
            }
          }
        }

        const elapsedSec = finalElapsed || ((performance.now() - startTime) / 1000).toFixed(2);
        const botTime = formatTime(new Date());
        timeEl.textContent = botTime;

        if (badgeEl) {
          badgeEl.textContent = `⏱️ ${elapsedSec}s`;
          badgeEl.style.display = "inline-flex";
        }

        if (finalCitations && finalCitations.length > 0) {
          citationsEl.innerHTML = `<div class="nu-sources"><strong>অফিসিয়াল সূত্র:</strong> ` +
            finalCitations.map(c => `<a href="${c.url}" target="_blank">🔗 ${c.title || 'Official Link'}</a>`).join("") +
            `</div>`;
        }

        if (finalChips && finalChips.length > 0) {
          renderChips(finalChips);
        }

        conversationHistory.push({ role: "bot", content: accumulatedText });

      } catch (err) {
        typingEl.style.display = "none";
        const elapsedSec = ((performance.now() - startTime) / 1000).toFixed(2);
        const botTime = formatTime(new Date());
        appendMessage("bot", `⚠️ সার্ভার সংযোগে সমস্যা হয়েছে: ${err.message}`, [], botTime, elapsedSec);
      }

      messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    window.__NU_SEND__ = sendMessage;

    function appendMessage(role, text, citations = [], timestamp = null, responseTime = null) {
      const msgDiv = document.createElement("div");
      msgDiv.className = `nu-msg nu-${role}`;
      const timeStr = timestamp || formatTime(new Date());

      if (role === "bot") {
        let citationsHtml = "";
        if (citations && citations.length > 0) {
          citationsHtml = `<div class="nu-sources"><strong>অফিসিয়াল সূত্র:</strong> ` +
            citations.map(c => `<a href="${c.url}" target="_blank">🔗 ${c.title || 'Official Link'}</a>`).join("") +
            `</div>`;
        }
        msgDiv.innerHTML = `
          <div class="nu-avatar">NU</div>
          <div class="nu-msg-content" style="position: relative;">
            ${formatMarkdown(text)}
            ${citationsHtml}
            <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; align-items: center; gap: 6px; font-size: 10px; color: #94a3b8; user-select: none;">
              ${responseTime ? `<span style="background: #ecfdf5; color: #047857; font-weight: 600; padding: 1px 6px; border-radius: 4px; border: 1px solid #a7f3d0;" title="Response time consumed">⏱️ ${responseTime}s</span>` : ''}
              <span>${timeStr}</span>
            </div>
          </div>
        `;
      } else {
        msgDiv.innerHTML = `
          <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px;">
            <div class="nu-msg-content">${text.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
            <div style="font-size: 10px; color: #94a3b8; padding-right: 4px; user-select: none;">${timeStr}</div>
          </div>
        `;
      }

      messagesBox.appendChild(msgDiv);
      messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    function renderChips(chips) {
      if (chipsEl) chipsEl.remove();
      chipsEl = document.createElement("div");
      chipsEl.id = "nu-chips";
      chipsEl.className = "nu-chips-container";
      chipsEl.innerHTML = chips.map(c => `<button class="nu-chip-btn" data-query="${c}">${c}</button>`).join("");
      messagesBox.appendChild(chipsEl);
      messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    sendBtn.addEventListener("click", () => sendMessage());
    inputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    messagesBox.addEventListener("click", (e) => {
      const chip = e.target.closest(".nu-chip-btn");
      if (chip) {
        const q = chip.getAttribute("data-query");
        sendMessage(q);
      }
    });

    clearBtn.addEventListener("click", () => {
      conversationHistory = [];
      const nowTime = formatTime(new Date());
      messagesBox.innerHTML = `
        <div class="nu-msg nu-bot">
          <div class="nu-avatar">NU</div>
          <div class="nu-msg-content">
            <p style="margin:0 0 6px 0;"><strong>নতুন কথোপকথন শুরু হয়েছে</strong></p>
            <p style="margin:0;">আপনার যেকোনো একাডেমিক বা অফিসিয়াল প্রশ্ন করুন।</p>
            <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; align-items: center; font-size: 10px; color: #94a3b8; user-select: none;">
              <span>${nowTime}</span>
            </div>
          </div>
        </div>
        <div id="nu-chips" class="nu-chips-container">
          <button class="nu-chip-btn" data-query="Token Service">🎫 টোকেন সার্ভিস (Token Service)</button>
          <button class="nu-chip-btn" data-query="Check token status">📋 টোকেন স্ট্যাটাস চেক</button>
          <button class="nu-chip-btn" data-query="আইসিটি দপ্তরের কর্মকর্তা ও কর্মচারীবৃন্দের তালিকা">💻 আইসিটি বিভাগ তালিকা</button>
          <button class="nu-chip-btn" data-query="Honours 4th year exam routine">📅 অনার্স ৪র্থ বর্ষ রুটিন</button>
        </div>
      `;
      chipsEl = document.getElementById("nu-chips");
    });

    if (isOpen || pendingMessage) {
      toggleWidget(true);
      if (pendingMessage) {
        sendMessage(pendingMessage);
        pendingMessage = null;
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
