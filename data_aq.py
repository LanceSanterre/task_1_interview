from pybaseball import schedule_and_record
import statsapi
import pandas as pd
import os

# All MLB teams with corresponding statsapi team IDs
mlb_teams = {
    "ARI": (109, "Arizona Diamondbacks"),
    "ATL": (144, "Atlanta Braves"),
    "BAL": (110, "Baltimore Orioles"),
    "BOS": (111, "Boston Red Sox"),
    "CHC": (112, "Chicago Cubs"),
    "CHW": (145, "Chicago White Sox"),
    "CIN": (113, "Cincinnati Reds"),
    "CLE": (114, "Cleveland Guardians"),
    "COL": (115, "Colorado Rockies"),
    "DET": (116, "Detroit Tigers"),
    "HOU": (117, "Houston Astros"),
    "KC": (118, "Kansas City Royals"),
    "LAA": (108, "Los Angeles Angels"),
    "LAD": (119, "Los Angeles Dodgers"),
    "MIA": (146, "Miami Marlins"),
    "MIL": (158, "Milwaukee Brewers"),
    "MIN": (142, "Minnesota Twins"),
    "NYM": (121, "New York Mets"),
    "NYY": (147, "New York Yankees"),
    "OAK": (133, "Oakland Athletics"),
    "PHI": (143, "Philadelphia Phillies"),
    "PIT": (134, "Pittsburgh Pirates"),
    "SD": (135, "San Diego Padres"),
    "SEA": (136, "Seattle Mariners"),
    "SF": (137, "San Francisco Giants"),
    "STL": (138, "St. Louis Cardinals"),
    "TB": (139, "Tampa Bay Rays"),
    "TEX": (140, "Texas Rangers"),
    "TOR": (141, "Toronto Blue Jays"),
    "WSN": (120, "Washington Nationals"),
}
years = list(range(2011, 2024))
output_dir = "team_scenarios"

os.makedirs(output_dir, exist_ok=True)

for abbr, (team_id, team_name) in mlb_teams.items():
    for year in years:
        print(f"📅 Processing {team_name} - {year}")
        try:
            schedule_df = schedule_and_record(year, abbr)
            schedule_df["DateClean"] = (
                schedule_df["Date"]
                .astype(str)
                .str.extract(r"([A-Za-z]{3,9}\s\d{1,2})")[0]
                + f" {year}"
            )
            schedule_df["Date"] = pd.to_datetime(
                schedule_df["DateClean"], errors="coerce"
            )
            schedule_df = schedule_df[schedule_df["Date"].notna()]

            games = statsapi.schedule(
                start_date=f"{year}-03-01",
                end_date=f"{year}-11-15",
                team=team_id,
                sportId=1,
            )
            games = [g for g in games if g.get("game_type") == "R"]

            games_df = pd.DataFrame(
                [
                    {
                        "Date": pd.to_datetime(game["game_date"]),
                        "home_team": game["home_name"],
                        "away_team": game["away_name"],
                        "game_id": game["game_id"],
                        "home_score": game["home_score"],
                        "away_score": game["away_score"],
                    }
                    for game in games
                ]
            )

            merged_df = pd.merge(schedule_df, games_df, on="Date", how="inner")
            merged_df = merged_df.drop_duplicates(subset="game_id").reset_index(
                drop=True
            )

            game_records = []

            for _, row in merged_df.iterrows():
                game_id = row["game_id"]
                is_home = row["home_team"] == team_name

                try:
                    data = statsapi.get("game", {"gamePk": game_id})
                    innings = data["liveData"]["linescore"]["innings"]

                    team_runs_6 = sum(
                        [
                            (
                                inning.get("home", {}).get("runs", 0)
                                if is_home
                                else inning.get("away", {}).get("runs", 0)
                            )
                            for inning in innings[:6]
                        ]
                    )
                    opp_runs_6 = sum(
                        [
                            (
                                inning.get("away", {}).get("runs", 0)
                                if is_home
                                else inning.get("home", {}).get("runs", 0)
                            )
                            for inning in innings[:6]
                        ]
                    )
                    team_runs_late = sum(
                        [
                            (
                                inning.get("home", {}).get("runs", 0)
                                if is_home
                                else inning.get("away", {}).get("runs", 0)
                            )
                            for inning in innings[6:]
                        ]
                    )
                    opp_runs_late = sum(
                        [
                            (
                                inning.get("away", {}).get("runs", 0)
                                if is_home
                                else inning.get("home", {}).get("runs", 0)
                            )
                            for inning in innings[6:]
                        ]
                    )
                    team_score = row["home_score"] if is_home else row["away_score"]
                    opp_score = row["away_score"] if is_home else row["home_score"]
                    won = team_score > opp_score

                    is_close_scenario = abs(team_runs_6 - opp_runs_6) <= 2
                    is_comeback_scenario = team_runs_6 < opp_runs_6
                    no_runs_scored_late = team_runs_late == 0 and opp_runs_late == 0
                    held_game = is_close_scenario and no_runs_scored_late

                    game_records.append(
                        {
                            "date": row["Date"],
                            "team": abbr,
                            "year": year,
                            "game_id": game_id,
                            "team_runs_6": team_runs_6,
                            "opp_runs_6": opp_runs_6,
                            "team_runs_7_9": team_runs_late,
                            "opp_runs_7_9": opp_runs_late,
                            "is_close_scenario": is_close_scenario,
                            "is_comeback_scenario": is_comeback_scenario,
                            "no_runs_scored_late": no_runs_scored_late,
                            "held_game": held_game,
                            "final_win": won,
                        }
                    )

                except Exception as e:
                    print(f"⚠️ Error on game {game_id}: {e}")

            df_results = pd.DataFrame(game_records)
            output_path = os.path.join(output_dir, f"{abbr}_{year}_scenarios.csv")
            df_results.to_csv(output_path, index=False)
            print(f"✅ Saved: {output_path}\n")

        except Exception as e:
            print(f"🚫 Failed for {team_name} - {year}: {e}\n")
