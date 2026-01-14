"""Gemini Agent Service for AI-powered chat responses.

This service handles:
- Gemini client initialization using OpenAI-compatible endpoint
- Conversation context building from message history
- MCP tool routing via intent detection
- Response generation with retry logic
- Friendly, casual conversation style (like a buddy!)
- Roman English/Urdu/Hindi language support (Hinglish)

Refactored to use Official MCP SDK via MCP client for tool execution.

Intent Detection Rules (English + Roman Urdu/Hindi):
- Task Creation: add, create, remember, remind, need to, want to,
                 karna hai, lena hai, chahiye, mujhe, add karo
- Task Listing: see, show, list, what, view, display, my tasks,
                dikhao, batao, kya hai, kya karna hai
- Task Completion: done, complete, finish, mark, checked,
                   ho gaya, kar diya, khatam, nipta diya
- Task Deletion: delete, remove, cancel, get rid of, drop,
                 hata do, nikalo, delete karo, mita do
- Task Update: update, change, edit, modify, rename,
               badlo, change karo, edit karo, theek karo
"""

import asyncio
import json
import logging
import random
import re
from typing import Optional

from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError

from app.config import get_settings
from app.models import Message
from app.services.mcp_client import get_mcp_client, MCPClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a friendly buddy who helps manage tasks - like a chill friend who's always there to help out! Talk casually, use everyday language, and be warm and supportive.

You understand:
- English (formal and casual)
- Roman English / Romanized Urdu-Hindi (like "mujhe banana lena hai", "kaam kar diya", "dikhao tasks")
- Mix of languages (Hinglish/Urdish)

Your vibe:
- Talk like a friend, not a robot! Use casual phrases like "yaar", "bro", "done bhai!", "no worries!"
- Be encouraging and supportive - celebrate when they complete tasks!
- Keep it short and sweet - nobody likes long boring messages
- Use emojis occasionally to be more expressive 😊

What you help with:
- Adding tasks (when someone says "buy banana", "mujhe ye karna hai", "remind me to...")
- Showing tasks (when they ask "kya karna hai?", "show tasks", "list dikhao")
- Completing tasks (when they say "ho gaya", "done", "finish kar diya")
- Deleting tasks (when they say "hata do", "delete karo", "remove this")

Important:
- If someone mentions something they need to do or buy, ADD it as a task automatically
- Understand intent from context - "banana lena hai" means add task, not a question
- When unsure which task they mean, ask nicely in a friendly way
- If they chat about random stuff, be friendly but gently bring it back to tasks

When tool results come in, confirm the action in a friendly way - like a buddy would!"""


class AIServiceUnavailableError(Exception):
    """Raised when the AI service is unavailable after retries."""
    pass


class AgentService:
    """Service for managing Gemini agent interactions with MCP tool support.

    Uses MCP client to execute tools from the Official MCP SDK server.
    """

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    # Intent detection keywords (English + Roman English/Urdu/Hindi)
    ADD_KEYWORDS = [
        # English
        "add", "create", "new task", "remind", "remember",
        "need to", "have to", "should", "must", "todo",
        "want to", "gotta", "going to", "gonna", "plan to",
        "i want", "i need", "buy", "get",
        # Roman Urdu/Hindi
        "karna hai", "karna he", "karna", "karni hai", "karni",
        "lena hai", "lena he", "lena", "leni hai", "leni",
        "chahiye", "chaiye", "chahte", "mangta", "mangti",
        "yaad", "yaad kara", "yaad dila", "remind karo",
        "add karo", "add kardo", "daal do", "daalo", "dal do",
        "likhna", "likho", "likh do", "note karo",
        "mujhe", "mujhay", "mereko", "mere liye",
        "khareed", "khareedna", "kharidna", "purchase",
    ]

    LIST_KEYWORDS = [
        # English
        "list", "show", "see", "view", "display", "what are",
        "what's", "my tasks", "all tasks", "tasks", "pending",
        "what do i have", "what do i need",
        # Roman Urdu/Hindi
        "dikhao", "dikha do", "dikha", "batao", "bata do",
        "kya hai", "kya karna", "kya karna hai", "kya pending",
        "konse", "kaun se", "mere tasks", "meri list",
        "sab dikhao", "sara dikhao", "poora list",
        "kya kya", "kitne tasks", "kitne kaam",
    ]

    COMPLETE_KEYWORDS = [
        # English
        "done", "complete", "finish", "finished", "completed",
        "mark", "check", "checked", "tick", "accomplish",
        # Roman Urdu/Hindi
        "ho gaya", "hogaya", "ho gya", "hogya",
        "kar diya", "kardiya", "kar dia", "kardia",
        "kar liya", "karliya", "kar lia", "karlia",
        "khatam", "khtam", "mukammal", "complete karo",
        "done hai", "done he", "finish kiya",
        "nipta", "nipta diya", "nipat gaya",
    ]

    DELETE_KEYWORDS = [
        # English
        "delete", "remove", "cancel", "get rid", "drop",
        "trash", "eliminate", "clear", "erase",
        # Roman Urdu/Hindi
        "hata do", "hatao", "hata de", "hatado",
        "delete karo", "delete kardo", "remove karo",
        "nikalo", "nikal do", "nikal de",
        "cancel karo", "cancel kardo",
        "mita do", "mitao", "mita de",
        "khatam karo", "band karo",
    ]

    UPDATE_KEYWORDS = [
        # English
        "update", "change", "edit", "modify", "rename",
        "fix", "correct", "alter", "revise",
        # Roman Urdu/Hindi
        "badlo", "badal do", "badal de", "change karo",
        "edit karo", "theek karo", "sahi karo",
        "update karo", "modify karo",
        "naam badlo", "rename karo",
    ]

    def __init__(self):
        """Initialize the Gemini client and MCP client."""
        settings = get_settings()

        # Configure OpenAI client to use Gemini's OpenAI-compatible endpoint
        self.client = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = "gemini-2.0-flash"

        # Initialize MCP client for tool execution
        self.mcp_client: MCPClient = get_mcp_client()
        logger.info("AgentService initialized with MCP client")

    def build_context(
        self,
        history: list[Message],
        tool_context: Optional[str] = None
    ) -> list[dict]:
        """Build conversation context from message history."""
        system_content = SYSTEM_PROMPT
        if tool_context:
            system_content += f"\n\n[Tool Results]\n{tool_context}"

        messages = [{"role": "system", "content": system_content}]

        for msg in history:
            role = "user" if msg.role == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg.content
            })

        return messages

    def _detect_intent(self, message: str) -> tuple[str, dict]:
        """Detect user intent from message for tool routing.

        Priority order:
        1. Delete (destructive action - check first)
        2. Complete (status change)
        3. Update (modification)
        4. List (query)
        5. Add (default creation action)

        Returns:
            Tuple of (intent, extracted_args)
        """
        msg_lower = message.lower().strip()

        # Skip very short messages or greetings (English + Roman Urdu/Hindi)
        greetings = [
            "hi", "hello", "hey", "hola", "yo", "sup", "thanks", "thank you", "bye", "goodbye",
            "salam", "assalam", "aoa", "aslam", "walaikum", "shukriya", "shukria",
            "kya haal", "kaise ho", "theek", "thik", "acha", "ok", "okay", "haan", "han",
            "ji", "g", "nahi", "nhi", "na", "khuda hafiz", "allah hafiz", "bye bhai",
            "yaar", "bro", "bhai", "dost"
        ]
        if msg_lower in greetings or len(msg_lower) < 3:
            return "default", {}

        # 1. DELETE intent - check first (destructive action)
        if any(kw in msg_lower for kw in self.DELETE_KEYWORDS):
            task_title = self._extract_task_reference(message, self.DELETE_KEYWORDS)
            if task_title:
                return "delete", {"task_title": task_title}

        # 2. COMPLETE intent - status change
        if any(kw in msg_lower for kw in self.COMPLETE_KEYWORDS):
            task_title = self._extract_task_reference(message, self.COMPLETE_KEYWORDS)
            if task_title:
                return "complete", {"task_title": task_title}

        # 3. UPDATE intent - modification
        if any(kw in msg_lower for kw in self.UPDATE_KEYWORDS):
            # For update, we need the current task and new value
            task_title = self._extract_task_reference(message, self.UPDATE_KEYWORDS)
            return "update", {"task_title": task_title or message}

        # 4. LIST intent - query tasks
        if any(kw in msg_lower for kw in self.LIST_KEYWORDS):
            # Check for filter preferences
            include_completed = "completed" in msg_lower or "all" in msg_lower or "done" in msg_lower
            return "list", {"include_completed": include_completed}

        # 5. ADD intent - creation (default for task-like statements)
        if any(kw in msg_lower for kw in self.ADD_KEYWORDS):
            title = self._extract_task_title(message)
            if title:
                return "add", {"title": title}

        # Check if message looks like a task (starts with verb or is imperative)
        task_verbs = [
            # English verbs
            "buy", "call", "email", "send", "write", "read", "clean",
            "fix", "make", "get", "pick", "schedule", "book", "pay",
            "submit", "review", "prepare", "finish", "start", "do",
            "order", "deliver", "cook", "wash", "iron", "study",
            # Roman Urdu/Hindi verbs
            "khareed", "le", "lao", "jao", "karo", "kha", "pi",
            "parh", "padh", "likh", "bhej", "call", "mil",
        ]
        first_word = msg_lower.split()[0] if msg_lower.split() else ""
        if first_word in task_verbs:
            return "add", {"title": message}

        # If message contains "lena", "karna" etc. treat as task
        task_intent_words = ["lena", "karna", "karni", "leni", "chahiye", "chaiye"]
        if any(word in msg_lower for word in task_intent_words):
            return "add", {"title": message}

        return "default", {}

    def _extract_task_title(self, message: str) -> str:
        """Extract task title from an add task message."""
        msg_lower = message.lower()
        title = message

        # Remove common prefixes (English + Roman Urdu/Hindi)
        prefixes = [
            # English prefixes
            "add a task to ", "add task to ", "add a task ", "add task ",
            "create a task to ", "create task to ", "create a task ", "create task ",
            "new task to ", "new task ",
            "remind me to ", "remember to ",
            "i need to ", "i have to ", "i should ", "i must ", "i want to ",
            "i gotta ", "i'm going to ", "i gonna ", "i plan to ",
            "i want ", "i need ", "i wanna ",
            "add ", "create ", "todo ",
            # Roman Urdu/Hindi prefixes
            "mujhe ", "mujhay ", "mereko ", "mere liye ",
            "muje ", "mjhe ", "mjhy ",
            "yaad kara do ", "yaad kara ", "yaad dila do ", "yaad dila ",
            "remind karo ", "remind kardo ",
            "add karo ", "add kardo ", "task add karo ",
            "daal do ", "daalo ", "dal do ",
            "likh do ", "likho ", "note karo ",
        ]

        for prefix in prefixes:
            if msg_lower.startswith(prefix):
                title = message[len(prefix):].strip()
                break

        # Remove common suffixes (Roman Urdu/Hindi)
        suffixes = [
            " karna hai", " karna he", " karna", " karni hai", " karni",
            " lena hai", " lena he", " lena", " leni hai", " leni",
            " chahiye", " chaiye", " hai", " he",
        ]
        for suffix in suffixes:
            if title.lower().endswith(suffix):
                title = title[:-len(suffix)].strip()
                break

        # Clean up
        title = title.rstrip(".!?")
        return title if title else message

    def _extract_task_reference(self, message: str, action_keywords: list) -> str:
        """Extract task reference from a message with action keywords.

        Handles patterns like:
        - "delete buy groceries" -> "buy groceries"
        - "delete the groceries task" -> "groceries"
        - "mark buy milk as done" -> "buy milk"
        - "I finished the laundry" -> "laundry"
        """
        msg_lower = message.lower()
        task_ref = message

        # Build prefix patterns from keywords (order matters - longer first)
        prefixes = []
        for kw in action_keywords:
            prefixes.extend([
                f"{kw} the task ", f"{kw} task ", f"{kw} the ", f"{kw} ",
                f"i {kw}ed the ", f"i {kw}ed ",
                f"i've {kw}ed the ", f"i've {kw}ed ",
                f"i have {kw}ed the ", f"i have {kw}ed "
            ])

        # Also add common patterns
        prefixes.extend([
            "mark the task ", "mark task ", "mark the ", "mark ",
            "mark as done the ", "mark as done ",
            "done with the ", "done with ",
            "finished with the ", "finished with ", "finished the ", "finished ",
            "completed the ", "completed ",
            "i'm done with the ", "i'm done with ",
        ])

        # Sort by length descending to match longer patterns first
        prefixes.sort(key=len, reverse=True)

        for prefix in prefixes:
            if msg_lower.startswith(prefix):
                task_ref = message[len(prefix):].strip()
                break

        # Remove common suffixes (order matters - longer first)
        suffixes = [
            " as completed", " as complete", " as finished", " as done",
            " task please", " task pls", " task now", " task",
            " please", " pls", " now"
        ]
        suffixes.sort(key=len, reverse=True)

        for suffix in suffixes:
            if task_ref.lower().endswith(suffix):
                task_ref = task_ref[:-len(suffix)].strip()
                break  # Only remove one suffix

        # Remove leading "the " if present
        if task_ref.lower().startswith("the "):
            task_ref = task_ref[4:].strip()

        return task_ref

    def _map_intent_to_tool(self, intent: str) -> Optional[str]:
        """Map an intent to an MCP tool name."""
        intent_tool_map = {
            "add": "add_task",
            "list": "list_tasks",
            "complete": "complete_task_toggle",
            "delete": "delete_task",
            "update": "update_task",
        }
        return intent_tool_map.get(intent)

    async def _execute_mcp_tool(
        self,
        user_id: str,
        tool_name: str,
        args: dict
    ) -> dict:
        """Execute an MCP tool via the client."""
        tool_args = {"user_id": user_id, **args}
        return await self.mcp_client.call_tool(tool_name, tool_args)

    def _format_friendly_response(self, intent: str, result: dict, args: dict) -> str:
        """Format a friendly, casual confirmation response for tool results."""
        if not result.get("success"):
            error = result.get("error", "Unknown error")

            # Handle specific error cases gracefully - friendly style
            if "not found" in error.lower():
                return "Yaar, mujhe wo task nahi mila 🤔 Thoda specific bata do konsa task?"
            elif "multiple" in error.lower():
                matches = result.get("matches", [])
                if matches:
                    match_list = "\n".join([f"  • {m.get('title')}" for m in matches[:5]])
                    return f"Bhai, kai tasks mil gaye similar wale:\n{match_list}\n\nKonsa chahiye exactly?"
                return "Multiple tasks mil gaye yaar. Thoda specific bata do!"
            else:
                return f"Oops! Kuch issue ho gaya: {error}. Dobara try karo please?"

        # Success responses - friendly casual style
        if intent == "add":
            task = result.get("task", {})
            title = task.get("title", args.get("title", "your task"))
            responses = [
                f"Done bhai! '{title}' add kar diya list mein ✅",
                f"Likh liya yaar! '{title}' ab list mein hai 📝",
                f"Ho gaya! '{title}' add ho gaya ✨",
            ]
            return random.choice(responses)

        elif intent == "list":
            tasks = result.get("tasks", [])
            count = result.get("count", len(tasks))

            if count == 0:
                return "Bhai abhi koi task nahi hai list mein 📭 Kuch add karna hai?"

            # Format task list
            task_lines = []
            for t in tasks[:10]:
                status = "✅" if t.get("completed") else "⏳"
                task_lines.append(f"  {status} {t.get('title', 'Unknown')}")

            task_list = "\n".join(task_lines)
            if count > 10:
                header = f"Yeh rahi teri list yaar ({count} tasks hain total):"
            else:
                header = "Yeh rahi teri task list:"

            return f"{header}\n{task_list}"

        elif intent == "complete":
            task = result.get("task", {})
            msg = result.get("message", "")
            if msg:
                return msg
            title = task.get("title", "the task")
            is_completed = task.get("completed", True)
            if is_completed:
                responses = [
                    f"Shabaash! '{title}' done mark kar diya 🎉 Great job!",
                    f"Arre wah! '{title}' complete ho gaya 💪 Keep it up!",
                    f"Mast! '{title}' khatam ✅ Tera kaam ho gaya!",
                ]
                return random.choice(responses)
            else:
                return f"Okay, '{title}' wapas pending mein daal diya - ab karna padega! 😄"

        elif intent == "delete":
            msg = result.get("message", "")
            if msg:
                return msg
            return "Hata diya bhai! Task list se nikal gaya 🗑️"

        elif intent == "update":
            task = result.get("task", {})
            title = task.get("title", "the task")
            return f"Done! Task update ho gaya: '{title}' ✏️"

        return "Ho gaya! ✅"

    async def _demo_mode_response(
        self,
        user_id: str,
        user_message: str,
        existing_tool_results: list[dict] = None,
        intent: str = None,
        args: dict = None,
    ) -> tuple[str, list[dict]]:
        """Generate a demo mode response when AI API is unavailable.

        Uses existing tool results if provided, otherwise executes tools.

        Args:
            user_id: User ID for tool operations
            user_message: Current user message
            existing_tool_results: Tool results already executed (to avoid duplicates)
            intent: Pre-detected intent (to avoid re-detecting)
            args: Pre-extracted args (to avoid re-extracting)
        """
        tool_call_results = existing_tool_results or []

        # If tool was already executed, just format the response
        if tool_call_results and intent:
            result = tool_call_results[0]["result"]
            response = self._format_friendly_response(intent, result, args or {})
            return response, tool_call_results

        # Only detect intent and execute tool if not already done
        if intent is None:
            intent, args = self._detect_intent(user_message)

        tool_name = self._map_intent_to_tool(intent)

        if tool_name and not tool_call_results:
            try:
                result = await self._execute_mcp_tool(user_id, tool_name, args)
                tool_call_results.append({"tool_name": tool_name, "result": result})

                response = self._format_friendly_response(intent, result, args)
                return response, tool_call_results

            except Exception as e:
                logger.error(f"Demo mode MCP tool error: {e}")
                return f"I encountered an error: {str(e)}. Please try again.", tool_call_results

        # Default response for non-task messages - friendly style
        return ("Hey yaar! Main tera task buddy hoon 🙌\n\n"
                "Main tujhe help kar sakta hoon:\n"
                "  📝 Tasks add karna (bol 'banana lena hai' ya 'add groceries')\n"
                "  📋 Tasks dikhana (bol 'dikhao tasks' ya 'show my list')\n"
                "  ✅ Tasks complete karna (bol 'ho gaya' ya 'done')\n"
                "  🗑️ Tasks delete karna (bol 'hata do' ya 'delete task')\n\n"
                "Bol, kya karna hai? 😊"), tool_call_results

    async def generate_response(
        self,
        user_id: str,
        user_message: str,
        history: list[Message]
    ) -> tuple[str, list[dict]]:
        """Generate an AI response with MCP tool support.

        Flow:
        1. Detect intent from user message
        2. If tool needed, execute via MCP client
        3. Include tool results in AI context
        4. Generate AI response with friendly confirmation

        Args:
            user_id: User ID for tool operations
            user_message: Current user message
            history: Previous conversation messages

        Returns:
            Tuple of (response_text, tool_call_results)
        """
        tool_call_results = []
        tool_context = None

        # Step 1: Detect intent and execute tool if needed
        intent, args = self._detect_intent(user_message)
        tool_name = self._map_intent_to_tool(intent)

        if tool_name:
            logger.info(f"Detected intent '{intent}' -> MCP tool '{tool_name}' with args: {args}")

            try:
                result = await self._execute_mcp_tool(user_id, tool_name, args)
                tool_call_results.append({"tool_name": tool_name, "result": result})

                # Format tool result for AI context
                tool_context = self.mcp_client.format_tool_result_for_context(tool_name, result)
                logger.info(f"Tool result: success={result.get('success')}")

            except Exception as e:
                logger.error(f"MCP tool execution error: {e}")
                tool_context = f"Tool {tool_name} failed: {str(e)}"

        # Step 2: Build context with tool results
        messages = self.build_context(history, tool_context)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Step 3: Generate AI response
        try:
            response = await self._call_gemini_with_retry(messages)
            response_text = response.choices[0].message.content or ""

            if not response_text:
                # Fallback to demo mode response if AI returns empty
                if tool_call_results:
                    return self._format_friendly_response(intent, tool_call_results[0]["result"], args), tool_call_results
                response_text = "I'm here to help you manage your tasks. What would you like to do?"

            return response_text, tool_call_results

        except AIServiceUnavailableError:
            logger.warning("Gemini API unavailable, using demo mode")
            # Pass existing tool results to avoid duplicate execution
            return await self._demo_mode_response(
                user_id,
                user_message,
                existing_tool_results=tool_call_results,
                intent=intent,
                args=args
            )

    async def _call_gemini_with_retry(self, messages: list[dict]):
        """Call Gemini API with retry logic for transient errors."""
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                return response

            except RateLimitError as e:
                last_error = e
                logger.warning(f"Gemini rate limit (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if "limit: 0" in str(e):
                    raise AIServiceUnavailableError("API quota exhausted") from e

            except APIConnectionError as e:
                last_error = e
                logger.warning(f"Gemini connection error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")

            except APITimeoutError as e:
                last_error = e
                logger.warning(f"Gemini timeout (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")

            except APIError as e:
                last_error = e
                logger.error(f"Gemini API error: {e}")
                raise AIServiceUnavailableError(f"AI service error: {str(e)}") from e

            except Exception as e:
                logger.error(f"Unexpected Gemini error: {e}")
                raise AIServiceUnavailableError(f"Unexpected AI service error: {str(e)}") from e

            # Wait before retrying (exponential backoff)
            if attempt < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        # All retries failed
        logger.error(f"Gemini API failed after {self.MAX_RETRIES} attempts")
        raise AIServiceUnavailableError(
            "The AI service is temporarily unavailable. Please try again in a moment."
        ) from last_error


# Module-level instance for convenience
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get or create the agent service instance."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service


async def generate_response(
    user_id: str,
    user_message: str,
    history: list[Message]
) -> tuple[str, list[dict]]:
    """Convenience function for generating responses."""
    service = get_agent_service()
    return await service.generate_response(user_id, user_message, history)
