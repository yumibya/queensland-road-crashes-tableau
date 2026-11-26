# Queensland Road Crashes, 2001–2023: Interactive Tableau Dashboard

An interactive Tableau dashboard analysing when, where and under what recorded conditions Queensland road crashes were most frequent and most severe, built from 23 years of police-reported crash data.

[Interactive version on Tableau Public](https://public.tableau.com/app/profile/yu.mi.buon.ya4762/viz/Queensland_Road_Crash2001-2023/QueenslandRoadCrashesDashboard)

<img width="3198" height="2498" alt="Queensland Road Crashes Dashboard-2" src="https://github.com/user-attachments/assets/b78f3cce-2e99-4df4-8b76-240596fd234b" />
*Figure 1. Queensland road crashes interactive dashboard*

## Question 

Total injury crashes in Queensland were stable over 23 years, so is road safety actually improving? And where do crashes turn fatal or serious most often, so that limited road safety effort can go where it could prevent the most deaths?

The dashboard breaks this into three questions:

- **When:** has severity changed over time, even where the total number of crashes has not?
- **Where:** does fatal risk differ between cities and remote areas, and is the gap changing?
- **What:** which speed limits, lighting conditions, times of day and road user types are associated with the worst outcomes?

## Data

- Source: [Crash data from Queensland roads](https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads), Queensland Government Open Data Portal.
- 393,879 police-reported crashes from 1 Jan 2001 to 31 Dec 2023, in five severity levels: fatal, hospitalisation, medical treatment, minor injury and property damage only (PDO).
- Property-damage-only crashes stopped being recorded after 31 Dec 2010, which cut recorded crashes by 44% in 2011. To keep years comparable, the analysis uses the **306,447 injury crashes** only.
- "Serious" means fatal or hospitalisation. The *fatal-or-serious share* is their percentage of injury crashes.

## Approach

1. **Validated and cleaned the data in Python.** No duplicates were found, and casualty counts agreed with severity levels. Text was trimmed and blanks were labelled by meaning (for example "Not a state road" rather than "Unknown"). 598 crashes without coordinates were excluded from maps only.
2. **Derived 24 fields**, including a monthly date, binary fatal and fatal-or-serious flags (whose averages give rates directly in Tableau) and a primary road user for each crash, assigned by vulnerability (pedestrian > motorcycle > bicycle > truck > bus > car).
3. **Built five visualisations and combined them into one dashboard** with a year selector, a council filter and a view switch, so a user can test whether a pattern holds in their own area or in a given year.

Design decisions:

- **Rates, not counts**, so conditions with many crashes do not look riskier just because they are common.
- **Small multiples with separate scales** for severity trends, because on a shared axis the fatal line (about 200 to 340 crashes a year) looks flat next to categories above 5,000.
- **One colour, one meaning**: teal for the fatal-or-serious share, red for fatal outcomes, a fixed colour per severity level. Dashed lines mark the statewide average.
- **Accessibility and fairness**: year-on-year changes use ▲ and ▼ as well as colour. Councils with fewer than 50 crashes are left off the council map so a few crashes do not label a community as dangerous, but their crashes remain in every statewide figure.

## Key findings (2001–2023)

### When: stable totals hid a shift in severity

Hospitalisation crashes rose 58% while medical-treatment crashes fell 24% and minor-injury crashes fell 39%. Fatal crashes fell 42% from a 2007 peak (338) to 2019 (197), then rose 34% to 264 in 2023 (Figure 2).

<img width="1098" height="684" alt="Screenshot 2026-11-26 at 3 32 01 PM" src="https://github.com/user-attachments/assets/81a7ecdb-74c8-4d35-8af0-a35e0b4d363f" />

*Figure 2. Queensland road crashes by severity, 2001–2023*

### Where: remote areas carried the highest fatal risk

A remote crash was more than five times as likely to be fatal as a major-city crash. The major-city fatal rate fell from 1.3% to 1.0%, while the remote rate rose from 5.5% to 6.4% (small numbers, so a direction rather than a precise estimate) (Figures 3a and 3b).

<img width="1093" height="678" alt="Screenshot 2026-11-26 at 3 33 03 PM" src="https://github.com/user-attachments/assets/b9a760ba-8c1e-459d-ad3e-17813b10f0a8" />

*Figure 3a. Crash volume and severity by local government area*

<img width="1105" height="681" alt="Screenshot 2026-11-26 at 3 33 31 PM" src="https://github.com/user-attachments/assets/93527360-6bfd-4ae9-be14-25c04996fd7e" />

*Figure 3b. Fatal crash rate by remoteness, 2001–2023*

### What: speed, lighting and road conditions

The fatal rate was 5.2% in 100–110 km/h zones versus 1.0% at 60 km/h, and 6.0% on unlit roads versus 1.6% in daylight. Unsealed or curved roads were about 3.5%. Unlit 100–110 km/h crashes were fatal in 7.8% of cases (Figures 4a to 4c).

<img width="1112" height="684" alt="Screenshot 2026-11-26 at 3 34 12 PM" src="https://github.com/user-attachments/assets/38d41f0d-45fa-4a61-af12-bc2ef294be94" />

*Figure 4a. Fatal crash rate by speed limit*

<img width="1104" height="679" alt="Screenshot 2026-11-26 at 3 34 31 PM" src="https://github.com/user-attachments/assets/87e9235d-51a4-44e2-b8d8-c04d9f7f2cc7" />

*Figure 4b. Fatal crash rate by lighting condition*

<img width="1114" height="677" alt="Screenshot 2026-11-26 at 3 34 58 PM" src="https://github.com/user-attachments/assets/14d43456-a8d5-469e-b06f-f3677fa50b2f" />

*Figure 4c. Fatal crash rate by weather condition*

### Time of day: night crashes were few but disproportionately deadly

Midnight to 5am made up 5.7% of crashes but 13.1% of fatal crashes, and 56.1% were fatal or serious, against 39.6% between 9am and 5pm (Figure 5).

<img width="1102" height="677" alt="Screenshot 2026-11-26 at 3 35 18 PM" src="https://github.com/user-attachments/assets/ffb0fe42-4612-4384-a03d-fffc61883968" />

*Figure 5. Crash severity by hour and day of week*

### Road users: vulnerable road users fared worst

Motorcyclists (62% serious) and pedestrians (57%) made up 17.1% of crashes but 33.3% of fatal crashes. Trucks had a similar serious share to bicycles but four times the fatal rate (4.2% versus 1.0%) (Figure 6).

<img width="1097" height="677" alt="Screenshot 2026-11-26 at 3 35 43 PM" src="https://github.com/user-attachments/assets/829218a8-7f32-47bc-89f7-f07fbc5d3e85" />

*Figure 6. Crash severity by road user type*

### Interactive example

Stepping the year selector to 2020 shows injury crashes falling 6% while fatal crashes rose 27%, an anomaly hidden in the 23-year totals (Figure 1).

## Limitations

- Observational data. Findings describe association with severity, not cause.
- The rise in the fatal-or-serious share (32.6% to 51.4%) persisted within groups, and the fatal rate stayed roughly flat (2.1% to 1.9%). A change in how injuries are recorded or admitted is therefore a plausible explanation, but the data cannot confirm it.
- The data has no age or gender fields, so gaps between road users may partly reflect who uses each mode.
- The 2011 drop reflects the end of PDO recording, not safer roads. The April 2020 dip coincides with COVID-19 restrictions.
- Remote and very remote areas have small crash numbers, so their trends are less precise.

## Tools and skills demonstrated

Python (data validation, cleaning, feature engineering), Tableau (calculated fields, small multiples, proportional symbol maps, heatmaps, interactive dashboard design), rate-based analysis, analytical writing.

## Repository contents

| Path | What it is |
|---|---|
| `Queensland_Road_Crash2001-2023.twbx` | Tableau packaged workbook (open in Tableau Desktop or Tableau Public) |
| `images/` | Dashboard and chart screenshots |

## Data source and attribution

Queensland Government Open Data Portal, *Crash data from Queensland roads*. Independent portfolio project, not affiliated with or endorsed by the Queensland Government.
