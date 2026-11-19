# Einkaufsliste Vaillant 7-8-9 Thermostat – Variante JLCPCB

> **Günstiger:** Die Lochraster-Variante ohne JLCPCB steht in
> [lochraster/README.md](lochraster/README.md) und hat eine eigene Einkaufsliste.
> Die Lochrasterplatine braucht Eckbohrungen an anderen Stellen. Für die
> JLCPCB-Platine müssen deshalb `pcb_holes` in der `.scad`-Datei wieder auf
> 2,5 / 67,5 / 47,5 zurückgesetzt werden.

Stand 19.11.2026, Preise inkl. MwSt. Drei Bestellungen: **JLCPCB** (Platine,
fertig bestückt), **Reichelt** (alles andere) und **Blinkyparts** (nur der ESP,
den hat Reichelt nicht).

## 1. JLCPCB – Platine mit SMD-Bestückung

Hochladen auf jlcpcb.com:

- `pcb/fertigung/vaillant-789-gerber.zip`
- dann bei „PCB Assembly“: `pcb/fertigung/BOM-JLCPCB.csv` und `pcb/fertigung/CPL-JLCPCB.csv`

Nur die neuesten Dateien verwenden (Stand nach dem Umbau auf Stiftleisten: in
der BOM stehen R3 und R4 in **einer** Zeile). Ältere Uploads passen nicht zur
neuen Platine.

## 2. Reichelt

| Menge | Teil | Art.-Nr. | Preis | Link |
| --- | --- | --- | --- | --- |
| 1 | DC/DC-Wandler TRACO TSR 0.5-2450 | TSR 0.5-2450 | 5,99 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/dc_dc-wandler_tsr_0_5_5_v_500_ma_sil-251065) |
| 1 | Waveshare E-Paper 2,9" s/w **V2** (inkl. Kabel) – nur begrenzte Stückzahl | DEBO EPA 2.9 | 19,70 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_display_epaper_2_9_schwarz_weiss_v2-224224) |
| 1 | Temperatur-/Feuchtesensor Adafruit **SHT31-D** | DEBO TEMP HUM | 17,50 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_temperatur-_und_feuchtigkeitssensor_sht31-d-235485) |
| 1 | Drehgeber ALPS EC11 mit Taster, 15 Impulse / 30 Rastungen | STEC11B01 | 4,65 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/drehimpulsegeber_15_impulse_30_rastungen_horizontal-73911) |
| 1 | Schraubklemme Phoenix MKDS 1,5 3-polig RM 5,08 | MKDS 1,5 3 5,08 | 1,20 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/leiterplattenklemme_3_polig_rm_5_08_mm_0_14_-_1_5_mm_-440492) |
| 2 | Buchsenleiste 1×8 RM 2,54 (für den ESP) | FIS BL1 08 Z | 2 × 0,76 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/buchsenleiste_2_54mm_1x8_trennbar_verzinnt-283790) |
| 1 | Stiftleiste 1×40, gewinkelt, RM 2,54 (für J2, J3, J4) | SL 1X40W 2,54 | 0,30 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/40pol_stiftleiste_gewinkelt_rm_2_54-19507) |
| 1 | Jumper-Kabel Buchse–Buchse, 20 cm, 40 Stück | DEBO KABELSET12 | 1,60 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_steckbrueckenkabel_40_pole_f_f_20_cm-282700) |

Summe ca. **52,50 €** zzgl. Versand.

## 3. Blinkyparts

| Menge | Teil | Preis | Link |
| --- | --- | --- | --- |
| 1 (besser 2, eins als Reserve) | ESP32-C3 SuperMini (Stiftleisten liegen bei) | 4,49 € | [blinkyparts](https://shop.blinkyparts.com/de/ESP32-C3-SuperMini-Kompaktes-WiFi-Bluetooth-5.0-Modul-mit-USB-C/blink23158) |

## Was du vermutlich schon hast

- 4 Schrauben für die Platine: Blechschrauben 2,2 × 6,5 mm (M2-Kernloch 1,8 mm)
- 2 Schrauben für das Gehäuse: Blechschrauben 2,9 × 9,5 mm oder M3 × 10
- PETG- oder ASA-Filament
- Litze für die Klemmen 7-8-9 (die alten Adern vom calorMATIC)

## Hinweise zu den Teilen

- **Sensor SHT31 statt SHT40:** Reichelt führt keinen SHT40. Der SHT31-D ist
  vergleichbar genau (±0,3 °C). `vaillant-789.yaml` ist schon auf
  `platform: sht3xd` (Adresse 0x44) umgestellt. Anschluss am Sensorboard:
  VIN, GND, SDA, SCL.
- **Drehgeber STEC11B01:** Die Achse ist rund, 6 × 25 mm mit Schlitz (keine
  D-Abflachung). Der Knopf in der `.scad`-Datei ist schon angepasst: runde
  Bohrung mit Steg für den Schlitz. Achse auf ca. 15 mm kürzen und den Schlitz
  danach neu einsägen (ca. 1 mm breit, 4 mm tief). In der YAML steht
  `resolution: 2`, also ein Schritt pro Raste. Zählt er nur jede zweite Raste,
  auf 4 stellen.
- **Display:** Die Variante V2 bestellen. Steht bei Reichelt „begrenzte
  Stückzahl“, notfalls bei BerryBase (EINKM-29, 16,90 €) – dann wäre es eine
  Bestellung mehr.
- **Günstigere Variante mit vier Shops:** Display (16,90 €) und SHT40 (6,20 €)
  bei BerryBase kaufen spart ca. 14 €. Dafür kommen ca. 5 € Versand dazu, und
  es ist eine Bestellung mehr.
