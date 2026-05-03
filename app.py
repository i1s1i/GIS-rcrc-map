import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd
import json
import os

# ─────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────
COLORS = {
    "bg":      "#0A0E17",
    "card":    "#111827",
    "border":  "#1F2937",
    "primary": "#D4A843",
    "text":    "#F1F5F9",
    "muted":   "#94A3B8",
    "sector": {
        "شمال": "#3B82F6",
        "شرق":  "#10B981",
        "جنوب": "#F59E0B",
        "غرب":  "#8B5CF6",
        "وسط":  "#EF4444",
    },
    "theme": {
        "01": "#3B82F6",   # السكان
        "02": "#10B981",   # الإسكان
        "03": "#F59E0B",   # الاقتصاد
        "05": "#8B5CF6",   # الثقافة
        "07": "#EF4444",   # النقل
        "09": "#D4A843",   # الرياض عالمياً
    }
}
SECTOR_ICONS = {"شمال": "⬆️", "شرق": "➡️", "جنوب": "⬇️", "غرب": "⬅️", "وسط": "🎯"}

THEME_ICONS = {
    "01": "👥", "02": "🏠", "03": "💼",
    "05": "🎭", "07": "🚇", "09": "🌍",
}

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df_meta = pd.read_csv("datasets.csv")
df_meta["default.records_count"] = pd.to_numeric(
    df_meta["default.records_count"], errors="coerce").fillna(0).astype(int)

with open("data/riyadh_districts.geojson", "r", encoding="utf-8") as f:
    riyadh_geo = json.load(f)

df_districts = pd.DataFrame([feat["properties"] for feat in riyadh_geo["features"]])

# ─────────────────────────────────────────────
# PRE-BUILD DATASET POPUP CONTENT (injected into each district popup)
# ─────────────────────────────────────────────
def make_dataset_popup_html(district_name, district_name_en, sector):
    """Generate rich HTML popup with all datasets organized by theme."""
    sec_color = COLORS["sector"].get(sector, "#888")

    # Group datasets by theme
    themes_grouped = {}
    for _, row in df_meta.iterrows():
        theme_raw = str(row.get("default.theme", "") or "")
        # Take first theme if multiple
        theme_key = theme_raw.split(",")[0].strip()[:2]
        if theme_key not in themes_grouped:
            themes_grouped[theme_key] = []
        themes_grouped[theme_key].append(row)

    # Build theme sections
    theme_sections = ""
    for theme_key, rows in sorted(themes_grouped.items()):
        t_color = COLORS["theme"].get(theme_key, "#888")
        t_icon  = THEME_ICONS.get(theme_key, "📂")
        # Use full theme name from first row
        theme_label = str(rows[0].get("default.theme", "") or "").split(",")[0].strip()

        datasets_html = ""
        for row in rows:
            title   = str(row["default.title"])
            count   = int(row["default.records_count"])
            keyword = str(row.get("default.keyword", "") or "")
            dataset_id = str(row.get("datasetid", "") or "")
            link = f"https://data.rcrc.gov.sa/explore/dataset/{dataset_id}/" if dataset_id else "#"

            # Keyword badges
            kw_badges = ""
            for kw in keyword.split(",")[:3]:
                kw = kw.strip()
                if kw:
                    kw_badges += f'<span style="background:rgba(255,255,255,0.08);border-radius:4px;padding:1px 5px;font-size:9px;margin-left:3px">{kw}</span>'

            datasets_html += f"""
            <div style="padding:6px 8px;margin:4px 0;background:rgba(255,255,255,0.04);
                        border-radius:6px;border-right:2px solid {t_color}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="font-size:11px;color:#F1F5F9;font-weight:500;flex:1;margin-left:6px">{title}</div>
                <div style="font-size:10px;color:{t_color};white-space:nowrap;font-weight:bold">{count:,}</div>
              </div>
              <div style="margin-top:3px">{kw_badges}</div>
            </div>"""

        theme_sections += f"""
        <div style="margin-bottom:10px">
          <div style="display:flex;align-items:center;margin-bottom:5px">
            <span style="background:{t_color};border-radius:4px;padding:2px 8px;
                         font-size:11px;font-weight:bold;color:#fff">
              {t_icon} {theme_label}
            </span>
            <span style="color:{t_color};font-size:10px;margin-right:8px">
              ({len(rows)} مجموعة)
            </span>
          </div>
          {datasets_html}
        </div>"""

    popup_html = f"""
    <div dir='rtl' style='
        font-family: Tahoma, Arial, sans-serif;
        width: 380px;
        max-height: 500px;
        overflow-y: auto;
        background: #111827;
        color: #F1F5F9;
        border-radius: 10px;
        font-size: 12px;
        scrollbar-width: thin;
        scrollbar-color: #374151 #111827;
    '>
      <!-- Header -->
      <div style='
        background: linear-gradient(135deg, {sec_color}cc, {sec_color}66);
        padding: 12px 16px;
        border-radius: 10px 10px 0 0;
        border-bottom: 1px solid {sec_color}44;
      '>
        <div style='font-size:18px;font-weight:bold'>🏘️ {district_name}</div>
        {'<div style="font-size:11px;opacity:0.8;margin-top:2px">' + district_name_en + '</div>' if district_name_en else ''}
        <div style='margin-top:6px;display:flex;gap:8px'>
          <span style='background:rgba(0,0,0,0.25);border-radius:4px;padding:2px 8px;font-size:11px'>
            {SECTOR_ICONS.get(sector,"")} قطاع {sector}
          </span>
          <span style='background:rgba(0,0,0,0.25);border-radius:4px;padding:2px 8px;font-size:11px'>
            📊 {len(df_meta)} مجموعة بيانات
          </span>
        </div>
      </div>

      <!-- Datasets by Theme -->
      <div style='padding: 12px 14px'>
        <div style='color:#D4A843;font-weight:bold;margin-bottom:10px;font-size:13px'>
          📂 مجموعات البيانات المتاحة — الرياض
        </div>
        <div style='color:#94A3B8;font-size:10px;margin-bottom:10px'>
          البيانات التالية متاحة لمدينة الرياض من منصة الهيئة الملكية للبيانات المفتوحة
        </div>
        {theme_sections}
      </div>
    </div>"""
    return popup_html


# Pre-generate popup per district (expensive once, cached)
print("Pre-generating district popups...")
district_popups = {}
for feat in riyadh_geo["features"]:
    props = feat["properties"]
    did = props.get("id")
    district_popups[did] = make_dataset_popup_html(
        district_name=props.get("name_ar", "حي"),
        district_name_en=props.get("name_en", ""),
        sector=props.get("sector", ""),
    )
print(f"Generated {len(district_popups)} popups.")


# ─────────────────────────────────────────────
# BUILD FOLIUM MAP
# ─────────────────────────────────────────────
def build_map(selected_sectors=None):
    if selected_sectors is None:
        selected_sectors = list(COLORS["sector"].keys())

    m = folium.Map(
        location=[24.7136, 46.6753],
        zoom_start=11,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    sector_groups = {}
    for s in COLORS["sector"]:
        fg = folium.FeatureGroup(
            name=f"{SECTOR_ICONS.get(s,'')} قطاع {s}",
            show=(s in selected_sectors)
        )
        sector_groups[s] = fg
        fg.add_to(m)

    for feat in riyadh_geo["features"]:
        props  = feat["properties"]
        sector = props["sector"]
        if sector not in selected_sectors:
            continue

        color   = COLORS["sector"].get(sector, "#888")
        did     = props.get("id")
        popup_h = district_popups.get(did, "<p>لا توجد بيانات</p>")
        name_ar = props.get("name_ar", "حي")

        try:
            folium.GeoJson(
                feat,
                style_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": c,
                    "weight": 1.5,
                    "fillOpacity": 0.3,
                },
                highlight_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": "#FFFFFF",
                    "weight": 3,
                    "fillOpacity": 0.6,
                },
                tooltip=folium.Tooltip(
                    f"<span style='font-family:Tahoma;font-size:13px'>"
                    f"<b>🏘️ {name_ar}</b> — قطاع {sector}</span>",
                    sticky=True,
                ),
                popup=folium.Popup(popup_h, max_width=400),
            ).add_to(sector_groups[sector])
        except Exception:
            pass

    # Map legend
    legend_html = """
    <div style="position:fixed;bottom:30px;right:10px;
        background:rgba(17,24,39,0.93);border:1px solid #1F2937;
        border-radius:10px;padding:12px 16px;z-index:9999;
        font-family:Tahoma,Arial;direction:rtl;font-size:12px;color:#F1F5F9">
        <div style="font-weight:bold;margin-bottom:8px;color:#D4A843">🗺️ القطاعات</div>
    """
    for s, c in COLORS["sector"].items():
        legend_html += (
            f'<div style="margin:4px 0">'
            f'<span style="display:inline-block;width:12px;height:12px;background:{c};'
            f'border-radius:3px;margin-left:6px;vertical-align:middle"></span>'
            f'{SECTOR_ICONS.get(s,"")} {s}</div>'
        )
    legend_html += (
        '<div style="margin-top:8px;color:#94A3B8;font-size:10px">'
        '💡 اضغط على الحي لرؤية البيانات</div></div>'
    )
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl(collapsed=False, position="topleft").add_to(m)
    return m.get_root().render()


# ─────────────────────────────────────────────
# DASH LAYOUT
# ─────────────────────────────────────────────
app = dash.Dash(__name__, title="داشبورد الرياض التفاعلي")

all_sectors = list(COLORS["sector"].keys())
CARD = {
    "backgroundColor": COLORS["card"],
    "borderRadius": "12px",
    "padding": "20px",
    "border": f"1px solid {COLORS['border']}",
    "flex": "1",
    "textAlign": "center",
    "minWidth": "130px",
}

def kpi(label, value, color=COLORS["text"]):
    return html.Div([
        html.Div(label, style={"color": COLORS["muted"], "fontSize": "11px", "marginBottom": "5px"}),
        html.Div(str(value), style={"color": color, "fontSize": "26px", "fontWeight": "bold"}),
    ], style=CARD)


app.layout = html.Div(
    dir="rtl",
    style={"fontFamily": "Tahoma, Arial, sans-serif",
           "backgroundColor": COLORS["bg"], "color": COLORS["text"],
           "minHeight": "100vh", "padding": "16px"},
    children=[
        # Header
        html.Div([
            html.H1("🏙️ داشبورد مدينة الرياض التفاعلي",
                    style={"color": COLORS["primary"], "margin": 0, "fontSize": "20px"}),
            html.Div("اضغط على أي حي لرؤية مجموعات البيانات المتاحة",
                     style={"color": COLORS["muted"], "fontSize": "12px", "marginTop": "3px"}),
        ], style={"marginBottom": "14px"}),

        # KPIs
        html.Div([
            kpi("الأحياء", len(df_districts), COLORS["primary"]),
            kpi("⬆️ شمال",  len(df_districts[df_districts.sector == "شمال"]), COLORS["sector"]["شمال"]),
            kpi("➡️ شرق",   len(df_districts[df_districts.sector == "شرق"]),  COLORS["sector"]["شرق"]),
            kpi("⬇️ جنوب",  len(df_districts[df_districts.sector == "جنوب"]), COLORS["sector"]["جنوب"]),
            kpi("⬅️ غرب",   len(df_districts[df_districts.sector == "غرب"]),  COLORS["sector"]["غرب"]),
            kpi("🎯 وسط",   len(df_districts[df_districts.sector == "وسط"]),  COLORS["sector"]["وسط"]),
            kpi("📂 مجموعات بيانات", len(df_meta), COLORS["primary"]),
        ], style={"display": "flex", "gap": "10px", "marginBottom": "14px", "flexWrap": "wrap"}),

        # Body
        html.Div([
            # Sidebar
            html.Div([
                html.Div("🔘 تصفية القطاعات",
                         style={"color": COLORS["primary"], "fontWeight": "bold",
                                "marginBottom": "12px", "fontSize": "13px"}),
                dcc.Checklist(
                    id="sector-filter",
                    options=[{"label": f" {SECTOR_ICONS.get(s,'')} {s}", "value": s}
                             for s in all_sectors],
                    value=all_sectors,
                    labelStyle={"display": "block", "margin": "8px 0",
                                "cursor": "pointer", "fontSize": "13px"},
                    inputStyle={"marginLeft": "8px"},
                ),
                html.Hr(style={"borderColor": COLORS["border"], "margin": "14px 0"}),

                # Datasets summary list
                html.Div("📊 ملخص البيانات المتاحة",
                         style={"color": COLORS["primary"], "fontWeight": "bold",
                                "marginBottom": "10px", "fontSize": "13px"}),
                *[
                    html.Div([
                        html.Div(f"{THEME_ICONS.get(str(row['default.theme'])[:2], '📂')} "
                                 f"{str(row['default.theme']).split(',')[0][:35]}",
                                 style={"fontSize": "10px", "color": COLORS["muted"],
                                        "marginBottom": "2px"}),
                        html.Div(row["default.title"][:42] + "…"
                                 if len(row["default.title"]) > 42 else row["default.title"],
                                 style={"fontSize": "11px", "color": COLORS["text"]}),
                        html.Div(f"{row['default.records_count']:,} سجل",
                                 style={"fontSize": "10px", "color": COLORS["primary"],
                                        "fontWeight": "bold"}),
                    ], style={
                        "padding": "7px 9px", "borderRadius": "6px",
                        "backgroundColor": COLORS["bg"], "marginBottom": "5px",
                        "border": f"1px solid {COLORS['border']}",
                        "borderRight": f"3px solid {COLORS['theme'].get(str(row['default.theme'])[:2], '#888')}",
                    })
                    for _, row in df_meta.iterrows()
                ],
            ], style={
                "width": "230px", "flexShrink": 0,
                "backgroundColor": COLORS["card"],
                "borderRadius": "12px", "padding": "14px",
                "border": f"1px solid {COLORS['border']}",
                "overflowY": "auto", "maxHeight": "670px",
            }),

            # Map + charts
            html.Div([
                # Map card
                html.Div([
                    html.Div("🗺️ خريطة أحياء الرياض — اضغط على حي لرؤية البيانات",
                             style={"color": COLORS["primary"], "fontWeight": "bold",
                                    "marginBottom": "8px", "fontSize": "13px"}),
                    html.Iframe(
                        id="map-iframe",
                        srcDoc=build_map(),
                        width="100%", height="520px",
                        style={"border": "none", "borderRadius": "8px"},
                    ),
                ], style={
                    "backgroundColor": COLORS["card"], "borderRadius": "12px",
                    "padding": "14px", "border": f"1px solid {COLORS['border']}",
                    "marginBottom": "12px",
                }),

                # Charts row
                html.Div([
                    html.Div([
                        dcc.Graph(id="sector-pie", config={"displayModeBar": False},
                                  style={"height": "230px"})
                    ], style={
                        "backgroundColor": COLORS["card"], "borderRadius": "12px",
                        "padding": "10px", "border": f"1px solid {COLORS['border']}",
                        "flex": "1",
                    }),
                    html.Div([
                        dcc.Graph(id="datasets-bar", config={"displayModeBar": False},
                                  style={"height": "230px"})
                    ], style={
                        "backgroundColor": COLORS["card"], "borderRadius": "12px",
                        "padding": "10px", "border": f"1px solid {COLORS['border']}",
                        "flex": "2",
                    }),
                ], style={"display": "flex", "gap": "12px"}),
            ], style={"flex": "1", "minWidth": 0}),
        ], style={"display": "flex", "gap": "12px", "alignItems": "flex-start"}),
    ]
)


# ─────────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────────
@callback(Output("map-iframe", "srcDoc"), Input("sector-filter", "value"))
def update_map(sectors):
    return build_map(sectors or [])


@callback(Output("sector-pie", "figure"), Input("sector-filter", "value"))
def update_pie(sectors):
    sectors = sectors or all_sectors
    df_f = df_districts[df_districts.sector.isin(sectors)]
    counts = df_f.groupby("sector").size().reset_index(name="count")
    fig = px.pie(counts, names="sector", values="count",
                 title="توزيع الأحياء حسب القطاع",
                 color="sector", color_discrete_map=COLORS["sector"], hole=0.4)
    fig.update_layout(
        paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"],
        font_color=COLORS["text"], margin=dict(t=35, b=0, l=0, r=0),
        title_font_size=12, legend=dict(font=dict(size=10)),
    )
    return fig


@callback(Output("datasets-bar", "figure"), Input("sector-filter", "value"))
def update_bar(_):
    df_top = df_meta.nlargest(10, "default.records_count").copy()
    df_top["short"] = df_top["default.title"].str[:38] + "…"
    fig = px.bar(df_top, x="default.records_count", y="short",
                 orientation="h", title="أكبر مجموعات البيانات (عدد السجلات)",
                 color_discrete_sequence=[COLORS["primary"]],
                 text="default.records_count")
    fig.update_layout(
        paper_bgcolor=COLORS["card"], plot_bgcolor=COLORS["card"],
        font_color=COLORS["text"], margin=dict(t=35, b=0, l=0, r=10),
        xaxis=dict(showgrid=False, color=COLORS["muted"]),
        yaxis=dict(showgrid=False, color=COLORS["muted"]),
        title_font_size=12, showlegend=False,
    )
    fig.update_traces(textfont_color="#111827", textfont_size=9)
    return fig


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
