"""Plotly charts of observed counts; no continuous multi-year series."""
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard_data import COUNT

PALETTE = ["#087F8C", "#C98936", "#316B9C", "#AD5D70", "#677D47", "#715F96"]


def polish(fig, title, height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#153348")),
        font=dict(family="Arial, sans-serif", size=13, color="#334B5B"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=16, t=60, b=45), height=height,
        legend=dict(orientation="h", y=1.08, x=0), dragmode=False,
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#E6EDF0", automargin=True)
    return fig


def ranked_bar(table, label, title, top=None):
    data = table.sort_values(COUNT, ascending=False, kind="stable")
    if top:
        data = data.head(top)
    fig = px.bar(data, x=COUNT, y=label, orientation="h", text=COUNT,
                 color_discrete_sequence=PALETTE,
                 custom_data=["share_of_selection_pct"],
                 labels={COUNT: "Source record occurrences | سجلات المصدر", label: ""})
    fig.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>%{x:,} source occurrences<br>%{customdata[0]:.1f}% of filtered selection<extra></extra>")
    fig.update_yaxes(categoryorder="total ascending")
    return polish(fig, title, max(330, min(760, 95 + 38 * len(data))))


def period_bar(table, title):
    # Categorical month labels deliberately cannot imply a continuous annual series.
    data = table.sort_values("period_id")
    fig = px.bar(data, x="period_id", y=COUNT, text=COUNT, color_discrete_sequence=PALETTE,
                 labels={COUNT: "Source record occurrences", "period_id": "Supplied reporting month"})
    fig.update_traces(texttemplate="%{text:,}", hovertemplate="%{x}<br>%{y:,} source occurrences<extra></extra>")
    fig.update_xaxes(type="category")
    return polish(fig, title)


def coverage_heatmap(matrix, governorates, year):
    """Draw availability metadata only; missing observations are never zero counts."""
    statuses = {"outside_source_scope": 0, "not_provided": 1, "future_period": 2, "observed": 3}
    labels = {"outside_source_scope": "Outside source scope", "not_provided": "Not supplied",
              "future_period": "After audit reporting cutoff", "observed": "Supplied records"}
    z, hover, y = [], [], []
    for row in governorates.itertuples():
        subset = matrix[matrix.governorate_id.eq(row.governorate_id) & matrix.year.eq(year)].set_index("month")
        z.append([statuses[subset.loc[m, "availability_status"]] for m in range(1, 13)])
        hover.append([f"{row.governorate_en} · {year}-{m:02d}<br>{labels[subset.loc[m, 'availability_status']]}"
                      + (f"<br>{int(subset.loc[m, COUNT]):,} source occurrences" if subset.loc[m, 'availability_status'] == 'observed' else "<br>Count unavailable")
                      for m in range(1, 13)])
        y.append(f"{row.governorate_en} | {row.governorate_ar}")
    colors = ["#E1E6EB", "#F4D9AC", "#CBD4E8", "#087F8C"]
    scale = [[i / 4, c] for i, c in enumerate(colors)] + [[(i + 1) / 4 - 0.00001, c] for i, c in enumerate(colors)]
    fig = go.Figure(go.Heatmap(z=z, x=[f"{m:02d}" for m in range(1, 13)], y=y, text=hover,
                             zmin=-0.5, zmax=3.5, colorscale=sorted(scale), showscale=False,
                             xgap=3, ygap=3, hovertemplate="%{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return polish(fig, f"{year} · Supplied coverage by governorate", 540)
