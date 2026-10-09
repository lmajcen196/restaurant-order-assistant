# Asistent za narudžbe

Web aplikacija koja koristi Gemini API za prepoznavanje narudžbi iz prirodnog jezika i odgovaranje na pitanja o jelovniku. Aplikacija je izrađena korištenjem FastAPI-ja (Python) za backend te Reacta i TypeScripta za frontend.

## Pokretanje aplikacije

**1. Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

U datoteku `backend/.env` potrebno je unijeti vlastiti Gemini API ključ.

Pokretanje backenda:

```bash
uvicorn app.main:app --reload --port 8000
```

**2. Frontend**

U novom terminalu:

```bash
cd frontend
npm install
npm run dev
```

Aplikacija je dostupna na lokalnoj adresi koju ispiše Vite.

## Moguća poboljšanja i testiranje

Aplikaciju bi bilo moguće unaprijediti dodavanjem prepoznavanja govora i boljom obradom složenijih ili dvosmislenih narudžbi. Ispravnost sustava mogla bi se provjeriti na skupu unaprijed pripremljenih narudžbi i pitanja, uspoređivanjem prepoznatih proizvoda, količina i preporuka s očekivanim rezultatima. Dodatno bi trebalo testirati narudžbe nedostupnih proizvoda te upite koji istovremeno sadrže narudžbu i pitanje o jelovniku.