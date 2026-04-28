"""
Generator ręcznie skurowanych przykładów treningowych.
Pokrywa 4 typy projektów telco/IT: nowy, legacy, ai, migracja.
Brak informacji company-specific.
"""
import json
import uuid
from pathlib import Path

EXAMPLES = [

    # ─────────────────────────────────────────────────────────────────────────
    # TYP: NOWY — nowe systemy od zera
    # ─────────────────────────────────────────────────────────────────────────

    {
        "opis_projektu": (
            "Portal self-service dla klientów indywidualnych operatora telekomunikacyjnego. "
            "Funkcjonalności: zarządzanie kontem (zmiana danych, hasła, adresu), "
            "podgląd i opłacanie faktur online, zarządzanie usługami (aktywacja, dezaktywacja pakietów), "
            "historia połączeń i zużycia danych, formularz zgłoszenia serwisowego z śledzeniem statusu. "
            "Stack: React 18 + TypeScript, FastAPI, PostgreSQL, Redis dla sesji, "
            "integracja z bramką płatności, OAuth2 SSO."
        ),
        "rzeczywiste_godziny": 920,
        "typ_projektu": "nowy",
        "historia_klienta": "Operator zrealizował wcześniej portal B2B (800h, dostarczony na czas). Doświadczony zespół frontend.",
        "wzorce_ryzyk": "Integracja z bramką płatności historycznie +30% do estymacji.",
        "komentarz_pm": "Niedoszacowano czasu na testy regresji i zabezpieczenia OWASP.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System zarządzania zgłoszeniami serwisowymi dla klientów biznesowych. "
            "Ticketing z priorytetami SLA, eskalacją, przypisywaniem do techników. "
            "Panel klienta (web + mobile PWA), panel dyspozytora, integracja z systemem field service. "
            "Powiadomienia SMS/email, raporty KPI, dashboard menadżerski. "
            "Backend: Node.js + TypeScript, MongoDB, WebSockets dla real-time statusu."
        ),
        "rzeczywiste_godziny": 1040,
        "typ_projektu": "nowy",
        "historia_klienta": "Brak historii — nowy klient.",
        "wzorce_ryzyk": "Real-time komponenty (WebSocket) historycznie trudne w testowaniu — +20%.",
        "komentarz_pm": "Zakres był dobrze określony, estymacja bliska rzeczywistości.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "API gateway dla ekosystemu mikroserwisów operatora. "
            "Rate limiting, autentykacja JWT + API keys, routing do 12 serwisów backendowych, "
            "transformacja payloadów, monitoring SLA, circuit breaker, retry logic. "
            "Dokumentacja OpenAPI, developer portal dla partnerów zewnętrznych. "
            "Stack: Kong Gateway + custom Lua plugins, Keycloak, Prometheus + Grafana."
        ),
        "rzeczywiste_godziny": 680,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient ma doświadczenie z mikroserwisami — 3 poprzednie projekty dostarczane terminowo.",
        "wzorce_ryzyk": "Custom plugins Lua wymagają specjalistów — ryzyko dostępności zasobów.",
        "komentarz_pm": "Dobrze oszacowany projekt, lekkie przekroczenie na dokumentacji dev portalu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Aplikacja mobilna iOS + Android do zarządzania abonamentem telefonicznym. "
            "Logowanie biometryczne, podgląd salda i faktur, doładowania, "
            "zmiana planu taryfowego, chat z obsługą klienta, powiadomienia push. "
            "React Native, integracja z REST API backendowym operatora, "
            "Apple Pay / Google Pay dla płatności."
        ),
        "rzeczywiste_godziny": 1160,
        "typ_projektu": "nowy",
        "historia_klienta": "Operator nie miał wcześniej aplikacji mobilnej — pierwsza implementacja.",
        "wzorce_ryzyk": "Pierwsza aplikacja mobilna u klienta — brak wewnętrznych procesów review i store submission. +25%.",
        "komentarz_pm": "Opóźnienia przy konfiguracji Apple Developer Program i Google Play Console.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System provisioning usług dla klientów B2B. Automatyczne uruchamianie internetu, "
            "telefonii i telewizji po podpisaniu umowy. Integracja z 4 systemami OSS/BSS, "
            "workflow engine (Camunda), notyfikacje statusu, rollback przy błędach. "
            "SLA: provisioning w < 4h robocze. API REST + SOAP dla starszych systemów."
        ),
        "rzeczywiste_godziny": 1580,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient realizował wcześniej provisioning manualny — integracje z tymi systemami już znane.",
        "wzorce_ryzyk": "SOAP integracje zawsze wymagają dodatkowego czasu na mapowanie danych — +40%.",
        "komentarz_pm": "Rollback logic był niedoszacowany — okazał się najtrudniejszym elementem.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Portal B2B dla partnerów handlowych operatora. Zarządzanie zamówieniami hurtowymi, "
            "katalog produktów z cennikami indywidualnymi, rabaty wolumenowe, faktury, "
            "raporty sprzedaży, API do integracji z systemami ERP partnerów. "
            "Role i uprawnienia (admin partnera, handlowiec, finanse). "
            "Angular 17, Java Spring Boot, Oracle DB."
        ),
        "rzeczywiste_godziny": 1320,
        "typ_projektu": "nowy",
        "historia_klienta": "Dwa poprzednie projekty Java Spring Boot — dostarczane z 10% przekroczeniem budżetu.",
        "wzorce_ryzyk": "Cenniki indywidualne i rabaty — logika biznesowa zawsze bardziej skomplikowana niż zakładano.",
        "komentarz_pm": "Logika rabatów okazała się bardzo złożona — 4 typy rabatów zamiast planowanych 2.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System monitorowania zużycia danych dla klientów prepaid. "
            "Real-time counter zużycia MB, SMS, minut. Automatyczne powiadomienia przy 80% i 100% limitu. "
            "Agregacja danych z 3 systemów billingowych, cache Redis, "
            "API mobilne i webowe. Obciążenie: 500k aktywnych sesji jednocześnie."
        ),
        "rzeczywiste_godziny": 760,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient realizował podobny system 2 lata temu (nieco mniejsza skala) — 640h.",
        "wzorce_ryzyk": "Skalowanie do 500k sesji — testy wydajnościowe zawsze ujawniają problemy.",
        "komentarz_pm": "Testy wydajnościowe i optymalizacja Redis zajęły 2x więcej niż planowano.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Elektroniczny system zarządzania umowami z klientami biznesowymi. "
            "Generowanie umów z szablonów Word/PDF, podpis elektroniczny (e-podpis kwalifikowany), "
            "repozytorium umów z wyszukiwarką, przypomnienia o terminach odnowień, "
            "workflow akceptacji (wielopoziomowy), integracja z systemem CRM i ERP."
        ),
        "rzeczywiste_godziny": 840,
        "typ_projektu": "nowy",
        "historia_klienta": "Brak historii dotyczącej systemów podpisu elektronicznego.",
        "wzorce_ryzyk": "E-podpis kwalifikowany — certyfikacja i testy prawne zawsze wydłużają projekt.",
        "komentarz_pm": "Certyfikacja podpisu elektronicznego zajęła 6 tygodni zamiast planowanych 2.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Platforma do zarządzania numerami telefonicznymi (Number Management System). "
            "Pule numerów, rezerwacje, przydziały do klientów, portowanie numerów (MNP), "
            "integracja z rejestrem krajowym, raportowanie, audyt zmian. "
            "Obsługa 50 milionów numerów, wysoka dostępność 99.99%."
        ),
        "rzeczywiste_godziny": 2200,
        "typ_projektu": "nowy",
        "historia_klienta": "Krytyczny system telco — klient nigdy wcześniej nie realizował projektu tej klasy.",
        "wzorce_ryzyk": "Systemy telco-grade z wymogiem 99.99% HA: każdy element infrastruktury podwójny.",
        "komentarz_pm": "Testy failover i disaster recovery zajęły 3 miesiące. Dobrze że zaplanowano bufor.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Prosty landing page z formularzem rejestracji na usługę internetową. "
            "Formularz wieloetapowy (dane osobowe → wybór pakietu → potwierdzenie), "
            "walidacja w czasie rzeczywistym, integracja z systemem kolejkowania leadów, "
            "A/B testy, Google Analytics. Stack: Next.js, Tailwind CSS."
        ),
        "rzeczywiste_godziny": 180,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient regularnie zleca drobne projekty webowe — dobre doświadczenia.",
        "wzorce_ryzyk": "Brak ryzyk — prosty zakres.",
        "komentarz_pm": "Dostarczony terminowo i w budżecie.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System kolejkowania i zarządzania wizytami w salonach sprzedaży. "
            "Kiosk do rejestracji (tablet), wyświetlacz kolejki (TV), "
            "powiadomienia SMS o zbliżającej się kolejce, panel doradcy, "
            "raporty czasu oczekiwania i obsługi, integracja z systemem CRM. "
            "50 salonów, 200 stanowisk."
        ),
        "rzeczywiste_godziny": 640,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient miał podobny system dla 10 salonów — teraz skalowanie do 50.",
        "wzorce_ryzyk": "Skalowanie z 10 do 50 salonów — konfiguracja per placówka zawsze czasochłonna.",
        "komentarz_pm": "Konfiguracja lokalizacyjna per salon pochłonęła 20% więcej czasu niż zakładano.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Narzędzie do planowania sieci radiowej 5G. "
            "Wizualizacja zasięgu na mapie (Mapbox GL), import danych z plików KML/shp, "
            "algorytm optymalizacji rozmieszczenia anten, eksport raportów PDF/Excel. "
            "Aplikacja webowa dla inżynierów sieci. Vue.js + Python backend + PostGIS."
        ),
        "rzeczywiste_godziny": 1100,
        "typ_projektu": "nowy",
        "historia_klienta": "Specjalistyczne narzędzie GIS — klient nie miał wcześniej takich projektów.",
        "wzorce_ryzyk": "Algorytmy optymalizacji i GIS — ekspercka wiedza domenowa wymagana, ryzyko dostępności specjalistów.",
        "komentarz_pm": "Algorytm optymalizacji okazał się bardzo złożony obliczeniowo — dodatkowa praca nad wydajnością.",
        "zrodlo": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYP: LEGACY — modernizacja i utrzymanie starych systemów
    # ─────────────────────────────────────────────────────────────────────────

    {
        "opis_projektu": (
            "Modernizacja systemu bilingowego napisanego w COBOL (lata 90.). "
            "Migracja logiki biznesowej do Java 17 + Spring Boot. "
            "Przepisanie 200 programów COBOL, zachowanie kompatybilności z formatami plików wyjściowych, "
            "testy regresji porównawcze (stary vs nowy system przez 6 miesięcy równolegle), "
            "dokumentacja kodu (brak dokumentacji w oryginale)."
        ),
        "rzeczywiste_godziny": 4800,
        "typ_projektu": "legacy",
        "historia_klienta": "System krytyczny, działający bez przerwy od 28 lat. Zero dokumentacji.",
        "wzorce_ryzyk": "Migracja COBOL bez dokumentacji — odkrywanie ukrytej logiki biznesowej to największe ryzyko. +80%.",
        "komentarz_pm": "Projekt trwał 2x dłużej niż planowano — odkryliśmy 40 nieudokumentowanych reguł biznesowych.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Upgrade systemu zarządzania siecią z Java 8 + Struts 2 do Java 21 + Spring Boot 3 + React. "
            "Refactoring 350k linii kodu, migracja z Oracle 11g do Oracle 19c, "
            "zastąpienie JSP nowym frontendem React, modernizacja API (REST zamiast SOAP), "
            "testy regresji dla 800 przypadków testowych."
        ),
        "rzeczywiste_godziny": 3200,
        "typ_projektu": "legacy",
        "historia_klienta": "System OSS, 12 lat w produkcji. Poprzedni upgrade (Java 6→8) zajął 1800h.",
        "wzorce_ryzyk": "SOAP → REST migracja przy zachowaniu kompatybilności z zewnętrznymi integracjami.",
        "komentarz_pm": "Zidentyfikowano 15 zewnętrznych systemów zintegrowanych przez SOAP — każde wymagało osobnej pracy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Refactoring modułu obsługi reklamacji — monolityczna aplikacja PHP 5.6 → PHP 8.2 + Laravel. "
            "Przepisanie 80k linii kodu, modernizacja schematu bazy danych (MySQL), "
            "dodanie testów jednostkowych (docelowe pokrycie 70%), CI/CD pipeline, "
            "zachowanie wszystkich funkcjonalności, zero downtime deployment."
        ),
        "rzeczywiste_godziny": 1440,
        "typ_projektu": "legacy",
        "historia_klienta": "Klient refaktorował już moduł zamówień (PHP 5.6→7.4, 900h). Ten moduł jest bardziej złożony.",
        "wzorce_ryzyk": "Przepisanie bez testów regresji jest ryzykowne — wiele edge case'ów w logice reklamacji.",
        "komentarz_pm": "Dodanie testów od zera zajęło 35% czasu projektu — warto było dla redukcji ryzyka.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Modernizacja systemu zarządzania zamówieniami hurtowymi — Oracle Forms 6i na web. "
            "Migracja 120 formularzy Oracle Forms do aplikacji webowej Angular + REST API. "
            "Zachowanie wszystkich reguł biznesowych, migracja danych Oracle, "
            "szkolenia użytkowników (300 osób), działanie równoległe przez 3 miesiące."
        ),
        "rzeczywiste_godziny": 2600,
        "typ_projektu": "legacy",
        "historia_klienta": "System z 1998 roku. Nigdy modernizowany. Klucz do działalności operatora.",
        "wzorce_ryzyk": "Oracle Forms migracja — wiele ukrytych triggerów i procedur PL/SQL. +60% do estymacji.",
        "komentarz_pm": "Odkryliśmy 200 procedur PL/SQL z logiką biznesową nieujętą w dokumentacji.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Optymalizacja wydajności systemu CRM — czas odpowiedzi strony wzrósł z 2s do 45s. "
            "Profilowanie SQL (Oracle), optymalizacja 150 wolnych zapytań, indeksy, partycjonowanie tabel, "
            "wprowadzenie cache (Redis), archiwizacja danych (5 lat historii do cold storage). "
            "Cel: powrót do < 3s dla 95% żądań."
        ),
        "rzeczywiste_godziny": 520,
        "typ_projektu": "legacy",
        "historia_klienta": "CRM działa od 8 lat — problemy wydajnościowe narastały przez 2 lata.",
        "wzorce_ryzyk": "Optymalizacja istniejącego schematu DB bez przebudowy — trudno przewidzieć efekty przed profilowaniem.",
        "komentarz_pm": "Zidentyfikowano 3 kluczowe zapytania N+1 odpowiadające za 70% degradacji — trafna diagnoza.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Upgrade i hardening serwera RADIUS do autentykacji PPPoE — "
            "migracja z FreeRADIUS 2.x do FreeRADIUS 3.x na nowym sprzęcie, "
            "implementacja EAP-TLS, integracja z nowym LDAP, "
            "testy failover, dokumentacja, obsługa 2 milionów sesji dziennie."
        ),
        "rzeczywiste_godziny": 380,
        "typ_projektu": "legacy",
        "historia_klienta": "Krytyczny element infrastruktury — ostatni upgrade był 6 lat temu.",
        "wzorce_ryzyk": "Migracja live systemu autentykacji — zero downtime wymagane, okno serwisowe max 30 minut.",
        "komentarz_pm": "Testy przed migracją były kluczowe — cut-over przebiegł sprawnie w 15 minut.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Dekomisja i zastąpienie systemu fakturowania dla klientów hurtowych. "
            "Stary system: RPG na IBM AS/400 (iSeries), nowy: Java + PostgreSQL + Jasper Reports. "
            "Migracja danych z 15 lat historii, równoległe działanie przez 6 miesięcy, "
            "szkolenie działu finansowego (50 osób), certyfikacja przez audytorów."
        ),
        "rzeczywiste_godziny": 3800,
        "typ_projektu": "legacy",
        "historia_klienta": "AS/400 — ostatni programista znający RPG odszedł 2 lata temu.",
        "wzorce_ryzyk": "Brak ekspertów RPG/AS400 na rynku — zrozumienie logiki z kodu źródłowego bez dokumentacji.",
        "komentarz_pm": "Reverse engineering 25 lat logiki biznesowej z RPG zajął 8 miesięcy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja portalu pracowniczego z Liferay 6.2 do Liferay DXP 2024. "
            "25 portletów, 60k użytkowników, integracja z Active Directory, "
            "migracja treści, motywu graficznego, 15 niestandardowych portletów do przebudowy. "
            "Zachowanie SSO i uprawnień rolowych."
        ),
        "rzeczywiste_godziny": 1200,
        "typ_projektu": "legacy",
        "historia_klienta": "Klient miał poprzednią migrację Liferay (5.x → 6.2) — 700h, dostarczono na czas.",
        "wzorce_ryzyk": "Niestandardowe portlety Liferay — API znacznie zmieniło się między wersjami.",
        "komentarz_pm": "7 z 15 portletów wymagało przepisania od nowa ze względu na zmiany API Liferay.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Security hardening systemu telco klasy OSS — system zarządzania siecią działający od 10 lat. "
            "Audyt bezpieczeństwa (150 punktów kontrolnych), implementacja poprawek, "
            "aktualizacja 45 zależności (CVE), wdrożenie WAF, "
            "segmentacja sieci, logi bezpieczeństwa do SIEM, certyfikacja ISO 27001."
        ),
        "rzeczywiste_godziny": 960,
        "typ_projektu": "legacy",
        "historia_klienta": "Ostatni audyt bezpieczeństwa 4 lata temu. Dług techniczny w zakresie security bardzo duży.",
        "wzorce_ryzyk": "Security hardening starych systemów — zależności często podatne, regresja po aktualizacji.",
        "komentarz_pm": "Aktualizacja 12 zależności spowodowała regresję wymagającą dodatkowej pracy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Przepisanie silnika reguł taryfowych z PL/SQL (40k linii) na mikroserwis Java. "
            "Reguły cenowe dla 200 planów taryfowych, testowanie paragonów (10k przypadków testowych), "
            "shadow mode — równoległe działanie starego i nowego przez 3 miesiące z porównaniem wyników. "
            "Zero tolerancji na błędy w naliczaniu opłat."
        ),
        "rzeczywiste_godziny": 2800,
        "typ_projektu": "legacy",
        "historia_klienta": "Silnik taryfowy — najważniejszy element bilingowy. Jeden błąd = milionowe reklamacje.",
        "wzorce_ryzyk": "Silniki taryfowe: każda reguła ma wyjątki, każdy wyjątek ma wyjątki. +50% do estymacji.",
        "komentarz_pm": "Odkryto 35 nieudokumentowanych reguł w PL/SQL podczas analizy kodu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Modernizacja systemu wydruku i dystrybucji faktur papierowych. "
            "Stary system: skrypty Perl + cron + drukarka matrix. "
            "Nowy: microservice Java, PDF generation (iText), "
            "integracja z dostawcą usług pocztowych API, tracking wysyłki, "
            "archiwum elektroniczne. 200k faktur miesięcznie."
        ),
        "rzeczywiste_godziny": 680,
        "typ_projektu": "legacy",
        "historia_klienta": "Prosty zakres — Perl skrypty dobrze udokumentowane.",
        "wzorce_ryzyk": "Integracja z zewnętrznym dostawcą pocztowym — API może się zmieniać.",
        "komentarz_pm": "Projekt przebiegł sprawnie — Perl był dobrze udokumentowany, co rzadkie.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Refactoring monolitu obsługi klienta — 1.2 mln linii kodu Delphi. "
            "Wydzielenie 6 modułów do osobnych serwisów, "
            "zachowanie bazy danych Firebird bez zmian, "
            "nowe REST API dla każdego serwisu, "
            "stopniowa migracja bez zatrzymania produkcji (strangler fig pattern)."
        ),
        "rzeczywiste_godziny": 5200,
        "typ_projektu": "legacy",
        "historia_klienta": "Monolit rozwijany przez 18 lat — 6 różnych zespołów zostawiło swój ślad.",
        "wzorce_ryzyk": "Delphi eksperci trudno dostępni na rynku. Monolit z ukrytymi zależnościami między modułami.",
        "komentarz_pm": "Zidentyfikowano cykliczne zależności między modułami wymagające 4 miesięcy analizy przed kodowaniem.",
        "zrodlo": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYP: AI — projekty z ML/AI/LLM
    # ─────────────────────────────────────────────────────────────────────────

    {
        "opis_projektu": (
            "Model predykcji churnu klientów mobilnych. "
            "Pipeline ML: ekstrakcja cech z danych bilingowych i CRM (12 miesięcy historii, "
            "500+ cech), trenowanie modeli (XGBoost, LightGBM, ensemble), "
            "threshold optimization, wyjaśnialność (SHAP), "
            "API do codziennej predykcji dla 5 milionów klientów, "
            "dashboard dla działu retencji, A/B test z grupą kontrolną."
        ),
        "rzeczywiste_godziny": 1680,
        "typ_projektu": "ai",
        "historia_klienta": "Klient miał wcześniej prosty scoring regresji logistycznej — chce ML z lepszą jakością.",
        "wzorce_ryzyk": "Feature engineering na danych bilingowych — jakość danych zazwyczaj gorsza niż zakładano.",
        "komentarz_pm": "Czyszczenie i normalizacja danych z 3 różnych systemów bilingowych zajęły 40% projektu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Chatbot obsługi klienta oparty na LLM (GPT-4 / Claude). "
            "Obsługa 50 najczęstszych pytań klientów (FAQ, statusy zamówień, faktury), "
            "integracja z systemami CRM i bilingowym przez API, "
            "escalation do agenta ludzkiego, logging konwersacji, "
            "dashboard analityczny, fine-tuning na historycznych transkryptach, "
            "wielojęzyczność (PL, EN, UA)."
        ),
        "rzeczywiste_godziny": 1240,
        "typ_projektu": "ai",
        "historia_klienta": "Klient ma obecne centrum obsługi klienta — chatbot ma odciążyć 30% ruchu.",
        "wzorce_ryzyk": "Integracja LLM z systemami transakcyjnymi — hallucynacje LLM krytyczne przy danych finansowych.",
        "komentarz_pm": "Guardrails przeciwko hallucynacjom i testy adversarialne zajęły 2x więcej niż planowano.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System wykrywania anomalii w sieci telekomunikacyjnej. "
            "Analiza strumieni danych z 10k urządzeń sieciowych (NetFlow, SNMP), "
            "modele Isolation Forest + Autoencoder dla detekcji anomalii, "
            "korelacja zdarzeń, automatyczne alerty dla NOC, "
            "dashboard real-time w Grafana, integracja z systemem ticketingowym."
        ),
        "rzeczywiste_godziny": 1480,
        "typ_projektu": "ai",
        "historia_klienta": "Operator ma duże doświadczenie z systemami monitorowania — ale pierwszy projekt ML.",
        "wzorce_ryzyk": "Dane z urządzeń sieciowych mają wiele braków i szumów — preprocessing krytyczny.",
        "komentarz_pm": "Wybór progu anomalii był trudny — wymagał 2 miesięcy kalibracji z zespołem NOC.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Silnik rekomendacji ofert dla klientów indywidualnych. "
            "Collaborative filtering + content-based dla rekomendacji upgradów i dodatków. "
            "A/B testy w czasie rzeczywistym, personalizacja powiadomień push, "
            "integracja z platformą e-commerce i CRM, "
            "monitoring metryk biznesowych (CTR, konwersja), "
            "MLflow do wersjonowania modeli."
        ),
        "rzeczywiste_godziny": 1360,
        "typ_projektu": "ai",
        "historia_klienta": "Klient prowadził ręczne kampanie marketingowe — pierwsza personalizacja AI.",
        "wzorce_ryzyk": "Cold start problem dla nowych klientów. Dane o zachowaniu rzadkie dla prepaid.",
        "komentarz_pm": "Cold start wymagał osobnego podejścia dla 40% bazy — niedoszacowany w planowaniu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "NLP pipeline do automatycznej klasyfikacji i routingu zgłoszeń serwisowych. "
            "Klasyfikacja do 45 kategorii, ekstrakcja encji (numer klienta, adres, typ usługi), "
            "sentiment analysis, automatyczne odpowiedzi dla prostych zgłoszeń, "
            "model BERT fine-tuned na 200k historycznych zgłoszeń, "
            "interfejs do korygowania predykcji przez agentów."
        ),
        "rzeczywiste_godziny": 960,
        "typ_projektu": "ai",
        "historia_klienta": "Klient obsługuje 50k zgłoszeń miesięcznie — klasyfikacja manualna jest wąskim gardłem.",
        "wzorce_ryzyk": "Fine-tuning BERT na specyficznym żargonie telco wymaga dużej ilości etykietowanych danych.",
        "komentarz_pm": "Etykietowanie danych treningowych (2000 zgłoszeń) przez ekspertów domenowych — 3 tygodnie.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Predykcja awarii sieci radiowych (predictive maintenance). "
            "Analiza telemetrii z 8000 stacji bazowych BTS/NodeB/eNodeB, "
            "modele predykcji awarii na 7 dni naprzód (random forest + LSTM), "
            "priorytetyzacja przeglądów technicznych, integracja z systemem field service, "
            "oszczędność kosztów przez prewencję zamiast naprawy awarii."
        ),
        "rzeczywiste_godziny": 1880,
        "typ_projektu": "ai",
        "historia_klienta": "Operator ma rozbudowane systemy monitorowania sieci — dane wysokiej jakości.",
        "wzorce_ryzyk": "Predykcja rzadkich awarii — klasy niezbalansowane, precision/recall trade-off.",
        "komentarz_pm": "Balansowanie klas i threshold tuning przy asymetrycznym koszcie błędów zajęło dużo czasu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Automatyczne tagowanie i wyszukiwanie semantyczne bazy wiedzy obsługi klienta. "
            "Embedding artykułów bazy wiedzy (sentence-transformers), "
            "vector store (Weaviate), semantic search API, "
            "integracja z CRM i chatbotem, interface dla redaktorów treści, "
            "monitoring jakości wyszukiwania (human feedback loop)."
        ),
        "rzeczywiste_godziny": 720,
        "typ_projektu": "ai",
        "historia_klienta": "10k artykułów w bazie wiedzy — klasyczne wyszukiwanie keyword-based już nie wystarcza.",
        "wzorce_ryzyk": "Jakość embeddingów zależy od jakości treści artykułów — wiele nieaktualnych.",
        "komentarz_pm": "Aktualizacja 30% artykułów bazy wiedzy przez redaktorów była konieczna przed wdrożeniem.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Computer vision do inspekcji infrastruktury sieciowej z dronów. "
            "Detekcja uszkodzeń na zdjęciach anten i masztów (YOLOv8), "
            "klasyfikacja typów uszkodzeń (pęknięcia, korozja, mechaniczne), "
            "aplikacja mobilna dla techników, integracja z systemem zarządzania majątkiem sieciowym, "
            "pipeline przetwarzania zdjęć (10k zdjęć miesięcznie)."
        ),
        "rzeczywiste_godziny": 1560,
        "typ_projektu": "ai",
        "historia_klienta": "Innowacyjny projekt — brak historycznych danych o podobnych wdrożeniach.",
        "wzorce_ryzyk": "Etykietowanie danych (uszkodzenia infrastruktury) wymaga certyfikowanych inżynierów — kosztowne i czasochłonne.",
        "komentarz_pm": "Zebranie 5000 etykietowanych zdjęć zajęło 4 miesiące — pierwsza i najtrudniejsza faza.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Dynamiczne ustalanie cen (dynamic pricing) dla usług roamingowych. "
            "Model optymalizacji cen w czasie rzeczywistym na podstawie popytu, pojemności sieci, "
            "cen konkurencji (web scraping), historycznych wzorców. "
            "Reinforcement learning (bandit algorithm), A/B testing, "
            "integracja z systemem billingowym, dashboard revenue managementu."
        ),
        "rzeczywiste_godziny": 2100,
        "typ_projektu": "ai",
        "historia_klienta": "Klient ma doświadczenie z BI — ale pierwszy projekt RL w środowisku produkcyjnym.",
        "wzorce_ryzyk": "RL w produkcji — niewłaściwa nagroda może prowadzić do niezamierzonego zachowania systemu.",
        "komentarz_pm": "Simulation environment przed wdrożeniem produkcyjnym był kluczowy — zajął 3 miesiące.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Automatyczne generowanie raportów technicznych z logów sieci. "
            "Pipeline: logi syslog/NetFlow → preprocessing → LLM (Claude) → raport PDF/Word. "
            "Szablony raportów dla NOC, działu sprzedaży, zarządu. "
            "Harmonogram automatycznych wysyłek email, "
            "feedback od odbiorców do poprawy jakości generowanych treści."
        ),
        "rzeczywiste_godziny": 580,
        "typ_projektu": "ai",
        "historia_klienta": "Raporty generowane ręcznie przez analityków — 40h/tydzień oszczędności.",
        "wzorce_ryzyk": "Prompt engineering dla raportów technicznych wymaga iteracji z odbiorcami.",
        "komentarz_pm": "Iteracje z odbiorcami raportów zajęły 6 tygodni — ale efekt końcowy bardzo dobry.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Optymalizacja pojemności sieci pakietowej z wykorzystaniem ML. "
            "Predykcja ruchu (LSTM na danych z 3 lat), "
            "automatyczne rekomendacje rozbudowy pojemności, "
            "symulator co-if dla planistów sieci, "
            "integracja z systemami zarządzania siecią, "
            "dashboard dla działu planowania."
        ),
        "rzeczywiste_godziny": 1720,
        "typ_projektu": "ai",
        "historia_klienta": "Operator posiada wysokiej jakości dane historyczne ruchu — dobry punkt startowy dla ML.",
        "wzorce_ryzyk": "Predykcja ruchu na 12+ miesięcy naprzód — dokładność modelu spada drastycznie dla długich horyzontów.",
        "komentarz_pm": "Zarządzanie oczekiwaniami biznesu odnośnie dokładności predykcji było kluczowym wyzwaniem.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Proof of concept: asystent AI dla specjalistów sieci oparty na RAG. "
            "Baza wiedzy: dokumentacja techniczna sprzętowa (5000 dokumentów), "
            "procedury konfiguracyjne, logi historycznych awarii. "
            "LangChain + Claude, interface webowy, ewaluacja odpowiedzi (RAGAS). "
            "Cel: PoC w 8 tygodni, 20 użytkowników pilotażowych."
        ),
        "rzeczywiste_godziny": 320,
        "typ_projektu": "ai",
        "historia_klienta": "Pierwszy projekt LLM w organizacji — PoC do oceny wartości przed inwestycją.",
        "wzorce_ryzyk": "PoC: ograniczony zakres, akceptowalna jakosc 'wystarczajaco dobra' - nie produkcja.",
        "komentarz_pm": "PoC dostarczony w 7 tygodni. Decyzja o wdrożeniu produkcyjnym podjęta po pozytywnym feedbacku.",
        "zrodlo": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYP: MIGRACJA — przeniesienie infrastruktury, danych, platform
    # ─────────────────────────────────────────────────────────────────────────

    {
        "opis_projektu": (
            "Migracja on-premise centrum danych do AWS (lift-and-shift + optimize). "
            "150 serwerów wirtualnych → EC2/ECS, "
            "migracja baz danych (Oracle → RDS Aurora, MongoDB → DocumentDB), "
            "sieć: VPN + Direct Connect, "
            "storage: SAN → S3 + EFS, "
            "disaster recovery, monitoring CloudWatch, IAM redesign. "
            "Zero downtime dla krytycznych systemów."
        ),
        "rzeczywiste_godziny": 4200,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient nie miał wcześniej workloadów w chmurze — pierwsza migracja cloud.",
        "wzorce_ryzyk": "Pierwsza migracja cloud: curve of learning, zmiany w sieciowaniu, IAM policies — +50%.",
        "komentarz_pm": "Sieciowanie i IAM redesign zajęły 2x więcej niż planowano — archetypowe problemy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja bazy danych Oracle 12c (3TB) do PostgreSQL 16. "
            "Konwersja schematów (ora2pg + ręczne dostosowania), migracja stored procedures (PL/SQL → PL/pgSQL), "
            "migracja danych z zachowaniem integralności, "
            "testy regresji aplikacji (12 aplikacji używa tej bazy), "
            "cutover plan z oknem serwisowym 4h."
        ),
        "rzeczywiste_godziny": 1640,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient realizował mniejszą migrację Oracle→PG (500GB) 2 lata temu — 800h, z małymi problemami.",
        "wzorce_ryzyk": "PL/SQL → PL/pgSQL: package'y Oracle nie mają odpowiednika — refactoring wymagany.",
        "komentarz_pm": "280 stored procedures wymagało ręcznej konwersji ze względu na Oracle-specific SQL.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja 8 serwisów z bare metal do Kubernetes (on-premise). "
            "Konteneryzacja (Dockerfile dla każdego serwisu), "
            "Helm charts, konfiguracja Ingress/NetworkPolicy, "
            "persistent volumes dla serwisów stateful, "
            "CI/CD pipeline (GitLab CI → ArgoCD), "
            "monitoring (Prometheus + Grafana), "
            "load testing po migracji."
        ),
        "rzeczywiste_godziny": 1080,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient miał wcześniej 3 serwisy na K8s (360h). Teraz skaluje na całą organizację.",
        "wzorce_ryzyk": "Serwisy stateful (bazy danych) w K8s wymagają szczególnej uwagi na storage i backup.",
        "komentarz_pm": "Persistent volumes i backup stateful workloadów zajęły 30% projektu — dobrze oszacowane.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Przeniesienie data lake z on-premise Hadoop/HDFS do Databricks na Azure. "
            "Migracja 200TB danych, przepisanie 150 job Spark (Scala → PySpark), "
            "Delta Lake format, Unity Catalog dla governance, "
            "migracja pipeline MLflow, "
            "szkolenie 25 data scientistów i data engineerów."
        ),
        "rzeczywiste_godziny": 2800,
        "typ_projektu": "migracja",
        "historia_klienta": "Hadoop od 7 lat — dług techniczny bardzo duży. Klient chce nowoczesny stack.",
        "wzorce_ryzyk": "Scala → PySpark: różnice w API, niekompatybilność niektórych bibliotek.",
        "komentarz_pm": "20 z 150 jobów miało zakodowane na stałe ścieżki HDFS — wymagały głębokiej przebudowy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja systemu zarządzania dokumentami z FileNet P8 do SharePoint Online (Microsoft 365). "
            "2 miliony dokumentów, zachowanie metadanych i historii wersji, "
            "migracja uprawnień (150 grup AD), "
            "integracja z aplikacjami biznesowymi przez Graph API, "
            "szkolenia użytkowników (500 osób)."
        ),
        "rzeczywiste_godziny": 1480,
        "typ_projektu": "migracja",
        "historia_klienta": "FileNet P8 działa od 12 lat — brak wewnętrznej wiedzy, vendor support wygasa.",
        "wzorce_ryzyk": "Migracja metadanych FileNet → SharePoint — różne modele obiektów.",
        "komentarz_pm": "Mapowanie 80 typów dokumentów FileNet na content types SharePoint zajęło miesiąc.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja systemu VoIP z Cisco CUCM na Cisco Webex Calling (cloud PBX). "
            "2500 użytkowników, 180 lokalizacji, migracja numerów (DID), "
            "konfiguracja urządzeń (telefony IP, softphone), "
            "integracja z systemem call center, "
            "szkolenia IT helpdesk i użytkowników końcowych."
        ),
        "rzeczywiste_godziny": 860,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient zna Cisco — wcześniejsza migracja CUCM (v8 → v11) 520h.",
        "wzorce_ryzyk": "Migracja numerów DID w live środowisku — okno serwisowe per lokalizacja.",
        "komentarz_pm": "Planowanie okien serwisowych dla 180 lokalizacji było logistycznie złożone.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja platformy e-commerce z Magento 1.9 do Magento 2.4. "
            "100k produktów, 500k klientów, historia zamówień (3 lata), "
            "migracja 25 niestandardowych modułów (przepisanie API), "
            "nowy motyw graficzny (PWA), "
            "integracja z ERP i systemem magazynowym."
        ),
        "rzeczywiste_godziny": 2200,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient nie miał poprzednich migracji Magento — ale doświadczeni z PHP i e-commerce.",
        "wzorce_ryzyk": "Magento 1→2: architektura całkowicie różna — moduły M1 wymagają przepisania od zera.",
        "komentarz_pm": "8 z 25 modułów okazało się niemożliwych do migracji — przepisano od podstaw.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja poczty email (25k skrzynek) z Lotus Notes 9 do Microsoft 365 Exchange Online. "
            "Migracja maili (archiwum 5 lat), kontaktów, kalendarzy, "
            "aplikacje Lotus Notes (15 baz danych) → SharePoint + Power Apps, "
            "DNS cutover, konfiguracja MX, DKIM/DMARC, "
            "szkolenia użytkowników."
        ),
        "rzeczywiste_godziny": 1340,
        "typ_projektu": "migracja",
        "historia_klienta": "Lotus Notes od 1996 roku — klient nigdy nie miał chmury.",
        "wzorce_ryzyk": "Lotus Notes bazy danych to często ukryte procesy biznesowe — inwentaryzacja krytyczna.",
        "komentarz_pm": "Zinwentaryzowano 47 baz Notes zamiast planowanych 15 — każda to osobny zakres.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Lift-and-shift 30 aplikacji webowych na Azure Kubernetes Service. "
            "Konteneryzacja (Docker), konfiguracja AKS, "
            "Azure Container Registry, Azure DevOps pipelines, "
            "Azure Monitor + Application Insights, "
            "Key Vault dla sekretów, "
            "Private Endpoints dla bezpieczeństwa."
        ),
        "rzeczywiste_godziny": 1860,
        "typ_projektu": "migracja",
        "historia_klienta": "5 z 30 aplikacji już na Azure — klient zna platformę.",
        "wzorce_ryzyk": "Aplikacje z hard-coded connection strings — wymagają refactoringu przed konteneryzacją.",
        "komentarz_pm": "12 aplikacji miało zakodowane sekrety w kodzie — wymuszało refactoring przed migracją.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja systemu monitorowania sieci (Cacti + Nagios) do Zabbix 6.4 + Grafana. "
            "1200 monitorowanych urządzeń, migracja 800 szablonów, "
            "konfiguracja triggerów i alertów, "
            "integracja z PagerDuty do eskalacji, "
            "dashboardy Grafana per typ sieci (core, dostęp, radiowa). "
            "Działanie równoległe przez 2 miesiące."
        ),
        "rzeczywiste_godziny": 760,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient używa Nagiosa od 10 lat — dobrze zdokumentowana konfiguracja.",
        "wzorce_ryzyk": "Nagios → Zabbix: różne koncepcje szablonów — konwersja nie jest 1:1.",
        "komentarz_pm": "Konwersja szablonów zajęła 30% więcej niż planowano — ale dashboardy Grafana bardzo dobrze odebrane.",
        "zrodlo": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DODATKOWE — rozszerzenie skali i różnorodności
    # ─────────────────────────────────────────────────────────────────────────

    {
        "opis_projektu": (
            "Mikroserwis do obsługi płatności cyklicznych (subskrypcje). "
            "Automatyczne pobieranie opłat miesięcznych, obsługa nieudanych transakcji (retry logic), "
            "zarządzanie kartami płatniczymi (tokenizacja PCI-DSS), "
            "powiadomienia SMS/email, raportowanie finansowe, "
            "integracja z 2 bramkami płatności (Stripe + lokalna)."
        ),
        "rzeczywiste_godziny": 780,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient oferuje subskrypcje, ale obsługa płatności jest manualna.",
        "wzorce_ryzyk": "PCI-DSS compliance: audyt i certyfikacja zawsze wydłuża projekt o 6-8 tygodni.",
        "komentarz_pm": "Certyfikacja PCI-DSS SAQ D zajęła 8 tygodni — ale planowano 4.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System zarządzania flotą pojazdów serwisowych operatora. "
            "Śledzenie GPS (500 pojazdów), planowanie tras i zleceń serwisowych, "
            "mobilna aplikacja dla techników (React Native), "
            "integracja z systemem zarządzania majątkiem, "
            "raporty wydajności i kosztów, "
            "alerty o przekroczeniu prędkości i stref."
        ),
        "rzeczywiste_godziny": 1120,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient zarządza flotą manualnie — pierwsze wdrożenie telematyki.",
        "wzorce_ryzyk": "Integracja z urządzeniami GPS różnych producentów — brak standardu protokołu.",
        "komentarz_pm": "Protokoły GPS różnych producentów: 4 różne formaty danych wymagające osobnych parserów.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Wewnętrzna platforma developer portal (Internal Developer Platform). "
            "Katalog API (AsyncAPI + OpenAPI), dokumentacja techniczna (Docusaurus), "
            "self-service infrastructure (Backstage), CI/CD templates, "
            "integracja z GitLab, Jira, Confluence. "
            "Zwiększenie produktywności 300 developerów."
        ),
        "rzeczywiste_godziny": 1440,
        "typ_projektu": "nowy",
        "historia_klienta": "Organizacja ma 12 zespołów developerskich — brak spójnych standardów.",
        "wzorce_ryzyk": "Backstage wymaga dużego nakładu na konfigurację i adopcję — często niedoceniane.",
        "komentarz_pm": "Backstage plugins i integracje zajęły 2x więcej niż dokumentacja sugerowała.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Modernizacja CDN dla dostarczania treści wideo (IPTV). "
            "Wymiana Varnish 4 na Varnish 7 + nowa konfiguracja VCL, "
            "dodanie warstwy cache L2 (Redis), "
            "origin shield, purge API, "
            "monitoring hit ratio i latency, "
            "obsługa 10Gbps peak traffic."
        ),
        "rzeczywiste_godziny": 420,
        "typ_projektu": "legacy",
        "historia_klienta": "CDN działa od 5 lat — Varnish 4 wychodzi z EOL support.",
        "wzorce_ryzyk": "VCL między wersjami — breaking changes w syntaxie i zachowaniu.",
        "komentarz_pm": "VCL migration z V4 na V7 miał breaking changes — ale dobrze udokumentowane przez Varnish.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Automatyzacja testów regresji dla systemu bilingowego. "
            "Framework testowy (Pytest + Selenium), "
            "600 przypadków testowych dla procesów bilingowych, "
            "integracja z CI/CD (GitLab CI), "
            "testy dymne po każdym deployu, "
            "reporting (Allure), "
            "środowisko testowe z anonimizowanymi danymi produkcyjnymi."
        ),
        "rzeczywiste_godziny": 860,
        "typ_projektu": "nowy",
        "historia_klienta": "Testy regresji robione manualnie przez 6 QA engineerów — 2 tygodnie per release.",
        "wzorce_ryzyk": "Automatyzacja testów Selenium jest krucha — każda zmiana UI może powodować flaky tests.",
        "komentarz_pm": "Przejście na Page Object Model od początku było dobrą decyzją — testy stabilne.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja systemu zarządzania tożsamością z Microsoft AD + LDAP do Azure AD B2C + Entra ID. "
            "80k użytkowników, migracja kont, synchronizacja atrybutów, "
            "konfiguracja MFA, SSPR, Conditional Access Policies, "
            "aktualizacja 40 aplikacji do OAuth2/OIDC (z LDAP bind), "
            "szkolenia helpdesk."
        ),
        "rzeczywiste_godziny": 1600,
        "typ_projektu": "migracja",
        "historia_klienta": "Klient ma 40 aplikacji z auth przez LDAP — każda wymaga osobnej pracy.",
        "wzorce_ryzyk": "Aplikacje z LDAP bind: wiele legacy apps nie wspiera OAuth2 — adapter lub refactoring.",
        "komentarz_pm": "8 aplikacji wymagało głębokiego refactoringu auth — bez możliwości prostego adaptera.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Sentiment analysis dla opinii klientów z wszystkich kanałów. "
            "Integracja danych z: call center (transkrypcje ASR), email, chat, social media, ankiety NPS. "
            "Fine-tuning modelu BERT-large-polish, "
            "dashboard dla zarządu (real-time NPS, tematy, trendy), "
            "alerty przy nagłym spadku sentymentu dla produktu/regionu."
        ),
        "rzeczywiste_godziny": 1140,
        "typ_projektu": "ai",
        "historia_klienta": "Klient analizuje NPS raz na kwartał ręcznie — potrzeba real-time.",
        "wzorce_ryzyk": "Transkrypcje call center mają niską jakość (szumy, akcenty) — preprocessing ASR trudny.",
        "komentarz_pm": "Jakość transkrypcji ASR wymagała dodatkowego modułu korekty — nieplanowany zakres.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System zarządzania siecią dostępową DSL (xDSL management system). "
            "DSLAM configuration API, line profiling, troubleshooting tool dla techników, "
            "integracja z CRM (podgląd parametrów linii klienta), "
            "bulk provisioning, alerty degradacji jakości linii (SNR, attenuation). "
            "Stack: Python + Django, PostgreSQL, NETCONF/YANG."
        ),
        "rzeczywiste_godziny": 1380,
        "typ_projektu": "nowy",
        "historia_klienta": "Operator zarządza 500k linii DSL — obecne narzędzia CLI nieefektywne.",
        "wzorce_ryzyk": "NETCONF/YANG integracja z urządzeniami różnych vendorów — niezgodności YANGmodeli.",
        "komentarz_pm": "Modele YANG różnych vendorów DSLAMów były niezgodne — osobne adaptery dla każdego.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Analityczna platforma danych klientów (Customer Data Platform). "
            "Unifikacja danych z 8 źródeł (CRM, billing, sieć, aplikacja mobilna, www), "
            "single customer view, segmentacja predyktywna, "
            "integracja z narzędziami marketingowymi, "
            "pipeline Kafka + Spark Streaming, lakehouse na S3 + Delta Lake."
        ),
        "rzeczywiste_godziny": 3200,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient ma dane w silosach — pierwsza CDP implementacja.",
        "wzorce_ryzyk": "Jakość danych z 8 źródeł: każde ma inne klucze i formaty — deduplication bardzo trudna.",
        "komentarz_pm": "Identity resolution (łączenie rekordów klienta z różnych systemów) zajął 35% projektu.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Automatyczne generowanie opisów produktów w katalogu telco przy pomocy LLM. "
            "Szablony per kategoria produktu, tone of voice guidelines, "
            "A/B testy konwersji opisów AI vs ręcznych, "
            "workflow akceptacji przez redaktorów, "
            "integracja z PIM (Product Information Management), "
            "10k produktów do opisania."
        ),
        "rzeczywiste_godziny": 460,
        "typ_projektu": "ai",
        "historia_klienta": "Klient ma PIM z 10k produktów — opisy pisane ręcznie przez redaktorów.",
        "wzorce_ryzyk": "LLM generuje treści wymagające weryfikacji — workflow akceptacji krytyczny.",
        "komentarz_pm": "Kalibracja promptów per kategoria produktu zajęła dłużej niż zakładano — wiele iteracji z redaktorami.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja platform CI/CD z Jenkins (on-premise) do GitLab CI/CD (cloud). "
            "200 pipeline'ów, migracja konfiguracji Jenkinsfile → .gitlab-ci.yml, "
            "konfiguracja runnerów, integracja z SonarQube, Nexus → GitLab Packages, "
            "szkolenia dla 80 developerów. Stopniowa migracja — 20 pipeline'ów miesięcznie."
        ),
        "rzeczywiste_godziny": 720,
        "typ_projektu": "migracja",
        "historia_klienta": "Jenkins od 8 lat — duży dług techniczny, wiele shared libraries.",
        "wzorce_ryzyk": "Shared Jenkins libraries: brak odpowiednika w GitLab CI — refactoring wymagany.",
        "komentarz_pm": "Shared libraries Jenkinsa wymagały przepisania na GitLab CI components — 4 tygodnie dodatkowej pracy.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "System zarządzania konfiguracją sieci (Network Configuration Management). "
            "Automatyczne backupy konfiguracji 3000 urządzeń (routery, switche, firewalle), "
            "diff konfiguracji, rollback, compliance check, "
            "integracja z systemem ticketingowym (zmiany wymagają ticketu), "
            "Web UI + REST API. Stack: Python + Ansible + PostgreSQL + React."
        ),
        "rzeczywiste_godziny": 1280,
        "typ_projektu": "nowy",
        "historia_klienta": "Backupy konfiguracji ręczne przez skrypty — brak spójności i historii zmian.",
        "wzorce_ryzyk": "3000 urządzeń różnych vendorów — Ansible moduły mają różną dojrzałość.",
        "komentarz_pm": "Stare urządzenia bez wsparcia Ansible wymagały własnych modułów SSH — 15% urządzeń.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Rozbudowa systemu BI o moduł analiz w czasie rzeczywistym. "
            "Architektura Lambda: warstwa batch (Spark) + warstwa speed (Kafka + Flink), "
            "dashboard real-time KPIs w Grafana, "
            "alerty biznesowe (spadek sprzedaży, wzrost churnu), "
            "8 nowych raportów operacyjnych."
        ),
        "rzeczywiste_godziny": 1560,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient ma działający system BI batch — rozbudowa o real-time.",
        "wzorce_ryzyk": "Flink i Kafka wymagają specjalistów — i są trudne w testowaniu distributed.",
        "komentarz_pm": "Testy failure scenarios w distributed streaming były bardzo czasochłonne.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Konsolidacja 4 systemów monitorowania (Zabbix, Nagios, Prometheus, Dynatrace) "
            "do jednej platformy Dynatrace Full Stack. "
            "Konfiguracja agentów na 400 serwerach, instrumentacja 60 aplikacji, "
            "migracja alertów (300 reguł), dashboardy Davis AI, "
            "deprecacja starych systemów, dokumentacja."
        ),
        "rzeczywiste_godziny": 940,
        "typ_projektu": "migracja",
        "historia_klienta": "4 narzędzia monitorowania = chaos — team NOC sprawdza 4 panele.",
        "wzorce_ryzyk": "Dynatrace OneAgent na legacy JVM może powodować problemy wydajnościowe.",
        "komentarz_pm": "2 aplikacje na starych JVM miały problemy z agentem — wymusiły aktualizację JVM.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Wdrożenie SIEM (Security Information and Event Management) — Splunk Enterprise. "
            "Integracja 35 źródeł logów (firewalle, serwery, aplikacje, AD), "
            "80 reguł detekcji zagrożeń (MITRE ATT&CK), "
            "playbooki odpowiedzi na incydenty, "
            "dashboard SOC, integracja z ticketingiem, "
            "szkolenia analityków bezpieczeństwa."
        ),
        "rzeczywiste_godziny": 1620,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient nie ma SIEM — incydenty bezpieczeństwa wykrywane z opóźnieniem.",
        "wzorce_ryzyk": "Splunk: wolumeny logów zawsze większe niż zakładano — koszty licencji i storage.",
        "komentarz_pm": "Wolumeny logów były 3x większe niż prognozowane — redesign architektury zbierania.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Nowa wersja API bilingowego (REST v3) z zachowaniem kompatybilności wstecznej z v1/v2. "
            "12 nowych endpointów, wersjonowanie API, "
            "deprecacja starych endpointów (plan 18 miesięcy), "
            "GraphQL gateway opcjonalny, "
            "dokumentacja OpenAPI 3.1, SDK Python/Java, "
            "testy kontraktowe (consumer-driven contracts)."
        ),
        "rzeczywiste_godziny": 1020,
        "typ_projektu": "legacy",
        "historia_klienta": "API v1 i v2 używane przez 40 zewnętrznych partnerów — kompatybilność wsteczna krytyczna.",
        "wzorce_ryzyk": "Testy kontraktowe z 40 partnerami — każdy ma inną interpretację API contract.",
        "komentarz_pm": "Koordynacja consumer-driven contracts z 40 partnerami zewnętrznymi trwała 2 miesiące.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Platforma zarządzania zgodą na przetwarzanie danych osobowych (Consent Management Platform). "
            "GDPR i ePrivacy compliance, rejestr zgód klientów, "
            "widget web/mobile do zbierania zgód, API dla systemów marketingowych, "
            "eksport raportów dla DPO, prawo do bycia zapomnianym (usuwanie danych z 12 systemów)."
        ),
        "rzeczywiste_godziny": 1080,
        "typ_projektu": "nowy",
        "historia_klienta": "Klient otrzymał karę UODO — pilne wdrożenie CMP.",
        "wzorce_ryzyk": "Integracja z 12 systemami dla prawa do bycia zapomnianym — każda integracja osobna.",
        "komentarz_pm": "2 systemy legacy nie miały API do usuwania danych — wymagały manualnych procedur.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Moduł obsługi zamówień urządzeń końcowych (CPE) dla klientów biznesowych. "
            "Konfiguracja urządzeń (router, ONT, set-top box) przez API ZeroTouch Provisioning, "
            "śledzenie wysyłki, aktywacja, auto-diagnostyka po instalacji, "
            "portal klienta do zarządzania urządzeniami, "
            "integracja z systemem magazynowym i logistyką."
        ),
        "rzeczywiste_godziny": 1460,
        "typ_projektu": "nowy",
        "historia_klienta": "Provisioning CPE manualny przez techników — 3 wizyty per klient.",
        "wzorce_ryzyk": "ZeroTouch Provisioning z urządzeniami różnych vendorów — brak pełnej standaryzacji TR-369.",
        "komentarz_pm": "TR-369 (USP) wsparcie u jednego z vendorów było niepełne — osobny adapter.",
        "zrodlo": "curated",
    },
    {
        "opis_projektu": (
            "Migracja systemu helpdesk z Remedy ITSM do ServiceNow. "
            "Migracja 5 lat historii ticketów (200k rekordów), "
            "konfiguracja ITIL workflows (Incident, Problem, Change, Request), "
            "integracja z monitoringiem (Zabbix alerts → ServiceNow), "
            "custom aplikacja do zarządzania infrastrukturą telco w ServiceNow. "
            "600 użytkowników."
        ),
        "rzeczywiste_godziny": 1760,
        "typ_projektu": "migracja",
        "historia_klienta": "Remedy ITSM od 10 lat — mocno skostniały, wiele customizacji.",
        "wzorce_ryzyk": "Customizacje Remedy często niemożliwe do 1:1 przeniesienia na ServiceNow.",
        "komentarz_pm": "30% customizacji Remedy wymagało przeprojektowania dla ServiceNow — decyzja biznesowa o uproszczeniu.",
        "zrodlo": "curated",
    },
]


def generate_curated(output_dir: str = "gepa/data/training") -> int:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    for example in EXAMPLES:
        fname = out / f"curated_{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(example, ensure_ascii=False, indent=2))
        written += 1

    return written


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "gepa/data/training"
    count = generate_curated(output_dir)
    print(f"Zapisano {count} przykładów do {output_dir}/")

    # Statystyki
    typy = {}
    godziny = []
    for ex in EXAMPLES:
        t = ex.get("typ_projektu", "?")
        typy[t] = typy.get(t, 0) + 1
        godziny.append(ex["rzeczywiste_godziny"])

    print(f"\nRozkład typów: {typy}")
    print(f"Zakres godzin: {min(godziny)}h – {max(godziny)}h")
    print(f"Mediana: {sorted(godziny)[len(godziny)//2]}h")
