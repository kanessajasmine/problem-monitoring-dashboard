import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Problem Monitoring", layout="wide")

# ---------------------------------------------------------------------------
# 1. GANTI URL INI dengan link CSV publik Google Sheets kamu
#    Cara ambil: File > Share > Publish to web > pilih sheet > CSV
#    Atau pakai pola:
#    https://docs.google.com/spreadsheets/d/<SHEET_ID>/gviz/tq?tqx=out:csv&sheet=<NAMA_SHEET>
# ---------------------------------------------------------------------------
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSd4Dt0jb5QKcw2ILlSvyWy1e5RjaBH_G5g9PO3UsBX77SV6qTu0gcU-oAtkPkNznukjEE9MKWaKBRb/pub?gid=1404587945&single=true&output=csv"

MONTH_ORDER = ["Feb 2026", "Mar 2026", "Apr 2026", "Mei 2026", "Juni 2026", "Juli 2026", "Agustus 2026"]

CAT_COLORS = {
    "Product Quality": "#B5482A",
    "Timeline": "#8A8F87",
    "Production Capacity": "#1F5673",
    "Product Development": "#6B5CA5",
    "Delivery": "#2F7D6B",
    "Pricing": "#B7922C",
    "Payment": "#7A5A1A",
    "Stock": "#9A5730",
    "Product Specification": "#3B6E91",
    "Competition": "#A0416A",
    "Internal Approval": "#55606B",
}

CUSTOM_CSS = """
<style>
html, body, [class*="css"]  { font-family: 'IBM Plex Sans', sans-serif; }
.block-container { padding-top: 1.5rem; max-width: 1280px; }
h1 { font-family: 'Space Grotesk', sans-serif; font-weight: 700; }
div[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #DADFDB; border-radius: 4px;
    padding: 14px 16px; border-left: 3px solid #161A19;
}
div[data-testid="stMetricLabel"] { font-size: 11px; text-transform: uppercase; color: #8B938F; }
div[data-testid="stMetricValue"] { font-size: 24px; font-family: 'Space Grotesk', sans-serif; }
.pill {
    display:inline-block; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:500;
}
hr { margin: 0.6rem 0 1.2rem 0; border-color: #DADFDB; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300)  # refresh otomatis tiap 5 menit
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ["bulan", "customer", "item", "production_factory", "problem",
                "root_cause", "action_plan", "problem_category"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    return df


def month_sort_key(m):
    try:
        return MONTH_ORDER.index(m)
    except ValueError:
        return 999


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
if SHEET_CSV_URL == "PASTE_URL_CSV_GOOGLE_SHEETS_DI_SINI":
    st.warning("Sambungkan dulu ke Google Sheets: isi SHEET_CSV_URL di app.py dengan link CSV publik sheet kamu.")
    st.stop()

df = load_data(SHEET_CSV_URL)

st.title("Problem Monitoring")
st.caption("Komplain & kendala produksi — data live dari Google Sheets")

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
with c1:
    bulan_opt = ["Semua bulan"] + sorted(df["bulan"].unique(), key=month_sort_key)
    f_bulan = st.selectbox("Bulan", bulan_opt)
with c2:
    factory_opt = ["Semua pabrik"] + sorted([x for x in df["production_factory"].unique() if x])
    f_factory = st.selectbox("Pabrik", factory_opt)
with c3:
    cat_opt = ["Semua kategori"] + sorted(df["problem_category"].unique())
    f_cat = st.selectbox("Kategori", cat_opt)
with c4:
    f_search = st.text_input("Cari customer / item / masalah", "")

fdf = df.copy()
if f_bulan != "Semua bulan":
    fdf = fdf[fdf["bulan"] == f_bulan]
if f_factory != "Semua pabrik":
    fdf = fdf[fdf["production_factory"] == f_factory]
if f_cat != "Semua kategori":
    fdf = fdf[fdf["problem_category"] == f_cat]
if f_search:
    s = f_search.lower()
    mask = (
        fdf["customer"].str.lower().str.contains(s)
        | fdf["item"].str.lower().str.contains(s)
        | fdf["problem"].str.lower().str.contains(s)
        | fdf["root_cause"].str.lower().str.contains(s)
    )
    fdf = fdf[mask]

st.caption(f"{len(fdf)} / {len(df)} kasus ditampilkan")
st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
total = len(fdf)
top_cat = fdf["problem_category"].value_counts().idxmax() if total else "-"
top_cat_n = fdf["problem_category"].value_counts().max() if total else 0
top_month = fdf["bulan"].value_counts().idxmax() if total else "-"
top_month_n = fdf["bulan"].value_counts().max() if total else 0
unique_customers = fdf["customer"].nunique()

k1.metric("Total kasus", total)
k2.metric("Kategori terbanyak", top_cat, f"{top_cat_n} kasus" if total else "")
k3.metric("Bulan terpadat", top_month, f"{top_month_n} kasus" if total else "")
k4.metric("Jumlah customer", unique_customers)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
col_a, col_b = st.columns([1.7, 1])

with col_a:
    st.subheader("Tren bulanan per kategori")
    months = sorted(fdf["bulan"].unique(), key=month_sort_key)
    fig = go.Figure()
    for cat in fdf["problem_category"].value_counts().index:
        counts = [len(fdf[(fdf["bulan"] == m) & (fdf["problem_category"] == cat)]) for m in months]
        fig.add_trace(go.Bar(
            name=cat, x=months, y=counts,
            marker_color=CAT_COLORS.get(cat, "#999999"),
        ))
    fig.update_layout(
        barmode="stack", height=320, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Distribusi kategori")
    vc = fdf["problem_category"].value_counts()
    for cat, n in vc.items():
        pct = round(n / total * 100) if total else 0
        color = CAT_COLORS.get(cat, "#999999")
        st.markdown(f"""
        <div style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
            <span>{cat}</span><span style="color:#8B938F;">{n} · {pct}%</span>
          </div>
          <div style="height:7px;background:#EEEFEC;border-radius:2px;">
            <div style="width:{pct}%;height:100%;background:{color};border-radius:2px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Detail table (tabel asli, bukan kartu)
# ---------------------------------------------------------------------------
st.subheader("Detail kasus")

table_df = fdf.sort_values("bulan", key=lambda s: s.map(month_sort_key)).reset_index(drop=True)

display_cols = ["bulan", "customer", "item", "production_factory", "problem_category", "problem"]
view_df = table_df[display_cols].rename(columns={
    "bulan": "Bulan",
    "customer": "Customer",
    "item": "Item",
    "production_factory": "Pabrik",
    "problem_category": "Kategori",
    "problem": "Ringkasan masalah",
})


def highlight_category(val):
    color = CAT_COLORS.get(val, "#999999")
    return f"background-color: {color}22; color: {color}; font-weight: 500;"


styled = view_df.style.map(highlight_category, subset=["Kategori"])

event = st.dataframe(
    styled,
    use_container_width=True,
    height=460,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
)

selected_rows = event.selection.rows if event and event.selection else []
if selected_rows:
    sel = table_df.iloc[selected_rows[0]]
    color = CAT_COLORS.get(sel["problem_category"], "#999999")
    st.markdown(
        f"<span class='pill' style='background:{color}22;color:{color};'>{sel['problem_category']}</span>",
        unsafe_allow_html=True,
    )
    d1, d2, d3 = st.columns(3)
    d1.markdown(f"**Masalah**  \n{sel['problem']}")
    d2.markdown(f"**Akar masalah**  \n{sel['root_cause']}")
    d3.markdown(f"**Rencana tindakan**  \n{sel['action_plan']}")
else:
    st.caption("Klik salah satu baris di tabel untuk melihat akar masalah dan rencana tindakan.")
