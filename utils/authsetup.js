import axios from "axios";

const API_URL = "http://localhost:4000/auth";

export const signup = async (role, data) => {
  const url = `${API_URL}/${role.toLowerCase()}/signup`;
  return axios.post(url, data);
};

export const login = async (role, data) => {
  const url = `${API_URL}/${role.toLowerCase()}/login`;
  return axios.post(url, data);
};

export const abcLogin = async () => {
  try {
    const res = await axios.get(`${API_URL}/abc/callback?code=demo123`);
    return res; // res.data will have token, role, user
  } catch (err) {
    console.error("ABC login failed:", err);
    throw err;
  }
};
