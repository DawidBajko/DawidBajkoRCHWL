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

# NAGŁÓWEK Z AUTOREM
st.title("📦 Mój Magazyn WMS")
st.write("autor: Dawid Bajko") # Dodany podpis autora małymi literami

# 1. Pobieranie kategorii
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
        cena_input = st.number_input("Cena jednostkowa", min_value=0.0)
        
        opcje_kat = {k['nazwa']: k['id'] for k in kategorie}
        wybrana_kat = st.selectbox("Wybierz kategorię", options=list(opcje_kat.keys()))
        
        submit = st.form_submit_button("Dodaj do magazynu")
        
        if submit:
            try:
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

# 3. Wyświetlanie produktów i obliczenia
st.subheader("Lista produktów w magazynie")
try:
    res_prod = supabase.table("produkty").select("*, kategoria(nazwa)").execute()
    produkty = res_prod.data
    
    if produkty:
        suma_calkowita = 0.0
        
        for p in produkty:
            ilosc = p['liczba'] if p['liczba'] else 0
            # Konwersja na float w razie gdyby baza zwróciła Decimal
            cena = float(p['cena']) if p['cena'] else 0.0
            wartosc_pozycji = ilosc * cena
            suma_calkowita += wartosc_pozycji
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            nazwa_kat = p['kategoria']['nazwa'] if p.get('kategoria') else "Brak"
            
            with col1:
                st.write(f"**{p['nazwa']}**")
                st.caption(f"Kat: {nazwa_kat}")
            with col2:
                st.write(f"{ilosc} szt. x {cena:.2f} zł")
            with col3:
                st.write(f"**Wartość: {wartosc_pozycji:.2f} zł**")
            with col4:
                if st.button("Usuń", key=f"del_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p['id']).execute()
                    st.rerun()
            st.divider()
        
        # Wyświetlenie sumy końcowej
        st.write("---")
        c1, c2 = st.columns([5, 2])
        c1.subheader("ŁĄCZNA WARTOŚĆ MAGAZYNU:")
        c2.subheader(f"{suma_calkowita:,.2f} zł")
        
    else:
        st.info("Magazyn jest pusty.")
except Exception as e:
    st.error(f"Błąd przy liście produktów: {e}")
