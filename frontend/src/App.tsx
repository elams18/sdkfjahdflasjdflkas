import { lazy, Suspense, useState } from "react";
import { Activity, Check } from "lucide-react";
import { AccuracyMetrics } from "./components/AccuracyMetrics";
import { ApiNotice } from "./components/ApiNotice";
import { DecisionControls } from "./components/DecisionControls";
import { DecisionDays } from "./components/DecisionDays";
import { IntervalTable } from "./components/IntervalTable";
import { useDashboardData } from "./hooks/useDashboardData";

const DeliveryChart = lazy(() =>
    import("./components/DeliveryChart").then((module) => ({
        default: module.DeliveryChart,
    })),
);

export default function App() {
    const [decisionDate, setDecisionDate] = useState("2026-01-01");
    const [cutoffTime, setCutoffTime] = useState("");
    const { dashboard, error, loading, refresh } = useDashboardData(decisionDate, cutoffTime);
    const selectedDay = dashboard?.selectedDay ?? undefined;
    const intervals = selectedDay?.intervals ?? [];
    const hasNoMatches = dashboard !== null && !dashboard.historicalDataAvailable;

    return (
        <div className="app-shell">
            <header className="topbar">
                <div className="topbar-heading">
                    <div className="eyebrow"><Activity size={14} /> RENEWABLES / DAY-AHEAD</div>
                    <h1>Wind forecast desk</h1>
                </div>
                <div className="topbar-right">
                    <span className="live-dot" />
                    <span>HISTORICAL PILOT</span>
                    <span className="topbar-divider" />
                    <span>GB NATIONAL</span>
                    <span className="topbar-divider" />
                    <div className="source-badge topbar-source">
                        <span className="source-mark">E</span> Elexon BMRS
                    </div>
                </div>
            </header>

            <main className="page">
                <DecisionControls
                    decisionDate={decisionDate}
                    cutoffTime={cutoffTime}
                    displayedCutoffTime={dashboard?.cutoffTime ?? ""}
                    loading={loading}
                    onDecisionDateChange={setDecisionDate}
                    onCutoffTimeChange={setCutoffTime}
                    onRefresh={refresh}
                />

                {error ? (
                    <ApiNotice title="Historical data unavailable" message={error} onRetry={refresh} />
                ) : (
                    <>
                        <AccuracyMetrics metrics={dashboard?.monthMetrics ?? null} />

                        {hasNoMatches && (
                            <ApiNotice
                                title="No matching historical intervals"
                                message="Current forecasts are not substituted for January vintages."
                            />
                        )}

                        <Suspense fallback={<div className="chart-state" role="status">Loading chart…</div>}>
                            <DeliveryChart selectedDay={selectedDay} loading={loading} />
                        </Suspense>

                        <div className="workspace-grid">
                            <div className="main-column">
                                <section className="snapshot-banner">
                                    <div className="snapshot-icon"><Check size={16} /></div>
                                    <div className="snapshot-copy">
                                        <strong>Forecast vintage rule</strong>
                                        <span>
                                            Latest Elexon publication at or before {dashboard?.cutoffTime ?? "the configured cutoff"} on each decision date. Pilot cutoff assumption, not client-confirmed policy.
                                        </span>
                                    </div>
                                    <div className="snapshot-resolution">Hourly comparison</div>
                                </section>
                                <IntervalTable intervals={intervals} loading={loading} />
                            </div>
                            <DecisionDays
                                days={dashboard?.days ?? []}
                                decisionDate={decisionDate}
                                loading={loading}
                                onSelect={setDecisionDate}
                            />
                        </div>
                    </>
                )}

                <footer className="page-footer">
                    <span><strong>Source</strong> {dashboard?.source ?? "Elexon BMRS FUELHH and WINDFOR"}</span>
                    <span>{dashboard?.dataResolution ?? "Hourly forecast values; actuals averaged from half-hour periods."}</span>
                    <span className="footer-disclaimer">Wind-only view. Not a complete procurement recommendation.</span>
                </footer>
            </main>
        </div>
    );
}