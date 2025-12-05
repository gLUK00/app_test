# Kampagnen verwalten

Eine **Kampagne** gruppiert Tests für ein Feature oder einen Workflow.

## Kampagne erstellen

1.  Im Dashboard auf **Add Campaign** klicken.
2.  Ausfüllen:
    *   **Name**: Eindeutiger Kampagnenname.
    *   **Beschreibung**: Optionaler Zweck.
3.  Speichern. Du wirst zur Detailseite weitergeleitet.

![Add-Campaign-Formular](../../assets/campaign_add.png)
> Formular "Add Campaign".

## Detailansicht

Kontrollzentrum der Kampagne.

![Kampagnen-Details](../../assets/campaign_detail.png)
> Details mit Information, Dateien, Tests.

### 1. Information
Zeigt Metadaten. Bearbeiten oder löschen möglich.

### 2. Dateiverwaltung
Dateien der Kampagne verwalten.
*   **Upload**: Dateien ins Workdir hochladen.
*   **Umbenennen/Löschen**: Bestehende Dateien verwalten.
*   **Download**: Dateien abrufen.

Zugriff in Tests via `{{test.files_dir}}`.

### 3. Testliste
Alle Tests der Kampagne.
*   **Reihenfolge**: Mit Pfeilen anpassen.
*   **Test hinzufügen**: Neuen Test anlegen.
*   **Ausführen**: Einzelnen Test starten.

## Kampagne ausführen

1.  **Execute Campaign** klicken.
2.  **Konfigurieren**:
    *   **Name**: Auto-generiert (z.B. "March 2023"), änderbar.
    *   **Environment**: Ziel-Umgebung (Variablen).
    *   **Stop on Failure**: Bei Fehler stoppen.
3.  **Starten**: Läuft im Hintergrund.

![Ausführungsmodal](../../assets/campaign_rapport.png)
> Ausführungsmodal mit Umgebungswahl.

### Live-Monitoring
Fortschrittsbalken und Status.
*   **Blau**: Läuft
*   **Grün**: Erfolgreich
*   **Rot**: Fehlgeschlagen

Klicke auf einen Report, um Logs zu sehen.
