# Research: Todo AI Chatbot with Voice Assistant (Phase-3 Enhanced)

**Feature Branch**: `005-todo-ai-chatbot` (enhanced with `001-voice-assistant`)
**Date**: 2026-01-25 (Voice Assistant addition)
**Status**: Complete

## Research Areas

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with GPT-4o-mini model

**Rationale**:
- OpenAI Agents SDK provides built-in tool calling (function calling) support
- GPT-4o-mini offers good balance of cost and capability for task intent parsing
- Native async support works well with FastAPI's async architecture
- Well-documented Python SDK with type hints

**Alternatives Considered**:
- LangChain: More complex, adds unnecessary abstraction layer for this use case
- Direct OpenAI API: Lower-level, would need to implement agent loop manually
- Claude API: Good alternative but user spec explicitly mentions OpenAI

**Implementation Notes**:
- Install: `openai>=1.0.0`
- Use `client.chat.completions.create()` with tools parameter
- Implement tool execution loop for multi-step conversations

---

### 2. MCP (Model Context Protocol) Server Implementation

**Decision**: Use official MCP Python SDK (`mcp>=1.0.0`)

**Rationale**:
- Official SDK ensures protocol compliance
- Provides typed interfaces for tool definitions
- Integrates naturally with OpenAI function calling format
- Stateless tool design aligns with server statelessness requirement

**Alternatives Considered**:
- Custom tool implementation: More work, less standardized
- LangChain tools: Adds dependency overhead

**Implementation Notes**:
- Each MCP tool maps to an OpenAI function definition
- Tools receive `user_id` as explicit parameter (no session state)
- Tools return structured JSON for consistent AI parsing
- Tool schema:
  ```python
  {
    "name": "add_task",
    "description": "Add a new task for the user",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string", "optional": True}
      },
      "required": ["user_id", "title"]
    }
  }
  ```

---

### 3. ChatKit UI Component Selection

**Decision**: Use `@chatscope/chat-ui-kit-react` for React chat components

**Rationale**:
- Purpose-built for chat interfaces
- Provides Message, MessageList, MessageInput, TypingIndicator components
- Works with React 19 and Next.js
- Customizable styling to match existing Tailwind/Radix design
- Supports conversation history display

**Alternatives Considered**:
- Build custom components: Time-consuming, reinventing the wheel
- Stream Chat SDK: Overkill, includes backend we don't need
- React Chat Widget: Less customizable

**Implementation Notes**:
- Install: `@chatscope/chat-ui-kit-react`
- Style overrides via CSS modules to match existing design system
- Integrate with TanStack Query for message fetching/sending

---

### 4. Conversation Persistence Strategy

**Decision**: Store conversations and messages in PostgreSQL via SQLModel

**Rationale**:
- Consistent with existing Phase-2 database setup
- SQLModel already in use for Task model
- Relational model fits conversation→messages relationship
- Easy to query conversation history by user_id

**Alternatives Considered**:
- Redis for ephemeral storage: Doesn't persist across restarts
- MongoDB: Adds new database technology
- Client-side storage only: Doesn't meet persistence requirements

**Implementation Notes**:
- Add `Conversation` and `Message` models to backend
- Create Alembic migration for new tables
- Index on `user_id` and `conversation_id` for efficient queries

---

### 5. JWT Authentication for Chat Endpoint

**Decision**: Reuse existing JWT validation from Phase-2 (`better-auth` tokens)

**Rationale**:
- Existing `better-auth` system generates JWTs on frontend
- Backend already has JWT validation for tasks API
- Consistent authentication across all endpoints
- No new authentication system needed

**Alternatives Considered**:
- Separate chat authentication: Adds complexity, inconsistent UX
- API keys: Less secure, harder to manage per-user

**Implementation Notes**:
- Extract `user_id` from JWT in chat endpoint
- Reuse existing `get_current_user` dependency
- Pass `user_id` to all MCP tool calls

---

### 6. Stateless Server Architecture

**Decision**: Full statelessness via database-backed conversation state

**Rationale**:
- Requirement from spec: server must not store in-memory state
- Each request fetches full conversation history from DB
- Enables horizontal scaling without session affinity
- OpenAI handles conversation context via messages array

**Alternatives Considered**:
- In-memory cache with Redis: Adds infrastructure complexity
- Session-based state: Breaks statelessness requirement

**Implementation Notes**:
- Fetch all messages for user's conversation on each request
- Pass conversation history to OpenAI as messages array
- Store new messages before returning response
- Maximum context window management (truncate old messages if needed)

---

### 7. Error Handling and Graceful Degradation

**Decision**: Implement tiered error handling with user-friendly messages

**Rationale**:
- AI service failures should not crash the application
- Users should receive helpful error messages
- Retry logic for transient failures

**Error Categories**:
| Error Type | User Message | Action |
|------------|--------------|--------|
| OpenAI API timeout | "I'm thinking... please wait or try again" | Auto-retry once |
| OpenAI API error | "I'm having trouble right now. Please try again." | Log, return error |
| Tool execution failure | "I couldn't complete that action. [specific reason]" | Return partial result |
| Database error | "Something went wrong. Please try again." | Log, return 500 |
| Invalid input | "I didn't understand that. Could you rephrase?" | Return 400 |

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| AI Model | OpenAI GPT-4o-mini | Latest |
| AI SDK | openai (Python) | >=1.0.0 |
| MCP SDK | mcp (Python) | >=1.0.0 |
| Backend | FastAPI | >=0.115.0 |
| Database | PostgreSQL + SQLModel | Existing |
| Frontend | Next.js 16 + React 19 | Existing |
| Chat UI | @chatscope/chat-ui-kit-react | Latest |
| Auth | better-auth (JWT) | Existing |

---

## Dependencies to Add

### Backend (requirements.txt additions)
```
openai>=1.0.0
mcp>=1.0.0
```

### Frontend (package.json additions)
```json
{
  "@chatscope/chat-ui-kit-react": "^2.0.0"
}
```

---

## Constitution Compliance Notes

| Principle | Compliance |
|-----------|------------|
| Data Integrity First | Messages stored atomically before response |
| Offline-First | Partial - chat requires network; queue failed sends |
| User Experience | <5s response target; loading indicators |
| TDD | Tests required for tools, endpoint, UI |
| Security & Privacy | JWT auth; user_id isolation; no third-party data |
| Performance | Async operations; message pagination if needed |

---

## Voice Assistant Research (2026-01-25)

### 8. Speech Recognition API Selection

**Decision**: Use Web Speech API (SpeechRecognition interface)

**Rationale**:
- Browser-native, no external API costs
- Good accuracy for clear English speech
- Real-time interim results support
- No server-side processing needed
- Works offline for basic recognition (browser-dependent)
- Already available in Chrome, Edge, Safari

**Alternatives Considered**:
- Google Cloud Speech-to-Text: Better accuracy but adds cost and latency
- Whisper API (OpenAI): Good accuracy but adds cost and server roundtrip
- AssemblyAI: Enterprise features not needed
- Deepgram: Overkill for simple voice commands

**Implementation Notes**:
- Check for `window.SpeechRecognition` or `window.webkitSpeechRecognition`
- Set `lang = 'en-US'` for English
- Set `interimResults = true` for real-time feedback
- Set `continuous = true` for continuous mode
- Handle `onresult`, `onerror`, `onend` events
- Implement 5-second silence timeout via custom timer

**Browser Support**:
| Browser | SpeechRecognition Support |
|---------|--------------------------|
| Chrome | ✅ Full (webkitSpeechRecognition) |
| Edge | ✅ Full (webkitSpeechRecognition) |
| Safari | ✅ Full (webkitSpeechRecognition) |
| Firefox | ❌ Not supported |
| Mobile Chrome | ✅ Full |
| Mobile Safari | ✅ Full |

**Fallback Strategy**: Hide voice button on unsupported browsers, show "Voice not supported" tooltip if user tries to access via keyboard shortcut.

---

### 9. Text-to-Speech API Selection

**Decision**: Use Web Speech API (SpeechSynthesis interface)

**Rationale**:
- Browser-native, no external API costs
- Access to system-installed voices
- User can select preferred voice
- Works offline
- Wider browser support than SpeechRecognition

**Alternatives Considered**:
- Google Cloud Text-to-Speech: Better voice quality but adds cost and latency
- Amazon Polly: Similar issues
- ElevenLabs: Premium quality but expensive
- Local TTS models: Too complex to integrate

**Implementation Notes**:
- Use `window.speechSynthesis.getVoices()` to list available voices
- Filter for English voices: `voice.lang.startsWith('en')`
- Store selected voice identifier in UserVoicePreferences
- Use `SpeechSynthesisUtterance` for each response
- Handle `onend`, `onerror` events
- Implement `cancel()` for barge-in

**Voice Selection UI**:
```typescript
// Get available voices
const voices = speechSynthesis.getVoices().filter(v => v.lang.startsWith('en'));

// Let user select
<select onChange={(e) => setPreferredVoice(e.target.value)}>
  {voices.map(v => (
    <option key={v.voiceURI} value={v.voiceURI}>
      {v.name} ({v.lang})
    </option>
  ))}
</select>
```

---

### 10. Continuous Conversation Mode Design

**Decision**: Button-activated continuous mode with 5-second silence timeout

**Rationale**:
- No wake word required (privacy-friendly, simpler implementation)
- Button provides clear user control
- 5-second timeout balances responsiveness with user thinking time
- Auto-restart listening after AI response completes

**Alternatives Considered**:
- Wake word detection: Complex, requires always-on microphone, privacy concerns
- Hold-to-talk: Fatiguing for multi-turn conversations
- Fully automatic: No clear user control, could be intrusive

**Implementation Notes**:
```typescript
// Continuous mode state machine
enum ContinuousState {
  INACTIVE,        // Toggle off
  WAITING_INPUT,   // Listening for user speech
  PROCESSING,      // Sending to AI
  SPEAKING,        // TTS playing
}

// Flow: INACTIVE → (toggle) → WAITING_INPUT → (speech) → PROCESSING →
//       (response) → SPEAKING → (TTS done) → WAITING_INPUT → ...

// Exit conditions:
// 1. User toggles button off → INACTIVE
// 2. "Stop listening" detected → INACTIVE
// 3. 5 seconds silence → INACTIVE
// 4. Error → INACTIVE (with notification)
```

**Barge-In Implementation**:
```typescript
// When user starts speaking during TTS
function handleBargeIn() {
  speechSynthesis.cancel(); // Stop TTS
  startRecognition();       // Process new input
}
```

---

### 11. Voice Preferences Storage

**Decision**: Server-side PostgreSQL storage for voice preferences

**Rationale**:
- Preferences persist across devices
- Consistent with existing user data storage
- Simple REST API for get/update
- Minimal data: 4 fields per user

**Alternatives Considered**:
- LocalStorage only: Doesn't sync across devices
- IndexedDB: Overkill for simple preferences
- Cookies: Size limitations, security concerns

**Data Model**:
```python
class UserVoicePreferences(SQLModel, table=True):
    __tablename__ = "user_voice_preferences"

    user_id: str = Field(primary_key=True)
    voice_output_enabled: bool = Field(default=True)
    continuous_mode_enabled: bool = Field(default=False)
    preferred_voice: str | None = Field(default=None)  # voiceURI
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**API Endpoints**:
- `GET /api/{user_id}/voice/preferences` → Returns current preferences
- `PUT /api/{user_id}/voice/preferences` → Updates preferences

---

### 12. Error Handling for Voice Features

**Decision**: Graceful degradation with user-friendly messages

**Error Categories**:
| Error Type | Detection | User Message | Fallback |
|------------|-----------|--------------|----------|
| Browser not supported | `!window.SpeechRecognition` | "Voice input not supported in this browser" | Hide voice button |
| Mic permission denied | `error.error === 'not-allowed'` | "Please allow microphone access to use voice" | Show settings link |
| No speech detected | `error.error === 'no-speech'` | "I didn't hear anything. Try again?" | Prompt retry |
| Network error | `error.error === 'network'` | "Network issue. Please check connection" | Suggest text input |
| Aborted | `error.error === 'aborted'` | (silent) | Normal cancellation |
| Audio busy | `error.error === 'audio-capture'` | "Microphone is busy. Close other apps?" | Suggest text |
| TTS unavailable | `!window.speechSynthesis` | "Voice output not available" | Text-only display |
| TTS error | `utterance.onerror` | "Couldn't play audio" | Text-only display |

---

### 13. Accessibility Considerations

**Decision**: Full keyboard and screen reader support for voice features

**Implementation**:
- Voice button has `aria-label` describing current state
- State changes announced via `aria-live` region
- Keyboard shortcut: `Ctrl+Shift+M` to toggle microphone
- Visual indicators complement audio feedback (not replace)
- Transcription visible for users who can't hear TTS
- All controls reachable via Tab navigation

---

## Updated Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| AI Model | OpenAI GPT-4o-mini | Latest |
| AI SDK | openai (Python) | >=1.0.0 |
| MCP SDK | mcp (Python) | >=1.0.0 |
| Backend | FastAPI | >=0.115.0 |
| Database | PostgreSQL + SQLModel | Existing |
| Frontend | Next.js 16 + React 19 | Existing |
| Chat UI | @chatscope/chat-ui-kit-react | Latest |
| Auth | better-auth (JWT) | Existing |
| **Speech Input** | Web Speech API (SpeechRecognition) | Browser-native |
| **Speech Output** | Web Speech API (SpeechSynthesis) | Browser-native |

---

## No Additional Dependencies for Voice

Voice features use browser-native APIs:
- `window.SpeechRecognition` / `window.webkitSpeechRecognition`
- `window.speechSynthesis`
- `SpeechSynthesisUtterance`

No npm packages or Python libraries needed for voice functionality.
