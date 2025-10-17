# Feature: EP-300 AI 語音互動
# 目的: 讓病患可以透過語音方便地詢問健康問題，並獲得基於知識庫的 AI 回覆。
# 對應 PRD: [Link to ../product_requirements_document.md#史詩-ep-300-ai-語音互動]

@patient @ai @voice @sprint-6
Feature: AI Voice Interaction

  Background:
    Given I am a registered and logged-in patient with ID "patient-001"
    And I have accessed the "Ask Ally" LIFF page
    And the AI Worker services (STT, LLM, TTS, RAG) are running

  @happy-path
  Scenario: US-301 Patient asks a question using voice and gets a successful response
    Given the RAG knowledge base contains information about "how to use an inhaler"
    When I record and upload a 15-second audio file asking in Mandarin "我應該如何使用吸入器？"
    Then the system should create a voice processing task with a unique task ID
    And I should see a message "Ally正在思考..."
    And within 15 seconds, I should receive a response via WebSocket containing:
      | type             | content                                     |
      | transcript_text  | "我應該如何使用吸入器？"                         |
      | response_text    | "好的，關於吸入器的正確用法是... (AI generated answer)" |
      | response_audio_url | "https://minio.respira.ally/audio/response-xyz.mp3" |
      | reference_links  | "[參考資料: 正確使用吸入器的步驟]"                   |
    And the response audio should be playable in the LIFF

  @edge-case
  Scenario: US-301 Patient asks a question in Taiwanese
    Given the RAG knowledge base contains information about "dietary advice"
    When I record and upload an audio file asking in Taiwanese "呷啥米對氣喘卡好？"
    Then the STT service should correctly transcribe the text to "吃什麼對氣喘比較好？"
    And I should receive a relevant text and audio response about dietary advice for asthma

  @sad-path
  Scenario: US-303 AI response confidence is low
    Given the RAG knowledge base does not contain information about "treating skin rashes"
    When I record and upload an audio file asking "我要怎麼治療皮膚過敏？"
    Then I should receive a response that includes the text "這個問題比較專業，建議您直接諮詢您的呼吸治療師喔。"
    And the response should not include any reference links

  @sad-path
  Scenario: US-301 Patient uploads a silent or unintelligible audio file
    When I record and upload a 10-second audio file containing only background noise
    Then the system should create a voice processing task
    And I should see a message "Ally正在處理..."
    And within 10 seconds, I should receive a response with the text "抱歉，我聽不清楚您說什麼，可以再試一次嗎？"
    And the response should not contain an audio URL or reference links

  @sad-path
  Scenario: US-301 A system error occurs during voice processing
    Given the LLM service is down
    When I record and upload a valid audio question
    Then I should eventually receive a response with the text "系統有點忙碌，請稍後再試一次。"

@system @ai-worker @sprint-6
Feature: AI Worker Voice Processing Pipeline

  Background:
    Given RabbitMQ is running and has a "voice_tasks" queue
    And a voice task is published to the queue with task_id "task-123" and audio_url "s3://audio/input.wav"

  @happy-path
  Scenario: US-302 AI worker processes a voice task successfully
    When the AI Worker consumes the task "task-123"
    Then it should perform the following steps in sequence:
      1. Download the audio from the audio_url
      2. Transcribe the audio to text using the STT service
      3. Retrieve relevant context from the RAG service using the transcribed text
      4. Generate a text response using the LLM service with the text and context
      5. Synthesize the text response to an audio file using the TTS service
      6. Upload the response audio to object storage
      7. Send the final result (transcript, response text, response audio URL) back via a callback or WebSocket push

  @sad-path
  Scenario: US-302 AI worker fails during a step and retries
    Given the TTS service is temporarily unavailable
    When the AI Worker processes task "task-123" and reaches the TTS step
    Then it should fail the task
    And the task should be re-queued according to the exponential backoff retry policy
    And after 3 failed attempts, the task should be moved to a dead-letter queue
    And a notification should be sent to the system administrator

  @sad-path
  Scenario: US-302 AI worker fails during the STT step
    Given the STT service is returning errors
    When the AI Worker consumes task "task-stt-fail"
    Then it should fail the task at the STT step
    And the task should be re-queued according to the exponential backoff retry policy
    And after 3 failed attempts, the task should be moved to a dead-letter queue
    And a notification should be sent to the system administrator
