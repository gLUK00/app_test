# Gestione Campagne

Una **Campagna** raggruppa test per una funzionalità o flusso.

## Creare una Campagna

1.  Nel Dashboard clic **Add Campaign**.
2.  Compila:
    *   **Nome**: Unico.
    *   **Descrizione**: Facoltativa.
3.  Salva e verrai reindirizzato al dettaglio.

> **[SCREENSHOT]** Form "Add Campaign".

## Dettaglio Campagna

Centro di controllo.

> **[SCREENSHOT]** Pagina con Informazioni, File, Tests.

### 1. Informazioni
Metadati. Puoi modificare o eliminare.

### 2. Gestione File
Gestisci file associati (dati test, risorse).
*   **Upload**: Aggiungi file al workdir della campagna.
*   **Rinomina/Elimina**: Gestione file.
*   **Download**: Scarica file.

Accesso nei test via `{{test.files_dir}}`.

### 3. Lista Test
Tutti i test della campagna.
*   **Riordina**: Frecce su/giù.
*   **Aggiungi Test**: Nuovo caso.
*   **Esegui**: Avvia test singolo.

## Esecuzione Campagna

1.  Clic **Execute Campaign**.
2.  **Configura**:
    *   **Nome**: Auto-generato (es. "March 2023"), modificabile.
    *   **Ambiente**: Seleziona filière (Variabili).
    *   **Stop on Failure**: Ferma al primo errore.
3.  **Avvia**: gira in background.

> **[SCREENSHOT]** Modal esecuzione con scelta ambiente.

### Monitoraggio Live
Barra di avanzamento e stato.
*   **Blu**: In esecuzione
*   **Verde**: OK
*   **Rosso**: Errore

Clic su un report per i log.
