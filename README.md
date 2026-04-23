# MedApp

Aplikacja wspiera pracę z dokumentacją badań: zbiera parametry liczbowe z badania, porównuje je z normami referencyjnymi, przygotowuje **szkic opisu tekstowego z użyciem AI** oraz umożliwia **edycję i zatwierdzenie** finalnej wersji zapisanej w bazie danych.

Dane identyfikujące pacjenta są **anonimizowane przed wysłaniem treści do API OpenAI** — do modelu trafiają wyłącznie dane techniczne badania.

---

## Stack technologiczny

| Warstwa | Technologie |
|--------|---------------|
| Backend | Python 3.12, **FastAPI**, **SQLAlchemy 2**, **Pydantic**, **PostgreSQL**, JWT (`python-jose`), bcrypt (`passlib`), **OpenAI SDK** |
| Frontend | **Next.js 15** (App Router), **React 19**, **TypeScript**, **Tailwind CSS**, **Shadcn UI** |
| Infrastruktura | **Docker**, **docker-compose**, Postgres 16 (Alpine) |

---

## Struktura projektu

```
medappai/
├── backend/
│   ├── app/
│   │   ├── core/           # Konfiguracja (Settings), bezpieczeństwo (JWT, hash haseł)
│   │   ├── db/             # Silnik SQLAlchemy, sesja bazy
│   │   ├── routers/        # Endpointy FastAPI (auth, pacjenci, analiza EMG, badania)
│   │   ├── schemas/        # Modele Pydantic (walidacja żądań i odpowiedzi)
│   │   ├── services/       # Normy medyczne, anonimizacja RODO, wywołanie OpenAI
│   │   ├── models.py       # Modele ORM (lekarze, pacjenci, badania)
│   │   └── main.py         # Punkt wejścia aplikacji, CORS, routery
│   ├── tests/              # Testy pytest (jednostkowe i integracyjne API)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt # pytest, ruff
│   ├── pytest.ini
│   └── ruff.toml
├── frontend/
│   ├── src/
│   │   ├── app/            # Layout, strona główna (formularz EMG)
│   │   ├── components/     # DescriptionEditor, komponenty UI (Shadcn)
│   │   └── lib/            # Klient API, utils
│   ├── Dockerfile
│   ├── vitest.config.ts
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Jak uruchomić

### Wymagania

- **Docker** i **Docker Compose** (zalecane), albo lokalnie: Python 3.12+, Node.js 20+, PostgreSQL 16.

### Opcja A — Docker Compose (cały stack)

Z katalogu głównego repozytorium:

```bash
docker compose up --build
```

Po starcie:

- Frontend: http://localhost:3000  
- Backend (API): http://localhost:8000  
- Sprawdzenie zdrowia API: http://localhost:8000/health  

**Pierwsze logowanie (domyślny seed lekarza w Compose):**

- E-mail: `doctor@example.com`  
- Hasło: `ChangeMe123!`  

Możesz zmienić wartości w pliku `.env` (zmienne `SEED_DOCTOR_EMAIL`, `SEED_DOCTOR_PASSWORD`) lub wyłączyć seed i włączyć rejestrację ustawiając `ALLOW_REGISTRATION=true`.

**Klucz OpenAI** — ustaw `OPENAI_API_KEY` w środowisku lub pliku `.env` w katalogu projektu (patrz `.env.example`). Bez klucza backend zwraca szkic zastępczy z surowymi danymi technicznymi zamiast odpowiedzi modelu.

### Opcja B — rozwój lokalny

1. **Baza:** uruchom Postgres i ustaw `DATABASE_URL` zgodnie z `backend/.env.example`.  
2. **Backend:**

   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend:**

   ```bash
   cd frontend
   npm install
   ```

   Skopiuj `frontend/.env.example` do `frontend/.env.local` i ustaw `NEXT_PUBLIC_API_URL=http://localhost:8000`.

   ```bash
   npm run dev
   ```

---

## Testy i jakość kodu

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
python -m ruff format --check app tests && python -m ruff check app tests
python -m pytest
```

- **pytest** — testy jednostkowe (`services`: normy, anonimizacja) oraz integracyjne HTTP (`TestClient`: `/health`, logowanie, `/analyze-emg`, zapis badania).
- **ruff** — sprawdzanie stylu importów, prostych błędów i formatowanie (konfiguracja w `backend/ruff.toml`).
- Testy API używają SQLite w pamięci (`DATABASE_URL` ustawiane w `tests/conftest.py`).

### Frontend

```bash
cd frontend
npm install
npm run check    # ESLint + Prettier + TypeScript + Vitest (jedna komenda)
```

Albo osobno: `npm run lint`, `npm run format:check`, `npm run typecheck`, `npm run test:run`.

- **ESLint** (`next lint`) — reguły Next.js i TypeScript (`eslint-config-prettier` wyłącza konflikty z Prettier).
- **Prettier** (+ `prettier-plugin-tailwindcss`) — jednolity styl i kolejność klas Tailwind.
- **Vitest** + **Testing Library** — testy pomocnicze (`cn`) i komponent `DescriptionEditor`.

### GitHub Actions

Przy pushu do gałęzi `main`, pull requeście oraz ręcznym uruchomieniu workflow ([Actions](https://docs.github.com/en/actions)) plik [`.github/workflows/ci.yml`](.github/workflows/ci.yml) uruchamia:

- **backend** — `ruff format --check`, `ruff check`, `pytest`;
- **frontend** — `npm run check` (ESLint, Prettier, TypeScript, Vitest).

---

## Licencja

Ten projekt jest udostępniany na licencji **MIT**.

```
MIT License

Copyright (c) 2026 Maxsoft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Autor

**Maxsoft**
