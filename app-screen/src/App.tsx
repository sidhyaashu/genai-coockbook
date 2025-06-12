// src/App.tsx
import React from "react";
import { WebSocketProvider } from "./components/WebSocketProvider";
import ScreenShare from "./components/ScreenShare";

const App: React.FC = () => {
  return (

    <WebSocketProvider url="ws://localhost:9084">
    
      <div className="container mx-auto p-4">
        <ScreenShare />
      </div>
    </WebSocketProvider>
  );
};

export default App;