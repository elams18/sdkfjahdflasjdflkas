import type { IntervalRow } from "../types";
import { formatBias, formatMw, formatTimestamp } from "../lib/format";

interface IntervalTableProps {
    intervals: IntervalRow[];
    loading: boolean;
}

export function IntervalTable({ intervals, loading }: IntervalTableProps) {
    return (
        <section className="table-section">
            <div className="section-heading table-heading">
                <div>
                    <div className="section-kicker">INTERVAL AUDIT</div>
                    <h2>Forecast against outturn</h2>
                </div>
                <span className="row-count">{intervals.filter((row) => row.errorMw !== null).length} matched / 24 hourly</span>
            </div>
            <div className="table-scroll">
                <table>
                    <thead>
                        <tr>
                            <th>Delivery start</th>
                            <th>Forecast vintage</th>
                            <th className="numeric">Forecast</th>
                            <th className="numeric">Actual</th>
                            <th className="numeric">Error</th>
                        </tr>
                    </thead>
                    <tbody>
                        {intervals.map((row) => (
                            <tr key={row.startTime}>
                                <td className="time-cell">{row.localTime}<span>UK</span></td>
                                <td className="vintage-cell">{formatTimestamp(row.publishTime)}</td>
                                <td className="numeric">{formatMw(row.forecastMw)}</td>
                                <td className="numeric">{formatMw(row.actualMw)}</td>
                                <td className={`numeric error-cell ${row.errorMw == null ? "muted" : row.errorMw > 0 ? "positive" : row.errorMw < 0 ? "negative" : ""}`}>
                                    {row.errorMw == null ? "Missing" : formatBias(row.errorMw)}
                                </td>
                            </tr>
                        ))}
                        {!loading && intervals.length === 0 && (
                            <tr><td className="empty-cell" colSpan={5}>No interval rows returned for this decision date.</td></tr>
                        )}
                        {loading && intervals.length === 0 && (
                            <tr><td className="empty-cell" colSpan={5}>Loading interval data…</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </section>
    );
}