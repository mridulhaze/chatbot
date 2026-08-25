import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional, Tuple
from google import genai
from google.genai import types

from backend.core.config import settings
from backend.models.schemas import ChatRequest, ChatResponse, SourceCitation
from .context import get_context_manager, SessionState
from .intent import get_intent_classifier
from .router import get_skill_router
from .skill_registry import get_skill_registry
from .mcp_client import get_mcp_client
from .preloaded_responses import get_preloaded_response

logger = logging.getLogger("NU_AI_ORCHESTRATOR")

# High-speed LRU / TTL response cache for repetitive queries
_CHAT_CACHE: Dict[str, Tuple[float, ChatResponse]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache

class AIOrchestrator:
    def __init__(self):
        self.context_mgr = get_context_manager()
        self.intent_classifier = get_intent_classifier()
        self.router = get_skill_router()
        self.skill_registry = get_skill_registry()
        self.mcp_client = get_mcp_client()
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.models = [settings.PRIMARY_MODEL] + settings.FALLBACK_MODELS
        self.executor = ThreadPoolExecutor(max_workers=8)

    def process_chat(self, req: ChatRequest) -> ChatResponse:
        """
        High-speed multi-stage orchestration turn:
        Stage 1: Instant Preloaded Knowledge Engine (< 0.001s)
        Stage 2: LRU In-Memory Cache Lookup (< 0.001s)
        Stage 3: Token Service & Status Shortcuts (< 0.01s)
        Stage 4: Parallel MCP Retrieval & Fast Gemini Generative Turn (< 1.5s)
        """
        raw_msg = req.message.strip()

        # Stage 1: Check Preloaded Instant Knowledge Engine (< 0.001s)
        preloaded = get_preloaded_response(raw_msg)
        if preloaded:
            return preloaded

        # Stage 2: Check in-memory query cache (< 0.001s)
        msg_clean = raw_msg.lower().strip(" .!?,;")
        cache_key = f"{msg_clean}_{req.service_code or ''}"
        now = time.time()
        if cache_key in _CHAT_CACHE:
            cached_time, cached_resp = _CHAT_CACHE[cache_key]
            if now - cached_time < CACHE_TTL_SECONDS:
                return cached_resp

        session = self.context_mgr.get_session(req.session_id)

        # Update service if provided in request
        if req.service_code:
            session.selected_service_code = req.service_code.upper()

        # Step 1: Intent & Entity Classification
        intent, entities = self.intent_classifier.classify(raw_msg, session_context=session)
        if "service_code" in entities:
            session.selected_service_code = entities["service_code"]

        # Step 2: Skill Routing
        skill_name = self.router.route(intent, entities, session_context=session)
        skill_def = self.skill_registry.get_skill(skill_name)
        session.active_skill = skill_name

        # Step 3: Handle Token Service Workflows
        if skill_name == "token_service":
            return self._handle_token_service_workflow(raw_msg, intent, entities, session)

        # Step 4: Handle Official Knowledge Skills (Examination, Admission, Result, Document, General)
        return self._handle_official_knowledge_skills(raw_msg, skill_name, intent, entities, session)

    def _handle_token_service_workflow(
        self,
        raw_msg: str,
        intent: str,
        entities: Dict[str, Any],
        session: SessionState
    ) -> ChatResponse:
        """
        Executes Token Service multi-turn workflow via Token MCP.
        """
        # Case A: Check Token Status
        if intent == "TOKEN_STATUS" or "token_id" in entities:
            token_id = entities.get("token_id", raw_msg.strip().upper())
            res = self.mcp_client.call_tool("token_mcp", "get_token_status", {"token_id": token_id})
            
            if res.get("success") and res.get("data"):
                data = res["data"]
                status = data["status"]
                service = data["service_name"]
                solver = data.get("solver_name") or "দায়িত্বপ্রাপ্ত ডেস্ক"
                created = data.get("created_date", "")
                solve_msg = data.get("solve_message")

                reply = f"### 🎫 সাপোর্ট টোকেন বিবরণী (Token Details)\n\n"
                reply += f"• **টোকেন আইডি:** `{data['token_id']}`\n"
                reply += f"• **সার্ভিস:** {service}\n"
                reply += f"• **বর্তমান অবস্থা (Status):** {data['status_display']}\n"
                reply += f"• **দায়িত্বপ্রাপ্ত দপ্তর:** {solver}\n"
                reply += f"• **দাখিলের তারিখ:** {created}\n"

                if solve_msg:
                    reply += f"\n---\n**✅ সমাধান (Resolution):**\n{solve_msg}\n"

                return ChatResponse(
                    reply=reply,
                    intent="TOKEN_STATUS",
                    skill_used="token_service",
                    token_card=data,
                    suggested_chips=["নতুন টোকেন খুলুন", "ভর্তি সংক্রান্ত তথ্য", "পরীক্ষার রুটিন"]
                )
            else:
                return ChatResponse(
                    reply=f"⚠️ দুঃখিত, `{token_id}` নম্বরের কোনো টোকেন ডাটাবেজে পাওয়া যায়নি। দয়া করে সঠিক টোকেন নম্বর দিন (যেমন: NU-2026-000123)।",
                    intent="TOKEN_STATUS",
                    skill_used="token_service",
                    suggested_chips=["টোকেন সেবা", "নতুন টোকেন তৈরি করুন"]
                )

        # Case B: User confirms token creation
        if intent == "TOKEN_CONFIRM_CREATE" or (session.pending_token_confirmation and "yes" in raw_msg.lower()):
            service_code = session.selected_service_code or "OTHER"
            problem = session.problem_description or raw_msg
            
            res = self.mcp_client.call_tool("token_mcp", "create_token", {
                "service_code": service_code,
                "problem": problem,
                "user_id": session.session_id
            })

            session.pending_token_confirmation = False
            session.similar_case_shown = False
            self.context_mgr.update_session(session)

            if res.get("success") and res.get("data"):
                t_data = res["data"]
                t_id = t_data["token_id"]
                session.last_created_token_id = t_id

                reply = f"### 🎫 আপনার সাপোর্ট টোকেন সফলভাবে তৈরি হয়েছে!\n\n"
                reply += f"• **টোকেন আইডি (Token ID):** `{t_id}`\n"
                reply += f"• **সার্ভিস:** {t_data['service_name']}\n"
                reply += f"• **সমস্যা:** {t_data['problem']}\n"
                reply += f"• **স্ট্যাটাস:** 🟡 **PENDING**\n\n"
                reply += f"পরবর্তীতে স্ট্যাটাস জানতে যেকোনো সময় টাইপ করুন: `Check {t_id}`।"

                return ChatResponse(
                    reply=reply,
                    intent="TOKEN_CREATE",
                    skill_used="token_service",
                    token_card=t_data,
                    suggested_chips=[f"Check {t_id}", "অন্যান্য জিজ্ঞাসা"]
                )

        # Case C: User cancels
        if intent == "TOKEN_CANCEL":
            session.pending_token_confirmation = False
            session.similar_case_shown = False
            self.context_mgr.update_session(session)
            return ChatResponse(
                reply="ধন্যবাদ! আপনার কোনো সমস্যা থাকলে যেকোনো সময় আবার যোগাযোগ করতে পারেন।",
                intent="TOKEN_CANCEL",
                skill_used="token_service",
                suggested_chips=["টোকেন সেবা", "নোটিশ দেখুন", "পরীক্ষার তথ্য"]
            )

        # Case D: Token Service Menu / Service selection
        if intent == "TOKEN_SERVICE_MENU" or (not session.selected_service_code and not session.problem_description):
            services_res = self.mcp_client.call_tool("token_mcp", "get_services", {})
            services = services_res.get("data", []) if services_res.get("success") else []
            
            buttons = [
                {"label": s["service_name"], "action": f"Service: {s['service_code']}"}
                for s in services
            ]

            reply = "### 🎫 জাতীয় বিশ্ববিদ্যালয় টোকেন ও সাপোর্ট সার্ভিস\n\n"
            reply += "অনুগ্রহ করে নিচে থেকে আপনার কাঙ্ক্ষিত সার্ভিসের ক্যাটাগরি নির্বাচন করুন অথবা আপনার সমস্যাটি সংক্ষেপে লিখুন:"

            return ChatResponse(
                reply=reply,
                intent="TOKEN_SERVICE_MENU",
                skill_used="token_service",
                interactive_buttons=buttons,
                suggested_chips=[s["service_name"] for s in services[:5]]
            )

        # Case E: User has described a problem -> Search similar solved cases
        session.problem_description = raw_msg
        service_code = session.selected_service_code or "OTHER"
        session.pending_token_confirmation = True
        self.context_mgr.update_session(session)

        sim_res = self.mcp_client.call_tool("token_mcp", "search_similar_solved_problems", {
            "problem": raw_msg,
            "service_code": service_code,
            "limit": 2
        })

        similar_cases = sim_res.get("data", []) if sim_res.get("success") else []

        if similar_cases:
            top = similar_cases[0]
            reply = f"### 🔎 অনুরুপ একটি পূর্ববর্তী সমাধান রেকর্ড পাওয়া গেছে\n\n"
            reply += f"• **বিষয় / সার্ভিস:** {top['service_name']}\n"
            reply += f"• **সাধারণ সমাধান (Common Resolution):**\n> {top['solution']}\n\n"
            reply += f"এই সমাধানে কি আপনার কাজ হয়েছে, নাকি আপনি সরাসরি জাতীয় বিশ্ববিদ্যালয়ের সাপোর্ট ডেস্কে একটি **সাপোর্ট টোকেন** খুলতে চান?"

            buttons = [
                {"label": "🎫 নতুন টোকেন তৈরি করুন (Create Token)", "action": "Create Token"},
                {"label": "✅ সমাধান পেয়েছি (Problem Solved)", "action": "Cancel"}
            ]

            return ChatResponse(
                reply=reply,
                intent="SOLVED_PROBLEM_SEARCH",
                skill_used="token_service",
                interactive_buttons=buttons,
                suggested_chips=["Create Token", "Cancel"]
            )
        else:
            reply = f"আপনার সমস্যার বিবরণ পেয়েছি: *\"{raw_msg}\"*\n\n"
            reply += f"আপনি কি জাতীয় বিশ্ববিদ্যালয়ের সংশ্লিষ্ট ডেস্কে একটি **অফিসিয়াল সাপোর্ট টোকেন** পাঠাতে চান?"

            buttons = [
                {"label": "🎫 টোকেন তৈরি করুন", "action": "Create Token"},
                {"label": "বাতিল করুন", "action": "Cancel"}
            ]

            return ChatResponse(
                reply=reply,
                intent="TOKEN_CONFIRM_CREATE",
                skill_used="token_service",
                interactive_buttons=buttons,
                suggested_chips=["Create Token", "Cancel"]
            )

    def _handle_official_knowledge_skills(
        self,
        raw_msg: str,
        skill_name: str,
        intent: str,
        entities: Dict[str, Any],
        session: SessionState
    ) -> ChatResponse:
        """
        High-speed retrieval and generation using parallel MCP search and optimized GenAI parameters.
        """
        # Parallel MCP Tool Execution (Runs in < 50ms concurrently)
        future_kn = self.executor.submit(self.mcp_client.call_tool, "knowledge_mcp", "search_nu_knowledge", {"query": raw_msg, "limit": 3})
        future_notices = self.executor.submit(self.mcp_client.call_tool, "knowledge_mcp", "search_notices", {"query": raw_msg, "limit": 3})

        kn_res = future_kn.result()
        notice_res = future_notices.result()

        knowledge_docs = kn_res.get("data", []) if kn_res.get("success") else []
        notices = notice_res.get("data", []) if notice_res.get("success") else []

        # Assemble Context
        context_parts = []
        citations = []

        for n in notices:
            context_parts.append(f"[অফিসিয়াল নোটিশ] শিরোনাম: {n.get('title')} | তারিখ: {n.get('published_date')} | লিংক: {n.get('url')}")
            citations.append(SourceCitation(
                title=n.get("title", "NU Notice"),
                url=n.get("url", "https://www.nu.ac.bd"),
                date=n.get("published_date")
            ))

        for k in knowledge_docs:
            context_parts.append(f"[অফিসিয়াল তথ্য] {k.get('content')[:400]}")

        combined_context = "\n\n".join(context_parts) if context_parts else "জাতীয় বিশ্ববিদ্যালয় অফিসিয়াল তথ্য ভাণ্ডার।"

        prompt = f"""
তুমি জাতীয় বিশ্ববিদ্যালয়ের স্মার্ট AI একাডেমিক অ্যাসিস্ট্যান্ট।
নিচে অফিসিয়াল তথ্যাবলি দেওয়া হলো:
=== OFFICIAL CONTEXT ===
{combined_context}
=== END CONTEXT ===

ব্যবহারকারীর প্রশ্ন: {raw_msg}

নির্দেশনা:
1. অফিসিয়াল কনটেক্সটের ভিত্তিতে সরাসরি, সংক্ষিপ্ত ও সুস্পষ্ট বাংলায় উত্তর দাও।
2. অপ্রয়োজনীয় ভূমিকা বা পুনরাবৃত্তি এড়িয়ে চলো।
3. তথ্যের সাথে প্রাসঙ্গিক লিংক উল্লেখ করো।
"""
        reply_text = "জাতীয় বিশ্ববিদ্যালয়ের সর্বশেষ তথ্য অনুসারে আপনার প্রশ্নের উত্তর অনুসন্ধান করা হয়েছে।"

        if self.client:
            config = types.GenerateContentConfig(
                max_output_tokens=600,
                temperature=0.2
            )
            for model_name in self.models:
                try:
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )
                    if res and res.text:
                        reply_text = res.text.strip()
                        break
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")

        resp = ChatResponse(
            reply=reply_text,
            citations=citations,
            intent=intent,
            skill_used=skill_name,
            suggested_chips=["🎫 টোকেন সেবা", "🎓 অনার্স ভর্তি", "📝 পরীক্ষার রুটিন", "📄 সকল নোটিশ"]
        )

        # Store in high-speed cache
        cache_key = f"{raw_msg.lower().strip(' .!?,;')}_{session.selected_service_code or ''}"
        _CHAT_CACHE[cache_key] = (time.time(), resp)
        if len(_CHAT_CACHE) > 200:
            oldest_key = min(_CHAT_CACHE.keys(), key=lambda k: _CHAT_CACHE[k][0])
            _CHAT_CACHE.pop(oldest_key, None)

        return resp

_ai_orchestrator_instance: Optional[AIOrchestrator] = None

def get_ai_orchestrator() -> AIOrchestrator:
    global _ai_orchestrator_instance
    if _ai_orchestrator_instance is None:
        _ai_orchestrator_instance = AIOrchestrator()
    return _ai_orchestrator_instance
