"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Workspace { id: string; name: string; created_at: string; }

export default function DashboardPage() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [name, setName] = useState("");

  async function loadWorkspaces() {
    const res = await apiFetch("/workspaces/");
    if (res.status === 401) { router.push("/login"); return; }
    setWorkspaces(await res.json());
  }

  async function createWorkspace(e: React.FormEvent) {
    e.preventDefault();
    await apiFetch("/workspaces/", { method: "POST", body: JSON.stringify({ name }) });
    setName("");
    loadWorkspaces();
  }

  async function deleteWorkspace(id: string) {
    await apiFetch(`/workspaces/${id}`, { method: "DELETE" });
    loadWorkspaces();
  }

  useEffect(() => { loadWorkspaces(); }, []);

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">My Workspaces</h1>
      <form onSubmit={createWorkspace} className="flex gap-2 mb-6">
        <input className="border p-2 rounded flex-1" placeholder="Workspace name" value={name} onChange={e => setName(e.target.value)} />
        <button className="bg-blue-600 text-white px-4 rounded" type="submit">Create</button>
      </form>
      <ul className="flex flex-col gap-2">
        {workspaces.map(ws => (
          <li key={ws.id} className="flex justify-between items-center border p-3 rounded">
            <span>{ws.name}</span>
            <button className="text-red-500" onClick={() => deleteWorkspace(ws.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
