// =====================================================================
//  Vaillant 7-8-9 Wandthermostat - Gehaeuse fuer 3D-Druck
//  ersetzt den calorMATIC 332 an der Wand, gleiche Wandloecher
//
//  Teile (Variable "part" setzen, dann F6 -> STL exportieren):
//    "back"  = Rueckplatte, wird an die Wand geschraubt
//    "front" = Frontgehaeuse mit Displayfenster (mit Front nach unten drucken)
//    "knob"  = Drehknopf fuer EC11 (6 mm D-Welle)
//    "all"   = alles nebeneinander zur Ansicht
//
//  Koordinaten: Ursprung unten links an der Aussenkante, X nach rechts,
//  Y nach oben, Z von der Wand weg. Alle Masse in mm.
//  Wandmasse aus Fotos geschaetzt (+-3 mm) -> Langloecher +-7 mm.
//  Vor dem Druck mit dem Messschieber pruefen und unten anpassen.
//
//  Empfohlen: PETG oder ASA (PLA wird an der Wand nah an der Heizung
//  weich), 0,2 mm Schicht, 3 Waende, 20 % Infill.
// =====================================================================

part = "all";        // "back" | "front" | "knob" | "all"

$fn = 48;

// ---------- Aussenmasse ----------
W       = 150;   // Breite (deckt die alte Halterung 144 x 89 ab)
H       = 100;   // Hoehe
D       = 36;    // Tiefe ab Wand (calorMATIC: 50)
wall    = 2.0;   // Seitenwaende
front_t = 2.0;   // Frontplatte
r_corner = 4;    // Eckenradius aussen
tol     = 0.25;  // Spiel Rueckplatte <-> Gehaeuse
plate_t = 3.0;   // Dicke Rueckplatte

// ---------- Wandbefestigung (alte Schraubenpositionen) ----------
// Gemessen ab unterer linker Ecke des NEUEN Gehaeuses. Die alte
// Halterung (ca. 144 x 89) liegt mittig darunter, also 3 mm von links
// und 5,5 mm von unten.
screw_ur = [118, 75.5];   // Schraube oben rechts
screw_ll = [27, 27.5];    // Schraube unten links
slot_len = 14;            // Langlochlaenge (+-7 mm Spiel)
screw_d  = 4.5;           // Schraubenschaft
head_d   = 9.5;           // Freiraum Schraubenkopf

// ---------- Kabeldurchfuehrung (Kabel kommt aus der Wand) ----------
cable_c = [124, 30.5];
cable_w = 30;
cable_h = 24;

// ---------- Display Waveshare 2,9" e-Paper Modul V2 ----------
disp_c     = [75, 70];      // Mitte der Modulplatine
disp_pcb   = [89.5, 38];    // Platinenmass
win        = [68, 30];      // Sichtfenster (aktive Flaeche 66,9 x 29,1)
win_off    = [0, 0];        // Versatz Fenster ggue. Platinenmitte -> am Modul nachmessen!
pocket_h   = 3;             // Hoehe der Fuehrungsrahmen hinter der Front

// ---------- Drehgeber EC11 ----------
enc_c    = [133, 70];
enc_hole = 7.4;             // M7-Gewindehals
enc_pin_off = 7.8;          // Verdrehsicherung (Nase) ueber der Achse, 0 = keine
enc_pin_d   = 2.6;

// ---------- Sensorkammer (SHT40) unten, belueftet ----------
ch_x = [40, 95];            // links / rechts
ch_y = 22;                  // Oberkante der Kammer
ch_wall = 1.6;

// ---------- Lochrasterplatine 70 x 50 ----------
pcb_origin = [10, 40];      // untere linke Ecke der Platine
// Eckloecher des Lochrasters (27 x 19 Loecher, RM 2,54, mittig auf 70 x 50),
// auf 2,2 mm aufgebohrt. Fuer die JLCPCB-Platine waeren es [2.5,2.5] ... [67.5,47.5].
pcb_holes  = [[1.98,2.14],[68.02,2.14],[1.98,47.86],[68.02,47.86]];
standoff_h = 5;

// ---------- Gewindeeinsaetze ruthex (mit dem Loetkolben einschmelzen) ----------
// Masse laut ruthex-Empfehlung; bei anderen Laengen nur hier aendern.
ins_m2_d = 3.2;   ins_m2_l = 4.0;     // ruthex M2 (RX-M2x4), Platine
ins_m3_d = 4.0;   ins_m3_l = 5.7;     // ruthex M3 (RX-M3x5.7), Front <-> Rueckplatte
ins_extra = 1.0;                      // Platz unter dem Einsatz fuer verdraengten Kunststoff
standoff_d = ins_m2_d + 2 * 1.65;     // Abstandshalter aussen (Wand 1,65 mm)

// ---------- Verschraubung Front <-> Rueckplatte (von unten) ----------
lock_x = [22, 128];
lock_z = 9;                 // Hoehe der Schraubenachse ab Wand
lock_block = [9, 9, 15];    // Block mit M3-Einsatz (Wand >= 2,5 mm)

// =====================================================================
module rounded_rect(size, r) {
    hull() for (x = [r, size[0]-r], y = [r, size[1]-r])
        translate([x, y]) circle(r = r);
}

module slot(p, len, d, horizontal, h) {
    hull() for (o = [-len/2, len/2])
        translate([p[0] + (horizontal ? o : 0), p[1] + (horizontal ? 0 : o), -1])
            cylinder(d = d, h = h);
}

// ---------------- Rueckplatte ----------------
module back() {
    pw = W - 2*wall - 2*tol;
    ph = H - 2*wall - 2*tol;
    difference() {
        union() {
            translate([wall+tol, wall+tol, 0])
                linear_extrude(plate_t) rounded_rect([pw, ph], 1);
            // Abstandshalter Platine
            for (h = pcb_holes)
                translate([pcb_origin[0]+h[0], pcb_origin[1]+h[1], 0])
                    cylinder(d = standoff_d, h = plate_t + standoff_h);
            // Schraubbloecke fuer die Front
            for (x = lock_x)
                translate([x - lock_block[0]/2, wall + tol, 0])
                    cube(lock_block);
        }
        // Langloecher: oben rechts waagerecht, unten links senkrecht
        slot(screw_ur, slot_len, screw_d, true,  plate_t + 2);
        slot(screw_ll, slot_len, screw_d, false, plate_t + 2);
        // Kabeldurchfuehrung
        translate([cable_c[0]-cable_w/2, cable_c[1]-cable_h/2, -1])
            cube([cable_w, cable_h, plate_t + 2]);
        // Abstandshalter: Bohrung fuer M2-Einsatz von oben, darunter Freiraum fuer die Schraube
        for (h = pcb_holes)
            translate([pcb_origin[0]+h[0], pcb_origin[1]+h[1], 0]) {
                translate([0, 0, plate_t + standoff_h - ins_m2_l - ins_extra])
                    cylinder(d = ins_m2_d, h = ins_m2_l + ins_extra + 1);
                translate([0, 0, 1])
                    cylinder(d = 2.2, h = plate_t + standoff_h);
            }
        // Schraubbloecke: Bohrung fuer M3-Einsatz von der Vorderkante (unten im Gehaeuse)
        for (x = lock_x)
            translate([x, wall + tol - 0.01, lock_z]) rotate([-90, 0, 0])
                cylinder(d = ins_m3_d, h = ins_m3_l + ins_extra);
    }
}

// ---------------- Frontgehaeuse ----------------
module front() {
    inner_d = D - front_t;                      // Innenraum ab Wand
    difference() {
        union() {
            // Schale
            difference() {
                linear_extrude(D) rounded_rect([W, H], r_corner);
                translate([wall, wall, -1])
                    linear_extrude(inner_d + 1) rounded_rect([W-2*wall, H-2*wall], max(r_corner-wall, 0.5));
            }
            // Sensorkammer: zwei Seitenwaende + Deckel (oben)
            translate([ch_x[0], wall, plate_t + 1])
                cube([ch_wall, ch_y - wall, inner_d - plate_t - 1]);
            translate([ch_x[1] - ch_wall, wall, plate_t + 1])
                cube([ch_wall, ch_y - wall, inner_d - plate_t - 1]);
            translate([ch_x[0], ch_y - ch_wall, plate_t + 1])
                cube([ch_x[1] - ch_x[0], ch_wall, inner_d - plate_t - 1]);
            // Fuehrungsrahmen fuer die Displayplatine
            translate([disp_c[0], disp_c[1], inner_d - pocket_h])
                difference() {
                    translate([-(disp_pcb[0]+4)/2, -(disp_pcb[1]+4)/2, 0])
                        cube([disp_pcb[0]+4, disp_pcb[1]+4, pocket_h]);
                    translate([-(disp_pcb[0]+0.6)/2, -(disp_pcb[1]+0.6)/2, -1])
                        cube([disp_pcb[0]+0.6, disp_pcb[1]+0.6, pocket_h + 2]);
                }
        }
        // Sichtfenster mit 45-Grad-Fase nach aussen
        translate([disp_c[0]+win_off[0], disp_c[1]+win_off[1], inner_d - 0.01])
            hull() {
                translate([-win[0]/2, -win[1]/2, 0]) cube([win[0], win[1], 0.01]);
                translate([-win[0]/2 - front_t, -win[1]/2 - front_t, front_t + 0.02])
                    cube([win[0] + 2*front_t, win[1] + 2*front_t, 0.01]);
            }
        // Drehgeber
        translate([enc_c[0], enc_c[1], inner_d - 1])
            cylinder(d = enc_hole, h = front_t + 2);
        if (enc_pin_off > 0)
            translate([enc_c[0], enc_c[1] + enc_pin_off, inner_d - 1])
                cylinder(d = enc_pin_d, h = 1.2 + 1);      // Sackloch fuer die Nase
        // Kabeldurchfuehrung in die Sensorkammer (Deckel, links, an der Rueckplatte)
        translate([ch_x[0] + 2, ch_y - ch_wall - 1, plate_t + 1 - 0.01])
            cube([6, ch_wall + 2, 4]);
        // Lueftung Sensorkammer: unten im Boden ...
        for (x = [ch_x[0] + 5 : 4 : ch_x[1] - 5])
            translate([x - 1, -1, 8]) cube([2, wall + 2, inner_d - 14]);
        // ... und in der Front
        for (x = [ch_x[0] + 5 : 4 : ch_x[1] - 5])
            translate([x - 1, wall + 4, inner_d - 1]) cube([2, ch_y - wall - 9, front_t + 2]);
        // Lueftung oben (Abwaerme ESP / Wandler)
        for (x = [30 : 4 : 120])
            translate([x - 1, H - wall - 1, 8]) cube([2, wall + 2, inner_d - 14]);
        // Schraubloecher M3 im Boden
        for (x = lock_x)
            translate([x, -1, lock_z]) rotate([-90, 0, 0])
                cylinder(d = 3.4, h = wall + 2);
    }
}

// ---------------- Drehknopf ----------------
// ALPS STEC11B01 (Reichelt): runde 6-mm-Achse mit Schlitz, 25 mm lang.
// Achse auf ca. 15 mm (ab Auflageflaeche des Gewindes) kuerzen, damit der
// Knopf knapp ueber der Mutter sitzt. Dabei geht der Schlitz an der Spitze
// verloren -> mit Puk-/Metallsaege neu einsaegen (ca. 1 mm breit, 4 mm tief).
// Der Steg im Knopf greift in diesen Schlitz. Ohne Schlitz: slot_rib_h = 0
// und knob_hole = 5.9 (Presssitz, ggf. ein Tropfen Kleber).
// Fuer einen Drehgeber mit D-Achse knob_shaft = "D" setzen.
knob_shaft   = "slot";   // "slot" | "D"
knob_hole    = 6.05;     // Bohrung; bei zu lockerem Sitz 5.95 probieren
slot_rib_w   = 0.9;      // Stegbreite (etwas schmaler als der Schlitz)
slot_rib_h   = 4.0;      // Steglaenge in den Schlitz hinein, 0 = kein Steg

module knob() {
    d = 20; h = 13; flat = 4.6; shaft_depth = 10;
    difference() {
        union() {
            cylinder(d = d, h = h - 1);
            translate([0, 0, h - 1]) cylinder(d1 = d, d2 = d - 2, h = 1);
        }
        // Griffrillen
        for (a = [0 : 15 : 359]) rotate(a) translate([d/2 + 0.3, 0, -1]) cylinder(d = 1.6, h = h + 2, $fn = 12);
        // Achsbohrung
        translate([0, 0, -1]) {
            if (knob_shaft == "D")
                intersection() {
                    cylinder(d = knob_hole, h = shaft_depth + 1);
                    translate([-knob_hole/2, -knob_hole/2, 0]) cube([knob_hole, flat, shaft_depth + 1]);
                }
            else
                difference() {
                    cylinder(d = knob_hole, h = shaft_depth + 1);
                    // Steg quer durch die Bohrung am Bohrungsgrund (greift in den Schlitz)
                    if (slot_rib_h > 0)
                        translate([-knob_hole/2 - 0.5, -slot_rib_w/2, shaft_depth + 1 - slot_rib_h])
                            cube([knob_hole + 1, slot_rib_w, slot_rib_h + 0.01]);
                }
        }
        // Markierung
        translate([0, d/2 - 3, h - 0.6]) cube([1.2, 4, 2], center = true);
    }
}

// =====================================================================
if (part == "back")  back();
if (part == "front") translate([0, H, D]) rotate([180, 0, 0]) front();   // Front nach unten
if (part == "knob")  knob();
if (part == "all") {
    back();
    translate([W + 15, 0, 0]) front();
    translate([2*W + 45, 20, 0]) knob();
}
