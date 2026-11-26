
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

log = []


def record(step, action, before, after, note=""):
    log.append({"Step": step, "Action": action, "Rows_Before": before,
                "Rows_Removed": before - after, "Rows_After": after, "Note": note})
    print(f"{step:<4} {action:<62} {before:>8,} -> {after:>8,}  {note}")


# ------------------------------------------------------------------
# 1. Load and inspect
# ------------------------------------------------------------------
df = pd.read_csv(SRC, low_memory=False)
n0 = len(df)
record("1", "Load raw file", n0, n0, f"{df.shape[1]} columns")

CAS = ["Count_Casualty_Fatality", "Count_Casualty_Hospitalised",
       "Count_Casualty_MedicallyTreated", "Count_Casualty_MinorInjury"]
UNITS = [c for c in df.columns if c.startswith("Count_Unit_")]

# ------------------------------------------------------------------
# 2. Standardise text: trim spaces, treat blank strings as missing
# ------------------------------------------------------------------
text_cols = df.select_dtypes(exclude="number").columns
for c in text_cols:
    df[c] = df[c].astype("string").str.strip().replace("", pd.NA)
record("2", "Trim whitespace in text columns", n0, len(df))

# ------------------------------------------------------------------
# 3. Duplicates
# ------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates()
record("3a", "Remove exact duplicate rows", before, len(df))

before = len(df)
df = df.drop_duplicates(subset="Crash_Ref_Number")
record("3b", "Remove duplicate Crash_Ref_Number", before, len(df))

before = len(df)
attrs = [c for c in df.columns if c != "Crash_Ref_Number"]
df = df.drop_duplicates(subset=attrs, keep="first")
record("3c", "Remove rows identical on every field except the ID", before, len(df),
       "same time, coordinates, street, casualties and vehicles")

# ------------------------------------------------------------------
# 4. Validity and consistency checks
# ------------------------------------------------------------------
before = len(df)
valid_hour = df["Crash_Hour"].between(0, 23)
qld_box = (df["Crash_Latitude"].between(-29.2, -9.0) &
           df["Crash_Longitude"].between(137.9, 153.6)) | df["Crash_Latitude"].isna()
df = df[valid_hour & qld_box]
record("4a", "Hour outside 0-23 or coordinates outside Queensland", before, len(df))

before = len(df)
df = df[df[CAS].sum(axis=1) == df["Count_Casualty_Total"]]
record("4b", "Casualty components do not add up to the total", before, len(df))

# Severity must match the most serious casualty recorded.
sev_from_counts = np.select(
    [df["Count_Casualty_Fatality"] > 0, df["Count_Casualty_Hospitalised"] > 0,
     df["Count_Casualty_MedicallyTreated"] > 0, df["Count_Casualty_MinorInjury"] > 0],
    ["Fatal", "Hospitalisation", "Medical treatment", "Minor injury"],
    default="Property damage only")
mismatch = df["Crash_Severity"] != sev_from_counts
before = len(df)
df = df[~mismatch]
record("4c", "Severity label contradicts casualty counts", before, len(df),
       "e.g. 'Hospitalisation' with no hospitalised casualty")

# ------------------------------------------------------------------
# 5. Scope: casualty crashes only (structural break in 2011)
# ------------------------------------------------------------------
pdo_by_year = (df[df["Crash_Severity"] == "Property damage only"]
               .groupby("Crash_Year").size())
last_pdo_year = int(pdo_by_year.index.max())
before = len(df)
df = df[df["Crash_Severity"] != "Property damage only"]
record("5", "Exclude 'Property damage only' crashes", before, len(df),
       f"recorded only up to {last_pdo_year}; none from {last_pdo_year + 1}")

# ------------------------------------------------------------------
# 6. Missing and 'Unknown' values (kept, standardised)
# ------------------------------------------------------------------
loc_unknown = df["Crash_Latitude"].isna() | (df["Loc_ABS_Remoteness"] == "Unknown")
record("6a", "Flag crashes with no location (kept for time analysis)",
       len(df), len(df), f"{int(loc_unknown.sum())} rows: Has_Location = 0")
df["Has_Location"] = (~loc_unknown).astype(int)

fill_cols = ["Crash_Speed_Limit", "Crash_Road_Vert_Align", "Crash_Road_Horiz_Align",
             "Crash_Road_Surface_Condition", "Crash_Atmospheric_Condition",
             "Crash_Lighting_Condition"]
n_filled = int(df[fill_cols].isna().sum().sum())
df[fill_cols] = df[fill_cols].fillna("Unknown")
record("6b", "Fill missing road-condition values with 'Unknown'", len(df), len(df),
       f"{n_filled} cells")

# ------------------------------------------------------------------
# 7. Outlier review (domain check, not automatic removal)
# ------------------------------------------------------------------
q1, q3 = df["Count_Casualty_Total"].quantile([0.25, 0.75])
iqr_flag = int((df["Count_Casualty_Total"] > q3 + 1.5 * (q3 - q1)).sum())
top = df.sort_values("Count_Casualty_Total", ascending=False).head(15)
top[["Crash_Ref_Number", "Crash_Year", "Crash_Severity", "Crash_Nature", "Crash_Type",
     "Count_Casualty_Total"] + UNITS].to_csv(OUT / "outlier_review.csv", index=False)
record("7", "Review extreme casualty counts (IQR rule)", len(df), len(df),
       f"IQR flags {iqr_flag} rows because Q1 = Q3 = {q1:g}; "
       f"max {int(df['Count_Casualty_Total'].max())} casualties; kept as real events")

# ------------------------------------------------------------------
# 8. Type conversion and derived fields
# ------------------------------------------------------------------
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["Crash_Year"] = df["Crash_Year"].astype(int)
df["Month_Num"] = df["Crash_Month"].map({m: i + 1 for i, m in enumerate(months)})
df["Crash_Date"] = pd.to_datetime(dict(year=df["Crash_Year"], month=df["Month_Num"], day=1))
df["Day_Num"] = df["Crash_Day_Of_Week"].map({d: i + 1 for i, d in enumerate(days)})
df["Is_Weekend"] = df["Day_Num"].isin([6, 7]).astype(int)

sev_order = {"Fatal": 1, "Hospitalisation": 2, "Medical treatment": 3, "Minor injury": 4}
df["Severity_Rank"] = df["Crash_Severity"].map(sev_order)
df["Is_Fatal"] = (df["Crash_Severity"] == "Fatal").astype(int)
df["Is_Fatal_or_Hospitalised"] = df["Crash_Severity"].isin(["Fatal", "Hospitalisation"]).astype(int)

speed_order = {"0 - 50 km/h": 1, "60 km/h": 2, "70 km/h": 3, "80 - 90 km/h": 4,
               "100 - 110 km/h": 5, "Unknown": 9}
df["Speed_Order"] = df["Crash_Speed_Limit"].map(speed_order)
remote_order = {"Major Cities": 1, "Inner Regional": 2, "Outer Regional": 3,
                "Remote": 4, "Very Remote": 5, "Unknown": 9}
df["Remoteness_Order"] = df["Loc_ABS_Remoteness"].map(remote_order)

df["Involves_Motorcycle"] = (df["Count_Unit_Motorcycle_Moped"] > 0).astype(int)
df["Involves_Pedestrian"] = (df["Count_Unit_Pedestrian"] > 0).astype(int)
df["Involves_Bicycle"] = (df["Count_Unit_Bicycle"] > 0).astype(int)
df["Involves_Truck"] = (df["Count_Unit_Truck"] > 0).astype(int)

assert df[["Month_Num", "Day_Num", "Severity_Rank", "Speed_Order",
           "Remoteness_Order"]].notna().all().all(), "unmapped category"

# ------------------------------------------------------------------
# 9. Keep the fields needed for analysis
#    (street names, suburbs and post codes dropped: not needed and
#     they would allow individual crashes to be located precisely)
# ------------------------------------------------------------------
keep = ["Crash_Ref_Number", "Crash_Severity", "Severity_Rank", "Is_Fatal",
        "Is_Fatal_or_Hospitalised", "Crash_Date", "Crash_Year", "Crash_Month", "Month_Num",
        "Crash_Day_Of_Week", "Day_Num", "Is_Weekend", "Crash_Hour",
        "Crash_Nature", "Crash_Type", "Crash_Latitude", "Crash_Longitude", "Has_Location",
        "Loc_Local_Government_Area", "Loc_Police_Region", "Loc_ABS_Remoteness",
        "Remoteness_Order", "Crash_Speed_Limit", "Speed_Order",
        "Crash_Road_Surface_Condition", "Crash_Atmospheric_Condition",
        "Crash_Lighting_Condition", "Crash_Roadway_Feature", "Crash_Controlling_Authority",
        "Crash_DCA_Group_Description"] + CAS + ["Count_Casualty_Total"] + UNITS + [
        "Involves_Motorcycle", "Involves_Pedestrian", "Involves_Bicycle", "Involves_Truck"]
dropped = [c for c in pd.read_csv(SRC, nrows=0).columns if c not in keep]
df = df[keep].sort_values(["Crash_Date", "Crash_Ref_Number"])
record("9", f"Keep {len(keep)} analysis fields, drop {len(dropped)}", len(df), len(df),
       "dropped: " + ", ".join(dropped))

df.to_csv(OUT / "crash_clean.csv", index=False, date_format="%Y-%m-%d")
pd.DataFrame(log).to_csv(OUT / "cleaning_log.csv", index=False)
print(f"\nFinal: {len(df):,} rows x {df.shape[1]} columns, "
      f"{df['Crash_Year'].min()}-{df['Crash_Year'].max()}")
