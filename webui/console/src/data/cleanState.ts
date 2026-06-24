import type {
  Asset,
  DashboardMetrics,
  Finding,
  SeverityDistributionPoint,
  VulnerabilityTrendPoint,
} from "@/types";

export const emptyAssets: Asset[] = [];
export const emptyFindings: Finding[] = [];
export const emptyTrendData: VulnerabilityTrendPoint[] = [];
export const emptySeverityDistribution: SeverityDistributionPoint[] = [];

export const emptyDashboardMetrics: DashboardMetrics = {
  totalScanned: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  autoRemediationRate: 0,
  pendingReviews: 0,
  meanTimeToRemediateHours: 0,
  trend: {
    critical: 0,
    high: 0,
    autoRemediationRate: 0,
    pendingReviews: 0,
  },
};
