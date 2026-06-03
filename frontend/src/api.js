import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendChatMessage = async (message) => {
  const response = await api.post("/chat", { message });
  return response.data;
};
