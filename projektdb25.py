import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- KONFIGURACJA ---
st.set_page_config(page_title="Magazyn WMS Pro", layout="wide", page_icon="📦")

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# --- LOGIKA DANYCH ---
def load_data():
    try:
        res_cat = supabase.table("kategoria").select("*").execute()
        res_prod = supabase.table("produkty").select("*, kategoria(nazwa)").execute()
        return res_cat.data, res_prod.data
    except Exception as e:
        st.error(f"Błąd bazy danych: {e}")
        return [], []

kategorie_data, produkty_data = load_data()
df = pd.DataFrame(produkty_data)

if not df.empty:
    df['kat_nazwa'] = df['kategoria'].apply(lambda x: x['nazwa'] if x else "Brak")
    df['cena'] = df['cena'].astype(float)
    df['wartosc_total'] = df['liczba'] * df['cena']

# --- PANEL BOCZNY ---
with st.sidebar:
    st.header("➕ Zarządzanie")
    with st.expander("Dodaj nowy produkt", expanded=False):
        if kategorie_data:
            with st.form("form_dodawania", clear_on_submit=True):
                nazwa_input = st.text_input("Nazwa produktu")
                ilosc_input = st.number_input("Ilość", min_value=0, step=1)
                cena_input = st.number_input("Cena (zł)", min_value=0.0, format="%.2f")
                opcje_kat = {k['nazwa']: k['id'] for k in kategorie_data}
                wybrana_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
                
                if st.form_submit_button("🚀 Dodaj do bazy"):
                    nowy = {"nazwa": nazwa_input, "liczba": ilosc_input, "cena": cena_input, "kategoria_id": opcje_kat[wybrana_kat]}
                    supabase.table("produkty").insert(nowy).execute()
                    st.success("Dodano produkt!")
                    st.rerun()

# --- GŁÓWNY PANEL: STATYSTYKI ---
st.title("📦 Inteligentny Magazyn WMS")

if not df.empty:
    m1, m2, m3 = st.columns(3)
    total_val = df['wartosc_total'].sum()
    low_stock_count = df[df['liczba'] < 5].shape[0]
    
    m1.metric("Całkowita wartość", f"{total_val:,.2f} zł")
    m2.metric("Liczba pozycji", len(df))
    m3.metric("Niskie stany (<5)", low_stock_count)

    fig = px.pie(df, values='wartosc_total', names='kat_nazwa', hole=0.4, title="Udział kategorii w wartości magazynu")
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- WYSZUKIWARKA I FILTRY ---
st.divider()
c_search, c_filter = st.columns([2, 1])
search_q = c_search.text_input("🔍 Szukaj produktu...", placeholder="Wpisz nazwę")
selected_cats = c_filter.multiselect("📂 Kategorie", options=df['kat_nazwa'].unique() if not df.empty else [])

filtered_df = df.copy()
if search_q:
    filtered_df = filtered_df[filtered_df['nazwa'].str.contains(search_q, case=False)]
if selected_cats:
    filtered_df = filtered_df[filtered_df['kat_nazwa'].isin(selected_cats)]

# --- LISTA PRODUKTÓW ---
if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            col1.markdown(f"**{row['nazwa']}**\n\n📁 {row['kat_nazwa']}")
            
            # Naprawiona linia 110:
            if row['liczba'] < 5:
                col2.markdown(f"⚠️ :red[{row['liczba']} szt.]")
            else:
                col2.markdown(f"**{row['liczba']}** szt.")
            
            b1, b2 = col2.columns(2)
            if b1.button("➕", key=f"p_{row['id']}"):
                supabase.table("produkty").update({"liczba": row['liczba'] + 1}).eq("id", row['id']).execute()
                st.rerun()
            if b2.button("➖", key=f"m_{row['id']}"):
                if row['liczba'] > 0:
                    supabase.table("produkty").update({"liczba": row['liczba'] - 1}).eq("id", row['id']).execute()
                    st.rerun()

            col3.write(f"{row['cena']:.2f} zł")
            col4.write(f"**{row['wartosc_total']:.2f} zł**")
            if col5.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("produkty").delete().eq("id", row['id']).execute()
                st.rerun()
            st.divider()
