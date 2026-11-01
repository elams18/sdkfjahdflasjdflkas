import type { Metrics } from "../types";
import { formatBias, formatMw } from "../lib/format";

function Metric({
    label,
    value,
    note,
    tone,
}: {
    label: string;
    value: string;
    note: string;
    tone?: string;
}) {
    return (
        <div className="metric">
            <div className="metric-label">{label}</div>
            <div className={`metric-value ${tone ?? ""}`}>{value}</div>
            <div className="metric-note">{note}</div>
        </div>
    );
}

export function AccuracyMetrics({ metrics }: { metrics: Metrics | null }) {
    if (!metrics) {
        return <div className="metrics-loading" role="status">Loading January accuracy…</div>;
    }

    return (
        <section className="metrics" aria-label="January forecast accuracy">
            <Metric label="Mean absolute error" value={formatMw(metrics.maeMw)} note="Month average · MW" />
            <Metric label="Root mean square error" value={formatMw(metrics.rmseMw)} note="Penalises larger misses" />
            <Metric
                label="Mean forecast bias"
                value={formatBias(metrics.meanBiasMw)}
                note="Positive means forecast above actual"
                tone={metrics.meanBiasMw > 0 ? "tone-warm" : "tone-cool"}
            />
            <Metric
                label="Matched coverage"
                value={`${metrics.coveragePct}%`}
                note={`${metrics.matchedIntervals} of ${metrics.expectedIntervals} hourly intervals`}
            />
        </section>
    );
}