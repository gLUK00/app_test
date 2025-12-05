# Test e Azioni

Un **Test** è una sequenza di **Azioni**. TestGyver le esegue in ordine.

## Creare un Test

1.  Dentro una Campagna, clic **Add Test**.
2.  Inserisci nome e descrizione.
3.  **Aggiungi Variabili** (opzionale): variabili del test (es. `username`).

## Aggiungere Azioni

1.  Clic **Add Action**.
2.  **Tipo Azione**: scegli tra i plugin disponibili (HTTP, SSH, Wait...).
3.  **Configura**: compila i parametri.

> **[SCREENSHOT]** Form configurazione azione (HTTP) con campi.

### Autocompletamento Variabili
Suggerimenti mentre scrivi:

> **[SCREENSHOT]** Dropdown su `{{` con suggerimenti colorati.

*   <span style="color:blue">**Variabili Globali**</span>: `{{variable_name}}`
*   <span style="color:green">**Variabili Test**</span>: `{{app.variable_name}}`
*   <span style="color:red">**Variabili Collezione**</span>: `{{test.test_id}}`, `{{test.files_dir}}`

### Variabili di Output
Alcune azioni producono output (es. body HTTP).
*   Visibili come **Output Variables**.
*   Riutilizzabili nelle azioni successive.

## Ordine delle Azioni
Eseguite nell'ordine della lista. Riordina con drag & drop o frecce.

## Esecuzione
Puoi eseguire un singolo test dalla pagina di dettaglio prima della campagna completa.
