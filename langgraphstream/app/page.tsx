"use client";

import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";

export default function App() {
  const thread = useStream<{ messages: Message[] }>({
    apiUrl: "http://localhost:2024",
    assistantId: "agent",
    // messagesKey: "messages",
  });

  return (
    <div>
      <div>
        {
          thread.messages.map((message)=>(
            <div key={message.id}>
              {message.type}
              {": "}
              {
                typeof message.content === "string"?
                message.content:
                message.content.map((part)=>{
                  if(part.type === "text") return part.text;
                  return null
                })
              }

            </div>
          ))
        }
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();

          const form = e.target as HTMLFormElement;
          const message = new FormData(form).get("message") as string;

          form.reset();
          thread.submit({ messages: [ message ] });
        }}
      >
        <input type="text" name="message" placeholder="Enter..." />
      </form>
    </div>
  );
}