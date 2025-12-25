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
st.title("📦 Inteligentny Magazyn WMS 📦")
st.write("Autor: **Dawid Bajko**")

# 1. Pobieranie danych
@st.cache_data(ttl=10) # Odświeżanie co 10 sekund dla wydajności
def load_data():
    res_cat = supabase.table("kategoria").select("*").execute()
    res_prod = supabase.table("produkty").select("*, kategoria(nazwa)").execute()
    return res_cat.data, res_prod.data

kategorie_data, produkty_data = load_data()

# --- PANEL BOCZNY (STATYSTYKI I DODAWANIE) ---
with st.sidebar:
    st.header("➕ Zarządzanie")
    
    # Formularz dodawania
    with st.expander("Dodaj nowy produkt", expanded=False):
        if kategorie_data:
            with st.form("form_dodawania"):
                nazwa_input = st.text_input("Nazwa")
                ilosc_input = st.number_input("Ilość", min_value=0, step=1)
                cena_input = st.number_input("Cena (zł)", min_value=0.0)
                opcje_kat = {k['nazwa']: k['id'] for k in kategorie_data}
                wybrana_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
                
                if st.form_submit_button("Zapisz w bazie"):
                    nowy = {"nazwa": nazwa_input, "liczba": ilosc_input, "cena": cena_input, "kategoria_id": opcje_kat[wybrana_kat]}
                    supabase.table("produkty").insert(nowy).execute()
                    st.success("Dodano!")
                    st.rerun()
        else:
            st.warning("Najpierw dodaj kategorie w Supabase!")

    # Statystyki w panelu bocznym
    st.divider()
    st.header("📊 Statystyki")
    if produkty_data:
        df = pd.DataFrame(produkty_data)
        total_val = (df['liczba'] * df['cena'].astype(float)).sum()
        st.metric("Wartość całkowita", f"{total_val:,.2f} zł")
        st.metric("Liczba indeksów", len(df))

# --- GŁÓWNA SEKCJA: FILTROWANIE ---
st.subheader("🔍 Przeglądaj zasoby")
col_search1, col_search2 = st.columns([2, 1])

with col_search1:
    search_query = st.text_input("Szukaj po nazwie produktu...", placeholder="Wpisz nazwę...")

with col_search2:
    filter_kat = st.multiselect("Filtruj kategoria", options=[k['nazwa'] for k in kategorie_data])

# --- LOGIKA FILTROWANIA ---
filtered_products = produkty_data
if search_query:
    filtered_products = [p for p in filtered_products if search_query.lower() in p['nazwa'].lower()]
if filter_kat:
    filtered_products = [p for p in filtered_products if p['kategoria'] and p['kategoria']['nazwa'] in filter_kat]

# --- WIZUALIZACJA (WYKRES) ---
if filtered_products:
    with st.expander("📈 Analiza graficzna", expanded=False):
        chart_data = pd.DataFrame([{"Produkt": p['nazwa'], "Wartość": p['liczba'] * float(p['cena'])} for p in filtered_products])
        st.bar_chart(chart_data.set_index("Produkt"))

# --- LISTA PRODUKTÓW Z EDYCJĄ ---
st.divider()
if filtered_products:
    for p in filtered_products:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            
            cena = float(p['cena'])
            wartosc = p['liczba'] * cena
            
            c1.write(f"**{p['nazwa']}**")
            c1.caption(f"Kat: {p['kategoria']['nazwa'] if p['kategoria'] else 'Brak'}")
            
            # Szybka zmiana ilości (+ / -)
            c2.write(f"Ilość: **{p['liczba']}**")
            sub_c1, sub_c2 = c2.columns(2)
            if sub_c1.button("➕", key=f"add_{p['id']}"):
                supabase.table("produkty").update({"liczba": p['liczba'] + 1}).eq("id", p['id']).execute()
                st.rerun()
            if sub_c2.button("➖", key=f"sub_{p['id']}"):
                if p['liczba'] > 0:
                    supabase.table("produkty").update({"liczba": p['liczba'] - 1}).eq("id", p['id']).execute()
                    st.rerun()

            c3.write(f"Cena: {cena:.2f} zł")
            c4.write(f"Suma: **{wartosc:.2f} zł**")
            
            if c5.button("🗑️", key=f"del_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
            st.divider()
else:
    st.info("Nie znaleziono produktów spełniających kryteria.")
