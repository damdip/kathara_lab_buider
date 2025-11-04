## Kathara Lab Creator — versione semplificata - generato con gpt mini 5

Un piccolo strumento Python per creare rapidamente laboratori Kathara.
Questo progetto genera la struttura di base dei laboratori (cartella
`created_labs/`), il file `lab.conf` e i file `.startup` per ogni
dispositivo, oltre a copiare template di configurazione per router e server
se presenti.

Il README seguente spiega scopo, utilizzo e struttura in modo chiaro e
ordinato.

---

## Scopo

- Automazione della creazione dei file necessari per avviare un laboratorio
  Kathara in modo interattivo.
- Ridurre la ripetitività: crea `lab.conf`, i file `.startup` per i
  dispositivi e le directory con template di configurazione (per FRR e
  per il server web) partendo da risposte guidate.

## Contratto (input / output / criteri di successo)

- Input: nome del laboratorio, lista dispositivi, tipo di ogni dispositivo,
  numero di interfacce, domini di collisione, indirizzi IP (opzionale) e
  rotte statiche per gli host.
- Output: directory `created_labs/<lab_name>/` contenente:
  - `lab.conf`
  - `<device>.startup` per ogni dispositivo (eseguibili)
  - eventuali directory `etc/frr/` per router (con template copiati)
  - eventuali directory `var/www/html/` per server (con `index.html`)
- Successo: i file sono creati senza errori e i file `.startup` risultano
  eseguibili (permessi 755).

## Come usarlo (rapido)

1. Assicurati di avere Python 3 installato.
2. Posizionati nella radice del progetto dove si trova
   `kathara_lab_creator.py`.
3. Avvia lo script:

```bash
python3 kathara_lab_creator.py
```

Lo script è interattivo: ti guiderà passo-passo nella definizione dei
dispositivi, delle interfacce, degli IP e delle rotte. Alla fine verrà
chiesto di confermare la creazione dei file.

## Struttura del repository (riepilogo)

- `kathara_lab_creator.py`  — script principale (interattivo).
- `created_labs/`           — directory di destinazione per i lab creati.
- `fileConfigurazione/`     — template per i protocolli di routing e il
  contenuto del server (es. `bgp/`, `ospf/`, `rip/`, `server/`).

Esempio di contenuto generato per un laboratorio `mio_lab`:

- `created_labs/mio_lab/lab.conf`
- `created_labs/mio_lab/r1.startup`, `r2.startup`, ...
- `created_labs/mio_lab/r1/etc/frr/daemons`, `frr.conf`, `vtysh.conf` (se
  r1 è router e sono presenti template)

## Note sull'implementazione

- I nomi dei dispositivi sono validati (solo lettere, numeri, `_` e `-`,
  non iniziano con `_` o `-`).
- Le interfacce sono indicate come `eth0`, `eth1`, ... e vengono mappate a
  domini di collisione (es. `A`, `B`, `DMZ`).
- Per i router è possibile selezionare il protocollo di routing (OSPF /
  RIP / BGP); i template corrispondenti vengono copiati da
  `fileConfigurazione/<protocol>` in `<device>/etc/frr/`.

## Edge cases / cose da ricordare

1. Se una directory `created_labs/<lab_name>` già esiste lo script chiede
   conferma per sovrascrivere (e rimuove la directory esistente).
2. Se non esistono i template per un protocollo (cartella in
   `fileConfigurazione/`), lo script segnala la mancanza e continua.
3. Gli IP vengono validati sul formato base IPv4/x (controllo ottetti e
   netmask tra 0 e 32); tuttavia non viene verificata la sovrapposizione di
   reti o la raggiungibilità.
4. Gli host possono avere rotte statiche aggiunte manualmente; lo script
   non impone controlli complessi su gateway fuori subnet.

## Personalizzazione e contributi

- Per aggiungere o modificare template FRR o la pagina `index.html` del
  server, modifica i file in `fileConfigurazione/`.
- PR, issue e suggerimenti sono graditi. Mantieni le modifiche piccole e
  documenta eventuali cambi di comportamento nello script.

## Dipendenze e requisiti

- Python 3.x
- Nessuna libreria esterna necessaria per l'esecuzione dello script base.

## Esempio pratico (workflow)

1. Lancia lo script e crea il laboratorio:

```bash
python3 kathara_lab_creator.py
```

2. Entra nella cartella creata e avvia il laboratorio con Kathara:

```bash
cd created_labs/<lab_name>
kathara lstart
```

3. Per fermare e pulire:

```bash
kathara lclean
```
---

Grazie per aver usato Kathara Lab Creator — spero renda la creazione dei tuoi
laboratori più veloce e piacevole!
