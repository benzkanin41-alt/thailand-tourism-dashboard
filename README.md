# Thailand Tourism Dashboard

Interactive dashboard for Thailand international tourist arrivals, with monthly, quarterly, annual views and MoM/QoQ/YoY growth.

## Online dashboard

After GitHub Pages deploys, open the project page URL shown in the repository Pages settings or the latest `Refresh and Deploy Dashboard` workflow run.

## Data refresh

The GitHub Actions workflow in `.github/workflows/deploy-pages.yml` refreshes the dashboard on the 15th day of every month at 09:17 Asia/Bangkok (`02:17 UTC`) and can also be run manually with `workflow_dispatch`.

## Sources

- MOTS tourism statistics category 411
- data.go.th `stattourism`
- data.go.th `trend_inbound_tourists`
- World Bank `ST.INT.ARVL` annual arrivals API

## Local rebuild

```powershell
python -X utf8 .\work\fetch_tourism_data.py --refresh
python -X utf8 .\work\build_dashboard.py
```
