import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "./api";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const mutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: data.data.response },
      ]);
    },
    onError: (error) => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "خطایی رخ داد. لطفا دوباره تلاش کنید.",
          isError: true,
        },
      ]);
    },
  });

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || mutation.isPending) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");

    mutation.mutate(userMessage);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100 font-sans">
      <header className="py-4 px-6 bg-slate-800/50 border-b border-slate-700/50 backdrop-blur text-center">
        <h1 className="text-xl font-bold tracking-wide text-cyan-400">
          Gemini AI Assistant
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Powered by Flask & React (v4)
        </p>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-w-4xl w-full mx-auto">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2">
            <span className="text-4xl">🤖</span>
            <p>Start a conversation with the AI assistant...</p>{" "}
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm shadow-md leading-relaxed ${
                msg.sender === "user"
                  ? "bg-cyan-600 text-white rounded-br-none"
                  : msg.isError
                    ? "bg-red-950/50 border border-red-500/30 text-red-200 rounded-bl-none"
                    : "bg-slate-850 border border-slate-700/60 text-slate-200 rounded-bl-none"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>
          </div>
        ))}

        {mutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-slate-800/60 border border-slate-700/40 rounded-2xl rounded-bl-none px-4 py-3 flex space-x-1.5 items-center">
              <div
                className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                style={{ animationDelay: "0ms" }}
              ></div>
              <div
                className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                style={{ animationDelay: "150ms" }}
              ></div>
              <div
                className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
                style={{ animationDelay: "300ms" }}
              ></div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <footer className="p-4 bg-slate-900 border-t border-slate-800/60">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={mutation.isPending}
            className="flex-1 bg-slate-800 border border-slate-700/80 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || mutation.isPending}
            className="bg-cyan-500 hover:bg-cyan-600 text-slate-900 font-semibold px-5 py-3 rounded-xl text-sm transition shadow-lg shadow-cyan-500/10 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}
