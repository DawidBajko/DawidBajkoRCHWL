# 1. Zmień "Kategoria" na "kategoria"
try:
    res_cat = supabase.table("kategoria").select("*").execute()
    kategorie = res_cat.data
except Exception as e:
    st.error(f"Błąd przy pobieraniu kategorii: {e}")
    kategorie = []

# ... wewnątrz formularza dodawania, zmień "Produkty" na "produkty"
# ORAZ upewnij się, że nazwy kolumn są takie jak w bazie (prawdopodobnie małe litery)
if st.form_submit_button("Dodaj do magazynu"):
    dane = {
        "nazwa": nazwa,        # sprawdź czy w Supabase masz 'Nazwa' czy 'nazwa'
        "liczba": ilosc,       # sprawdź czy 'Liczba' czy 'liczba'
        "cena": cena,          # sprawdź czy 'Cena' czy 'cena'
        "kategoria_id": opcje_kat[wybrana_kat]
    }
    supabase.table("produkty").insert(dane).execute()
    st.success("Dodano produkt!")
    st.rerun()

# 3. Zmień "Produkty" na "produkty"
try:
    res_prod = supabase.table("produkty").select("*").execute()
    produkty = res_prod.data
