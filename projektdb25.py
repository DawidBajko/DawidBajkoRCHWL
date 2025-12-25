import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Połączenie z bazą
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Problem z Secrets: {e}")
    st.stop()

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn WMS", layout="wide")
st.title("📦 Magazyn WMS 📦")
st.write("Autor: **Dawid Bajko**")

# 1. Pobieranie danych
def load_data():
    try:
        res_cat = supabase.table("kategoria").select("*").execute()
        res_prod = supabase.table("produkty").select("*, kategoria(nazwa)").execute()
        return res_cat.data, res_prod.data
    except:
        return [], []

kategorie_data, produkty_data = load_data()

# --- PANEL BOCZNY (DODAWANIE I STATYSTYKI) ---
with st.sidebar:
    st.header("➕ Nowy Produkt")
    if kategorie_data:
        with st.form("form_dodawania"):
            nazwa_input = st.text_input("Nazwa")
            ilosc_input = st.number_input("Ilość", min_value=0, step=1)
            cena_input = st.number_input("Cena (zł)", min_value=0.0)
            opcje_kat = {k['nazwa']: k['id'] for k in kategorie_data}
            wybrana_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
            
            if st.form_submit_button("Dodaj do bazy"):
                nowy = {
                    "nazwa": nazwa_input, 
                    "liczba": ilosc_input, 
                    "cena": cena_input, 
                    "kategoria_id": opcje_kat[wybrana_kat]
                }
                supabase.table("produkty").insert(nowy).execute()
                st.success("Dodano!")
                st.rerun()
    
    st.divider()
    st.header("📊 Podsumowanie")
    if produkty_data:
        df = pd.DataFrame(produkty_data)
        total_val = (df['liczba'] * df['cena'].astype(float)).sum()
        st.metric("Wartość magazynu", f"{total_val:,.2f} zł")
        st.metric("Liczba produktów", len(df))

# --- WYSZUKIWARKA I FILTRY ---
st.subheader("🔍 Wyszukiwarka")
col_search1, col_search2 = st.columns([2, 1])

with col_search1:
    search_query = st.text_input("Szukaj po nazwie...", placeholder="Wpisz nazwę produktu")

with col_search2:
    naukowe_nazwy_kat = [k['nazwa'] for k in kategorie_data]
    filter_kat = st.multiselect("Filtruj wg kategorii", options=naukowe_nazwy_kat)

# --- LOGIKA FILTROWANIA ---
filtered_products = produkty_data
if search_query:
    filtered_products = [p for p in filtered_products if search_query.lower() in p['nazwa'].lower()]
if filter_kat:
    filtered_products = [p for p in filtered_products if p['kategoria'] and p['kategoria']['nazwa'] in filter_kat]

# --- LISTA PRODUKTÓW ---
st.divider()
if filtered_products:
    for p in filtered_products:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            
            cena = float(p['cena'])
            wartosc = p['liczba'] * cena
            nazwa_kat = p['kategoria']['nazwa'] if p['kategoria'] else "Brak"
            
            c1.write(f"**{p['nazwa']}**")
            c1.caption(f"Kategoria: {nazwa_kat}")
            
            # Szybka zmiana ilości
            c2.write(f"Ilość: **{p['liczba']}**")
            b1, b2 = c2.columns(2)
            if b1.button("➕", key=f"plus_{p['id']}"):
                supabase.table("produkty").update({"liczba": p['liczba'] + 1}).eq("id", p['id']).execute()
                st.rerun()
            if b2.button("➖", key=f"minus_{p['id']}"):
                if p['liczba'] > 0:
                    supabase.table("produkty").update({"liczba": p['liczba'] - 1}).eq("id", p['id']).execute()
                    st.rerun()

            c3.write(f"Cena: {cena:.2f} zł")
            c4.write(f"Wartość: **{wartosc:.2f} zł**")
            
            if c5.button("🗑️", key=f"del_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
            st.divider()
else:
    st.info("Brak produktów do wyświetlenia.")
