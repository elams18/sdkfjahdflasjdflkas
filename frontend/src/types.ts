export interface Metrics {
  maeMw: number;
  rmseMw: number;
  meanBiasMw: number;
  matchedIntervals: number;
  expectedIntervals: number;
  coveragePct: number;
}

export interface DaySummary {
  decisionDate: string;
  deliveryDate: string;
  cutoffTime: string;
  cutoffTimeZone: string;
  latestPublishTime: string | null;
  metrics: Metrics;
}

export interface IntervalRow {
  startTime: string;
  localTime: string;
  forecastMw: number | null;
  actualMw: number | null;
  errorMw: number | null;
  publishTime: string | null;
}

export interface DashboardResponse {
  decisionDate: string;
  deliveryDate: string;
  cutoffTime: string;
  cutoffTimeZone: string;
  dataResolution: string;
  monthMetrics: Metrics;
  days: DaySummary[];
  selectedDay: (DaySummary & { intervals: IntervalRow[] }) | null;
  source: string;
  historicalDataAvailable: boolean;
}