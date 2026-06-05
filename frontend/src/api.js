import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendChatMessage = async (payload) => {
  const response = await api.post("/chat", payload);
  return response.data;
};

export const getChatHistory = async (chatId) => {
  const response = await api.get(`/chat/${chatId}/history`);
  return response.data;
};
