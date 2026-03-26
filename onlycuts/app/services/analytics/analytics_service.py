class AnalyticsService:
    def capture(self) -> dict:
        # TODO persist richer metrics once metrics_snapshots table exists.
        return {"captured": True}
