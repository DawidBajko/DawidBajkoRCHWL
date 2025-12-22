import streamlit as st
from supabase import create_client, Client

# Połączenie z bazą
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Problem z Secrets: {e}")
    st.stop()

st.title("📦 Mój Magazyn WMS")

# 1. Pobieranie kategorii (używamy małych liter)
try:
    res_cat = supabase.table("kategoria").select("*").execute()
    kategorie = res_cat.data
except Exception as e:
    st.error(f"Błąd przy pobieraniu kategorii: {e}")
    kategorie = []

# 2. Formularz dodawania
st.subheader("Dodaj nowy produkt")
if kategorie:
    with st.form("dodaj_produkt"):
        nazwa_input = st.text_input("Nazwa produktu")
        ilosc_input = st.number_input("Ilość", min_value=0, step=1)
        cena_input = st.number_input("Cena", min_value=0.0)
        
        opcje_kat = {k['Nazwa']: k['id'] for k in kategorie}
        wybrana_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        if st.form_submit_button("Dodaj do magazynu"):
            try:
                # UWAGA: Tutaj wpisałem nazwy kolumn z wielkiej litery 
                # tak jak masz na pierwszym zdjęciu (Nazwa, Liczba, Cena, Kategoria_id)
                dane = {
                    "Nazwa": nazwa_input,
                    "Liczba": ilosc_input,
                    "Cena": cena_input,
                    "Kategoria_id": opcje_kat[wybrana_kat]
                }
                supabase.table("produkty").insert(dane).execute()
                st.success("Dodano produkt!")
                st.rerun()
            except Exception as e:
                st.error(f"Błąd podczas dodawania: {e}")
else:
    st.warning("Dodaj najpierw przynajmniej jedną kategorię bezpośrednio w Supabase!")

# 3. Wyświetlanie produktów
st.subheader("Lista produktów w magazynie")
try:
    res_prod = supabase.table("produkty").select("*").execute()
    produkty = res_prod.data
    
    if produkty:
        for p in produkty:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{p['Nazwa']}**")
            col2.write(f"Ilość: {p['Liczba']} | Cena: {p['Cena']} zł")
            if col3.button("Usuń", key=f"del_{p['id']}"):
                try:
                    supabase.table("produkty").delete().eq("id", p['id']).execute()
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd usuwania: {e}")
    else:
        st.info("Magazyn jest pusty.")
except Exception as e:
    st.error(f"Błąd przy pobieraniu listy produktów: {e}")
