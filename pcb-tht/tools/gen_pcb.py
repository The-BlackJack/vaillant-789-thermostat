# -*- coding: utf-8 -*-
"""Erzeugt die Platine: Umriss, Bauteile, Netze, Routing (eigener A*-Router), Masseflaechen."""
import os, sys, json, math, heapq, time
import numpy as np
import pcbnew
import design as D

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)
KFP = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
OX, OY = 100.0, 100.0          # Platinenursprung in KiCad-Koordinaten
BW, BH = 70.0, 50.0
MM = pcbnew.FromMM
CLR = 0.2                       # Abstand Kupfer-Kupfer
VIA_D, VIA_DRILL = 0.7, 0.3          # Restring 0,2 mm (JLC-DFM)
VIA_PAD_GAP = 0.6                    # Abstand Via-Rand zu Pad (Leiterbahn-Vias)
STITCH_PAD_GAP = 2.0                 # Abstand Stitching-Via zu Pad
PITCH = 0.1


def V(x, y):
    return pcbnew.VECTOR2I(MM(OX + x), MM(OY + y))


def load_fp(fpid):
    lib, name = fpid.split(":")
    path = os.path.join(PRJ, "vaillant.pretty") if lib == "vaillant" else os.path.join(KFP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def build_board():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings()
    # Umriss
    pts = [(0, 0), (BW, 0), (BW, BH), (0, BH)]
    for i in range(4):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*pts[i])); s.SetEnd(V(*pts[(i + 1) % 4]))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1))
        b.Add(s)
    nets = {}
    for n in D.nets() + [NC_NET]:
        ni = pcbnew.NETINFO_ITEM(b, n if n == NC_NET else "/" + n)
        b.Add(ni)
        nets[n] = ni
    uuids = json.load(open(os.path.join(HERE, "sym_uuids.json")))
    for p in D.PARTS:
        fp = load_fp(p["fp"])
        fp.SetReference(p["ref"]); fp.SetValue(p["value"])
        if "grid" in p:
            fit_grid(fp, p["grid"])
        else:
            x, y, rot = p["pos"]
            fp.SetPosition(V(x, y)); fp.SetOrientationDegrees(rot)
        fp.SetPath(pcbnew.KIID_PATH("/" + uuids[p["ref"]]))
        for k in ("lcsc", "mpn"):
            if p.get(k):
                fp.SetField(k.upper(), p[k])
                f = fp.GetField(k.upper())
                f.SetLayer(pcbnew.F_Fab); f.SetVisible(False)
        if p.get("smd"):
            fp.Reference().SetLayer(pcbnew.F_Fab)    # SMD-Bezeichner nur auf Fab-Lage
        else:
            fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0)))
            fp.Reference().SetTextThickness(MM(0.15))
        if p.get("nobom"):
            fp.Reference().SetVisible(False)
        for pad in fp.Pads():
            n = p["pins"].get(pad.GetNumber())
            if pad.GetNumber() in p["pins"] and n is None:
                n = NC_NET
            if n:
                pad.SetNet(nets[n])
        ref = fp.Reference()
        ref.SetTextSize(pcbnew.VECTOR2I(MM(0.8), MM(0.8))); ref.SetTextThickness(MM(0.12))
        if p["ref"] in REF_POS:
            rx, ry, rr = REF_POS[p["ref"]]
            ref.SetPosition(V(rx, ry)); ref.SetTextAngleDegrees(rr)
        elif p["ref"][0] in "HJ" or p["ref"] == "A1":
            if p["ref"] != "A1":
                ref.SetVisible(False)
        else:
            cb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
            ref.SetPosition(cb.Centre())
            ref.SetTextAngleDegrees(90 if cb.GetHeight() > cb.GetWidth() * 1.5 else 0)
        if p["ref"] == "U1":
            for pad in fp.Pads():
                if pad.GetNumber() == "3":
                    pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        b.Add(fp)
        for i, lab in enumerate(p.get("labels", [])):
            pad = [q for q in fp.Pads() if q.GetNumber() == str(i + 1)][0]
            px, py = pcbnew.ToMM(pad.GetPosition().x) - OX, pcbnew.ToMM(pad.GetPosition().y) - OY
            add_text(b, lab, px, py + (2.1 if py < 10 else -2.1), 0.7)
    return b, nets


def fit_grid(fp, grid):
    """Footprint so drehen/verschieben, dass seine Pads auf den Rasterpunkten liegen."""
    tgt = {k: D.G(*v) for k, v in grid.items()}
    best = None
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(V(0, 0))
        pads = {q.GetNumber(): (pcbnew.ToMM(q.GetPosition().x) - OX, pcbnew.ToMM(q.GetPosition().y) - OY)
                for q in fp.Pads()}
        keys = [k for k in tgt if k in pads]
        dx = sum(tgt[k][0] - pads[k][0] for k in keys) / len(keys)
        dy = sum(tgt[k][1] - pads[k][1] for k in keys) / len(keys)
        err = sum((pads[k][0] + dx - tgt[k][0]) ** 2 + (pads[k][1] + dy - tgt[k][1]) ** 2 for k in keys)
        if best is None or err < best[0] - 1e-6:
            best = (err, rot, dx, dy)
    err, rot, dx, dy = best
    if err > 3.0:
        print("WARNUNG: Footprint %s passt schlecht aufs Raster (Fehler %.2f)" % (fp.GetReference(), err))
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(V(dx, dy))


NC_NET = "unconnected-(A1-IO2-Pad6)"
REF_POS = {"C3": (44.7, 43.5, 90), "C5": (29.5, 39.4, 0), "R4": (25.9, 33.8, 90), "J1": (61.0, 45.6, 0), "U4": (60.2, 9.5, 90),
           "C8": (56.5, 19.5, 90), "C7": (42.5, 15.0, 0), "C1": (44.1, 37.5, 90), "U2": (36.54, 45.95, 0)}


# ----------------------------------------------------------------------------- Router
class Grid:
    def __init__(self, board, nets):
        self.b = board
        self.W = int(round(BW / PITCH)) + 1
        self.H = int(round(BH / PITCH)) + 1
        self.netid = {n: i + 1 for i, n in enumerate(sorted(nets))}
        self.cu = np.zeros((2, self.H, self.W), np.int32)       # 0 frei, >0 Netz, -1 Hindernis
        self.padmask = np.zeros((self.H, self.W), bool)
        self.pads = {}            # net -> list of (layers, cellmask-indices)
        xs = np.arange(self.W) * PITCH
        ys = np.arange(self.H) * PITCH
        self.X, self.Y = np.meshgrid(xs, ys)
        # Rand: 0,15 mm Band als Hindernis
        e = 0.15
        edge = (self.X < e) | (self.X > BW - e) | (self.Y < e) | (self.Y > BH - e)
        self.cu[:, edge] = -1
        self.tracks = []          # (net, layer, x0,y0,x1,y1,w)
        self.vias = []            # (net, x, y)

    def cell(self, x, y):
        return int(round(y / PITCH)), int(round(x / PITCH))

    def block_rect(self, x0, y0, x1, y1, layers=(0, 1)):
        m = (self.X >= x0) & (self.X <= x1) & (self.Y >= y0) & (self.Y <= y1)
        for l in layers:
            self.cu[l][m] = -1

    def block_circle(self, x, y, r, layers=(0, 1)):
        m = (self.X - x) ** 2 + (self.Y - y) ** 2 <= r * r
        for l in layers:
            self.cu[l][m] = -1

    def add_pads(self):
        for fp in self.b.GetFootprints():
            for pad in fp.Pads():
                lays = [l for l, L in ((0, pcbnew.F_Cu), (1, pcbnew.B_Cu)) if pad.IsOnLayer(L)]
                if pad.HasHole() and not lays:
                    # NPTH Montageloch: Schraubenkopf freihalten
                    c = pad.GetPosition()
                    self.block_circle(pcbnew.ToMM(c.x) - OX, pcbnew.ToMM(c.y) - OY, 2.0)
                    continue
                if not lays:
                    continue
                n = pad.GetNetname().lstrip("/")
                if n.startswith("unconnected"):
                    n = ""
                bb = pad.GetBoundingBox()
                x0, x1 = pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetRight()) - OX
                y0, y1 = pcbnew.ToMM(bb.GetTop()) - OY, pcbnew.ToMM(bb.GetBottom()) - OY
                i0, i1 = max(0, int(math.floor(y0 / PITCH))), min(self.H - 1, int(math.ceil(y1 / PITCH)))
                j0, j1 = max(0, int(math.floor(x0 / PITCH))), min(self.W - 1, int(math.ceil(x1 / PITCH)))
                cells = []
                for l, L in ((0, pcbnew.F_Cu), (1, pcbnew.B_Cu)):
                    if l not in lays:
                        continue
                    poly = pad.GetEffectivePolygon(L, pcbnew.ERROR_OUTSIDE)
                    for i in range(i0, i1 + 1):
                        for j in range(j0, j1 + 1):
                            if poly.Contains(V(j * PITCH, i * PITCH)):
                                cells.append((l, i, j))
                # Kupfer etwas grosszuegiger markieren (Rasterfehler)
                for l in lays:
                    sub = self.cu[l, i0:i1 + 1, j0:j1 + 1]
                    m = np.zeros_like(sub, bool)
                    for (ll, i, j) in cells:
                        if ll == l:
                            m[i - i0, j - j0] = True
                    sub[m] = self.netid.get(n, -1) if n else -1
                for (_, i, j) in cells:
                    self.padmask[i, j] = True
                if n:
                    self.pads.setdefault(n, []).append(dict(cells=cells, pos=(pcbnew.ToMM(pad.GetPosition().x) - OX,
                                                                             pcbnew.ToMM(pad.GetPosition().y) - OY),
                                                           name=fp.GetReference() + "." + pad.GetNumber()))

    def add_silk(self):
        """Bestueckungsdruck rastern: Vias sollen nicht unter Druck-Linien/Text liegen."""
        m = np.zeros((self.H, self.W), bool)
        items = [d for d in self.b.GetDrawings() if d.GetLayer() == pcbnew.F_SilkS]
        for fp in self.b.GetFootprints():
            items += [d for d in fp.GraphicalItems() if d.GetLayer() == pcbnew.F_SilkS]
            items += [f for f in fp.GetFields() if f.IsVisible() and f.GetLayer() == pcbnew.F_SilkS]
        for it in items:
            bb = it.GetBoundingBox()
            x0, x1 = pcbnew.ToMM(bb.GetLeft()) - OX, pcbnew.ToMM(bb.GetRight()) - OX
            y0, y1 = pcbnew.ToMM(bb.GetTop()) - OY, pcbnew.ToMM(bb.GetBottom()) - OY
            i0, i1 = max(0, int(y0 / PITCH)), min(self.H - 1, int(y1 / PITCH) + 1)
            j0, j1 = max(0, int(x0 / PITCH)), min(self.W - 1, int(x1 / PITCH) + 1)
            if isinstance(it, pcbnew.PCB_SHAPE):
                poly = pcbnew.SHAPE_POLY_SET()
                it.TransformShapeToPolygon(poly, pcbnew.F_SilkS, 0, MM(0.01), pcbnew.ERROR_OUTSIDE)
                for i in range(i0, i1 + 1):
                    for j in range(j0, j1 + 1):
                        if poly.Contains(V(j * PITCH, i * PITCH)):
                            m[i, j] = True
            else:
                m[i0:i1 + 1, j0:j1 + 1] = True
        self.silkvia = self.dilate(m, (0.2 + VIA_D / 2) / PITCH + 0.5)

    @staticmethod
    def dilate(m, r_cells):
        out = m.copy()
        R = int(math.ceil(r_cells))
        H, W = m.shape
        for dy in range(-R, R + 1):
            for dx in range(-R, R + 1):
                if dx * dx + dy * dy > r_cells * r_cells or (dx == 0 and dy == 0):
                    continue
                ys0, ys1 = max(0, dy), H + min(0, dy)
                xs0, xs1 = max(0, dx), W + min(0, dx)
                out[ys0:ys1, xs0:xs1] |= m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        return out

    def raster_seg(self, l, x0, y0, x1, y1, w, val):
        r = w / 2
        xa, xb = min(x0, x1) - r - PITCH, max(x0, x1) + r + PITCH
        ya, yb = min(y0, y1) - r - PITCH, max(y0, y1) + r + PITCH
        i0, i1 = max(0, int(ya / PITCH)), min(self.H - 1, int(yb / PITCH) + 1)
        j0, j1 = max(0, int(xa / PITCH)), min(self.W - 1, int(xb / PITCH) + 1)
        X = self.X[i0:i1 + 1, j0:j1 + 1]; Y = self.Y[i0:i1 + 1, j0:j1 + 1]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 == 0:
            t = np.zeros_like(X)
        else:
            t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
        d2 = (X - (x0 + t * dx)) ** 2 + (Y - (y0 + t * dy)) ** 2
        m = d2 <= (r + 0.03) ** 2
        sub = self.cu[l, i0:i1 + 1, j0:j1 + 1]
        sub[m & (sub == 0)] = val
        return (i0, j0, m)

    def route_net(self, net, w, log):
        nid = self.netid[net]
        pads = self.pads.get(net, [])
        if len(pads) < 2:
            return True
        r_tr = (CLR + w / 2) / PITCH + 0.75
        r_via = (CLR + VIA_D / 2) / PITCH + 0.75
        other = [(self.cu[l] != 0) & (self.cu[l] != nid) for l in (0, 1)]
        blk = [self.dilate(other[l], r_tr) for l in (0, 1)]
        vblk = (self.dilate(other[0], r_via) | self.dilate(other[1], r_via)
                | self.dilate(self.padmask, (VIA_PAD_GAP + VIA_D / 2) / PITCH) | self.silkvia)
        W, H = self.W, self.H
        N = W * H
        free = np.concatenate([~blk[0].ravel(), ~blk[1].ravel()]).astype(np.uint8)
        vok = (~vblk).ravel().astype(np.uint8)
        tree = np.zeros(2 * N, np.uint8)
        # Startpad: das erste
        order = [0]
        rest = list(range(1, len(pads)))
        for (l, i, j) in pads[0]["cells"]:
            tree[l * N + i * W + j] = 1
        conn_pos = [pads[0]["pos"]]
        ok = True
        while rest:
            # naechstes Pad: kleinster Abstand zum verbundenen Teil
            k = min(rest, key=lambda r: min(math.hypot(pads[r]["pos"][0] - c[0], pads[r]["pos"][1] - c[1]) for c in conn_pos))
            rest.remove(k)
            path = self.astar(pads[k]["cells"], tree, free, vok, W, H, N)
            if path is None:
                log.append("FAIL %s: %s" % (net, pads[k]["name"]))
                ok = False
                continue
            self.commit(net, nid, path, w, tree, N)
            for (l, i, j) in pads[k]["cells"]:
                tree[l * N + i * W + j] = 1
            conn_pos.append(pads[k]["pos"])
            # Mindestabstand fuer neu gelegte Bahnen dieses Netzes zu sich selbst egal -> free bleibt
        return ok

    def astar(self, starts, tree, free, vok, W, H, N):
        tidx = np.nonzero(tree)[0]
        if len(tidx) == 0:
            return None
        tl = tidx // N; ti = (tidx % N) // W; tj = tidx % W
        bi0, bi1, bj0, bj1 = ti.min(), ti.max(), tj.min(), tj.max()
        INF = 1e18
        g = {}
        came = {}
        heap = []
        SQ2 = 1.41421356
        for (l, i, j) in starts:
            idx = l * N + i * W + j
            g[idx] = 0.0
            came[idx] = (-1, -1)
            di = max(bi0 - i, 0, i - bi1); dj = max(bj0 - j, 0, j - bj1)
            h = max(di, dj) + (SQ2 - 1) * min(di, dj)
            heapq.heappush(heap, (h * 1.2, 0.0, idx, -1))
        dirs = [(0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0), (1, 1, SQ2), (1, -1, SQ2), (-1, 1, SQ2), (-1, -1, SQ2)]
        VIA_COST = 25.0
        TURN = 0.6
        closed = set()
        n_exp = 0
        while heap:
            f, gc, idx, d = heapq.heappop(heap)
            if idx in closed:
                continue
            closed.add(idx)
            n_exp += 1
            if n_exp > 900000:
                return None
            if tree[idx] and gc > 0 or (tree[idx] and came[idx][0] == -1 and False):
                # Pfad rekonstruieren
                path = []
                cur = idx
                while cur != -1:
                    l = cur // N; r = cur % N
                    path.append((l, r // W, r % W))
                    cur = came[cur][0]
                return path[::-1]
            l = idx // N; r = idx % N; i = r // W; j = r % W
            lc = 1.0 if l == 0 else 1.15
            for k, (di, dj, c) in enumerate(dirs):
                ni, nj = i + di, j + dj
                if ni < 0 or nj < 0 or ni >= H or nj >= W:
                    continue
                nidx = l * N + ni * W + nj
                if not free[nidx] or nidx in closed:
                    continue
                if c > 1.0:
                    # diagonal: beide Nachbarn muessen frei sein (keine Ecken schneiden)
                    if not free[l * N + i * W + nj] or not free[l * N + ni * W + j]:
                        continue
                ng = gc + c * lc + (TURN if (d != -1 and d != k and d < 8) else 0.0)
                if ng < g.get(nidx, INF):
                    g[nidx] = ng
                    came[nidx] = (idx, k)
                    ddi = max(bi0 - ni, 0, ni - bi1); ddj = max(bj0 - nj, 0, nj - bj1)
                    h = max(ddi, ddj) + (SQ2 - 1) * min(ddi, ddj)
                    heapq.heappush(heap, (ng + 1.2 * h, ng, nidx, k))
            # Via
            if vok[r]:
                nidx = (1 - l) * N + r
                if free[nidx] and nidx not in closed:
                    ng = gc + VIA_COST
                    if ng < g.get(nidx, INF):
                        g[nidx] = ng
                        came[nidx] = (idx, 8)
                        di_ = max(bi0 - i, 0, i - bi1); dj_ = max(bj0 - j, 0, j - bj1)
                        h = max(di_, dj_) + (SQ2 - 1) * min(di_, dj_)
                        heapq.heappush(heap, (ng + 1.2 * h, ng, nidx, 8))
        return None

    def commit(self, net, nid, path, w, tree, N):
        # Pfad in Segmente zerlegen
        segs = []
        start = path[0]
        prev = path[0]
        pdir = None
        for p in path[1:]:
            if p[0] != prev[0]:
                if prev != start:
                    segs.append((start, prev))
                self.vias.append((net, prev[2] * PITCH, prev[1] * PITCH))
                for l in (0, 1):
                    m = (self.X - prev[2] * PITCH) ** 2 + (self.Y - prev[1] * PITCH) ** 2 <= (VIA_D / 2 + 0.03) ** 2
                    self.cu[l][m & (self.cu[l] == 0)] = nid
                start = p; prev = p; pdir = None
                continue
            dvec = (p[1] - prev[1], p[2] - prev[2])
            if pdir is not None and dvec != pdir:
                segs.append((start, prev))
                start = prev
            pdir = dvec
            prev = p
        if prev != start:
            segs.append((start, prev))
        W = self.W
        for (a, b2) in segs:
            l = a[0]
            x0, y0, x1, y1 = a[2] * PITCH, a[1] * PITCH, b2[2] * PITCH, b2[1] * PITCH
            self.tracks.append((net, l, x0, y0, x1, y1, w))
            i0, j0, m = self.raster_seg(l, x0, y0, x1, y1, w, nid)
            ii, jj = np.nonzero(m)
            tree[l * N + (ii + i0) * W + (jj + j0)] = 1
        for (l, i, j) in path:
            tree[l * N + i * W + j] = 1


def route_all(b, nets, order):
    g = Grid(b, nets)
    g.add_pads()
    g.add_silk()
    # Antennen-Sperrflaeche (ESP oben) und zwischen den Buchsenleisten am Antennenende
    for (x0, y0, x1, y1) in D_KEEPOUTS:
        g.block_rect(x0, y0, x1, y1)
    log = []
    fails = []
    for n in order:
        t = time.time()
        ok = g.route_net(n, D.WIDTH.get(n, D.DEFAULT_WIDTH), log)
        if not ok:
            fails.append(n)
        print("  %-9s %s %.1fs" % (n, "ok" if ok else "FEHLER", time.time() - t), flush=True)
    return g, fails, log


# ESP: Modul 18 x 22,5 mm, Mitte (15, 11.5) -> Antennenende oben bei y ~0.25
D_KEEPOUTS = [(8.6, 0.0, 20.8, 8.0)]


def add_keepouts(b):
    for (x0, y0, x1, y1) in D_KEEPOUTS:
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu)
        z.SetLayerSet(ls)
        o = z.Outline(); o.NewOutline()
        for (x, y) in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            o.Append(MM(OX + x), MM(OY + y))
        z.SetZoneName("Antenne ESP")
        b.Add(z)


def add_gnd_zones(b, gnd):
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b)
        z.SetLayer(L); z.SetNet(gnd)
        o = z.Outline(); o.NewOutline()
        for (x, y) in [(0, 0), (BW, 0), (BW, BH), (0, BH)]:
            o.Append(MM(OX + x), MM(OY + y))
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        z.SetThermalReliefGap(MM(0.4))
        z.SetThermalReliefSpokeWidth(MM(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetAssignedPriority(0)
        b.Add(z)


def stitch(g, gnd_id_name="GND", step=4.0):
    nid = g.netid[gnd_id_name]
    r = (CLR + VIA_D / 2) / PITCH + 1.5
    other = [(g.cu[l] != 0) for l in (0, 1)]       # Abstand zu allem Kupfer
    blk = (g.dilate(other[0], r) | g.dilate(other[1], r)
           | g.dilate(g.padmask, (STITCH_PAD_GAP + VIA_D / 2) / PITCH) | g.silkvia)
    added = 0
    y = 2.0
    while y < BH - 1.5:
        x = 2.0
        while x < BW - 1.5:
            i, j = g.cell(x, y)
            if not blk[i, j]:
                g.vias.append(("GND", j * PITCH, i * PITCH))
                for l in (0, 1):
                    m = (g.X - x) ** 2 + (g.Y - y) ** 2 <= (VIA_D / 2) ** 2
                    g.cu[l][m] = nid
                added += 1
            x += step
        y += step
    return added


LOGO = dict(file=os.path.join(PRJ, "logo-hund.png"), cx=31.0, cy=13.0, size=12.5, px=0.08)


def add_logo(b, file, cx, cy, size, px):
    """Schwarz-weiss-Bild als gefuellte Rechtecke auf den Bestueckungsdruck (schwarz = Druck)."""
    from PIL import Image
    im = Image.open(file).convert("L")
    n = int(round(size / px))
    w, h = im.size
    sc = n / max(w, h)
    im = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
    W, H = im.size
    pix = im.load()
    x0, y0 = cx - W * px / 2, cy - H * px / 2
    # waagerechte Laeufe je Zeile, gleiche Laeufe in Folgezeilen zusammenfassen
    open_runs = {}
    rects = []
    for y in range(H + 1):
        runs = set()
        if y < H:
            x = 0
            while x < W:
                if pix[x, y] < 128:
                    s = x
                    while x < W and pix[x, y] < 128:
                        x += 1
                    runs.add((s, x))
                else:
                    x += 1
        for r in list(open_runs):
            if r not in runs:
                rects.append((r[0], open_runs.pop(r), r[1], y))
        for r in runs:
            open_runs.setdefault(r, y)
    for (xa, ya, xb, yb) in rects:
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetStart(V(x0 + xa * px, y0 + ya * px)); s.SetEnd(V(x0 + xb * px, y0 + yb * px))
        s.SetFilled(True); s.SetWidth(0); s.SetLayer(pcbnew.F_SilkS)
        b.Add(s)
    return len(rects)


def fix_silk(b):
    """Druck-Linien mind. 0,15 mm, Textstrich mind. 0,15 mm (JLC-DFM)."""
    for fp in b.GetFootprints():
        for d in fp.GraphicalItems():
            if d.GetLayer() == pcbnew.F_SilkS and isinstance(d, pcbnew.PCB_SHAPE) and d.GetWidth() < MM(0.15):
                d.SetWidth(MM(0.15))
            if d.GetLayer() == pcbnew.F_SilkS and isinstance(d, pcbnew.PCB_TEXT):
                d.SetTextThickness(max(d.GetTextThickness(), MM(0.15)))
        for f in fp.GetFields():
            if f.GetLayer() == pcbnew.F_SilkS:
                f.SetTextThickness(max(f.GetTextThickness(), MM(0.15)))
    for d in b.GetDrawings():
        if d.GetLayer() == pcbnew.F_SilkS and isinstance(d, pcbnew.PCB_TEXT):
            d.SetTextThickness(max(d.GetTextThickness(), MM(0.15)))


def add_text(b, s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0, just=None):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s); t.SetPosition(V(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size))); t.SetTextThickness(MM(0.15 if size >= 0.8 else 0.12))
    t.SetTextAngleDegrees(rot)
    if just == "left":
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    b.Add(t)


def main():
    b, nets = build_board()
    # Beschriftung (vor dem Routen, damit Vias nicht unter Text landen)
    for t, (c, r) in (("7", (24, 11)), ("8", (24, 13)), ("9", (24, 15))):
        add_text(b, t, 52.4, D.G(c, r)[1], 1.5)
    add_text(b, "THERME", 63.0, 26.0, 0.9)
    for it in SILK:
        add_text(b, it[0], it[1], it[2], it[3] if len(it) > 3 else 0.9)
    add_text(b, "Vaillant 7-8-9 THT v1.0", 3.4, 36.0, 0.9, rot=90)
    print("Logo-Rechtecke:", add_logo(b, **LOGO))
    fix_silk(b)
    order = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    default = ["K7", "K7R", "OPOUT", "FB", "FILT", "OPTO_C", "OPTO_A", "PWM", "UB", "+9V", "+V", "K8", "VDC", "+5V",
               "+3V3", "SDA", "SCL", "EPD_DIN", "EPD_CLK", "EPD_CS", "EPD_DC", "EPD_RST", "EPD_BUSY",
               "ENC_A", "ENC_B", "ENC_SW", "GND"]
    order = order or default
    best = None
    for attempt in range(8):
        print("Durchgang", attempt + 1, flush=True)
        g, fails, log = route_all(b, nets, order)
        if best is None or len(fails) < len(best[1]):
            best = (g, fails, log, list(order))
        if not fails:
            break
        print("  fehlgeschlagen:", fails, log)
        order = fails + [n for n in order if n not in fails]
    g, fails, log, order = best
    print("Reihenfolge:", ",".join(order))
    nst = stitch(g)
    print("Stitching-Vias:", nst)
    for (net, l, x0, y0, x1, y1, w) in g.tracks:
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(MM(w))
        t.SetLayer(pcbnew.F_Cu if l == 0 else pcbnew.B_Cu); t.SetNet(nets[net])
        b.Add(t)
    for (net, x, y) in g.vias:
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(V(x, y)); v.SetDrill(MM(VIA_DRILL)); v.SetWidth(MM(VIA_D))
        v.SetNet(nets[net])
        b.Add(v)
    add_keepouts(b)
    add_gnd_zones(b, nets["GND"])
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    # Stitching-Vias ohne Anbindung an beide Masseflaechen wieder entfernen
    for _ in range(3):
        zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
        bad = []
        for t in b.GetTracks():
            if t.GetClass() == "PCB_VIA" and t.GetNetname() == "/GND":
                p = t.GetPosition()
                n = sum(1 for z in zones if z.GetFilledPolysList(z.GetLayer()).Contains(p))
                if n < 2 and not any(tr.GetClass() != "PCB_VIA" and (tr.GetStart() == p or tr.GetEnd() == p)
                                     for tr in b.GetTracks()):
                    bad.append(t)
        if not bad:
            break
        for t in bad:
            b.Remove(t)
        print("entfernte Vias:", len(bad))
        filler.Fill(b.Zones())
    out = os.path.join(PRJ, D.PROJECT + ".kicad_pcb")
    b.Save(out)
    print("gespeichert", out, "Fehler:", fails)


SILK = [("DISPLAY", 50.2, 2.2), ("SENSOR", 10.8, 44.4)]

if __name__ == "__main__":
    main()
