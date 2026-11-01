import { LoaderCircle } from "lucide-react";
import {
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import type { DashboardResponse } from "../types";
import { formatThousands, formatTimestamp } from "../lib/format";

interface DeliveryChartProps {
    selectedDay: NonNullable<DashboardResponse["selectedDay"]> | undefined;
    loading: boolean;
}

export function DeliveryChart({ selectedDay, loading }: DeliveryChartProps) {
    const intervals = selectedDay?.intervals ?? [];
    const deliveryHeading = selectedDay
        ? new Date(`${selectedDay.deliveryDate}T12:00:00`).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "long",
        })
        : "Selected delivery day";

    return (
        <section className="chart-section">
            <div className="section-heading">
                <div>
                    <div className="section-kicker">DELIVERY PROFILE</div>
                    <h2>{deliveryHeading}</h2>
                </div>
                <div className="chart-summary">
                    <span className="coverage-led">
                        <span className="live-dot" /> {selectedDay?.metrics.coveragePct ?? 0}% matched
                    </span>
                    <span>Latest vintage {formatTimestamp(selectedDay?.latestPublishTime)}</span>
                </div>
            </div>
            {loading && !selectedDay ? (
                <div className="chart-state" role="status">
                    <LoaderCircle className="spin" size={22} /> Loading Elexon data
                </div>
            ) : (
                <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={intervals} margin={{ top: 12, right: 12, bottom: 0, left: 0 }}>
                            <CartesianGrid stroke="#e1e4dc" vertical={false} />
                            <XAxis dataKey="localTime" tickLine={false} axisLine={false} interval={3} tick={{ fill: "#79817a", fontSize: 11 }} />
                            <YAxis tickLine={false} axisLine={false} width={66} tick={{ fill: "#79817a", fontSize: 11 }} tickFormatter={(value: number) => `${formatThousands(value / 1000)}k`} />
                            <Tooltip
                                contentStyle={{ border: "1px solid #dfe3da", borderRadius: 4, fontSize: 12 }}
                                formatter={(value) => `${formatThousands(Number(value))} MW`}
                                labelFormatter={(label) => `${label} UK time`}
                            />
                            <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, color: "#555f58", paddingTop: 10 }} />
                            <Line type="monotone" dataKey="forecastMw" name="Day-ahead forecast" stroke="#c48722" strokeWidth={2.5} dot={false} connectNulls={false} activeDot={{ r: 4 }} />
                            <Line type="monotone" dataKey="actualMw" name="Actual outturn" stroke="#167763" strokeWidth={2.5} dot={false} connectNulls={false} activeDot={{ r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}
            <div className="chart-footnote">
                Forecast MW is compared with the mean of the two corresponding half-hour actual MW values.
            </div>
        </section>
    );
}