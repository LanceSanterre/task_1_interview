import pandas as pd
import glob
import os

# Paths
data_path = "/Users/lancesanterre/interview/data_aq/team_scenarios"
output_path = "/Users/lancesanterre/interview/data_aq/team_data"
os.makedirs(output_path, exist_ok=True)

team_list = [
    "ARI",
    "ATL",
    "BAL",
    "BOS",
    "CHC",
    "CHW",
    "CIN",
    "CLE",
    "COL",
    "DET",
    "HOU",
    "KC",
    "LAA",
    "LAD",
    "MIA",
    "MIL",
    "MIN",
    "NYM",
    "NYY",
    "OAK",
    "PHI",
    "PIT",
    "SD",
    "SEA",
    "SF",
    "STL",
    "TB",
    "TEX",
    "TOR",
    "WSN",
]

bool_cols = [
    "is_close_scenario",
    "is_comeback_scenario",
    "no_runs_scored_late",
    "held_game",
    "final_win",
]

num_cols = ["team_runs_6", "opp_runs_6", "team_runs_7_9", "opp_runs_7_9"]

all_teams_data = []

for team_abbr in team_list:
    csv_files = sorted(glob.glob(os.path.join(data_path, f"{team_abbr}_*.csv")))
    team_data = []

    for file in csv_files:
        df = pd.read_csv(file)

        # Ensure numeric for run columns (missing -> 0)
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Ensure booleans for scenario/result flags
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool)

        # Derived: comeback wins (boolean per game)
        df["comeback_wins"] = df["is_comeback_scenario"] & df["final_win"]

        # NEW: led by 1–2 runs after 6th (per game)
        margin_after6 = df["team_runs_6"] - df["opp_runs_6"]
        df["lead_1_2_runs_6th"] = margin_after6.isin([1, 2]).astype(int)

        # Aggregate for this year/team
        agg_row = {
            "team": df["team"].iloc[0] if "team" in df.columns else team_abbr,
            "year": int(df["year"].iloc[0]),
            "is_close_scenario": int(df["is_close_scenario"].sum()),
            "is_comeback_scenario": int(df["is_comeback_scenario"].sum()),
            "no_runs_scored_late": int(df["no_runs_scored_late"].sum()),
            "held_game": int(df["held_game"].sum()),
            "comeback_wins": int(df["comeback_wins"].sum()),
            "final_win": int(df["final_win"].sum()),
            "lead_1_2_runs_6th": int(
                df["lead_1_2_runs_6th"].sum()
            ),  # NEW aggregated count
            "total_games": int(len(df)),
        }
        team_data.append(agg_row)
        all_teams_data.append(agg_row)

    # Save per-team yearly summary (now includes lead_1_2_runs_6th)
    team_yearly_df = pd.DataFrame(team_data)
    team_yearly_df = team_yearly_df[
        [
            "team",
            "year",
            "is_close_scenario",
            "is_comeback_scenario",
            "no_runs_scored_late",
            "held_game",
            "comeback_wins",
            "final_win",
            "lead_1_2_runs_6th",
            "total_games",
        ]
    ]
    team_yearly_df.to_csv(f"{output_path}/{team_abbr}_yearly_summary.csv", index=False)
    print(f"✅ Saved {team_abbr}_yearly_summary.csv")

# Optional: combined file for all teams (also includes lead_1_2_runs_6th)
all_df = pd.DataFrame(all_teams_data)
all_df = all_df[
    [
        "team",
        "year",
        "is_close_scenario",
        "is_comeback_scenario",
        "no_runs_scored_late",
        "held_game",
        "comeback_wins",
        "final_win",
        "lead_1_2_runs_6th",
        "total_games",
    ]
]
all_df.to_csv(f"{output_path}/all_teams_yearly_summary.csv", index=False)
print("✅ All teams combined summary saved as all_teams_yearly_summary.csv")
