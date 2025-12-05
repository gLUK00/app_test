# Tests und Aktionen

Ein **Test** ist eine Abfolge von **Aktionen**. TestGyver führt sie der Reihe nach aus.

## Test erstellen

1.  In einer Kampagne auf **Add Test** klicken.
2.  Name und Beschreibung eingeben.
3.  **Variablen hinzufügen** (optional): Testspezifische Variablen (z.B. `username`).

## Aktionen hinzufügen

Bausteine des Tests.

1.  **Add Action** klicken.
2.  **Aktionstyp wählen**: Plugins wie HTTP, SSH, Wait...
3.  **Konfigurieren**: Parameter ausfüllen.

> **[SCREENSHOT]** Aktionsformular (HTTP) mit Feldern.

### Variablen-Autocomplete
Beim Tippen schlägt TestGyver Variablen vor:

> **[SCREENSHOT]** Dropdown bei `{{` mit farbigen Vorschlägen.

*   <span style="color:blue">**Globale Variablen**</span>: `{{variable_name}}`
*   <span style="color:green">**Test-Variablen**</span>: `{{app.variable_name}}`
*   <span style="color:red">**Sammlungs-Variablen**</span>: `{{test.test_id}}`, `{{test.files_dir}}`

### Output-Variablen
Manche Aktionen erzeugen Output (z.B. HTTP-Body).
*   Werden als **Output Variables** angezeigt.
*   In folgenden Aktionen nutzbar.

## Reihenfolge
Aktionen laufen in Listenreihenfolge. Per Drag & Drop oder Pfeile anpassbar.

## Ausführung
Einzelne Tests können in der Detailansicht gestartet werden, bevor die ganze Kampagne läuft.
