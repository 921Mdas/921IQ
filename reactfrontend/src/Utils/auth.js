
import { API_AUTH_URL } from "../api";


export const signupUser = async (formData) => {
  const response = await fetch(`${API_AUTH_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Signup failed");
  }

  return await response.json(); // { token }
};

export const loginUser = async (formData) => {

  console.log('testing auth url', API_AUTH_URL)
  const response = await fetch(`${API_AUTH_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  });

  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail || "Login failed");
  }

  return await response.json(); // { token }
};