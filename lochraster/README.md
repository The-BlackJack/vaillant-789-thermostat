# Lochraster-Version (ohne JLCPCB)

Gleiche Schaltung wie in `CLAUDE.md`, aufgebaut auf einer Lochrasterplatine
70 × 50 mm mit bedrahteten Bauteilen. Alles wird bei **Reichelt** bestellt,
nur der ESP bei **Blinkyparts**.

| Datei | Inhalt |
| --- | --- |
| `layout-bauteilseite.png` | Bestückung von oben; die Drähte auf der Lötseite sind blass eingezeichnet |
| `layout-loetseite.png` | Lötseite (gespiegelt), danach wird verdrahtet |
| `verdrahtung.md` | Lochkoordinaten aller Bauteile, Kabel und Drahtstrecken |
| `lochraster.py` | erzeugt Layout und Liste neu und prüft jede Verbindung gegen die Netzliste |

Geprüft wurde Folgendes:
- Alle 27 Netze sind verbunden.
- Kein Loch gehört zu zwei Netzen.
- Kein Bauteilbein steckt unter dem Gehäuse eines anderen Bauteils.
- Alle Drähte auf der Lötseite laufen waagerecht oder senkrecht und kreuzen sich nicht.
- Es bleibt genau eine isolierte Drahtbrücke: +5 V von C8 (+) zum ESP-Pin 5V.

## Platine vorbereiten

1. Die Lochrasterplatine (90 × 70) auf **27 × 19 Löcher** zuschneiden, also
   70 × 50 mm mit den Löchern mittig. Die Kanten mit Schleifpapier glätten.
2. Die vier Ecklöcher (Spalte 0/26, Zeile 0/18) auf **2,2 mm** aufbohren.
   Die `.scad`-Datei hat die Abstandshalter schon auf diese Positionen gesetzt.
3. Unter den Schraubenköpfen eine Kunststoffscheibe einlegen, weil die
   Nachbarlöcher Lötaugen haben.

## Reihenfolge beim Löten

Erst die flachen Teile, dann die hohen: Widerstände und Dioden, dann die
SMD-Kondensatoren C3/C5, dann IC-Fassung, Optokoppler, Kerkos, 78L09,
Buchsenleisten, Elkos, TSR und Schraubklemme. Danach die Drähte auf der
Lötseite nach `layout-loetseite.png`.

**Tipps für die Drähte:**
- Für Strecken über ein Loch reicht eine Lötbrücke.
- Für längere Strecken nimmst du Silberdraht oder die abgeschnittenen Beinchen der Widerstände.
- Die isolierte +5-V-Brücke ist ein Stück Litze.

**Achtung:**
- **Elkos C1, C7, C8:** Polarität beachten (+ steht in `verdrahtung.md`).
- **D1:** Ring zeigt nach oben.
- **D2:** Ring zeigt nach links.
- **U1, U3:** Pin 1 ist oben links.
- **78L09:** Die flache Seite zeigt zur Unterkante. Von links: OUT, GND, IN. Das bitte im Datenblatt des gelieferten Typs gegenprüfen.
- **C3/C5 (SMD 1210):** Sie werden quer über zwei benachbarte Lötaugen gelötet.
- **R4:** Er steht aufrecht (Raster 5,08).

**Höhe:** C8 (1000 µF, 10 × 16 mm) ist das höchste Teil. Zusammen mit
Abstandshalter und Platine liegt seine Oberkante bei etwa 26 mm ab der Wand.
Die Rückseite des Displays liegt bei etwa 29 mm, das passt also. Notfalls C8
liegend einbauen.

## Kabel

Die Kabel von Display, Sensor und Drehgeber werden **direkt neben den
ESP-Pins** eingelötet. Die Positionen stehen im Bild und in `verdrahtung.md`.
Abnehmbar bleiben sie trotzdem:

- **Display:** Das beiliegende Kabel hat am Modul einen Stecker. Die
  Dupont-Buchsen am anderen Ende abschneiden und die Litzen einlöten. Für
  „PWR“ gilt: Hat dein Kabel nur 8 Adern, lässt du das Loch frei.
- **Sensor (SHT31-D):** Vier Jumper-Kabel aufstecken, also VIN, GND, SDA und
  SCL. Das andere Ende abschneiden und einlöten.
- **Drehgeber:** Fünf Litzen direkt an den Drehgeber und an die Platine löten:
  A, C (Mitte, GND), B, Taster und Taster-GND.

## Einkaufsliste

### Reichelt

| Menge | Teil | Art.-Nr. | ca. Preis | Link |
| --- | --- | --- | --- | --- |
| 1 | Lochrasterplatine doppelseitig 90 × 70 (wird zugeschnitten) | LR-DS-79 | 2,60 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/lochrasterplatine_doppelseitig_90_x_70_mm-319109) |
| 1 | DC/DC-Wandler TRACO TSR 0.5-2450 (U4) | TSR 0.5-2450 | 5,99 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/dc_dc-wandler_tsr_0_5_5_v_500_ma_sil-251065) |
| 1 | Spannungsregler 78L09, TO-92 (U2) | µA 78L09 | 0,19 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/spannungsregler_fest_8_6_9_4_v_to-92-23474) |
| 1 | Optokoppler PC817, DIP-4 (U1) | PC817X1NSZ1B | 0,35 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/optokoppler_5kv_80v_4_8ma_80_dip-4-319088) |
| 1 | LM358, DIP-8 (U3) | LM 358 DIP | 0,25 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/operationsverstaerker_2-fach_dip-8-10483) |
| 1 | IC-Fassung 8-polig | GS 8 | 0,04 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/ic-sockel_8-polig_doppelter_federkontakt-8230) |
| 1 | Schottky-Diode 1N5819 (D1) | 1N 5819 | 0,05 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/schottkydiode_40_v_1_a_do-41-41850) |
| 1 | Diode 1N4148 (D2) | 1N 4148 | 0,02 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/schalt-diode_100_v_150_ma_do-35-1730) |
| 3 | Widerstand 100 kΩ 1 % (R3, R4 + Reserve) | METALL 100K | je 0,09 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/widerstand_metallschicht_100_kohm_0207_0_6_w_1_-11458) |
| 1 | Widerstand 120 kΩ 1 % (R5) | METALL 120K | 0,07 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/widerstand_metallschicht_120_kohm_0207_0_6_w_1_-11490) |
| 1 | Widerstand 10 kΩ 1 % (R2) | METALL 10,0K | ca. 0,09 € | [Suche](https://www.reichelt.de/de/de/shop/suche/METALL%2010,0K) |
| 1 | Widerstand 330 Ω 1 % (R1) | METALL 330 | ca. 0,09 € | [Suche](https://www.reichelt.de/de/de/shop/suche/METALL%20330) |
| 1 | Widerstand 220 Ω 1 % (R6) | METALL 220 | ca. 0,09 € | [Suche](https://www.reichelt.de/de/de/shop/suche/METALL%20220) |
| 1 | Widerstand 100 Ω 0,6 W (R7) | METALL 100 | ca. 0,09 € | [Suche](https://www.reichelt.de/de/de/shop/suche/METALL%20100) |
| 2 | Kerko 100 nF X7R RM 5 (C4, C6) | X7R-5 100N | je 0,05 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/vielschicht-kerko_100_nf_50_100_v_x7r_10_rm_5_0-22865) |
| 2 | Kerko 4,7 µF 50 V X7R, SMD 1210 (C3, C5) | KEM X7R1210 4,7U | je 0,39 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/vielschicht-kerko_4_7_f_50v_125_c-207177) |
| 1 | Elko 100 µF/35 V, 6,3 × 11 (C1) | RAD 105 100/35 | 0,07 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/elko_radial_100_f_35v_rm2_5_1000h_105_c_20_-42401) |
| 1 | Elko 220 µF/35 V, 8 × 15 (C7) | RAD FC 220/35 | 0,31 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/elko_radial_220_f_35_v_105_low_esr_8_x_15_mm_rm_3_5-84640) |
| 1 | Elko 1000 µF/10 V, 10 × 16 (C8) | FC-A 1000U 10A | 0,56 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/elko_radial_1000_f_10v_105_c_low_esr_aec-q200-376204) |
| 1 | Schraubklemme 3-pol. RM 5,08 (J1) | MKDS 1,5 3 5,08 | 1,20 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/leiterplattenklemme_3_polig_rm_5_08_mm_0_14_-_1_5_mm_-440492) |
| 2 | Buchsenleiste 1×8 RM 2,54 (für den ESP) | FIS BL1 08 Z | je 0,76 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/buchsenleiste_2_54mm_1x8_trennbar_verzinnt-283790) |
| 1 | Silberdraht 0,6 mm, 10 m (optional, sonst Beinchen-Reste) | SILBER 0,6MM | 5,55 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/silberdraht_mit_kupferkern_0_6_mm_10_m-18069) |
| 1 | Waveshare E-Paper 2,9" s/w V2 (begrenzte Stückzahl) | DEBO EPA 2.9 | 19,70 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_display_epaper_2_9_schwarz_weiss_v2-224224) |
| 1 | Sensor Adafruit SHT31-D | DEBO TEMP HUM | 17,50 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_temperatur-_und_feuchtigkeitssensor_sht31-d-235485) |
| 1 | Drehgeber ALPS EC11 mit Taster | STEC11B01 | 4,65 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/drehimpulsegeber_15_impulse_30_rastungen_horizontal-73911) |
| 1 | Jumper-Kabel Buchse–Buchse, 20 cm (für den Sensor) | DEBO KABELSET12 | 1,60 € | [reichelt](https://www.reichelt.de/de/de/shop/produkt/entwicklerboards_-_steckbrueckenkabel_40_pole_f_f_20_cm-282700) |

Summe ca. **64 €** zzgl. Versand. Ohne Silberdraht sind es ca. 58 €.
Platine und Bauteile allein kosten etwa 20 €, der Rest sind Display, Sensor
und Drehgeber.

Die Artikel mit „Suche“ habe ich nicht einzeln geöffnet, sie folgen aber dem
Reichelt-Schema `METALL <Wert>`. Im Warenkorb kurz auf 0207 und 1 % achten.

### Blinkyparts

| Menge | Teil | Preis | Link |
| --- | --- | --- | --- |
| 1–2 | ESP32-C3 SuperMini | 4,49 € | [blinkyparts](https://shop.blinkyparts.com/de/ESP32-C3-SuperMini-Kompaktes-WiFi-Bluetooth-5.0-Modul-mit-USB-C/blink23158) |

## Neu erzeugen

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" lochraster.py
```
