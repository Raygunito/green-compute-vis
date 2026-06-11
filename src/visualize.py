"""
Data visualisation for Global Data Center & AI Water/Electricity Usage dataset.
Outputs all charts to ../output/
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "data_center_hybrid.csv"
OUT  = BASE / "output"
OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["savefig.bbox"] = "tight"

df = pd.read_csv(DATA)

# ── Colour Palette ─────────────────────────────────────────────────────────
pal_cool  = {"Air Cooled": "#4C9F70", "Evaporative": "#D95F02", "Liquid Cooled": "#7570B3"}
pal_type  = {"Enterprise/Standard": "#1B9E77", "Colocation": "#D95F02", "Hyperscale/AI": "#7570B3"}
pal_stress = {"Low": "#4C9F70", "Medium": "#E6AB02", "High": "#D95F02"}


def save(fig, name: str):
    """Save figure as PNG and close it."""
    fig.savefig(OUT / f"{name}.png", facecolor="white", edgecolor="none")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# 1. YEARLY AGGREGATED TRENDS
# ═══════════════════════════════════════════════════════════════════════════
yearly = df.groupby("Year").agg(
    total_elec_mwh=("Daily_Electricity_Usage_MWh", "sum"),
    total_water_mgal=("Daily_Water_Usage_Gallons", "sum"),
    avg_pue=("PUE", "mean"),
    avg_wue=("WUE_L_per_kWh", "mean"),
    avg_cap_mw=("Estimated_Capacity_MW", "mean"),
    facilities=("Facility_ID", "nunique"),
).reset_index()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

# 1a – Total daily electricity
ax = axes[0]
ax.fill_between(yearly["Year"], yearly["total_elec_mwh"] / 1e6, alpha=0.3, color="#2196F3")
ax.plot(yearly["Year"], yearly["total_elec_mwh"] / 1e6, marker="o", color="#2196F3", linewidth=2)
ax.set_title("Total Daily Electricity Usage")
ax.set_ylabel("Million MWh")
ax.set_xlabel("Year")

# 1b – Total daily water
ax = axes[1]
ax.fill_between(yearly["Year"], yearly["total_water_mgal"] / 1e9, alpha=0.3, color="#4CAF50")
ax.plot(yearly["Year"], yearly["total_water_mgal"] / 1e9, marker="o", color="#4CAF50", linewidth=2)
ax.set_title("Total Daily Water Usage")
ax.set_ylabel("Billion Gallons")
ax.set_xlabel("Year")

# 1c – Average PUE
ax = axes[2]
ax.plot(yearly["Year"], yearly["avg_pue"], marker="s", color="#E91E63", linewidth=2)
ax.set_title("Average PUE (lower = better)")
ax.set_ylabel("PUE")
ax.set_xlabel("Year")
ax.invert_yaxis()

# 1d – Average WUE
ax = axes[3]
ax.plot(yearly["Year"], yearly["avg_wue"], marker="s", color="#FF9800", linewidth=2)
ax.set_title("Average WUE (L/kWh)")
ax.set_ylabel("WUE (L/kWh)")
ax.set_xlabel("Year")

# 1e – Average Capacity
ax = axes[4]
ax.bar(yearly["Year"], yearly["avg_cap_mw"], color="#9C27B0", alpha=0.7)
ax.set_title("Average Facility Capacity")
ax.set_ylabel("MW")
ax.set_xlabel("Year")

# 1f – Unique Facilities
ax = axes[5]
ax.fill_between(yearly["Year"], yearly["facilities"], alpha=0.3, color="#607D8B")
ax.plot(yearly["Year"], yearly["facilities"], marker="D", color="#607D8B", linewidth=2)
ax.set_title("Unique Facilities per Year")
ax.set_ylabel("Count")
ax.set_xlabel("Year")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

fig.suptitle("Yearly Aggregated Trends (2019–2025)", fontsize=16, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "01_yearly_trends")


# ═══════════════════════════════════════════════════════════════════════════
# 2. COOLING SYSTEM COMPARISON
# ═══════════════════════════════════════════════════════════════════════════
cool_agg = df.groupby("Cooling_System_Type").agg(
    avg_pue=("PUE", "mean"),
    avg_wue=("WUE_L_per_kWh", "mean"),
    avg_elec=("Daily_Electricity_Usage_MWh", "mean"),
    avg_water=("Daily_Water_Usage_Gallons", "mean"),
    count=("Facility_ID", "nunique"),
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for ax, col, title, ylab in [
    (axes[0], "avg_pue", "Avg PUE by Cooling Type", "PUE"),
    (axes[1], "avg_wue", "Avg WUE by Cooling Type", "WUE (L/kWh)"),
    (axes[2], "avg_elec", "Avg Daily Electricity by Cooling Type", "MWh"),
    (axes[3], "avg_water", "Avg Daily Water by Cooling Type", "Gallons"),
]:
    bars = ax.bar(cool_agg["Cooling_System_Type"], cool_agg[col],
                  color=[pal_cool[t] for t in cool_agg["Cooling_System_Type"]], alpha=0.85, edgecolor="white")
    ax.set_title(title)
    ax.set_ylabel(ylab)
    ax.set_xlabel("")
    for bar, val in zip(bars, cool_agg[col]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_height() * 0.01,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("Cooling System Type Comparison", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "02_cooling_comparison")


# ═══════════════════════════════════════════════════════════════════════════
# 3. FACILITY TYPE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
type_agg = df.groupby("Facility_Type").agg(
    avg_pue=("PUE", "mean"),
    avg_wue=("WUE_L_per_kWh", "mean"),
    avg_cap=("Estimated_Capacity_MW", "mean"),
    avg_elec=("Daily_Electricity_Usage_MWh", "mean"),
    avg_water=("Daily_Water_Usage_Gallons", "mean"),
    count=("Facility_ID", "nunique"),
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

metrics = [
    ("avg_pue", "Avg PUE by Facility Type", "PUE"),
    ("avg_wue", "Avg WUE by Facility Type", "WUE (L/kWh)"),
    ("avg_cap", "Avg Capacity by Facility Type", "MW"),
    ("avg_elec", "Avg Daily Electricity by Facility Type", "MWh"),
]
for ax, (col, title, ylab) in zip(axes, metrics):
    bars = ax.bar(type_agg["Facility_Type"], type_agg[col],
                  color=[pal_type[t] for t in type_agg["Facility_Type"]], alpha=0.85, edgecolor="white")
    ax.set_title(title)
    ax.set_ylabel(ylab)
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=15)
    for bar, val in zip(bars, type_agg[col]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_height() * 0.01,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("Facility Type Analysis", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "03_facility_type")


# ═══════════════════════════════════════════════════════════════════════════
# 4. WATER STRESS TIER ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
stress_agg = df.groupby("Surrounding_Water_Stress_Tier").agg(
    avg_pue=("PUE", "mean"),
    avg_wue=("WUE_L_per_kWh", "mean"),
    avg_water=("Daily_Water_Usage_Gallons", "mean"),
    avg_elec=("Daily_Electricity_Usage_MWh", "mean"),
    count=("Facility_ID", "nunique"),
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

stress_metrics = [
    ("avg_pue", "Avg PUE by Water Stress Tier", "PUE"),
    ("avg_wue", "Avg WUE by Water Stress Tier", "WUE (L/kWh)"),
    ("avg_water", "Avg Daily Water by Water Stress Tier", "Gallons"),
    ("avg_elec", "Avg Daily Electricity by Water Stress Tier", "MWh"),
]
for ax, (col, title, ylab) in zip(axes, stress_metrics):
    order = ["Low", "Medium", "High"]
    bars = ax.bar(order, [stress_agg.set_index("Surrounding_Water_Stress_Tier").loc[o, col] for o in order],
                  color=[pal_stress[o] for o in order], alpha=0.85, edgecolor="white")
    ax.set_title(title)
    ax.set_ylabel(ylab)
    ax.set_xlabel("")
    for bar, val in zip(bars, [stress_agg.set_index("Surrounding_Water_Stress_Tier").loc[o, col] for o in order]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_height() * 0.01,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("Water Stress Tier Analysis", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "04_water_stress")


# ═══════════════════════════════════════════════════════════════════════════
# 5. TOP 15 COUNTRIES
# ═══════════════════════════════════════════════════════════════════════════
country_agg = df.groupby("Country").agg(
    total_elec=("Daily_Electricity_Usage_MWh", "sum"),
    total_water=("Daily_Water_Usage_Gallons", "sum"),
    avg_pue=("PUE", "mean"),
    facilities=("Facility_ID", "nunique"),
).reset_index()

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Top 15 electricity
top_elec = country_agg.nlargest(15, "total_elec")
ax = axes[0][0]
bars = ax.barh(top_elec["Country"][::-1], top_elec["total_elec"][::-1] / 1e6, color="#2196F3", alpha=0.8)
ax.set_title("Top 15 Countries — Total Daily Electricity")
ax.set_xlabel("Million MWh")
for bar, val in zip(bars, top_elec["total_elec"][::-1] / 1e6):
    ax.text(bar.get_width() + bar.get_width() * 0.005, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}", va="center", fontsize=8)

# Top 15 water
top_water = country_agg.nlargest(15, "total_water")
ax = axes[0][1]
bars = ax.barh(top_water["Country"][::-1], top_water["total_water"][::-1] / 1e9, color="#4CAF50", alpha=0.8)
ax.set_title("Top 15 Countries — Total Daily Water")
ax.set_xlabel("Billion Gallons")
for bar, val in zip(bars, top_water["total_water"][::-1] / 1e9):
    ax.text(bar.get_width() + bar.get_width() * 0.005, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}", va="center", fontsize=8)

# Avg PUE by country (top 15 by facility count)
top_by_fac = country_agg.nlargest(15, "facilities")
ax = axes[1][0]
bars = ax.barh(top_by_fac["Country"][::-1], top_by_fac["avg_pue"][::-1], color="#E91E63", alpha=0.8)
ax.set_title("Avg PUE — Top 15 Countries by Facility Count (lower = better)")
ax.set_xlabel("PUE")
for bar, val in zip(bars, top_by_fac["avg_pue"][::-1]):
    ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=8)

# Facilities per country (top 15)
ax = axes[1][1]
bars = ax.barh(top_by_fac["Country"][::-1], top_by_fac["facilities"][::-1], color="#607D8B", alpha=0.8)
ax.set_title("Facility Count — Top 15 Countries")
ax.set_xlabel("Unique Facilities")
for bar, val in zip(bars, top_by_fac["facilities"][::-1]):
    ax.text(bar.get_width() + bar.get_width() * 0.005, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", fontsize=8)

fig.suptitle("Country-Level Analysis", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "05_top_countries")


# ═══════════════════════════════════════════════════════════════════════════
# 6. CORRELATION HEATMAP
# ═══════════════════════════════════════════════════════════════════════════
num_cols = ["Estimated_Capacity_MW", "PUE", "WUE_L_per_kWh",
            "Daily_Electricity_Usage_MWh", "Daily_Water_Usage_Gallons"]
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, mask=mask, annot=True, fmt=".3f", cmap="RdBu_r", center=0,
            square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1)
ax.set_title("Correlation Heatmap — Numeric Features", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "06_correlation_heatmap")


# ═══════════════════════════════════════════════════════════════════════════
# 7. DISTRIBUTIONS
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

dist_plots = [
    ("PUE", "#E91E63", "PUE Distribution"),
    ("WUE_L_per_kWh", "#FF9800", "WUE Distribution (L/kWh)"),
    ("Estimated_Capacity_MW", "#9C27B0", "Capacity Distribution (MW)"),
    ("Daily_Electricity_Usage_MWh", "#2196F3", "Daily Electricity Distribution (MWh)"),
    ("Daily_Water_Usage_Gallons", "#4CAF50", "Daily Water Distribution (Gallons)"),
]
for i, (col, color, title) in enumerate(dist_plots):
    ax = axes[i]
    data_col = df[col]
    ax.hist(data_col, bins=80, color=color, alpha=0.7, edgecolor="white", linewidth=0.3)
    ax.set_title(title)
    ax.set_ylabel("Frequency")
    # Add mean line
    mean_val = data_col.mean()
    ax.axvline(mean_val, color="black", linestyle="--", linewidth=1.2, label=f"Mean: {mean_val:.2f}")
    ax.legend(fontsize=8)

# Hide extra subplot
axes[5].set_visible(False)

fig.suptitle("Distributions of Key Numeric Features", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "07_distributions")


# ═══════════════════════════════════════════════════════════════════════════
# 8. SCATTER: Capacity vs Electricity (colored by Facility Type)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 8))
sample = df.sample(n=min(5000, len(df)), random_state=42)
for ftype in sample["Facility_Type"].unique():
    subset = sample[sample["Facility_Type"] == ftype]
    ax.scatter(subset["Estimated_Capacity_MW"], subset["Daily_Electricity_Usage_MWh"],
               c=pal_type.get(ftype, "#999999"), label=ftype, alpha=0.5, s=20, edgecolors="none")
ax.set_xlabel("Estimated Capacity (MW)")
ax.set_ylabel("Daily Electricity Usage (MWh)")
ax.set_title("Capacity vs Daily Electricity Usage (5k sample)")
ax.legend(title="Facility Type", markerscale=2)
fig.tight_layout()
save(fig, "08_capacity_vs_electricity")


# ═══════════════════════════════════════════════════════════════════════════
# 9. SCATTER: PUE vs WUE (colored by Cooling Type)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 8))
sample2 = df.sample(n=min(5000, len(df)), random_state=42)
for ctype in sample2["Cooling_System_Type"].unique():
    subset = sample2[sample2["Cooling_System_Type"] == ctype]
    ax.scatter(subset["PUE"], subset["WUE_L_per_kWh"],
               c=pal_cool.get(ctype, "#999999"), label=ctype, alpha=0.5, s=20, edgecolors="none")
ax.set_xlabel("PUE")
ax.set_ylabel("WUE (L/kWh)")
ax.set_title("PUE vs WUE (5k sample)")
ax.legend(title="Cooling Type", markerscale=2)
fig.tight_layout()
save(fig, "09_pue_vs_wue")


# ═══════════════════════════════════════════════════════════════════════════
# 10. BOX PLOTS — PUE by Cooling Type & Facility Type
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# PUE by Cooling Type
ax = axes[0]
order_cool = ["Air Cooled", "Evaporative", "Liquid Cooled"]
sns.boxplot(data=df, x="Cooling_System_Type", y="PUE", order=order_cool,
            hue="Cooling_System_Type", palette=pal_cool, legend=False,
            ax=ax, linewidth=0.8, fliersize=1.5)
ax.set_title("PUE by Cooling System Type")
ax.set_xlabel("")

# PUE by Facility Type
ax = axes[1]
order_ftype = ["Enterprise/Standard", "Colocation", "Hyperscale/AI"]
sns.boxplot(data=df, x="Facility_Type", y="PUE", order=order_ftype,
            hue="Facility_Type", palette=pal_type, legend=False,
            ax=ax, linewidth=0.8, fliersize=1.5)
ax.set_title("PUE by Facility Type")
ax.set_xlabel("")

fig.suptitle("PUE Distributions (Box Plots)", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "10_pue_boxplots")


# ═══════════════════════════════════════════════════════════════════════════
# 11. PUE TREND OVER TIME BY COOLING TYPE
# ═══════════════════════════════════════════════════════════════════════════
pue_trend = df.groupby(["Year", "Cooling_System_Type"])["PUE"].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 7))
for ctype in ["Air Cooled", "Evaporative", "Liquid Cooled"]:
    subset = pue_trend[pue_trend["Cooling_System_Type"] == ctype]
    ax.plot(subset["Year"], subset["PUE"], marker="o", linewidth=2.5,
            color=pal_cool[ctype], label=ctype, markersize=8)
ax.set_xlabel("Year")
ax.set_ylabel("Average PUE")
ax.set_title("PUE Trend by Cooling System Type (2019–2025)")
ax.legend(title="Cooling Type")
ax.invert_yaxis()
fig.tight_layout()
save(fig, "11_pue_trend_by_cooling")


# ═══════════════════════════════════════════════════════════════════════════
# 12. STACKED AREA — Facility Types Over Time
# ═══════════════════════════════════════════════════════════════════════════
ftype_year = df.groupby(["Year", "Facility_Type"])["Facility_ID"].nunique().reset_index()
ftype_pivot = ftype_year.pivot(index="Year", columns="Facility_Type", values="Facility_ID").fillna(0)

fig, ax = plt.subplots(figsize=(12, 7))
ax.stackplot(ftype_pivot.index,
             ftype_pivot.get("Enterprise/Standard", [0] * len(ftype_pivot)),
             ftype_pivot.get("Colocation", [0] * len(ftype_pivot)),
             ftype_pivot.get("Hyperscale/AI", [0] * len(ftype_pivot)),
             labels=["Enterprise/Standard", "Colocation", "Hyperscale/AI"],
             colors=[pal_type["Enterprise/Standard"], pal_type["Colocation"], pal_type["Hyperscale/AI"]],
             alpha=0.8)
ax.set_title("Facility Count by Type Over Time")
ax.set_xlabel("Year")
ax.set_ylabel("Unique Facilities")
ax.legend(loc="upper left")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
fig.tight_layout()
save(fig, "12_facility_type_trend")


# ═══════════════════════════════════════════════════════════════════════════
# 13. WATER USAGE: Evaporative vs Other Cooling (scatter by water stress)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 8))
sample3 = df.sample(n=min(5000, len(df)), random_state=42)
for stress in ["Low", "Medium", "High"]:
    subset = sample3[sample3["Surrounding_Water_Stress_Tier"] == stress]
    ax.scatter(subset["Daily_Electricity_Usage_MWh"], subset["Daily_Water_Usage_Gallons"],
               c=pal_stress[stress], label=stress, alpha=0.5, s=20, edgecolors="none")
ax.set_xlabel("Daily Electricity Usage (MWh)")
ax.set_ylabel("Daily Water Usage (Gallons)")
ax.set_title("Electricity vs Water Usage by Water Stress Tier (5k sample)")
ax.legend(title="Water Stress Tier", markerscale=2)
fig.tight_layout()
save(fig, "13_elec_vs_water_by_stress")


# ═══════════════════════════════════════════════════════════════════════════
# 14. PIE CHARTS — Composition
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Facility Type
ftype_counts = df["Facility_Type"].value_counts()
axes[0].pie(ftype_counts.values, labels=ftype_counts.index, autopct="%1.1f%%",
            colors=[pal_type.get(t, "#999") for t in ftype_counts.index],
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1})
axes[0].set_title("Facility Type Distribution")

# Cooling Type
cool_counts = df["Cooling_System_Type"].value_counts()
axes[1].pie(cool_counts.values, labels=cool_counts.index, autopct="%1.1f%%",
            colors=[pal_cool.get(t, "#999") for t in cool_counts.index],
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1})
axes[1].set_title("Cooling System Distribution")

# Water Stress Tier
stress_counts = df["Surrounding_Water_Stress_Tier"].value_counts()
axes[2].pie(stress_counts.values, labels=stress_counts.index, autopct="%1.1f%%",
            colors=[pal_stress.get(t, "#999") for t in stress_counts.index],
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1})
axes[2].set_title("Water Stress Tier Distribution")

fig.suptitle("Dataset Composition", fontsize=16, fontweight="bold")
fig.tight_layout()
save(fig, "14_composition_pies")


print(f"✅ All 14 visualisations saved to: {OUT.resolve()}")
print(f"   Files: {sorted([f.name for f in OUT.glob('*.png')])}")
