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

# 1. Pobieranie kategorii (małe litery nazwa tabeli)
try:
    res_cat = supabase.table("kategoria").select("*").execute()
    kategorie = res_cat.data
except Exception as e:
    st.error(f"Błąd przy pobieraniu kategorii: {e}")
    kategorie = []

# 2. Formularz dodawania
st.subheader("Dodaj nowy produkt")
if kategorie:
    with st.form("form_dodawania"):
        nazwa_input = st.text_input("Nazwa produktu")
        ilosc_input = st.number_input("Ilość", min_value=0, step=1)
        cena_input = st.number_input("Cena", min_value=0.0)
        
        # POPRAWKA: używamy małego 'nazwa', bo tak masz w tabeli kategoria
        opcje_kat = {k['nazwa']: k['id'] for k in kategorie}
        wybrana_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        submit = st.form_submit_button("Dodaj do magazynu")
        
        if submit:
            try:
                # POPRAWKA: wszystkie klucze z małej litery zgodnie ze zdjęciem z Supabase
                nowy_produkt = {
                    "nazwa": nazwa_input,
                    "liczba": ilosc_input,
                    "cena": cena_input,
                    "kategoria_id": opcje_kat[wybrana_kat]
                }
                supabase.table("produkty").insert(nowy_produkt).execute()
                st.success("Dodano produkt!")
                st.rerun()
            except Exception as e:
                st.error(f"Błąd podczas dodawania: {e}")
else:
    st.warning("Dodaj najpierw kategorie w Supabase!")

# 3. Wyświetlanie produktów
st.subheader("Lista produktów w magazynie")
try:
    # Pobieramy produkty i łączymy z kategorią, żeby wyświetlić jej nazwę
    res_prod = supabase.table("produkty").select("*, kategoria(nazwa)").execute()
    produkty = res_prod.data
    
    if produkty:
        for p in produkty:
            col1, col2, col3 = st.columns([3, 2, 1])
            nazwa_kat = p['kategoria']['nazwa'] if p.get('kategoria') else "Brak"
            
            col1.write(f"**{p['nazwa']}** ({nazwa_kat})")
            col2.write(f"Ilość: {p['liczba']} | Cena: {p['cena']} zł")
            
            if col3.button("Usuń", key=f"del_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
    else:
        st.info("Magazyn jest pusty.")
except Exception as e:
    st.error(f"Błąd przy liście produktów: {e}")
