import streamlit as st
import pandas as pd
import requests
import io
import re
import altair as alt

# Set the layout to wide
st.set_page_config(layout="wide")

# Load the CSS file
try:
    with open("styles.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("styles.css not found. Applying minimal fallback styles.")
    st.markdown("""
    <style>
    body { background-color: var(--main-bg-color, #FFFFFF); color: var(--text-color, #000000); }
    .stButton>button { background-color: var(--button-color, #008CBA); color: white; border: none; padding: 0.25em 0.75em; border-radius: 0.25rem; }
    .stButton>button:hover { opacity: 0.8; }
    div[data-testid="stSidebarUserContent"] { background-color: var(--sidebar-bg-color, #E0F7FA); }
    header[data-testid="stHeader"] { background-color: var(--top-bar-color, #006B8A); }
    h1, h2, h3, h4, h5, h6, .stMarkdown p, .stDataFrame, .stAlert { color: var(--text-color, #000000) !important; }
    .vega-embed .mark-text text, .vega-embed .title-text, .vega-embed .axis .label-text, 
    .vega-embed .axis .title-text, .vega-embed .legend .label-text, .vega-embed .legend .title-text { 
        fill: var(--text-color) !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# Define color palettes
color_palettes = {
    "Ocean Breeze": {"button_color": "#008CBA", "sidebar_bg_color": "#E0F7FA", "main_bg_color": "#B2EBF2", "text_color": "#003B2E", "top_bar_color": "#006B8A"},
    "Forest Green": {"button_color": "#4CAF50", "sidebar_bg_color": "#E8F5E9", "main_bg_color": "#C8E6C9", "text_color": "#1B5E20", "top_bar_color": "#3E8E41"},
    "Sunset Glow": {"button_color": "#FF5722", "sidebar_bg_color": "#FFF3E0", "main_bg_color": "#FFE0B2", "text_color": "#6A2C20", "top_bar_color": "#E64A19"},
    "Midnight Blue": {"button_color": "#1A237E", "sidebar_bg_color": "#E8EAF6", "main_bg_color": "#C5CAE9", "text_color": "#0D47A1", "top_bar_color": "#283593"},
    "Cherry Blossom": {"button_color": "#E91E63", "sidebar_bg_color": "#FCE4EC", "main_bg_color": "#F8BBD0", "text_color": "#880E4F", "top_bar_color": "#C2185B"},
    "Citrus Splash": {"button_color": "#FFEB3B", "sidebar_bg_color": "#FFFDE7", "main_bg_color": "#FFF59D", "text_color": "#F57F17", "top_bar_color": "#FBC02D"}, # Text might need to be darker for this button
    "Royal Purple": {"button_color": "#9C27B0", "sidebar_bg_color": "#F3E5F5", "main_bg_color": "#E1BEE7", "text_color": "#4A148C", "top_bar_color": "#7B1FA2"},
    "Coral Reef": {"button_color": "#FF7043", "sidebar_bg_color": "#FBE9E7", "main_bg_color": "#FFCCBC", "text_color": "#BF360C", "top_bar_color": "#D84315"},
    "Cool Gray": {"button_color": "#607D8B", "sidebar_bg_color": "#ECEFF1", "main_bg_color": "#CFD8DC", "text_color": "#37474F", "top_bar_color": "#455A64"},
    "Golden Sand": {"button_color": "#FFD54F", "sidebar_bg_color": "#FFF8E1", "main_bg_color": "#FFE082", "text_color": "#FF6F00", "top_bar_color": "#FFA000"}, # Text might need to be darker
    "Mystic Lavender": {"button_color": "#BA68C8", "sidebar_bg_color": "#F3E5F5", "main_bg_color": "#E1BEE7", "text_color": "#4A148C", "top_bar_color": "#8E24AA"},
    "Teal Dream": {"button_color": "#009688", "sidebar_bg_color": "#E0F2F1", "main_bg_color": "#B2DFDB", "text_color": "#004D40", "top_bar_color": "#00796B"},
    "Amber Glow": {"button_color": "#FFC107", "sidebar_bg_color": "#FFF8E1", "main_bg_color": "#FFECB3", "text_color": "#FF6F00", "top_bar_color": "#FFA000"}, # Text might need to be darker
    "Slate Blue": {"button_color": "#3F51B5", "sidebar_bg_color": "#E8EAF6", "main_bg_color": "#C5CAE9", "text_color": "#1A237E", "top_bar_color": "#303F9F"},
    "Spring Meadow": {"button_color": "#8BC34A", "sidebar_bg_color": "#F1F8E9", "main_bg_color": "#DCEDC8", "text_color": "#33691E", "top_bar_color": "#689F38"},
    "Rosewood": {"button_color": "#880E4F", "sidebar_bg_color": "#FCE4EC", "main_bg_color": "#F8BBD0", "text_color": "#4A148C", "top_bar_color": "#D81B60"},
    "Sandstone": {"button_color": "#A1887F", "sidebar_bg_color": "#EFEBE9", "main_bg_color": "#D7CCC8", "text_color": "#5D4037", "top_bar_color": "#8D6E63"},
    "Ruby Red": {"button_color": "#D32F2F", "sidebar_bg_color": "#FFEBEE", "main_bg_color": "#FFCDD2", "text_color": "#B71C1C", "top_bar_color": "#C62828"},
    "Mossy Green": {"button_color": "#689F38", "sidebar_bg_color": "#F1F8E9", "main_bg_color": "#DCEDC8", "text_color": "#33691E", "top_bar_color": "#558B2F"},
    "Cobalt Blue": {"button_color": "#0D47A1", "sidebar_bg_color": "#E3F2FD", "main_bg_color": "#BBDEFB", "text_color": "#0D47A1", "top_bar_color": "#1976D2"},
    "Graphite Night": {"button_color": "#00A0B0", "sidebar_bg_color": "#333333", "main_bg_color": "#222222", "text_color": "#E0E0E0", "top_bar_color": "#404040"},
    "Desert Mirage": {"button_color": "#D2691E", "sidebar_bg_color": "#F5F5DC", "main_bg_color": "#DEB887", "text_color": "#5C4033", "top_bar_color": "#A0522D"},
    "Emerald Isle": {"button_color": "#FFD700", "sidebar_bg_color": "#F0FFF0", "main_bg_color": "#90EE90", "text_color": "#006400", "top_bar_color": "#2E8B57"}, # Text might need to be darker
    "Lavender Dreams": {"button_color": "#9370DB", "sidebar_bg_color": "#E6E6FA", "main_bg_color": "#D8BFD8", "text_color": "#483D8B", "top_bar_color": "#7B68EE"},
    "Crimson Peak": {"button_color": "#DC143C", "sidebar_bg_color": "#EEEEEE", "main_bg_color": "#DCDCDC", "text_color": "#400000", "top_bar_color": "#B22222"},
    # --- EVEN MORE NEW PALETTES START HERE ---
    "Mocha Delight": {"button_color": "#A0522D", "sidebar_bg_color": "#F5F5DC", "main_bg_color": "#FFEBCD", "text_color": "#5D4037", "top_bar_color": "#8B4513"},
    "Steel Blue": {"button_color": "#4682B4", "sidebar_bg_color": "#E0E5EC", "main_bg_color": "#B0C4DE", "text_color": "#2F4F4F", "top_bar_color": "#5F7C8A"},
    "Volcanic Ash": {"button_color": "#FF4500", "sidebar_bg_color": "#4A4A4A", "main_bg_color": "#303030", "text_color": "#E8E8E8", "top_bar_color": "#202020"},
    "Minty Fresh": {"button_color": "#20B2AA", "sidebar_bg_color": "#F0FFF0", "main_bg_color": "#AFEEEE", "text_color": "#00695C", "top_bar_color": "#48D1CC"},
    "Autumn Harvest": {"button_color": "#FF8C00", "sidebar_bg_color": "#FFF8DC", "main_bg_color": "#FFE4B5", "text_color": "#8B4513", "top_bar_color": "#D2691E"},
    # --- EVEN MORE NEW PALETTES END HERE ---
}


# --- Sidebar Controls ---
st.sidebar.title("Display Options")

# Palette Selection
st.sidebar.subheader("Color Palette")
selected_palette_name = st.sidebar.selectbox(
    "Select Palette",
    list(color_palettes.keys()), # Dynamically gets all keys
    key="palette_selector"
)
selected_palette = color_palettes[selected_palette_name]

# Chart Formatting Options
st.sidebar.subheader("Chart Axis Formatting")

# X-axis Date Formats
x_axis_date_formats_options = {
    "YYYY-MM-DD (%Y-%m-%d)": "%Y-%m-%d", "YY-MM-DD (%y-%m-%d)": "%y-%m-%d",
    "Month D, YYYY (%b %d, %Y)": "%b %d, %Y", "MM/DD/YY (%m/%d/%y)": "%m/%d/%y",
    "YYYY-MM (%Y-%m)": "%Y-%m", "YY-MM (%y-%m)": "%y-%m",
}
selected_x_date_format_key = st.sidebar.selectbox(
    "X-Axis Date Format", list(x_axis_date_formats_options.keys()), index=0, key="x_date_format_selector"
)
selected_x_date_format = x_axis_date_formats_options[selected_x_date_format_key]

# X-axis Label Rotation
x_axis_rotation_options = {
    "Angled (-45°)": -45, "Horizontal (0°)": 0, "Vertical (90°)": 90, "Vertical (-90°)": -90,
}
selected_x_rotation_key = st.sidebar.selectbox(
    "X-Axis Label Rotation", list(x_axis_rotation_options.keys()), index=0, key="x_rotation_selector"
)
selected_x_rotation_angle = x_axis_rotation_options[selected_x_rotation_key]

# Y-axis Price Formats
y_axis_price_formats_options = {
    "Currency ($1,234.56)": "$,.2f", "Currency ($1234.56)": "$.2f", "Number (1,234.56)": ",.2f",
    "Number (1234.56)": ".2f", "Currency, Integer ($1,235)": "$,.0f",
}
selected_y_price_format_key = st.sidebar.selectbox(
    "Y-Axis Price Format", list(y_axis_price_formats_options.keys()), index=0, key="y_price_format_selector"
)
selected_y_price_format = y_axis_price_formats_options[selected_y_price_format_key]

# Y-axis Volume Formats
y_axis_volume_formats_options = {
    "Integer (1,234,567)": ",.0f", "SI Suffix (1.23M)": ".2s", "SI Suffix, Integer (1M)": ".0s",
    "Integer (1234567)": ".0f",
}
selected_y_volume_format_key = st.sidebar.selectbox(
    "Y-Axis Volume Format", list(y_axis_volume_formats_options.keys()), index=0, key="y_volume_format_selector"
)
selected_y_volume_format = y_axis_volume_formats_options[selected_y_volume_format_key]


# Inject the selected palette colors into the CSS variables
st.markdown(
    f"""
    <style>
    :root {{
        --top-bar-color: {selected_palette["top_bar_color"]};
        --sidebar-bg-color: {selected_palette["sidebar_bg_color"]};
        --main-bg-color: {selected_palette["main_bg_color"]};
        --button-color: {selected_palette["button_color"]};
        --text-color: {selected_palette["text_color"]};
    }}
    .vega-embed .mark-text text, .vega-embed .title-text, .vega-embed .axis .label-text, 
    .vega-embed .axis .title-text, .vega-embed .legend .label-text, .vega-embed .legend .title-text {{ 
        fill: var(--text-color) !important; 
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Main application content ---
st.title("Stock Data and Style Demo")

# --- Input for Google Sheet URL ---
st.header("Load Data from Google Sheet")
user_sheet_url = st.text_input(
    "Paste your Google Sheet URL here (expects headers in the first row):", value="", key="gsheet_url_input"
)

def parse_gsheet_url(url):
    id_match = re.search(r"/spreadsheets/d/([^/]+)", url)
    if not id_match: return None, None
    spreadsheet_id = id_match.group(1)
    gid_match = re.search(r"[#&?]gid=([^&]+)", url)
    sheet_gid = "0" 
    if gid_match: sheet_gid = gid_match.group(1)
    return spreadsheet_id, sheet_gid

@st.cache_data(ttl=3600)
def fetch_spreadsheet_title(spreadsheet_id):
    if not spreadsheet_id: return None
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=h, timeout=10)
        r.raise_for_status()
        m = re.search(r"<title>(.*?)</title>", r.text, re.I | re.S)
        if m:
            t = re.sub(r"\s*-\s*Google Sheets\s*$", "", m.group(1).strip(), flags=re.I)
            if len(t) > 100 or "Sign in" in t or "Error" in t: return None
            return t if t else None
        return None
    except: return None

@st.cache_data(ttl=600)
def load_data_from_google_sheet(export_url):
    try:
        r = requests.get(export_url, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')), header=0)
        df.columns = df.columns.str.strip()
        if 'Date' not in df.columns: st.error("'Date' column missing."); return pd.DataFrame()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        if df.empty: st.error("No valid dates."); return pd.DataFrame()
        for col in ['Close', 'Volume']:
            if col not in df.columns:
                st.warning(f"'{col}' column missing."); df[col] = pd.NA
            else:
                if df[col].dtype == 'object': df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e: st.error(f"Data load error: {e}"); return pd.DataFrame()

stock_data_loaded = pd.DataFrame()
spreadsheet_title_to_display = None
title_fetch_attempted = bool(user_sheet_url)

if user_sheet_url:
    spreadsheet_id, sheet_gid = parse_gsheet_url(user_sheet_url)
    if spreadsheet_id:
        spreadsheet_title_to_display = fetch_spreadsheet_title(spreadsheet_id)
        if spreadsheet_title_to_display: st.subheader(f"Spreadsheet: {spreadsheet_title_to_display}")
        CSV_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_gid}"
        st.markdown(f"Loading GID `{sheet_gid}`...")
        stock_data_loaded = load_data_from_google_sheet(CSV_EXPORT_URL)
    else: st.error("Invalid Google Sheet URL.")

# --- Display Stock Data with Altair ---
if not stock_data_loaded.empty:
    if title_fetch_attempted and not spreadsheet_title_to_display and spreadsheet_id:
        st.info("Note: Spreadsheet title couldn't be fetched (private sheet or network issue).")
    
    if st.checkbox("Show first 5 rows of loaded data", key="show_head_gsheet_altair"):
        st.write("Columns found:", stock_data_loaded.columns.tolist())
        st.dataframe(stock_data_loaded.head())

    mark_color = selected_palette.get("button_color", "#008CBA")
    common_x_axis = alt.X('Date:T', title='Date', 
                          axis=alt.Axis(format=selected_x_date_format, labelAngle=selected_x_rotation_angle))

    if 'Close' in stock_data_loaded.columns and not stock_data_loaded['Close'].isnull().all():
        price_chart = alt.Chart(stock_data_loaded).mark_line(
            strokeWidth=2, color=mark_color
        ).encode(
            x=common_x_axis,
            y=alt.Y('Close:Q', title='Closing Price', scale=alt.Scale(zero=False),
                    axis=alt.Axis(format=selected_y_price_format)),
            tooltip=[ alt.Tooltip('Date:T', title='Date', format=selected_x_date_format), 
                      alt.Tooltip('Close:Q', title='Price', format=selected_y_price_format) ]
        ).properties(title=alt.TitleParams(text='Stock Closing Price', fontSize=16), height=350).interactive()
        st.altair_chart(price_chart, use_container_width=True)
    else:
        if user_sheet_url and spreadsheet_id: st.info("Closing price data missing or invalid.")

    if 'Volume' in stock_data_loaded.columns and not stock_data_loaded['Volume'].isnull().all():
        volume_chart = alt.Chart(stock_data_loaded).mark_bar(color=mark_color).encode(
            x=common_x_axis,
            y=alt.Y('Volume:Q', title='Volume', axis=alt.Axis(format=selected_y_volume_format)),
            tooltip=[ alt.Tooltip('Date:T', title='Date', format=selected_x_date_format),
                      alt.Tooltip('Volume:Q', title='Volume', format=selected_y_volume_format) ]
        ).properties(title=alt.TitleParams(text='Trading Volume', fontSize=16), height=250).interactive()
        st.altair_chart(volume_chart, use_container_width=True)
    else:
        if user_sheet_url and spreadsheet_id: st.info("Volume data missing or invalid.")

    if st.checkbox("Show Full Historical Data Table", key="show_data_table_gsheet_altair"):
        df_display = stock_data_loaded.copy()
        if 'Date' in df_display.columns:
            try: df_display = df_display.set_index('Date')
            except: pass 
        st.subheader("Historical Data Table"); st.dataframe(df_display)

elif user_sheet_url and not spreadsheet_id: pass
elif user_sheet_url and spreadsheet_id and stock_data_loaded.empty:
    msg = "Doc title failed. " if not spreadsheet_title_to_display and title_fetch_attempted else ""
    st.warning(f"{msg}No data loaded. Check URL, sharing, GID, columns.")