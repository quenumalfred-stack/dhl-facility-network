# DHL U.S. Facility Network Analysis

End-to-end analytics project using Python, SQL, and Tableau to analyze DHL facility distribution and Saturday pickup coverage across the U.S.

## Repository Structure

- `python/dhl_facility_refactored.py` - data cleaning and export pipeline
- `sql/dhl_facility_analysis_queries.sql` - SQL analysis queries
- `data/dhl_facilities_clean.csv` - cleaned dataset used for analysis and dashboarding
- `assets/` - dashboard screenshots (add your exported Tableau PNG here)

## Business Questions

1. Which U.S. states have the highest DHL facility concentration?
2. What is the distribution of DHL facility categories?
3. How does Saturday pickup availability differ by facility category?

## How To Run (Python)

```bash
python3 python/dhl_facility_refactored.py --input data/dhl_facilities_clean.csv --output-dir outputs
```

## How To Run (SQL)

Use your MySQL schema (example `dhl_project`) and run:

```sql
USE dhl_project;
SOURCE sql/dhl_facility_analysis_queries.sql;
```

## Tableau Dashboard

Dashboard title: `DHL U.S. Facility Network Dashboard`

Core visuals:
- US Facility Map
- Top States by Facilities
- Facility Mix
- Saturday Coverage by Category

## Key Insights

- Texas, Florida, and California have the highest facility counts.
- Drop Box and Drop Off Facility is the dominant network category.
- Saturday pickup is highest in DHL Staffed Facility and lowest in Drop Box and Drop Off Facility.
