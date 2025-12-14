# Lighthouse Performance Evidence (UI)

## What this is
Lighthouse Performance run against the project UI served locally (http://127.0.0.1:8080/).  
Purpose: document baseline front-end performance signals for the exam deliverable.

## Evidence files
- `lighthouse-performance-metrics_localhost-8080_2025-12-14.png`  
  Snapshot of Lighthouse performance score + key metrics (FCP/LCP/CLS/TBT).
- `lighthouse-performance-opportunities_localhost-8080_2025-12-14.png`  
  Lighthouse “Opportunities/Diagnostics” suggestions for potential improvements.
- `lighthouse-report_localhost-8080_2025-12-14.json`  
  Full raw Lighthouse report (source data behind the screenshots).

## Key takeaway
This UI is lightweight and scores very high locally; remaining suggestions are mostly minor optimizations (e.g., reduce/minify CSS/JS) rather than functional performance issues.