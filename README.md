# MLB Comeback & Hold Metrics Analysis

This project calculates and analyzes advanced MLB metrics such as LGCI (Late Game Comeback Index) and LGWPI (Late Game Win Probability Index). It provides insights into team performance in comeback and hold situations, useful for predictive modeling and betting analysis.

## Project Structure
- `data_aq.py` — Script to scrape and acquire raw MLB game data.
- `data_combination.py` — Script to combine and preprocess acquired data into analysis-ready format.
- `task_1.ipynb` — Jupyter Notebook containing the analysis, visualizations, and statistical testing.

## How to Run

1. **Set up environment**
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

2. **Acquire data**
   - Run the following to scrape and save MLB data:
     ```bash
     python data_aq.py
     ```

3. **Combine data**
   - Merge and preprocess the data:
     ```bash
     python data_combination.py
     ```

4. **Run the analysis**
   - Open `task_1.ipynb` in Jupyter Notebook or Jupyter Lab:
     ```bash
     jupyter notebook task_1.ipynb
     ```
   - Execute all cells to reproduce the results and visualizations.

## Output
The notebook will generate:
- Statistical summaries of LGCI and LGWPI
- Yearly and team-level significance testing
- Top and bottom ranked teams in each metric
- Visualizations of performance trends

## Notes
- Ensure you have a stable internet connection when running `data_aq.py` as it scrapes live data sources.
- The scripts assume your Python version is 3.9+.

---

Author: Lance Santerre  
