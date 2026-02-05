# Quickstart: Todo AI Chatbot with Voice Assistant (Phase-3 Enhanced)

**Feature Branch**: `005-todo-ai-chatbot` (enhanced with `001-voice-assistant`)
**Prerequisites**: Phase-3 base chatbot completed (chat interface working)

## Overview

This guide covers the implementation of Voice Assistant capabilities for the existing AI-powered chat interface. Users can manage tasks through voice commands using the Web Speech API (SpeechRecognition and SpeechSynthesis).

## Prerequisites

Before starting implementation:

1. **Backend running**: FastAPI server on port 8080
2. **Frontend running**: Next.js on port 3000
3. **Database configured**: PostgreSQL with existing tasks table
4. **Auth working**: better-auth JWT authentication functional
5. **OpenAI API key**: Required for AI agent

## Quick Setup

### 1. Environment Variables

Add to `backend/.env`:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

Add to `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
pip install openai>=1.0.0 mcp>=1.0.0
```

**Frontend:**
```bash
cd frontend
npm install @chatscope/chat-ui-kit-react
```

### 3. Run Database Migration

```bash
cd backend
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

## Implementation Order

Follow this sequence for implementation:

### Phase 3.1: Backend Foundation (Priority: Critical)

1. **Add database models** (`backend/app/models/`)
   - Create `conversation.py` with Conversation model
   - Create `message.py` with Message model
   - Update `__init__.py` to export new models

2. **Create MCP tools** (`backend/app/mcp/`)
   - Create `tools.py` with tool implementations
   - Each tool: accept user_id, perform DB operation, return JSON

3. **Create AI agent service** (`backend/app/services/`)
   - Create `agent.py` with OpenAI integration
   - Implement tool calling loop
   - Handle conversation context

### Phase 3.2: Chat API (Priority: Critical)

4. **Create chat routes** (`backend/app/api/routes/chat.py`)
   - POST `/{user_id}/chat` - main chat endpoint
   - GET `/{user_id}/chat/history` - conversation history

5. **Add JWT validation**
   - Reuse existing auth dependency
   - Validate user_id matches JWT

### Phase 3.3: Frontend Chat UI (Priority: High)

6. **Create chat components** (`frontend/src/components/chat/`)
   - ChatContainer - main chat wrapper
   - MessageList - displays conversation
   - MessageInput - user input
   - TypingIndicator - loading state

7. **Create chat page** (`frontend/src/app/(dashboard)/chat/page.tsx`)
   - Replace or augment existing dashboard
   - Integrate ChatKit components

8. **Add API integration** (`frontend/src/lib/chat-api.ts`)
   - sendMessage function
   - getHistory function
   - Handle streaming if needed

### Phase 3.4: Testing & Validation

9. **Backend tests**
   - Unit tests for MCP tools
   - Integration tests for chat endpoint
   - Test conversation persistence

10. **Frontend tests**
    - Component tests for chat UI
    - Integration tests for API calls

## Key Files to Create

```
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py    # NEW
│   │   └── message.py         # NEW
│   ├── mcp/
│   │   ├── __init__.py        # NEW
│   │   └── tools.py           # NEW
│   ├── services/
│   │   └── agent.py           # NEW
│   └── api/routes/
│       └── chat.py            # NEW

frontend/
├── src/
│   ├── components/chat/
│   │   ├── chat-container.tsx # NEW
│   │   ├── message-list.tsx   # NEW
│   │   └── message-input.tsx  # NEW
│   ├── app/(dashboard)/
│   │   └── chat/
│   │       └── page.tsx       # NEW
│   └── lib/
│       └── chat-api.ts        # NEW
```

## Testing the Implementation

### Manual Testing Flow

1. **Start servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && uvicorn app.main:app --reload --port 8080

   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

2. **Open chat interface:**
   - Navigate to http://localhost:3000/dashboard/chat
   - Ensure you're logged in

3. **Test conversation flow:**
   ```
   You: "Add a task to buy groceries"
   AI: "I've added 'buy groceries' to your tasks!"

   You: "What are my tasks?"
   AI: "Here are your tasks: 1. Buy groceries (pending)..."

   You: "Mark groceries as done"
   AI: "Done! I've marked 'buy groceries' as complete."
   ```

4. **Test persistence:**
   - Refresh the page
   - Verify conversation history loads

### Automated Tests

```bash
# Backend tests
cd backend && pytest tests/test_chat.py -v

# Frontend tests
cd frontend && npm test -- --testPathPattern=chat
```

## Common Issues

| Issue | Solution |
|-------|----------|
| OpenAI API errors | Check OPENAI_API_KEY is set correctly |
| JWT validation fails | Ensure token is passed in Authorization header |
| Conversation not persisting | Check database migration ran successfully |
| Chat UI not loading | Verify @chatscope/chat-ui-kit-react installed |
| CORS errors | Check CORS_ORIGINS includes frontend URL |

## Next Steps

After completing implementation:

1. Run full test suite
2. Test on staging environment
3. Performance testing with concurrent users
4. User acceptance testing

Refer to `spec.md` for complete requirements and `data-model.md` for database schema details.

---

# Voice Assistant Implementation (Phase 3.7-3.14)

## Prerequisites for Voice

1. **Base chatbot working**: Chat interface functional with AI responses
2. **Modern browser**: Chrome, Edge, or Safari (Firefox doesn't support SpeechRecognition)
3. **Microphone**: Working microphone connected to device
4. **HTTPS or localhost**: Speech APIs require secure context

## Quick Setup for Voice

### 1. Run Database Migration for Voice Preferences

```bash
cd backend
alembic revision --autogenerate -m "Add voice preferences and message input method"
alembic upgrade head
```

### 2. No Additional Dependencies Needed

Voice features use browser-native APIs:
- `window.SpeechRecognition` / `window.webkitSpeechRecognition`
- `window.speechSynthesis`

No npm packages or Python libraries to install.

## Voice Implementation Order

### Phase 3.7: Backend Voice Preferences (Priority: Critical)

1. **Add voice preferences model** (`backend/app/models/voice_preferences.py`)
   ```python
   class UserVoicePreferences(SQLModel, table=True):
       user_id: str = Field(primary_key=True)
       voice_output_enabled: bool = Field(default=True)
       continuous_mode_enabled: bool = Field(default=False)
       preferred_voice: str | None = Field(default=None)
       updated_at: datetime
   ```

2. **Add input_method to Message model**
   ```python
   input_method: InputMethod = Field(default=InputMethod.TEXT)
   ```

3. **Create voice API routes** (`backend/app/api/routes/voice.py`)
   - GET `/{user_id}/voice/preferences`
   - PUT `/{user_id}/voice/preferences`

### Phase 3.8-3.9: Speech Hooks (Priority: Critical)

4. **Create speech recognition hook** (`frontend/src/hooks/use-speech-recognition.ts`)
   ```typescript
   export function useSpeechRecognition() {
     const [isListening, setIsListening] = useState(false);
     const [transcript, setTranscript] = useState('');
     const [error, setError] = useState<string | null>(null);

     // Initialize SpeechRecognition
     // Handle interim/final results
     // 5-second silence timeout

     return { isListening, transcript, error, start, stop, cancel };
   }
   ```

5. **Create speech synthesis hook** (`frontend/src/hooks/use-speech-synthesis.ts`)
   ```typescript
   export function useSpeechSynthesis() {
     const [isSpeaking, setIsSpeaking] = useState(false);
     const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

     // Get available voices
     // speak(text, voiceURI)
     // stop()

     return { isSpeaking, voices, speak, stop };
   }
   ```

### Phase 3.10: Voice UI Components (Priority: High)

6. **Create VoiceButton component** (`frontend/src/components/chat/voice/voice-button.tsx`)
   - Microphone icon with states: idle, listening, processing, error
   - Pulsing animation when listening
   - Accessible with keyboard (Ctrl+Shift+M)

7. **Create VoiceIndicator component** (`frontend/src/components/chat/voice/voice-indicator.tsx`)
   - Shows real-time transcription
   - Processing spinner
   - Error messages

8. **Create VoiceSettings component** (`frontend/src/components/chat/voice/voice-settings.tsx`)
   - Voice output toggle
   - Voice selection dropdown
   - Preview button

9. **Create ContinuousModeToggle** (`frontend/src/components/chat/voice/continuous-mode.tsx`)
   - Toggle button for continuous listening

### Phase 3.11-3.12: Integration (Priority: High)

10. **Modify MessageInput**
    - Add VoiceButton next to send button
    - Handle voice input submission

11. **Modify ChatContainer**
    - Add VoiceIndicator
    - Add VoiceSettings in header
    - Implement auto-speak for voice commands

12. **Implement Continuous Mode**
    - Auto-restart listening after AI response
    - 5-second silence timeout
    - Barge-in support

### Phase 3.13-3.14: Error Handling & Testing

13. **Add browser compatibility detection**
    ```typescript
    const isVoiceSupported =
      'SpeechRecognition' in window ||
      'webkitSpeechRecognition' in window;
    ```

14. **Handle all error scenarios**
    - Mic permission denied
    - No speech detected
    - Network errors
    - TTS unavailable

## Key Files to Create (Voice)

```
backend/
├── app/
│   ├── models/
│   │   └── voice_preferences.py   # NEW
│   ├── api/routes/
│   │   └── voice.py               # NEW
│   └── schemas/
│       └── voice.py               # NEW

frontend/
├── src/
│   ├── components/chat/voice/
│   │   ├── voice-button.tsx       # NEW
│   │   ├── voice-indicator.tsx    # NEW
│   │   ├── voice-settings.tsx     # NEW
│   │   └── continuous-mode.tsx    # NEW
│   ├── hooks/
│   │   ├── use-speech-recognition.ts  # NEW
│   │   ├── use-speech-synthesis.ts    # NEW
│   │   └── use-voice-preferences.ts   # NEW
│   ├── lib/
│   │   └── voice-api.ts           # NEW
│   └── types/
│       └── voice.ts               # NEW
```

## Testing Voice Features

### Manual Testing Flow

1. **Test voice input:**
   - Click microphone button
   - Say "Add a task to call mom"
   - Verify transcription appears
   - Verify task is created

2. **Test voice output:**
   - Enable voice output in settings
   - Use voice command
   - Verify AI response is spoken

3. **Test continuous mode:**
   - Enable continuous mode
   - Speak multiple commands
   - Verify each is processed without re-clicking mic

4. **Test error handling:**
   - Deny microphone permission → see helpful message
   - Speak in noisy environment → see retry option
   - Test in Firefox → voice button hidden

### Browser Compatibility Test

| Browser | Expected Behavior |
|---------|-------------------|
| Chrome | ✅ Full voice support |
| Edge | ✅ Full voice support |
| Safari | ✅ Full voice support |
| Firefox | ⚠️ Voice button hidden, text-only |

## Common Voice Issues

| Issue | Solution |
|-------|----------|
| "Voice not supported" | Use Chrome, Edge, or Safari |
| Mic permission denied | Check browser settings, site must be HTTPS |
| No speech detected | Speak louder, check mic is working |
| TTS not playing | Check device volume, try different voice |
| Continuous mode stops | Normal after 5s silence; re-enable to continue |
| Voice selection empty | Wait for voices to load (async) |

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Transcription latency | < 3 seconds | Time from speech end to text displayed |
| TTS start latency | < 2 seconds | Time from response to audio start |
| Recognition accuracy | > 90% | Manual testing in quiet environment |
| Continuous turns | 5+ | Count successful turns without manual restart |
