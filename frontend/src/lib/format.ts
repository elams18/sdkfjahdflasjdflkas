const numberFormat = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

export function formatMw(value: number | null | undefined): string {
    return value == null ? "Unavailable" : `${numberFormat.format(value)} MW`;
}

export function formatTimestamp(value: string | null | undefined): string {
    if (!value) return "No eligible vintage";
    return new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Europe/London",
        timeZoneName: "short",
    }).format(new Date(value));
}

export function formatBias(value: number): string {
    if (value === 0) return "0 MW";
    return `${value > 0 ? "+" : "−"}${numberFormat.format(Math.abs(value))} MW`;
}

export function formatThousands(value: number): string {
    return numberFormat.format(value);
}