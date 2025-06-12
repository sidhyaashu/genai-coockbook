Client-to-Agent Flow:
Connection Establishment - Client opens SSE connection to /events/{user_id}, triggering session creation and storing request queue in active_sessions
Message Transmission - Client sends POST to /send/{user_id} with JSON payload containing mime_type and data
Queue Processing - Server retrieves session's live_request_queue and forwards message to agent via send_content() or send_realtime()

Agent-to-Client Flow:
Event Generation - Agent processes requests and generates events through live_events async generator
Stream Processing - agent_to_client_sse() filters events and formats them as SSE-compatible JSON
Real-time Delivery - Events stream to client via persistent HTTP connection with proper SSE headers


Session Management:¶
Per-User Isolation - Each user gets unique session stored in active_sessions dict
Lifecycle Management - Sessions auto-cleanup on disconnect with proper resource disposal
Concurrent Support - Multiple users can have simultaneous active sessions

Error Handling:¶
Session Validation - POST requests validate session existence before processing
Stream Resilience - SSE streams handle exceptions and perform cleanup automatically
Connection Recovery - Clients can reconnect by re-establishing SSE connection


https://google.github.io/adk-docs/streaming/custom-streaming/
https://google.github.io/adk-docs/streaming/custom-streaming-ws/