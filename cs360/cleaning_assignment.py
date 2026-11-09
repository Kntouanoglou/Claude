"""
CS360 - Data Handling with Python
Assignment: Cleaning and Visualising Data

Data: export_english.csv (weekly case counts in Catalonia, 2020-2022, broken
down by region, sex, age group and socioeconomic index).

The CSV uses its own codes for missing information. When the file is loaded
they are turned into the three missing forms the assignment deals with:

    "Not available"            -> None
    socioeconomic_index == -1  -> NaN   (the file's own "unknown" code)
    population == 0            -> NaN   (a group cannot have 0 people)
    blank / whitespace cell    -> ""    (kept as an empty string)

Run:  python cleaning_assignment.py
Output: the printed matrices / counts, and plot1.png ... plot4.png
"""

import copy
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")  # save figures to files, no window needed
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "export_english.csv")

nan = float("nan")


# ---------------------------------------------------------------------------
# Task 1: clean the matrix
# ---------------------------------------------------------------------------
def is_missing(v):
    """True for None, NaN and empty / whitespace-only strings."""
    if v is None:  # check None first: math.isnan(None) raises TypeError
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def clean_matrix(matrix, fill=-1):
    """Return a NEW matrix in which every missing cell is replaced by `fill`.

    Works for any number of rows and columns (rows may even differ in length).
    Returns (cleaned, replaced) where `replaced` is a list of (row, col)
    positions that were filled in. The original matrix is not modified.
    """
    cleaned = copy.deepcopy(matrix)
    replaced = []
    for i, row in enumerate(cleaned):
        for j, value in enumerate(row):
            if is_missing(value):
                row[j] = fill
                replaced.append((i, j))
    return cleaned, replaced


# ---------------------------------------------------------------------------
# Loading the CSV into a list of lists
# ---------------------------------------------------------------------------
def to_number(text):
    """Convert a CSV string to int/float when possible, otherwise keep it."""
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        rows = [[to_number(cell) for cell in row] for row in reader]

    se = header.index("socioeconomic_index")
    pop = header.index("population")
    for row in rows:
        for j, value in enumerate(row):
            if isinstance(value, str) and value.strip() == "Not available":
                row[j] = None
        if row[se] == -1:
            row[se] = nan
        if row[pop] == 0:
            row[pop] = nan
    return header, rows


def show(matrix, title, limit=None):
    print(f"\n{title}")
    shown = matrix if limit is None else matrix[:limit]
    for row in shown:
        print("  ", row)
    if limit is not None and len(matrix) > limit:
        print(f"   ... ({len(matrix) - limit} more rows)")


# ---------------------------------------------------------------------------
# Task 2: plots
# ---------------------------------------------------------------------------
def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, name), dpi=200)
    plt.close()
    print("saved", name)


def make_plots(header, cleaned, replaced_rows):
    pop = header.index("population")
    cases = header.index("cases")
    se = header.index("socioeconomic_index")

    xs_all = [r[pop] for r in cleaned]
    ys_all = [r[cases] for r in cleaned]

    # rows whose x (population) or y (cases) was replaced
    plot_bad = {i for i, j in replaced_rows if j in (pop, cases)}
    good = [i for i in range(len(cleaned)) if i not in plot_bad]
    bad = sorted(plot_bad)

    # (a) all cleaned points
    plt.figure(figsize=(8, 5))
    plt.scatter(xs_all, ys_all, s=8, alpha=0.4, color="tab:blue",
                label="all points (cleaned)")
    plt.xscale("symlog", linthresh=10)  # symlog so x = -1 is still drawn
    plt.xlim(left=-3)
    plt.title("Cleaned data: population vs weekly cases")
    plt.xlabel("population of group (symlog scale)")
    plt.ylabel("weekly cases")
    plt.legend()
    savefig("plot1_cleaned.png")

    # (b) replaced points in a different colour / marker
    plt.figure(figsize=(8, 5))
    plt.scatter([xs_all[i] for i in good], [ys_all[i] for i in good],
                s=8, alpha=0.4, color="tab:blue", label="original observations")
    plt.scatter([xs_all[i] for i in bad], [ys_all[i] for i in bad],
                s=40, color="tab:red", marker="x",
                label=f"population replaced by -1 ({len(bad)})")
    plt.axvline(0, color="grey", lw=0.8, ls="--")
    plt.xscale("symlog", linthresh=10)
    plt.xlim(left=-3)
    plt.title("Population vs weekly cases, replaced values highlighted")
    plt.xlabel("population of group (symlog scale)")
    plt.ylabel("weekly cases")
    plt.legend()
    savefig("plot2_replaced_highlighted.png")

    # (c) only rows with no missing value at all
    any_bad = {i for i, _ in replaced_rows}
    valid = [i for i in range(len(cleaned)) if i not in any_bad]
    plt.figure(figsize=(8, 5))
    plt.scatter([xs_all[i] for i in valid], [ys_all[i] for i in valid],
                s=8, alpha=0.4, color="tab:green",
                label=f"complete rows only ({len(valid)})")
    plt.xscale("log")
    plt.title("Valid points only (rows with any missing value removed)")
    plt.xlabel("population of group (log scale)")
    plt.ylabel("weekly cases")
    plt.legend()
    savefig("plot3_valid_only.png")

    # extra: socioeconomic index vs cases per 100,000 people
    se_bad = {i for i, j in replaced_rows if j in (se, pop)}
    def rate(r):
        return r[cases] / r[pop] * 100_000

    plt.figure(figsize=(8, 5))
    g = [i for i in range(len(cleaned)) if i not in se_bad]
    b = sorted(se_bad)
    plt.scatter([cleaned[i][se] for i in g], [rate(cleaned[i]) for i in g],
                s=8, alpha=0.3, color="tab:blue", label="original observations")
    plt.scatter([cleaned[i][se] for i in b], [rate(cleaned[i]) for i in b],
                s=40, color="tab:red", marker="x",
                label=f"index and/or population replaced by -1 ({len(b)})")
    plt.yscale("symlog", linthresh=10)
    plt.xticks([-1, 1, 2, 3, 4])
    plt.title("Socioeconomic index vs cases per 100,000")
    plt.xlabel("socioeconomic index")
    plt.ylabel("cases per 100,000 (symlog scale)")
    plt.legend()
    savefig("plot4_socioeconomic_rate.png")


# ---------------------------------------------------------------------------
# Numbers used in the Task 3 report
# ---------------------------------------------------------------------------
def mean(v):
    return sum(v) / len(v)


def fit_line(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, sxy / math.sqrt(sxx * syy)


def summary(header, original, cleaned, replaced):
    pop = header.index("population")
    cases = header.index("cases")
    se = header.index("socioeconomic_index")
    bad_rows = {i for i, _ in replaced}
    valid = [i for i in range(len(cleaned)) if i not in bad_rows]

    print("\n--- statistics for the report ---")
    p_clean = [r[pop] for r in cleaned]
    p_valid = [cleaned[i][pop] for i in valid]
    s_clean = [r[se] for r in cleaned]
    s_valid = [cleaned[i][se] for i in valid]
    print(f"mean population: cleaned {mean(p_clean):.1f}, valid rows {mean(p_valid):.1f}")
    print(f"min population:  cleaned {min(p_clean)}, valid rows {min(p_valid)}")
    print(f"mean socioeconomic index: cleaned {mean(s_clean):.3f}, valid {mean(s_valid):.3f}")
    s_med = sorted(s_valid)[len(s_valid) // 2]
    print(f"median socioeconomic index (valid): {s_med}")

    c_all = [r[cases] for r in cleaned]
    print(f"cases: mean {mean(c_all):.2f}, max {max(c_all)}")

    m, c, r = fit_line(p_clean, c_all)
    print(f"line cases~population, cleaned: slope {m * 1000:.4f} per 1000 people, "
          f"intercept {c:.3f}, r = {r:.3f}")
    m, c, r = fit_line(p_valid, [cleaned[i][cases] for i in valid])
    print(f"line cases~population, valid:   slope {m * 1000:.4f} per 1000 people, "
          f"intercept {c:.3f}, r = {r:.3f}")

    rates = [r_[cases] / r_[pop] * 100_000 for r_ in cleaned]
    print(f"cases per 100k: cleaned min {min(rates):.0f}, mean {mean(rates):.1f}")
    rv = [rates[i] for i in valid]
    print(f"cases per 100k: valid   min {min(rv):.1f}, mean {mean(rv):.1f}")
    for k in (1, 2, 3, 4):
        sel = [rates[i] for i in valid if cleaned[i][se] == k]
        print(f"   index {k}: mean rate {mean(sel):.1f} per 100k  (n={len(sel)})")


def main():
    # Quick check on the example matrix from the handout (Task 1d: any shape)
    example = [
        [1.0, 2.1], [2.0, 3.9], [3.0, None], [4.0, 8.2], [None, 10.1],
        [6.0, 11.8], [7.0, nan], [8.0, 16.1], [9.0, ""], [10.0, 20.3],
        [nan, 22.0], [12.0, 23.9], [13.0, 26.2], [14.0, None], [15.0, 30.1],
    ]
    ex_clean, ex_rep = clean_matrix(example)
    show(example, "Handout example - original:")
    show(ex_clean, "Handout example - cleaned:")
    print(f"values replaced: {len(ex_rep)}")
    assert example[2][1] is None, "original must stay unchanged"

    # The CSV dataset
    header, data = load_csv(CSV_PATH)
    cleaned, replaced = clean_matrix(data, fill=-1)

    print(f"\nCSV: {len(data)} rows x {len(header)} columns")
    print("columns:", header)
    show(data, "Original matrix (first 5 rows):", limit=5)
    show(cleaned, "Cleaned matrix (first 5 rows):", limit=5)

    changed_rows = sorted({i for i, _ in replaced})
    print(f"\nRows that contained missing values ({len(changed_rows)}), first 5:")
    for i in changed_rows[:5]:
        print(f"  row {i}\n    original: {data[i]}\n    cleaned:  {cleaned[i]}")

    print(f"\nTotal values replaced: {len(replaced)} "
          f"in {len(changed_rows)} of {len(data)} rows")
    per_col = {}
    for _, j in replaced:
        per_col[header[j]] = per_col.get(header[j], 0) + 1
    for name, n in per_col.items():
        print(f"   {name:22s} {n}")

    # the original is untouched
    assert sum(is_missing(v) for row in data for v in row) == len(replaced)

    make_plots(header, cleaned, replaced)
    summary(header, data, cleaned, replaced)


if __name__ == "__main__":
    main()
