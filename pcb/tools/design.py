# -*- coding: utf-8 -*-
"""Gemeinsame Netzliste + Bauteildaten fuer Schaltplan und Platine.

Koordinaten "pos" = Platine (mm, Ursprung oben links der Platine, y nach unten),
"sch" = Schaltplan (mm, A3). Netze/Pins entsprechen der Schaltung in CLAUDE.md.
"""

PROJECT = "vaillant-789"

# Bauteile ------------------------------------------------------------------
# smd=True -> JLCPCB bestueckt (BOM/CPL), False -> selbst einloeten
PARTS = [
    # --- Versorgung -------------------------------------------------------
    dict(ref="J1", sym="Connector:Screw_Terminal_01x03", value="Klemme 9-8-7",
         fp="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
         pins={"1": "GND", "2": "K8", "3": "K7"}, pos=(64.6, 40.7, 90), sch=(30.48, 50.8), smd=False,
         mpn="Phoenix MKDS 1,5/3-5,08 (oder kompatibel)"),
    dict(ref="D1", sym="Device:D_Schottky", value="1N5819WS", fp="Diode_SMD:D_SOD-323",
         pins={"1": "+V", "2": "K8"}, pos=(55.5, 36.0, 0), sch=(55.88, 40.64), smd=True,
         lcsc="C191023", mpn="1N5819WS"),
    dict(ref="C1", sym="Device:C_Polarized", value="100uF/35V", fp="Capacitor_SMD:CP_Elec_6.3x7.7",
         pins={"1": "+V", "2": "GND"}, pos=(51.5, 44.0, 0), sch=(76.2, 40.64), smd=True,
         lcsc="C2836442", mpn="RVT100UF35V67RV0034"),
    dict(ref="U2", sym="Regulator_Linear:L7809", value="CJ78M09", fp="Package_TO_SOT_SMD:TO-252-2",
         pins={"1": "+V", "2": "GND", "3": "+9V"}, pos=(41.0, 42.0, 0), sch=(101.6, 40.64), smd=True,
         lcsc="C9071", mpn="CJ78M09"),
    dict(ref="C3", sym="Device:C", value="1uF/50V", fp="Capacitor_SMD:C_0805_2012Metric",
         pins={"1": "+V", "2": "GND"}, pos=(40.0, 36.6, 0), sch=(121.92, 40.64), smd=True,
         lcsc="C28323", mpn="CL21B105KBFNNNE"),
    dict(ref="C4", sym="Device:C", value="100nF", fp="Capacitor_SMD:C_0603_1608Metric",
         pins={"1": "+9V", "2": "GND"}, pos=(33.0, 47.5, 0), sch=(137.16, 40.64), smd=True,
         lcsc="C14663", mpn="CC0603KRX7R9BB104"),
    dict(ref="R7", sym="Device:R", value="100R 2W", fp="Resistor_SMD:R_2512_6332Metric",
         pins={"1": "+V", "2": "VDC"}, pos=(53.5, 31.0, 0), sch=(157.48, 40.64), smd=True,
         lcsc="C175280", mpn="CRH2512F100RE04Z"),
    dict(ref="C7", sym="Device:C_Polarized", value="220uF/35V", fp="Capacitor_SMD:CP_Elec_6.3x7.7",
         pins={"1": "VDC", "2": "GND"}, pos=(53.5, 25.3, 0), sch=(177.8, 40.64), smd=True,
         lcsc="C7471881", mpn="189RV0019"),
    dict(ref="U4", sym="Converter_DCDC:TSR_1-2450", value="TSR 0.5-2450",
         fp="Converter_DCDC:Converter_DCDC_TRACO_TSR0.5-24xx_TSR0.5-24xxx_THT",
         pins={"1": "VDC", "2": "GND", "3": "+5V"}, pos=(51.6, 12.5, 0), sch=(203.2, 40.64), smd=False,
         mpn="TRACO TSR 0.5-2450"),
    dict(ref="C8", sym="Device:C_Polarized", value="1000uF/16V", fp="Capacitor_SMD:CP_Elec_10x10",
         pins={"1": "+5V", "2": "GND"}, pos=(64.0, 15.5, 90), sch=(228.6, 40.64), smd=True,
         lcsc="C3359", mpn="RVT1C102M1010"),
    # --- Steuerung Klemme 7 ---------------------------------------------------
    dict(ref="R1", sym="Device:R", value="330R", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "PWM", "2": "OPTO_A"}, pos=(8.24, 25.6, 270), sch=(30.48, 101.6), smd=True,
         lcsc="C23138", mpn="0603WAF3300T5E"),
    dict(ref="U1", sym="Isolator:EL817", value="EL817S1(C)", fp="Package_DIP:SMDIP-4_W9.53mm",
         pins={"1": "OPTO_A", "2": "GND", "3": "GND", "4": "OPTO_C"}, pos=(13.0, 30.0, 0),
         sch=(55.88, 101.6), smd=True, lcsc="C2912100", mpn="EL817S1(C)(TU)-F"),
    dict(ref="R2", sym="Device:R", value="10k", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "+9V", "2": "OPTO_C"}, pos=(22.5, 27.0, 0), sch=(81.28, 101.6), smd=True,
         lcsc="C25804", mpn="0603WAF1002T5E"),
    dict(ref="R3", sym="Device:R", value="100k 1%", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "OPTO_C", "2": "FILT"}, pos=(22.5, 30.0, 0), sch=(99.06, 101.6), smd=True,
         lcsc="C25803", mpn="0603WAF1003T5E"),
    dict(ref="C5", sym="Device:C", value="4.7uF/50V X7R", fp="Capacitor_SMD:C_1206_3216Metric",
         pins={"1": "FILT", "2": "GND"}, pos=(22.5, 33.4, 0), sch=(116.84, 101.6), smd=True,
         lcsc="C29823", mpn="1206B475K500NT"),
    dict(ref="U3", sym="Amplifier_Operational:LM358", value="LM358", fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
         pins={"3": "FILT", "2": "FB", "1": "OPOUT", "5": "GND", "6": "UB", "7": "UB", "8": "+V", "4": "GND"},
         units={1: (142.24, 101.6), 2: (175.26, 101.6), 3: (200.66, 101.6)},
         pos=(31.0, 31.0, 0), sch=None, smd=True, lcsc="C7950", mpn="LM358DR2G"),
    dict(ref="R4", sym="Device:R", value="100k 1%", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "FB", "2": "GND"}, pos=(30.5, 36.4, 0), sch=(223.52, 101.6), smd=True,
         lcsc="C25803", mpn="0603WAF1003T5E"),
    dict(ref="R5", sym="Device:R", value="120k 1%", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "FB", "2": "OPOUT"}, pos=(29.0, 25.6, 0), sch=(241.3, 101.6), smd=True,
         lcsc="C25808", mpn="0603WAF1203T5E"),
    dict(ref="C6", sym="Device:C", value="100nF", fp="Capacitor_SMD:C_0603_1608Metric",
         pins={"1": "+V", "2": "GND"}, pos=(37.0, 29.0, 90), sch=(259.08, 101.6), smd=True,
         lcsc="C14663", mpn="CC0603KRX7R9BB104"),
    dict(ref="D2", sym="Device:D", value="1N4148WS", fp="Diode_SMD:D_SOD-323",
         pins={"1": "OPOUT", "2": "K7R"}, pos=(38.4, 33.6, 0), sch=(279.4, 101.6), smd=True,
         lcsc="C2128", mpn="1N4148WS"),
    dict(ref="R6", sym="Device:R", value="220R", fp="Resistor_SMD:R_0603_1608Metric",
         pins={"1": "K7R", "2": "K7"}, pos=(42.4, 33.6, 0), sch=(299.72, 101.6), smd=True,
         lcsc="C22962", mpn="0603WAF2200T5E"),
    # --- Peripherie ------------------------------------------------------------
    dict(ref="A1", sym="vaillant:ESP32-C3_SuperMini", value="ESP32-C3 SuperMini",
         fp="vaillant:ESP32-C3_SuperMini_Socket",
         pins={"1": "+5V", "2": "GND", "3": "+3V3", "4": "EPD_CLK", "5": "PWM", "6": None,
               "7": "EPD_BUSY", "8": "ENC_SW", "9": "EPD_DC", "10": "EPD_DIN", "11": "EPD_CS",
               "12": "SDA", "13": "SCL", "14": "EPD_RST", "15": "ENC_B", "16": "ENC_A"},
         pos=(15.0, 11.5, 0), sch=(60.96, 162.56), smd=False,
         mpn="ESP32-C3 SuperMini + 2x Buchsenleiste 1x8 RM2,54"),
    # Steckverbinder: gewinkelte Stiftleisten RM 2,54 fuer Dupont-Buchsen (flach, kein Crimpen)
    dict(ref="J2", sym="Connector_Generic:Conn_01x09", value="E-Paper",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Horizontal",
         pins={"1": "+3V3", "2": "GND", "3": "EPD_DIN", "4": "EPD_CLK", "5": "EPD_CS", "6": "EPD_DC",
               "7": "EPD_RST", "8": "EPD_BUSY", "9": "+3V3"}, pos=(46.7, 3.6, 270), sch=(127.0, 162.56),
         smd=False, mpn="Stiftleiste 1x9 gewinkelt RM 2,54 (Pin 9 = PWR neuerer Waveshare-Module)"),
    dict(ref="J3", sym="Connector_Generic:Conn_01x04", value="SHT-Sensor",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Horizontal",
         pins={"1": "+3V3", "2": "GND", "3": "SDA", "4": "SCL"}, pos=(14.45, 39.3, 270),
         sch=(165.1, 162.56), smd=False, mpn="Stiftleiste 1x4 gewinkelt RM 2,54"),
    dict(ref="J4", sym="Connector_Generic:Conn_01x05", value="Drehgeber EC11",
         fp="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Horizontal",
         pins={"1": "ENC_A", "2": "GND", "3": "ENC_B", "4": "ENC_SW", "5": "GND"}, pos=(28.3, 39.3, 270),
         sch=(203.2, 162.56), smd=False, mpn="Stiftleiste 1x5 gewinkelt RM 2,54"),
]
for i, (x, y) in enumerate([(2.5, 2.5), (67.5, 2.5), (2.5, 47.5), (67.5, 47.5)]):
    PARTS.append(dict(ref="H%d" % (i + 1), sym="Mechanical:MountingHole", value="M2",
                      fp="MountingHole:MountingHole_2.2mm_M2", pins={}, pos=(x, y, 0),
                      sch=(248.92 + i * 12.7, 162.56), smd=False, nobom=True))

# Netze, die eine PWR_FLAG brauchen (power_in ohne Treiber)
PWR_FLAGS = ["GND", "+V", "VDC"]

# Leiterbahnbreiten (mm)
WIDTH = {"K8": 0.5, "+V": 0.5, "VDC": 0.5, "+5V": 0.5, "GND": 0.4, "+9V": 0.4}
DEFAULT_WIDTH = 0.25


def nets():
    s = set()
    for p in PARTS:
        for n in p["pins"].values():
            if n:
                s.add(n)
    return sorted(s)
