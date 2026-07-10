"use client";

import { create } from "zustand";

type ConnectionState = "connecting" | "connected" | "offline" | "error";

interface ConnectionStore {
	state: ConnectionState;
	lastError: string | null;
}

export const useConnection = create<ConnectionStore>(() => ({
	state: "connecting",
	lastError: null,
}));
