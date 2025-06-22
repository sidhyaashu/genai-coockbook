import { createReadStream } from "fs";
import path from "path";
import { Agent } from "@mastra/core/agent";
import { OpenAIVoice } from "@mastra/voice-openai";
import { openai } from "@ai-sdk/openai";
 
// Initialize the voice provider with default settings
const voice = new OpenAIVoice();
 
// Create an agent with voice capabilities
export const agent = new Agent({
  name: "Agent",
  instructions: `You are a helpful assistant with both STT and TTS capabilities.`,
  model: openai("gpt-4o"),
  voice,
});
 
// The agent can now use voice for interaction
const audioStream = await agent.voice.speak("Hello, I'm your AI assistant!", {
  filetype: "m4a",
});
 
playAudio(audioStream!);
 
try {
  const transcription = await agent.voice.listen(audioStream);
  console.log(transcription);
} catch (error) {
  console.error("Error transcribing audio:", error);
}