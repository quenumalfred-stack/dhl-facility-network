USE dhl_project;

-- 1) Total facilities
SELECT COUNT(*) AS total_facilities
FROM dhl_facilities;

-- 2) Facility mix
SELECT
  LOCATION_TH AS location_category,
  COUNT(*) AS facilities,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dhl_facilities), 2) AS pct_total
FROM dhl_facilities
GROUP BY LOCATION_TH
ORDER BY facilities DESC;

-- 3) Saturday pickup rate by type
SELECT
  LOCATION_TH AS location_category,
  COUNT(*) AS facilities,
  SUM(CASE WHEN LOWER(LAST_PICKUP) LIKE '%no sat pickup%' THEN 0 ELSE 1 END) AS sat_pickup_sites,
  ROUND(
    100.0 * SUM(CASE WHEN LOWER(LAST_PICKUP) LIKE '%no sat pickup%' THEN 0 ELSE 1 END) / COUNT(*),
    2
  ) AS sat_pickup_rate_pct
FROM dhl_facilities
GROUP BY LOCATION_TH
ORDER BY sat_pickup_rate_pct DESC;

