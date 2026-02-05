# Tasks: Todo AI Chatbot - Voice Assistant

**Input**: Design documents from `/specs/005-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/voice-api.yaml
**Branch**: `001-voice-assistant`

**Note**: Text chat phases (3.1-3.6) are already complete. These tasks cover Voice Assistant implementation (phases 3.7-3.14).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US7, US8, US9, US10 for voice features)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/hf-deploy/app/` for source, `backend/hf-deploy/tests/` for tests
- **Frontend**: `frontend/src/` for source

---

## Phase 1: Setup (Voice Infrastructure)

**Purpose**: Database infrastructure and backend API for voice preferences

- [x] T001 Create `UserVoicePreferences` SQLModel in `backend/hf-deploy/app/models/voice_preferences.py`
- [x] T002 [P] Add `InputMethod` enum to `backend/hf-deploy/app/models/message.py` with values: text, voice
- [x] T003 [P] Add `input_method` field to existing `Message` model with default 'text'
- [x] T004 Create Alembic migration for voice_preferences table and message.input_method column in `backend/hf-deploy/alembic/versions/003_add_voice_support.py`
- [ ] T005 Run migration and verify schema with `alembic upgrade head`

---

## Phase 2: Foundational (Voice Backend API)

**Purpose**: REST endpoints for voice preferences - MUST complete before frontend voice work

**Checkpoint**: Backend API ready - frontend voice implementation can begin

- [x] T006 Create voice preference schemas in `backend/hf-deploy/app/schemas/voice.py` (VoicePreferences, VoicePreferencesUpdate)
- [x] T007 Create voice preferences routes in `backend/hf-deploy/app/api/routes/voice.py` with GET and PUT endpoints
- [x] T008 Register voice routes in `backend/hf-deploy/app/main.py`
- [x] T009 [P] Update chat schemas in `backend/hf-deploy/app/schemas/chat.py` to accept `input_method` parameter
- [x] T010 [P] Update `add_message` function in `backend/hf-deploy/app/mcp/tools.py` to store `input_method`
- [x] T011 Write unit tests for voice preferences API in `backend/hf-deploy/tests/test_voice.py`

---

## Phase 3: User Story 7 - Voice Input for Commands (Priority: P1)

**Goal**: Enable users to speak commands to the chatbot using their microphone

**Independent Test**: Press microphone button, speak "Add a task to call mom", verify text appears and task is created

### Implementation for User Story 7

- [x] T012 [P] [US7] Create TypeScript voice types in `frontend/src/types/voice.ts` (VoiceState enum, SpeechRecognitionResult interface)
- [x] T013 [US7] Create `useSpeechRecognition` hook in `frontend/src/hooks/use-speech-recognition.ts` with start/stop/cancel functions
- [x] T014 [US7] Add browser compatibility detection to `useSpeechRecognition` hook (check for SpeechRecognition API)
- [x] T015 [US7] Implement interim results display in `useSpeechRecognition` hook
- [x] T016 [US7] Implement end-of-speech auto-detection with 5-second silence timeout
- [x] T017 [US7] Handle speech recognition errors (permission denied, no speech, network) in hook
- [x] T018 [P] [US7] Create `VoiceButton` component in `frontend/src/components/chat/voice/voice-button.tsx` with mic icon and visual states
- [x] T019 [P] [US7] Create `VoiceIndicator` component in `frontend/src/components/chat/voice/voice-indicator.tsx` for real-time transcription display
- [x] T020 [US7] Integrate `VoiceButton` into `MessageInput` component in `frontend/src/components/chat/message-input.tsx`
- [x] T021 [US7] Update `useChat` hook in `frontend/src/hooks/use-chat.ts` to pass `input_method` to API
- [x] T022 [US7] Add voice input state management to `ChatContainer` in `frontend/src/components/chat/chat-container.tsx`

**Checkpoint**: Users can speak to input messages - voice-to-text working

---

## Phase 4: User Story 8 - Voice Output for Responses (Priority: P2)

**Goal**: Enable AI assistant to speak responses aloud through device speakers

**Independent Test**: Send a command and verify the AI response is spoken aloud

### Implementation for User Story 8

- [ ] T023 [US8] Create `useSpeechSynthesis` hook in `frontend/src/hooks/use-speech-synthesis.ts` with speak/stop functions
- [ ] T024 [US8] Implement voice selection in `useSpeechSynthesis` hook using `speechSynthesis.getVoices()`
- [ ] T025 [US8] Implement queue management for TTS in `useSpeechSynthesis` hook
- [ ] T026 [US8] Implement barge-in (stop on new input) in `useSpeechSynthesis` hook
- [ ] T027 [P] [US8] Create `VoiceSettings` component in `frontend/src/components/chat/voice/voice-settings.tsx` with voice toggle and selection
- [ ] T028 [P] [US8] Create `useVoicePreferences` hook in `frontend/src/hooks/use-voice-preferences.ts` to sync with backend API
- [ ] T029 [P] [US8] Create `voice-api.ts` client in `frontend/src/lib/voice-api.ts` for preferences API calls
- [ ] T030 [US8] Integrate auto-speak for AI responses in `ChatContainer` (speak if voice_output_enabled and last input was voice)
- [ ] T031 [US8] Add `VoiceSettings` to chat header in `frontend/src/components/chat/chat-container.tsx`

**Checkpoint**: AI responses are spoken aloud when voice output is enabled

---

## Phase 5: User Story 9 - Continuous Voice Conversation (Priority: P2)

**Goal**: Enable hands-free continuous conversation without repeatedly tapping microphone

**Independent Test**: Enable continuous mode, speak multiple commands in sequence, verify each is processed automatically

### Implementation for User Story 9

- [ ] T032 [P] [US9] Create `ContinuousModeToggle` component in `frontend/src/components/chat/voice/continuous-mode.tsx`
- [ ] T033 [US9] Implement continuous listening flow in `ChatContainer`: listen → speak → send → respond → speak → auto-listen
- [ ] T034 [US9] Handle exit conditions: "Stop listening" command, 5-second silence, manual toggle off
- [ ] T035 [US9] Implement barge-in during AI response: detect voice activity during TTS, stop TTS, process new command
- [ ] T036 [US9] Add continuous mode visual indicator to `ChatContainer`
- [ ] T037 [US9] Persist continuous mode preference via `useVoicePreferences` hook

**Checkpoint**: Continuous conversation mode allows 5+ voice turns without manual reactivation

---

## Phase 6: User Story 10 - Voice Feedback and Status (Priority: P3)

**Goal**: Provide clear audio and visual feedback about voice system status

**Independent Test**: Activate voice input and observe status indicators through listening, processing, and response phases

### Implementation for User Story 10

- [ ] T038 [US10] Add pulsing animation to `VoiceButton` during listening state
- [ ] T039 [US10] Add processing spinner to `VoiceIndicator` component
- [ ] T040 [US10] Add error messages with retry option to `VoiceIndicator` component
- [ ] T041 [P] [US10] Implement microphone permission denied handling with settings link
- [ ] T042 [P] [US10] Implement browser compatibility check: hide voice controls on unsupported browsers (Firefox)
- [ ] T043 [US10] Add aria-labels and keyboard navigation support to all voice components
- [ ] T044 [US10] Add `Ctrl+Shift+M` keyboard shortcut for voice toggle

**Checkpoint**: Users have clear feedback about voice system status at all times

---

## Phase 7: Error Handling & Cross-Browser Testing

**Purpose**: Graceful degradation and comprehensive error handling

- [ ] T045 Handle "no speech detected" error: prompt user to try again in `VoiceIndicator`
- [ ] T046 Handle network error: show error, suggest text input in `VoiceIndicator`
- [ ] T047 Handle low confidence: show partial result, ask to confirm or retry
- [ ] T048 Handle TTS errors: fall back to text-only display with notification
- [ ] T049 [P] Test voice input on Chrome desktop
- [ ] T050 [P] Test voice input on Edge desktop
- [ ] T051 [P] Test voice input on Safari desktop
- [ ] T052 [P] Test voice output on Chrome, Edge, Safari
- [ ] T053 Verify graceful fallback on Firefox (no SpeechRecognition)

---

## Phase 8: Polish & Validation

**Purpose**: Final testing, accessibility, and performance validation

- [ ] T054 [P] Screen reader compatibility testing for voice components
- [ ] T055 [P] Keyboard navigation testing for all voice controls
- [ ] T056 Performance testing: verify transcription latency < 3 seconds
- [ ] T057 Performance testing: verify TTS start latency < 2 seconds
- [ ] T058 Manual test: complete task management action via voice on first attempt
- [ ] T059 Manual test: continuous mode for 5+ consecutive interactions
- [ ] T060 Run quickstart.md validation for voice features
- [ ] T061 Update chat page with voice feature documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Backend API)**: Depends on Phase 1 - BLOCKS frontend voice work
- **Phase 3 (US7 Voice Input)**: Depends on Phase 2 - Core voice functionality
- **Phase 4 (US8 Voice Output)**: Depends on Phase 2 - Can run parallel to Phase 3
- **Phase 5 (US9 Continuous Mode)**: Depends on Phases 3 & 4
- **Phase 6 (US10 Feedback)**: Depends on Phases 3 & 4
- **Phase 7 (Error Handling)**: Depends on Phase 6
- **Phase 8 (Polish)**: Depends on Phase 7

### User Story Dependencies

- **US7 (Voice Input)**: Can start after Phase 2 - Core voice feature
- **US8 (Voice Output)**: Can start after Phase 2 - Can run in parallel with US7
- **US9 (Continuous Mode)**: Depends on US7 + US8 completion
- **US10 (Voice Feedback)**: Depends on US7 + US8 components existing

### Within Each User Story

- TypeScript types before hooks
- Hooks before components
- Components before integration
- Integration before testing

### Parallel Opportunities

- T002, T003 can run in parallel (different model files)
- T006, T009, T010 can run in parallel (different schema files)
- T012 can run parallel with T018, T019 (types vs components)
- T023-T026 can start while US7 components are being built
- T027, T028, T029 can run in parallel (different files)
- T032 can run in parallel with T027-T029
- T049-T053 browser tests can all run in parallel

---

## Parallel Example: Phase 3 (Voice Input)

```bash
# Launch types and components together:
Task: "Create TypeScript voice types in frontend/src/types/voice.ts"
Task: "Create VoiceButton component in frontend/src/components/chat/voice/voice-button.tsx"
Task: "Create VoiceIndicator component in frontend/src/components/chat/voice/voice-indicator.tsx"

# Then sequentially: hooks → integration
```

---

## Implementation Strategy

### MVP First (Voice Input Only - US7)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Backend API (T006-T011)
3. Complete Phase 3: User Story 7 (T012-T022)
4. **STOP and VALIDATE**: Test voice input works independently
5. Deploy/demo voice-to-text functionality

### Incremental Delivery

1. Setup + Backend API → Foundation ready
2. Add US7 (Voice Input) → Test independently → Demo voice commands
3. Add US8 (Voice Output) → Test independently → Demo full voice loop
4. Add US9 (Continuous) → Test independently → Demo hands-free mode
5. Add US10 (Feedback) → Polish UX → Full voice assistant

### Parallel Team Strategy

With 2 developers:
1. Both complete Phase 1 + 2 together
2. Developer A: US7 (Voice Input)
3. Developer B: US8 (Voice Output)
4. Join for US9, US10, and testing

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 61 |
| **Phase 1 (Setup)** | 5 |
| **Phase 2 (Backend API)** | 6 |
| **US7 (Voice Input)** | 11 |
| **US8 (Voice Output)** | 9 |
| **US9 (Continuous Mode)** | 6 |
| **US10 (Voice Feedback)** | 7 |
| **Error Handling** | 9 |
| **Polish/Validation** | 8 |
| **Parallel Opportunities** | 22 tasks marked [P] |

**MVP Scope**: Phases 1-3 (US7 Voice Input) = 22 tasks
**Full Feature**: All phases = 61 tasks

---

## Notes

- Voice processing happens client-side (browser APIs) - no backend voice processing
- Backend only stores voice preferences
- Firefox users see text-only chat (no voice features)
- All voice features degrade gracefully to text mode
- Test on Chrome/Edge first (best Web Speech API support)
