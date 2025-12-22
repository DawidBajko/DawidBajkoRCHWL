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

# 1. Pobieranie kategorii
try:
    res_cat = supabase.table("Kategoria").select("*").execute()
    kategorie = res_cat.data
except Exception as e:
    st.error(f"Błąd przy pobieraniu kategorii: {e}")
    kategorie = []

# 2. Formularz dodawania
st.subheader("Dodaj nowy produkt")
if kategorie:
    with st.form("dodaj_produkt"):
        nazwa = st.text_input("Nazwa produktu")
        ilosc = st.number_input("Ilość", min_value=0, step=1)
        cena = st.number_input("Cena", min_value=0.0)
        
        opcje_kat = {k['Nazwa']: k['id'] for k in kategorie}
        wybrana_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        if st.form_submit_button("Dodaj do magazynu"):
            dane = {
                "Nazwa": nazwa,
                "Liczba": ilosc,
                "Cena": cena,
                "Kategoria_id": opcje_kat[wybrana_kat]
            }
            supabase.table("Produkty").insert(dane).execute()
            st.success("Dodano produkt!")
            st.rerun()
else:
    st.warning("Najpierw dodaj kategorie w Supabase!")

# 3. Wyświetlanie produktów
st.subheader("Lista produktów w magazynie")
try:
    res_prod = supabase.table("Produkty").select("*").execute()
    produkty = res_prod.data
    
    if produkty:
        for p in produkty:
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.write(f"**{p['Nazwa']}**")
            col2.write(f"Ilość: {p['Liczba']} | Cena: {p['Cena']} zł")
            if col3.button("Usuń", key=f"del_{p['id']}"):
                supabase.table("Produkty").delete().eq("id", p['id']).execute()
                st.rerun()
    else:
        st.info("Magazyn jest pusty.")
except Exception as e:
    st.error(f"Błąd przy pobieraniu produktów: {e}")
