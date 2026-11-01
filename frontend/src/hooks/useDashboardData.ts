import { useEffect, useRef, useState } from "react";
import type { DashboardResponse } from "../types";

const API_URL = (
    import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "")
).replace(/\/$/, "");

export function useDashboardData(decisionDate: string, cutoffTime: string) {
    const [refreshKey, setRefreshKey] = useState(0);
    const refreshRequested = useRef(false);
    const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const controller = new AbortController();
        const params = new URLSearchParams({ decision_date: decisionDate });
        if (cutoffTime) params.set("cutoff_time", cutoffTime);
        params.set("refresh_data", String(refreshRequested.current));
        refreshRequested.current = false;

        setLoading(true);
        setError(null);
        setDashboard((current) =>
            current?.decisionDate === decisionDate &&
            (!cutoffTime || current.cutoffTime === cutoffTime)
                ? current
                : null,
        );

        fetch(`${API_URL}/api/dashboard?${params}`, { signal: controller.signal })
            .then(async (response) => {
                if (!response.ok) {
                    const body = await response.json().catch(() => null);
                    throw new Error(body?.detail ?? `Data service returned ${response.status}`);
                }
                return response.json() as Promise<DashboardResponse>;
            })
            .then(setDashboard)
            .catch((reason: unknown) => {
                if (controller.signal.aborted) return;
                setError(reason instanceof Error ? reason.message : "Unable to load Elexon data.");
            })
            .finally(() => {
                if (!controller.signal.aborted) setLoading(false);
            });

        return () => controller.abort();
    }, [decisionDate, cutoffTime, refreshKey]);

    function refresh() {
        refreshRequested.current = true;
        setRefreshKey((key) => key + 1);
    }

    return { dashboard, error, loading, refresh };
}