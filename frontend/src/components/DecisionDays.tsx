import type { DaySummary } from "../types";
import { formatThousands } from "../lib/format";

interface DecisionDaysProps {
    days: DaySummary[];
    decisionDate: string;
    loading: boolean;
    onSelect(date: string): void;
}

export function DecisionDays({ days, decisionDate, loading, onSelect }: DecisionDaysProps) {
    return (
        <aside className="day-rail">
            <div className="rail-heading">
                <div><div className="section-kicker">JANUARY REVIEW</div><h2>Decision days</h2></div>
                <span>{days.length || 31}</span>
            </div>
            <div className="day-list">
                {days.map((day) => (
                    <button
                        className={`day-row ${decisionDate === day.decisionDate ? "active" : ""}`}
                        key={day.decisionDate}
                        type="button"
                        onClick={() => onSelect(day.decisionDate)}
                    >
                        <span className="day-date">
                            {new Date(`${day.decisionDate}T12:00:00`).toLocaleDateString("en-GB", {
                                weekday: "short",
                                day: "2-digit",
                            })}
                        </span>
                        <span className="day-mae">
                            {day.metrics.matchedIntervals ? `${formatThousands(day.metrics.maeMw)} MW` : "No match"}
                        </span>
                        <span className={`day-coverage ${day.metrics.coveragePct === 100 ? "complete" : day.metrics.coveragePct > 0 ? "partial" : "empty"}`}>
                            {day.metrics.coveragePct}%
                        </span>
                    </button>
                ))}
                {loading && days.length === 0 && (
                    <div className="day-list-state" role="status">Loading decision days…</div>
                )}
                {!loading && days.length === 0 && (
                    <div className="day-list-state">No decision-day data.</div>
                )}
            </div>
            <div className="rail-note"><span className="coverage-dot" /> Select a decision date to inspect its next-day delivery.</div>
        </aside>
    );
}