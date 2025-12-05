# Reports und Monitoring

Reports zeigen die Ausführungshistorie.

## Zugriff

*   **Vom Dashboard**: Tab "Reports" (falls vorhanden) oder über die Kampagne.
*   **Von der Kampagne**: Abschnitt "Reports" listet alle Läufe.

## Report-Details

Klick öffnet die Detailansicht:

![Report-Seite](../../assets/campaign_rapport.png)
> Report-Seite mit Status und Testliste.

### Header
*   **Status**: Success, Failure oder Running.
*   **Progress**: Fertigstellungsgrad.
*   **Environment**: Verwendete Umgebung.
*   **Timings**: Start, Ende, Dauer.

### Testergebnisse
Liste aller ausgeführten Tests.
*   **Status-Icon**: ✅ Pass / ❌ Fail.
*   **Logs**: Aufklappen für Details.
    *   Gesendete/empfangene Daten.
    *   Laufzeit je Aktion.
    *   Fehlermeldungen bei Fehlern.

## Echtzeit-Updates
WebSockets aktualisieren live. Kein Reload nötig.
