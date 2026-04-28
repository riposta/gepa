def metryka_wyceny(gold, pred, trace=None) -> float:
    rzeczywiste = getattr(gold, "rzeczywiste_godziny", 0) or 0
    szacunek = getattr(pred, "szacunek_godzin", 0) or 0
    uzasadnienie = getattr(pred, "uzasadnienie", "") or ""
    pewnosc = getattr(pred, "pewnosc", 0.5) or 0.5

    # Dokładność (50%)
    if rzeczywiste == 0:
        dokladnosc = 0.0
    else:
        blad = abs(szacunek - rzeczywiste) / rzeczywiste
        dokladnosc = max(0.0, 1.0 - blad)

    # Uzasadnienie (30%) — długość jako proxy jakości
    uzasadnienie_score = min(1.0, len(uzasadnienie) / 150)

    # Kalibracja pewności (20%)
    if pewnosc < 0.2 or pewnosc > 0.95:
        kalibracja = 0.3
    elif 0.3 <= pewnosc <= 0.85:
        kalibracja = 1.0
    else:
        kalibracja = 0.7

    return round(
        0.5 * dokladnosc + 0.3 * uzasadnienie_score + 0.2 * kalibracja,
        4,
    )


def metryka_wyceny_z_feedbackiem(gold, pred, trace=None) -> tuple[float, str]:
    score = metryka_wyceny(gold, pred, trace)

    rzeczywiste = getattr(gold, "rzeczywiste_godziny", 0) or 0
    szacunek = getattr(pred, "szacunek_godzin", 0) or 0
    uzasadnienie = getattr(pred, "uzasadnienie", "") or ""
    pewnosc = getattr(pred, "pewnosc", 0.5) or 0.5

    feedback_parts = []

    if rzeczywiste > 0:
        blad = (szacunek - rzeczywiste) / rzeczywiste
        if blad > 0.3:
            feedback_parts.append(
                f"Szacunek za wysoki o {blad:.0%} — sprawdź czy nie duplikujesz zadań."
            )
        elif blad < -0.3:
            feedback_parts.append(
                f"Szacunek za niski o {abs(blad):.0%} — uwzględnij bufor na ryzyko i testy."
            )

    if len(uzasadnienie) < 80:
        feedback_parts.append(
            "Uzasadnienie zbyt krótkie — dodaj podział na komponenty (backend/frontend/testy)."
        )

    if pewnosc > 0.95:
        feedback_parts.append(
            "Zbyt wysoka pewność — dla nowych projektów trzymaj pewność poniżej 0.9."
        )
    elif pewnosc < 0.2:
        feedback_parts.append(
            "Zbyt niska pewność — jeśli masz historyczne dane, podnieś pewność."
        )

    feedback = " ".join(feedback_parts) if feedback_parts else "Wycena w normie."
    return score, feedback
