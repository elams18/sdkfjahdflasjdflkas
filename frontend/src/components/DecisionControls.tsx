import { CalendarDays, Clock3, RefreshCw } from "lucide-react";

interface DecisionControlsProps {
    decisionDate: string;
    cutoffTime: string;
    displayedCutoffTime: string;
    loading: boolean;
    onDecisionDateChange(value: string): void;
    onCutoffTimeChange(value: string): void;
    onRefresh(): void;
}

export function DecisionControls({
    decisionDate,
    cutoffTime,
    displayedCutoffTime,
    loading,
    onDecisionDateChange,
    onCutoffTimeChange,
    onRefresh,
}: DecisionControlsProps) {
    return (
        <section className="control-bar" aria-label="Decision snapshot controls">
            <label className="control-field">
                <span>Decision date</span>
                <div className="control-input-shell">
                    <input
                        type="date"
                        min="2026-01-01"
                        max="2026-01-31"
                        value={decisionDate}
                        onChange={(event) => onDecisionDateChange(event.target.value)}
                    />
                    <CalendarDays className="control-picker-icon" size={15} aria-hidden="true" />
                </div>
            </label>
            <label className="control-field cutoff-control">
                <span>Decision cutoff</span>
                <div className="control-input-shell">
                    <input
                        type="time"
                        value={cutoffTime || displayedCutoffTime}
                        onChange={(event) => onCutoffTimeChange(event.target.value)}
                    />
                    <Clock3 className="control-picker-icon" size={15} aria-hidden="true" />
                </div>
            </label>
            <div className="control-hint">Europe/London</div>
            <button
                className="refresh-button"
                type="button"
                onClick={onRefresh}
                disabled={loading}
            >
                <RefreshCw size={15} className={loading ? "spin" : ""} />
                Refresh data
            </button>
        </section>
    );
}