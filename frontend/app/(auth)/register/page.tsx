"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const res = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) { setError("Registration failed"); return; }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    router.push("/dashboard");
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-80">
        <h1 className="text-2xl font-bold">Register</h1>
        {error && <p className="text-red-500">{error}</p>}
        <input className="border p-2 rounded" type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input className="border p-2 rounded" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="bg-blue-600 text-white p-2 rounded" type="submit">Register</button>
        <a href="/login" className="text-center text-blue-600">Already have an account?</a>
      </form>
    </div>
  );
}
