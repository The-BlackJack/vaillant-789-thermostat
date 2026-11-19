# -*- coding: utf-8 -*-
"""THT-Variante: JLCPCB fertigt nur die Leiterplatte, alle Teile werden selbst eingeloetet
(Reichelt-Teile wie in lochraster/README.md).

"pos" = (x, y, Drehung) in mm, Ursprung oben links auf der Platine, y nach unten.
Bei Zweibeinern liegt "pos" auf Pad 1. Montageloecher sitzen auf den Eckloechern des
Lochrasters ("grid"), damit das Gehaeuse (.scad) fuer beide Varianten passt.
"""

PROJECT = "vaillant-789"
GX0, GY0, GP = 1.98, 2.14, 2.54


def G(c, r):
    return (GX0 + GP * c, GY0 + GP * r)


R10 = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
CAP1210 = "Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder"
DISC = "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm"

PARTS = [
    # --- Versorgung -------------------------------------------------------
    dict(ref="J1", sym="Connector:Screw_Terminal_01x03", value="Klemme 9-8-7",
         fp="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
         pins={"1": "GND", "2": "K8", "3": "K7"}, pos=(62.94, 40.24, 90), sch=(30.48, 50.8), mpn="MKDS 1,5 3 5,08"),
    dict(ref="D1", sym="Device:D_Schottky", value="1N5819", fp="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
         pins={"1": "+V", "2": "K8"}, pos=(54.5, 32.5, 270), sch=(55.88, 40.64), mpn="1N 5819"),
    dict(ref="C1", sym="Device:C_Polarized", value="100uF/35V", fp="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
         pins={"1": "+V", "2": "GND"}, pos=(47.25, 37.5, 0), sch=(76.2, 40.64), mpn="RAD 105 100/35"),
    dict(ref="U2", sym="Regulator_Linear:L78L09_TO92", value="78L09", fp="Package_TO_SOT_THT:TO-92_Inline_Wide",
         pins={"1": "+9V", "2": "GND", "3": "+V"}, pos=(34.0, 43.5, 0), sch=(101.6, 40.64), mpn="µA 78L09"),
    dict(ref="C3", sym="Device:C", value="4.7uF/50V X7R 1210", fp=CAP1210,
         pins={"1": "+V", "2": "GND"}, pos=(42.5, 43.5, 90), sch=(121.92, 40.64), mpn="KEM X7R1210 4,7U"),
    dict(ref="C4", sym="Device:C", value="100nF", fp=DISC,
         pins={"1": "+9V", "2": "GND"}, pos=(34.0, 47.6, 0), sch=(137.16, 40.64), mpn="X7R-5 100N"),
    dict(ref="R7", sym="Device:R", value="100R 0,6W", fp=R10,
         pins={"1": "VDC", "2": "+V"}, pos=(48.5, 7.5, 270), sch=(157.48, 40.64), mpn="METALL 100"),
    dict(ref="C7", sym="Device:C_Polarized", value="220uF/35V", fp="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
         pins={"1": "VDC", "2": "GND"}, pos=(40.75, 9.8, 0), sch=(177.8, 40.64), mpn="RAD FC 220/35"),
    dict(ref="U4", sym="Converter_DCDC:TSR_1-2450", value="TSR 0.5-2450",
         fp="Converter_DCDC:Converter_DCDC_TRACO_TSR0.5-24xx_TSR0.5-24xxx_THT",
         pins={"1": "VDC", "2": "GND", "3": "+5V"}, pos=(55.86, 4.68, 0), sch=(203.2, 40.64), mpn="TSR 0.5-2450"),
    dict(ref="C8", sym="Device:C_Polarized", value="1000uF/10V", fp="Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
         pins={"1": "+5V", "2": "GND"}, pos=(61.0, 19.5, 0), sch=(228.6, 40.64), mpn="FC-A 1000U 10A"),
    # --- Steuerung Klemme 7 ---------------------------------------------------
    dict(ref="R1", sym="Device:R", value="330R", fp=R10,
         pins={"1": "OPTO_A", "2": "PWM"}, pos=(7.0, 29.6, 0), sch=(30.48, 101.6), mpn="METALL 330"),
    dict(ref="U1", sym="Isolator:PC817", value="PC817", fp="Package_DIP:DIP-4_W7.62mm",
         pins={"1": "OPTO_A", "2": "GND", "3": "GND", "4": "OPTO_C"}, pos=(8.0, 33.0, 0),
         sch=(55.88, 101.6), mpn="PC817X1NSZ1B"),
    dict(ref="R2", sym="Device:R", value="10k", fp=R10,
         pins={"1": "OPTO_C", "2": "+9V"}, pos=(15.0, 43.0, 0), sch=(81.28, 101.6), mpn="METALL 10,0K"),
    dict(ref="R3", sym="Device:R", value="100k 1%", fp=R10,
         pins={"1": "OPTO_C", "2": "FILT"}, pos=(15.0, 39.5, 0), sch=(99.06, 101.6), mpn="METALL 100K"),
    dict(ref="C5", sym="Device:C", value="4.7uF/50V X7R 1210", fp=CAP1210,
         pins={"1": "FILT", "2": "GND"}, pos=(29.5, 41.5, 0), sch=(116.84, 101.6), mpn="KEM X7R1210 4,7U"),
    dict(ref="U3", sym="Amplifier_Operational:LM358", value="LM358", fp="Package_DIP:DIP-8_W7.62mm",
         pins={"3": "FILT", "2": "FB", "1": "OPOUT", "5": "GND", "6": "UB", "7": "UB", "8": "+V", "4": "GND"},
         pos=(32.0, 30.0, 0), units={1: (142.24, 101.6), 2: (175.26, 101.6), 3: (200.66, 101.6)}, sch=None,
         mpn="LM 358 DIP + Fassung GS 8"),
    dict(ref="R4", sym="Device:R", value="100k 1%", fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical",
         pins={"1": "FB", "2": "GND"}, pos=(28.0, 31.27, 270), sch=(223.52, 101.6), mpn="METALL 100K"),
    dict(ref="R5", sym="Device:R", value="120k 1%", fp=R10,
         pins={"1": "FB", "2": "OPOUT"}, pos=(29.5, 26.5, 0), sch=(241.3, 101.6), mpn="METALL 120K"),
    dict(ref="C6", sym="Device:C", value="100nF", fp=DISC,
         pins={"1": "+V", "2": "GND"}, pos=(43.0, 30.0, 270), sch=(259.08, 101.6), mpn="X7R-5 100N"),
    dict(ref="D2", sym="Device:D", value="1N4148", fp="Diode_THT:D_DO-35_SOD27_P10.16mm_Horizontal",
         pins={"1": "OPOUT", "2": "K7R"}, pos=(31.0, 23.5, 0), sch=(279.4, 101.6), mpn="1N 4148"),
    dict(ref="R6", sym="Device:R", value="220R", fp=R10,
         pins={"1": "K7R", "2": "K7"}, pos=(43.5, 23.5, 0), sch=(299.72, 101.6), mpn="METALL 220"),
    # --- Peripherie ------------------------------------------------------------
    dict(ref="A1", sym="vaillant:ESP32-C3_SuperMini", value="ESP32-C3 SuperMini",
         fp="vaillant:ESP32-C3_SuperMini_Socket",
         pins={"1": "+5V", "2": "GND", "3": "+3V3", "4": "EPD_CLK", "5": "PWM", "6": None,
               "7": "EPD_BUSY", "8": "ENC_SW", "9": "EPD_DC", "10": "EPD_DIN", "11": "EPD_CS",
               "12": "SDA", "13": "SCL", "14": "EPD_RST", "15": "ENC_B", "16": "ENC_A"},
         pos=(14.68, 16.11, 0), sch=(60.96, 162.56),
         mpn="ESP32-C3 SuperMini + 2x Buchsenleiste FIS BL1 08 Z"),
    # Kabel-Loetpunkte (Litzen direkt einloeten oder Stiftleiste)
    dict(ref="J2", sym="Connector_Generic:Conn_01x09", value="Display",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical",
         pins={"1": "+3V3", "2": "GND", "3": "EPD_DIN", "4": "EPD_CLK", "5": "EPD_CS", "6": "EPD_DC",
               "7": "EPD_RST", "8": "EPD_BUSY", "9": "+3V3"}, pos=(24.0, 2.14, 90), sch=(127.0, 162.56),
         mpn="Display-Kabel einloeten (Pin 9 = PWR neuerer Module)",
         labels=["VCC", "GND", "DIN", "CLK", "CS", "DC", "RST", "BSY", "PWR"]),
    dict(ref="J3", sym="Connector_Generic:Conn_01x04", value="Sensor",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
         pins={"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL"}, pos=(7.06, 47.86, 90), sch=(165.1, 162.56),
         mpn="Sensor-Kabel einloeten", labels=["VIN", "GND", "SDA", "SCL"]),
    dict(ref="J4", sym="Connector_Generic:Conn_01x05", value="Drehgeber",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
         pins={"1": "ENC_A", "2": "GND", "3": "ENC_B", "4": "ENC_SW", "5": "GND"}, pos=(19.76, 47.86, 90),
         sch=(203.2, 162.56), mpn="Drehgeber-Litzen einloeten", labels=["A", "C", "B", "SW", "GND"]),
]
for i, (c, r) in enumerate([(0, 0), (26, 0), (0, 18), (26, 18)]):
    PARTS.append(dict(ref="H%d" % (i + 1), sym="Mechanical:MountingHole", value="M2",
                      fp="MountingHole:MountingHole_2.2mm_M2", pins={}, grid={"": (c, r)},
                      sch=(248.92 + i * 12.7, 162.56), nobom=True))
for p in PARTS:
    p["smd"] = False       # nichts wird bestueckt

PWR_FLAGS = ["GND", "+V", "VDC"]
WIDTH = {"K8": 0.6, "+V": 0.6, "VDC": 0.6, "+5V": 0.6, "GND": 0.5, "+9V": 0.4}
DEFAULT_WIDTH = 0.3


def nets():
    s = set()
    for p in PARTS:
        for n in p["pins"].values():
            if n:
                s.add(n)
    return sorted(s)
