#!/usr/bin/env python3
"""
Seed Qdrant Cloud with injection molding simulation knowledge.
v2: ~400 high-quality chunks covering popular topics, recent software,
    advanced processes, theory, and practical troubleshooting.

Uses fastembed for local embeddings (all-MiniLM-L6-v2, 384 dims).
"""

import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding

# ── Config ──
QDRANT_URL = "https://d072a605-3a1a-471a-aaf3-a6bdd11f07d2.us-west-2-0.aws.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9tpiCCNFb9wWBzxVJkT21qcWDYqZ0PV1fu9siVlo3kY"
COLLECTION = "moldsim_knowledge"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384


def c(text, category, subcategory=None):
    """Shorthand to create a chunk dict."""
    d = {"text": text, "category": category}
    if subcategory:
        d["subcategory"] = subcategory
    return d


# ═══════════════════════════════════════════
# 1. MATERIALS (~40 chunks)
# ═══════════════════════════════════════════
def material_chunks():
    materials = [
        ("ABS Generic", "ABS", "amorphous", "220-260°C", "40-80°C", "0.4-0.7%",
         "General-purpose ABS. Good impact resistance and processability. Hygroscopic — dry at 80°C for 3h. Max shear rate 50000 1/s. Residence time max 8 min. Cross-WLF: n=0.2694, τ*=30820 Pa, D1=4.89e10 Pa·s, D2=373.15 K, A1=23.76, A2=51.6 K. Tait PVT: b5=413.15 K, b6=2.0e-7 K/Pa."),
        ("PP Homopolymer", "PP", "semi-crystalline", "200-280°C", "20-60°C", "1.0-2.5%",
         "Standard PP with good chemical resistance. Higher crystallinity = more shrinkage. Dry at 80°C for 2h if needed. Max shear rate 100000 1/s. Cross-WLF: n=0.2848, τ*=23540 Pa, D1=1.58e14 Pa·s, D2=263.15 K. Note: PP shrinks significantly more than amorphous resins."),
        ("PP Copolymer", "PP", "semi-crystalline", "200-260°C", "20-50°C", "1.0-2.0%",
         "Random copolymer PP with better clarity and lower melting point than homopolymer. Improved impact at low temps. Cross-WLF: n=0.3, τ*=25000 Pa. Lower crystallinity than homo-PP gives slightly lower shrinkage."),
        ("PA6 (Nylon 6)", "PA", "semi-crystalline", "230-280°C", "60-90°C", "0.8-1.5%",
         "PA6 polyamide. Highly hygroscopic — MUST dry at 80°C for 4-6h, moisture <0.2%. Crystallization strongly affected by mold temp: higher mold temp = more crystallinity = better mechanical properties but more shrinkage. Cross-WLF: n=0.2532, τ*=39000 Pa."),
        ("PA66 (Nylon 66)", "PA", "semi-crystalline", "270-300°C", "70-100°C", "1.0-2.0%",
         "PA66 with higher melting point than PA6 (262°C vs 220°C). Very hygroscopic — dry at 80°C for 4-6h. Narrower processing window. Higher melt temp needed. Cross-WLF: n=0.2415, τ*=60000 Pa. Excellent wear resistance and stiffness."),
        ("PA66-GF30", "PA", "semi-crystalline", "275-300°C", "80-100°C", "0.3-0.5% (flow), 0.8-1.2% (cross)",
         "30% glass fiber reinforced PA66. Anisotropic shrinkage — much less in flow direction due to fiber alignment. Dry 4-6h at 80°C. Max shear rate 60000 1/s. Fiber orientation models: Folgar-Tucker, RSC, ARD-RSC. Cross-WLF: n=0.4091, τ*=75800 Pa."),
        ("PC (Polycarbonate)", "PC", "amorphous", "280-320°C", "80-110°C", "0.5-0.7%",
         "PC — high-performance amorphous with excellent impact and optical clarity. Very high melt viscosity. Sensitive to moisture — dry at 120°C for 4h. Max shear rate 40000 1/s. Prone to stress cracking. Cross-WLF: n=0.0867, τ*=320000 Pa (very high τ*)."),
        ("PC/ABS", "PC/ABS", "amorphous", "240-280°C", "60-80°C", "0.5-0.7%",
         "PC/ABS blend combines PC toughness with ABS processability. Easier to fill than pure PC. Dry at 100°C for 3-4h. Good for automotive interiors, electronics housings. Cross-WLF: n=0.2200, τ*=80000 Pa."),
        ("POM (Acetal/Delrin)", "POM", "semi-crystalline", "190-210°C", "60-90°C", "1.8-2.2%",
         "POM (polyoxymethylene) — high crystallinity (75-80%). Very high shrinkage. Excellent dimensional stability, low friction. No drying needed. Narrow processing window — decomposes above 230°C releasing formaldehyde. Cross-WLF: n=0.2960, τ*=41500 Pa."),
        ("HDPE", "PE", "semi-crystalline", "200-280°C", "10-60°C", "2.0-4.0%",
         "HDPE with very high shrinkage (2-4%) due to high crystallinity. Low viscosity, easy to process. No drying needed. Used for bottles, containers, pipes. Very sensitive to cooling rate — fast cooling = less crystallinity = less shrinkage."),
        ("LDPE", "PE", "semi-crystalline", "180-240°C", "20-40°C", "1.5-3.0%",
         "LDPE — flexible, branched PE. Lower crystallinity than HDPE. Good for thin-wall packaging, squeeze bottles. No drying needed. Highly elastic melt — significant die swell."),
        ("PMMA (Acrylic)", "PMMA", "amorphous", "220-260°C", "50-80°C", "0.3-0.7%",
         "PMMA — optically clear, UV resistant. Stiff but brittle. Dry at 80°C for 3h. Excellent for light guides, displays. Sensitive to thermal degradation — avoid excessive residence time. Cross-WLF: n=0.2350, τ*=22000 Pa."),
        ("PBT", "PBT", "semi-crystalline", "240-270°C", "40-80°C", "1.0-2.0%",
         "PBT polyester. Faster crystallization than PET — easier to mold. Dry at 120°C for 4h. Good chemical resistance, electrical properties. Used in connectors, automotive. Cross-WLF: n=0.3230, τ*=56200 Pa."),
        ("PBT-GF30", "PBT", "semi-crystalline", "250-270°C", "60-90°C", "0.3-0.5% (flow), 0.7-1.0% (cross)",
         "30% glass fiber reinforced PBT. Anisotropic shrinkage like PA66-GF30. Dry at 120°C for 4h. Excellent dimensional stability for connectors. Fiber orientation critical for warpage prediction."),
        ("PET", "PET", "semi-crystalline", "260-280°C", "10-30°C", "1.2-2.0%",
         "PET polyester — slower crystallization than PBT. At low mold temps (10-30°C) stays mostly amorphous = transparent. At high mold temps crystallizes = opaque. Dry at 150°C for 4-6h. Used for preforms, bottles."),
        ("PS (Polystyrene)", "PS", "amorphous", "180-260°C", "10-50°C", "0.3-0.6%",
         "PS — brittle, low cost, excellent processability. No drying needed. Very low shrinkage. Used for packaging, disposables. Easy to mold — wide processing window."),
        ("HIPS", "PS", "amorphous", "200-260°C", "20-60°C", "0.4-0.7%",
         "High Impact PS — PS with rubber phase for improved impact. Low cost. Slightly higher shrinkage than PS. Used for food packaging, appliance housings."),
        ("TPU", "TPU", "varies", "190-230°C", "20-50°C", "0.5-1.5%",
         "Thermoplastic polyurethane — flexible elastomer. Hardness ranges from 60A to 75D Shore. Hygroscopic — dry at 80°C for 2-4h. Very high melt viscosity at low shear. Prone to sticking — use mold release."),
        ("SAN", "SAN", "amorphous", "220-260°C", "40-70°C", "0.4-0.6%",
         "Styrene-acrylonitrile copolymer. Better chemical and heat resistance than PS. Transparent. Dry at 80°C for 2h. Used for housewares, cosmetic packaging."),
        ("ASA", "ASA", "amorphous", "240-270°C", "40-70°C", "0.4-0.7%",
         "Acrylonitrile-styrene-acrylate. UV-stable ABS alternative. Better weatherability. Dry at 80°C for 3h. Used for automotive exterior, outdoor applications."),
    ]

    chunks = []
    for name, family, typ, melt, mold, shrink, notes in materials:
        chunks.append(c(
            f"## {name}\nFamily: {family} | Type: {typ}\nMelt temp: {melt} | Mold temp: {mold} | Shrinkage: {shrink}\n{notes}",
            "material", family
        ))
        # Processing guidance chunk per material
        chunks.append(c(
            f"Processing guidance for {name} ({family}): Recommended melt temperature range {melt}, mold temperature {mold}. "
            f"Expected shrinkage {shrink}. {'Must be dried before processing. ' if 'dry' in notes.lower() else 'No drying required. '}"
            f"{'Anisotropic shrinkage due to fiber reinforcement — flow vs cross-flow direction differs significantly. ' if 'GF' in name else ''}"
            f"{'Semi-crystalline — crystallization behavior depends on cooling rate and mold temperature. ' if typ == 'semi-crystalline' else 'Amorphous — isotropic shrinkage, minimal crystallization effects. '}",
            "material", f"{family}_processing"
        ))
    return chunks


# ═══════════════════════════════════════════
# 2. TROUBLESHOOTING (~80 chunks)
# ═══════════════════════════════════════════
def troubleshooting_chunks():
    defects = [
        # (defect_name, causes, solutions, simulation_indicators, prevention_tips)
        ("Short Shot (Incomplete Fill)",
         "Insufficient injection pressure or speed. Melt temperature too low. Inadequate venting. Gate too small or poorly located. Wall section too thin. Flow path too long.",
         "Increase injection pressure/speed. Raise melt temperature. Add or enlarge vents (0.025-0.05mm depth for most resins). Relocate/enlarge gate. Increase wall thickness or add flow leaders. Consider sequential valve gating for long flow paths.",
         "In simulation: look for unfilled regions at end of fill. High pressure drop along flow path. Melt front temperature dropping below no-flow temperature. Maximum injection pressure reached before 100% fill.",
         "Flow length-to-thickness ratio (L/t) should be checked against material datasheet limits. ABS: L/t ~150, PP: ~250, PA: ~150, PC: ~100. Use flow leaders for thin sections."),

        ("Flash (Excess Material)",
         "Excessive injection/packing pressure. Low clamp tonnage. Worn or damaged parting line. Mold deflection. Melt temperature too high reducing viscosity.",
         "Reduce injection/packing pressure. Increase clamp force. Check/repair parting line and shut-offs. Reduce melt temperature. Optimize VP switchover to prevent pressure spikes.",
         "In simulation: clamp force exceeding machine capacity. Pressure at parting line > steel yield strength. Mold deflection analysis shows gap opening.",
         "Required clamp force = projected area × cavity pressure. Rule of thumb: 3-5 tons/in² for most resins. Moldflow/Moldex3D clamp force result should be < 80% of machine capacity."),

        ("Sink Marks",
         "Insufficient packing pressure or time. Part sections too thick. Rib-to-wall ratio too high (>60%). Gate freezing too early. Cooling too slow in thick sections.",
         "Increase packing pressure (typically 50-80% of injection pressure). Extend packing time until gate freeze. Core out thick sections. Reduce rib-to-wall ratio to 50-60%. Add internal gas channels or foam. Ensure cooling targets thick areas.",
         "In simulation: volumetric shrinkage results show hot spots. Sink mark index > 3% indicates visible sinks. Packing pressure doesn't reach thick areas — check pressure distribution at end of packing.",
         "Design rule: rib thickness = 50-60% of adjacent wall. Boss OD should be 2× ID. Wall transitions should be gradual (3:1 taper ratio). Check sink index contour plot in simulation."),

        ("Warpage (Part Distortion)",
         "Non-uniform cooling (differential temperatures top vs bottom). Anisotropic shrinkage from fiber orientation. Non-uniform packing pressure distribution. Residual stress from constrained shrinkage. Gate location creating asymmetric flow.",
         "Balance cooling channels (equal flow rates, uniform distance to cavity). Optimize gate location for balanced fill. Adjust fiber orientation via gate design. Reduce packing pressure differential. Use warpage-optimized processing. Consider annealing for stress relief.",
         "In simulation: warpage analysis shows total deflection, with breakdown into differential cooling, differential shrinkage, and orientation effects. Check which component dominates. If cooling-dominated: fix cooling. If orientation-dominated: change gate location.",
         "Warpage tolerance: typically ±0.1-0.5mm for consumer parts, ±0.05mm for precision parts. Moldflow's warpage indicator can predict deflection magnitude and direction. Compare in-plane vs out-of-plane components."),

        ("Weld Lines (Knit Lines)",
         "Multiple flow fronts meeting. Flow around cores, holes, or inserts. Multi-gate designs. Temperature drop at melt front. Low pressure at weld location.",
         "Relocate gate to push weld lines to non-critical areas. Increase melt temperature to improve weld strength. Increase injection speed. Raise mold temperature at weld locations. Add overflow wells. Use sequential valve gating.",
         "In simulation: weld line results show location and melt front temperature at meeting point. Temperature difference indicator — higher temp = stronger weld. Air trap results often coincide with weld lines.",
         "Weld line strength: typically 60-90% of base material for amorphous, 40-70% for semi-crystalline. Glass-filled materials show worst weld lines (fibers don't cross the weld). Minimum acceptable weld temp: Tg+30°C for amorphous materials."),

        ("Burn Marks",
         "Trapped air compressed to high temperature (diesel effect). Inadequate venting. Excessive injection speed. Long flow paths with dead ends. Gas generated by material degradation.",
         "Add/improve venting (last-to-fill areas). Reduce injection speed, especially near end of fill. Reduce melt temperature. Ensure vent depth appropriate for material (0.01-0.025mm for crystalline, 0.025-0.05mm for amorphous). Reduce clamp force slightly to allow parting line venting.",
         "In simulation: air trap results show locations where gas is trapped. Air trap + high temperature = burn risk. Melt front advancement animation shows where air is compressed. Vent location recommendations from fill analysis.",
         "Prevention: always check air trap results before cutting steel. Place vents at every last-to-fill location. Vent depth guide: PP=0.025mm, ABS=0.05mm, PA=0.015mm, PC=0.04mm. Vent land length: 2-3mm, then relief to atmosphere."),

        ("Jetting",
         "Melt entering cavity as a jet (unrestricted stream). Gate too small creating high velocity. Gate aimed into open space rather than cavity wall. Cold slug entering first.",
         "Enlarge gate or use fan/tab gate instead of pin gate. Position gate so melt impinges on cavity wall (not free flight). Reduce injection speed during initial fill. Use cold slug well opposite sprue. Increase melt temperature.",
         "In simulation: jetting is visible in melt front advancement as irregular front pattern. Some simulators have explicit jetting detection. Check fill animation frame by frame at gate entrance.",
         "Gate design rule for jetting prevention: gate should direct flow into a wall within 2× gate diameter. Fan gates and submarine gates help prevent jetting. Tab gates (with 90° turn) also effective."),

        ("Splay (Silver Streaks)",
         "Moisture in resin (most common cause). Material degradation from excessive temperature or residence time. Trapped gas from additives or colorants. Shear heating at gate.",
         "Verify material is properly dried (check moisture content with Karl Fischer or halogen analyzer). Reduce melt temperature. Reduce screw RPM and back pressure. Check for contamination. Reduce gate shear.",
         "In simulation: splay is difficult to predict directly. High shear rate at gate (>50000 1/s for most resins) suggests splay risk. Temperature rise due to shear heating at gate indicates degradation risk.",
         "Drying guide: PA: 80°C for 4-6h (max 0.1% moisture). PC: 120°C for 4h (max 0.02%). PBT/PET: 120-150°C for 4h. ABS: 80°C for 3h. PP/PE: typically no drying needed."),

        ("Voids (Internal Bubbles)",
         "Thick sections with insufficient packing. Material shrinking away from center during cooling. Moisture. Excessive decompression after plasticating.",
         "Increase packing pressure and time. Reduce wall thickness or core out. Ensure adequate gate size for packing. Properly dry material. Reduce decompression stroke.",
         "In simulation: void prediction comes from volumetric shrinkage analysis. High shrinkage in core of thick sections (>50% of nominal wall) indicates void risk. Sink index + section thickness analysis.",
         "Void vs sink mark: thin sections get sink marks on surface, thick sections (>6mm) tend to get internal voids instead. Critical for structural parts — voids reduce load-bearing capacity."),

        ("Flow Marks (Flow Lines)",
         "Melt flow hesitation. Variable wall thickness. Low melt or mold temperature. Slow injection speed. Gate marks spreading downstream.",
         "Increase melt and mold temperature. Increase injection speed for more uniform flow. Minimize wall thickness variations. Use textured surfaces to hide flow marks. Optimize gate location and size.",
         "In simulation: hesitation analysis shows where flow slows/stops. Temperature contours at fill show cold fronts that cause visible marks. Shear stress patterns at cavity surface.",
         "Flow marks are cosmetic — primarily concern for Class A surfaces. Parts with textured surfaces can tolerate more flow marks. Critical for transparent parts (PMMA, PC, SAN)."),

        ("Delamination (Surface Peeling)",
         "Incompatible materials mixed (contamination or wrong regrind). Excessive shear stress at surface. Moisture in resin. Mold release agent buildup.",
         "Check material purity (no contamination or wrong regrind). Reduce injection speed to lower surface shear. Dry material properly. Clean mold surface. Check hopper and barrel for cross-contamination.",
         "In simulation: very high surface shear stress (>0.3 MPa for most resins) indicates delamination risk. Check shear stress at wall results.",
         "Prevention: keep regrind ratio <25%. Ensure material compatibility when using blends. Purge barrel thoroughly when changing materials."),

        ("Brittleness (Reduced Impact Strength)",
         "Material degradation from excessive temperature or residence time. Moisture (especially PA, PC). Weld lines in critical stress areas. Excessive regrind. Crystallization issues (too fast cooling for PA).",
         "Reduce melt temperature and residence time. Ensure proper drying. Relocate weld lines from high-stress areas. Limit regrind percentage. Optimize mold temperature for crystallization (especially semi-crystalline).",
         "In simulation: weld line locations relative to stress-bearing areas. Fiber orientation in critical regions (glass-filled parts). Cooling rate analysis for crystallization prediction.",
         "PA parts need adequate mold temp (80-100°C) for proper crystallization and toughness. PC/ABS needs proper drying. Excessive barrel temperature causes chain scission = brittleness."),

        ("Ejection Problems (Sticking, Drag Marks)",
         "Insufficient draft angle. Undercuts. Over-packing causing part swelling onto core. High friction surface finish. Inadequate ejection system. Part too hot at ejection (not cooled enough).",
         "Increase draft angle (minimum 0.5° per side, 1° preferred). Add mold release if needed. Reduce packing pressure. Ensure adequate cooling time. Check ejector pin layout covers both sides of core. Use air poplift for deep cores.",
         "In simulation: check part temperature at end of cooling — if core area is still above HDT, part will deform during ejection. Shrinkage onto core analysis. In-mold stress at ejection.",
         "Draft angle rules: 1° per 25mm depth minimum. Textured surfaces need more draft (add 1° per 0.025mm texture depth). SPI-A1 finish: 3° minimum draft."),

        ("Dimensional Inaccuracy",
         "Incorrect shrinkage compensation in mold. Non-uniform shrinkage. Warpage. Process variation. Moisture absorption post-molding (especially PA).",
         "Use simulation-predicted shrinkage for mold scaling (not nominal datasheet values). Optimize process for minimum warpage. Use GD&T to specify critical dimensions. Control post-mold conditioning.",
         "In simulation: compare predicted shrinkage to mold compensation. Check dimensional stability over process window (DOE). Warpage impact on key dimensions. Shrinkage anisotropy (especially fiber-filled).",
         "Tolerances: general purpose ±0.1mm, precision ±0.05mm, tight ±0.025mm. Semi-crystalline materials are harder to hold tight tolerances. PA absorbs 2-3% moisture post-molding affecting dimensions."),

        ("Gate Blush / Gate Vestige",
         "Shear heating and stress concentration at gate. Gate too small causing excessive shear. Cold slug entering through gate. Improper gate-to-wall transition.",
         "Enlarge gate. Add cold slug well. Smooth gate-to-part transition. Reduce injection speed during initial fill. Consider hot tip or valve gate for cosmetic parts.",
         "In simulation: shear rate at gate — exceeding material limit indicates blush risk. Temperature rise at gate from shear heating. Pressure drop across gate.",
         "For cosmetic parts: valve gates eliminate gate vestige. Submarine/tunnel gates place vestige below parting line. Fan gates reduce shear concentration."),

        ("Race Tracking (Simulation Issue)",
         "Flow preferentially following thicker sections or channels, creating unbalanced fill. Edge effects in flat parts. Runner system imbalance.",
         "Identify race tracking in fill animation — look for flow that advances faster in certain regions. Add flow restrictors in thick channels. Equalize wall thickness. Balance runner system using runner balancing tools.",
         "In simulation: fill time contours showing uneven advancement. Race tracking leads to air traps, weld lines in unexpected locations, and premature gate freeze in thin sections while thick sections are still filling.",
         "Race tracking makes simulation results inaccurate if mesh is too coarse to capture thin/thick transitions. Use at least 4-6 elements through thickness for 3D mesh in these regions."),

        ("Cooling Issues",
         "Unbalanced cooling (different temperatures on core vs cavity side). Insufficient cooling in thick areas. Cooling channels too far from cavity surface. Turbulent vs laminar flow in channels.",
         "Ensure equal cooling on both sides (≤5°C differential). Add conformal cooling channels for complex geometries. Maintain turbulent flow in channels (Reynolds number > 10000). Use baffles or bubblers for deep cores. Check coolant flow rate.",
         "In simulation: circuit coolant temperature rise > 3°C indicates insufficient flow. Temperature difference across part thickness > 5°C causes warpage. Hot spots with temperature > average + 10°C need additional cooling.",
         "Cooling time ≈ wall_thickness² / (π² × thermal_diffusivity) × ln(8/π² × (Tm-Tw)/(Te-Tw)). Cooling is typically 60-80% of cycle time. 1mm wall thickness increase ≈ 2-4s extra cooling."),

        ("Overpacking",
         "V/P switchover position too late — pressure still building at switchover. Packing pressure too high. Non-uniform packing distribution. Short shot protection causing intentional overfilling.",
         "Set V/P switchover at 95-98% volumetric fill. Reduce packing pressure. Profile packing pressure (higher initial, then taper). Check pressure distribution — areas near gate may be overpacked while far areas are under-packed.",
         "In simulation: peak pressure exceeding machine capacity. Clamp force exceeding machine limit. Part weight above target. Volumetric shrinkage near gate approaching zero or negative.",
         "V/P switchover methods: by position (most common), by pressure, by time. Position-based: switch when screw reaches position for ~98% fill. Pressure-based: switch when cavity pressure reaches threshold."),

        ("Mold Filling Imbalance",
         "Unequal runner lengths or diameters in multi-cavity molds. Shear-induced imbalance in geometrically balanced runners. Thermal imbalance. Cavity geometry differences.",
         "Use Beaumont's MeltFlipper technology for shear-induced imbalance. Balance runner diameters using simulation. Ensure thermal symmetry. Consider hot runner with individual zone control. Use sequential valve gating.",
         "In simulation: fill time results showing cavities filling at different times. Volume filled vs time curve showing step pattern. Runner pressure drop analysis showing imbalance.",
         "Even geometrically balanced H-pattern runners have shear-induced imbalance (Beaumont effect): inner cavities fill before outer. This is caused by non-uniform shear history in runner bends."),

        ("Hesitation (Flow Stagnation)",
         "Thin section adjacent to thick section — melt hesitates in thin area while thick fills. Complex geometry with varying flow resistance. Low injection speed. Low melt temperature.",
         "Increase injection speed to push through thin sections before hesitation. Raise melt temperature. Add flow leaders to guide melt through thin areas. Equalize wall thickness. Relocate gate to fill thin sections first.",
         "In simulation: fill animation shows melt front stopping in thin region and later resuming as pressure builds. Temperature drop in hesitation zone (frozen skin grows). Weld lines from hesitation can be weak.",
         "Hesitation is a key concern for thin-wall molding. Flow leaders (locally thicker channels) direct melt to fill critical thin areas before hesitation can occur."),
    ]

    chunks = []
    for defect, causes, solutions, sim, prevention in defects:
        chunks.append(c(
            f"## {defect}\n\n**Root Causes:**\n{causes}\n\n**Solutions:**\n{solutions}",
            "troubleshooting", defect.split('(')[0].strip()
        ))
        chunks.append(c(
            f"## {defect} — Simulation & Prevention\n\n**Simulation Indicators:**\n{sim}\n\n**Prevention Tips:**\n{prevention}",
            "troubleshooting", f"{defect.split('(')[0].strip()}_simulation"
        ))
    return chunks


# ═══════════════════════════════════════════
# 3. WARPAGE DEEP DIVE (~15 chunks)
# ═══════════════════════════════════════════
def warpage_chunks():
    return [
        c("## Warpage Analysis Overview\nWarpage in injection molded parts results from three main sources: (1) differential cooling — uneven temperatures between cavity and core sides cause differential shrinkage through thickness, (2) differential shrinkage — non-uniform volumetric shrinkage due to packing pressure distribution, (3) orientation effects — molecular and fiber alignment causing anisotropic shrinkage. In Moldflow, warpage results decompose into these three components. The dominant component determines the corrective action.", "warpage", "overview"),
        c("## Warpage from Differential Cooling\nWhen one side of the part cools faster (closer to cooling channels, better thermal contact), that side shrinks less initially and constrains the hotter side. This creates bending toward the hotter (more-shrunk) side. Fix: balance cooling circuit layout, equalize coolant temperatures, use conformal cooling. Target: <5°C temperature difference across part thickness. In simulation: check 'Temperature at end of fill' and 'Temperature, Part, Frozen layer fraction' results.", "warpage", "differential_cooling"),
        c("## Warpage from Differential Shrinkage (Packing)\nAreas closer to the gate receive higher packing pressure and show less volumetric shrinkage. Areas far from gate or behind frozen gates show higher shrinkage. This creates non-uniform shrinkage across the part, causing warpage. Fix: optimize gate count and location for uniform pressure distribution. Multiple gates may help large parts. Check 'Volumetric shrinkage at ejection' plot — should be uniform.", "warpage", "differential_shrinkage"),
        c("## Warpage from Fiber Orientation (Glass-Filled)\nIn glass-fiber reinforced materials, fibers align with flow direction near the surface (shell layer) and perpendicular to flow in the core (fountain flow effect). Shrinkage is lower in fiber direction, higher perpendicular. This creates differential shrinkage between shell and core layers. Gate location dramatically affects fiber orientation pattern. Fix: optimize gate for desired fiber orientation, consider multiple gates, use fiber-interaction models (RSC, ARD-RSC, MRD) for accurate prediction.", "warpage", "fiber_orientation"),
        c("## Fiber Orientation Models for Warpage\nFolgar-Tucker (FT) model: standard fiber orientation prediction, tends to over-predict fiber alignment. RSC (Reduced Strain Closure): slows down fiber orientation evolution, more accurate for concentrated suspensions (>15% GF). ARD-RSC: anisotropic rotary diffusion, most accurate for fiber interaction. MRD: Moldflow Rotational Diffusion model in Moldflow 2024+. pARD-RSC: latest model accounting for fiber concentration gradients. For warpage accuracy with GF materials, always use RSC or better.", "warpage", "fiber_models"),
        c("## Warpage Prediction Accuracy\nTypical warpage prediction accuracy: ±20-30% for unfilled materials, ±30-50% for glass-filled due to fiber orientation complexity. Improving accuracy: (1) use 3D mesh not midplane/dual-domain for fiber-filled, (2) calibrate material shrinkage data (pvT + CRIMS), (3) use appropriate fiber orientation model, (4) model actual cooling circuit geometry, (5) include mold deformation effects. CRIMS (Corrected Residual In-Mold Stress) shrinkage data significantly improves warpage prediction vs standard pvT-only.", "warpage", "accuracy"),
        c("## Warpage Compensation in Mold Design\nApproach: (1) run simulation to predict warpage magnitude and direction, (2) apply inverse deformation to mold cavity geometry (morph mesh or CAD), (3) re-run simulation to verify compensation, (4) iterate 2-3 times. Moldflow's warpage compensation tool automates this. Typical workflow: export deformed shape → import into CAD → mirror/invert deformation → modify tooling. Works well for simple bending, harder for complex 3D warpage.", "warpage", "compensation"),
        c("## Warpage DOE (Design of Experiments)\nMoldflow DOE can optimize process parameters to minimize warpage. Key DOE factors: melt temperature, mold temperature (both sides independently), packing pressure profile, cooling time, injection speed. Run DOE with 3-5 levels per factor. Response: total warpage deflection at critical dimensions. Moldflow's DOE uses Taguchi or full-factorial designs. For fiber-filled parts, gate location should be a DOE factor (requires separate studies).", "warpage", "doe"),
        c("## Warpage in Semi-Crystalline vs Amorphous\nSemi-crystalline materials (PP, PA, POM, PBT) show 2-5× higher warpage than amorphous (ABS, PC, PS) because crystallization shrinkage is large and sensitive to cooling rate. Faster cooling = less crystallinity = less shrinkage but also less uniform. Amorphous warpage is primarily from cooling differential and packing. Semi-crystalline adds crystallization non-uniformity. For PA with moisture absorption: warpage can change weeks after molding as part absorbs atmospheric moisture and swells.", "warpage", "material_type"),
        c("## In-Mold Stress and Post-Ejection Warpage\nResidual stresses frozen into the part during cooling cause post-ejection warpage. Even if part looks flat in mold, it may warp after ejection as internal stresses relax. Annealing (heating to just below HDT) can relieve stresses — part warps to its 'natural' stress-free shape. Simulation predicts both 'in-mold' displacement (constrained by mold) and 'post-ejection' warpage (free to deform). Always report post-ejection warpage for part quality prediction.", "warpage", "residual_stress"),
        c("## Practical Warpage Reduction Checklist\n1. Balance cooling: equal circuit flow rates, equal distance from cavity surface, turbulent flow (Re>10000)\n2. Optimize gate location: fill analysis for balanced flow, minimize last-to-fill distance\n3. Adjust packing: profile packing pressure, extend hold time until gate freeze\n4. Uniform wall thickness: minimize thick/thin transitions, use gradual transitions (3:1 taper)\n5. Consider material change: switch to lower-shrinkage grade, or add glass fiber for dimensional stability\n6. Conformal cooling: additively manufactured cooling for complex geometries\n7. Mold temperature: sometimes higher uniform mold temp gives lower warpage (more uniform crystallization)", "warpage", "checklist"),
    ]


# ═══════════════════════════════════════════
# 4. COOLING SYSTEM (~20 chunks)
# ═══════════════════════════════════════════
def cooling_chunks():
    return [
        c("## Cooling System Design Fundamentals\nCooling time is typically 60-80% of total cycle time. Key parameters: coolant temperature, flow rate (turbulent preferred, Re>10000), channel diameter (typically 8-12mm), channel-to-cavity distance (1.5-2× channel diameter), channel-to-channel spacing (3-5× channel diameter). Cooling efficiency depends on: channel layout, coolant properties, heat load from polymer melt.", "cooling", "fundamentals"),
        c("## Cooling Time Estimation\nAnalytical formula: t_cool = (h²/(π²·α)) × ln((8/π²) × (Tmelt - Twall)/(Teject - Twall)) where h=wall thickness, α=thermal diffusivity, Tmelt=melt temp, Twall=mold wall temp, Teject=ejection temp. For ABS (2mm wall, 240°C melt, 60°C mold, 90°C eject): t_cool ≈ 12s. Rule of thumb: every 1mm additional wall thickness adds 2-4 seconds of cooling time.", "cooling", "estimation"),
        c("## Cooling Channel Layout Strategies\nStraight-drilled channels: simplest, parallel or series circuits. Baffles: for deep core cooling, single blade divides channel into up/down flow. Bubblers (fountains): vertical tube inside bore, coolant flows up through tube, returns around outside. Thermal pins: sealed heat pipes with phase-change fluid for very efficient heat transfer in cores. Conformal cooling: follows cavity contour, requires additive manufacturing or hybrid tooling.", "cooling", "channel_types"),
        c("## Conformal Cooling Overview\nConformal cooling channels follow the part geometry contour, maintaining uniform distance from cavity surface. Benefits: 20-40% cycle time reduction, more uniform cooling, less warpage. Manufacturing: DMLS/SLM metal 3D printing, hybrid tooling (printed insert in conventional base). Materials: maraging steel (18Ni-300), H13 tool steel (emerging). Limitations: higher tooling cost ($5K-30K premium), channel size limits, powder removal challenges, fatigue life concerns.", "cooling", "conformal_overview"),
        c("## Conformal Cooling Design Rules\nChannel cross-section: circular preferred, D-shaped acceptable. Diameter: 3-6mm typical for conformal (smaller than conventional). Wall-to-channel distance: minimum 2× channel diameter for structural integrity. Channel-to-channel spacing: 2-3× diameter. Surface roughness inside channel: Ra <6.3μm for adequate flow. Pressure drop: keep <2 bar per circuit. Design for powder evacuation: avoid dead ends, U-turns, include drain holes.", "cooling", "conformal_design"),
        c("## Conformal Cooling in Moldflow 2024-2026\nMoldflow 2024: improved conformal cooling solver, better pressure drop prediction in non-circular channels. Moldflow 2025: conformal cooling optimization using topology-based approach — auto-generates optimized channel layout for given constraints. Moldflow 2026: expanded optimization with multi-objective (cycle time + warpage), support for lattice cooling structures, improved thermal FEA coupling.", "cooling", "conformal_software"),
        c("## Cooling Analysis in Simulation\nKey results to check: (1) Circuit coolant temperature — rise should be <3°C per circuit. (2) Circuit Reynolds number — should be >10000 for turbulent flow. (3) Mold surface temperature — uniformity target <5°C range. (4) Time to reach ejection temperature — determines minimum cooling time. (5) Frozen layer fraction — should reach target (typically >80%) before ejection.", "cooling", "analysis_results"),
        c("## Series vs Parallel Cooling Circuits\nSeries: one coolant stream passes through multiple channels sequentially. Advantages: simpler plumbing, higher flow velocity (more turbulent). Disadvantages: temperature rises along circuit, later channels are less effective. Parallel: multiple channels fed from common manifold. Advantages: more uniform temperature. Disadvantages: flow may not distribute equally, lower velocity per channel. Recommendation: series for small molds, parallel with flow regulators for large multi-zone molds.", "cooling", "circuit_types"),
        c("## Mold Temperature Control\nMold temperature units: water at 10-90°C, oil at 90-200°C, electric cartridge heaters for high-temp applications. For semi-crystalline materials needing high mold temp (PA: 80-100°C, PPS: 130-150°C), use pressurized hot water or oil. Mold temperature profiling: different zones at different temperatures to manage crystallization or manage warpage. Variotherm/rapid heat-cool: cycle mold between high temp (fill) and low temp (cool) — eliminates weld lines, improves surface finish.", "cooling", "temperature_control"),
        c("## Cooling System Troubleshooting\nHot spots: areas remaining hot after cooling — check for inadequate cooling channel coverage, blocked channels, or excessively thick part sections. Solution: add cooling channels, baffles, or conformal cooling. Condensation: when mold temperature is below dew point — use dehumidified air in mold area. Scale buildup: reduces heat transfer — use water treatment, periodic descaling. Coolant leaks: check O-rings at channel connections, especially at parting line crossovers.", "cooling", "troubleshooting"),
        c("## Cooling for Deep Cores and Thin Pins\nDeep cores (L/D > 3) are hard to cool with conventional channels. Solutions: baffles (flat blade dividing bore), bubblers (central tube), thermal pins (heat pipes), beryllium copper inserts (BeCu — 3-5× thermal conductivity of steel). For thin core pins (<5mm diameter): use BeCu material. Thermal pin specifications: typically 6-12mm diameter, can transfer 10× more heat than steel. BeCu conductivity: ~110 W/m·K vs H13 steel ~25 W/m·K.", "cooling", "deep_cores"),
        c("## Cycle Time Optimization through Cooling\nCooling time reduction strategies: (1) Conformal cooling: 20-40% reduction typical. (2) Higher coolant flow rate (ensure turbulent): 5-15% reduction. (3) Optimize wall thickness (DFM): 10-30% reduction per mm of wall reduction. (4) BeCu or high-conductivity inserts: 10-20% reduction in hot spots. (5) Variotherm (rapid heating/cooling): allows higher mold temp during fill without extending cooling. (6) In-mold cooling simulation optimization.", "cooling", "cycle_optimization"),
    ]


# ═══════════════════════════════════════════
# 5. GATE & RUNNER DESIGN (~20 chunks)
# ═══════════════════════════════════════════
def gate_runner_chunks():
    return [
        c("## Gate Types and Selection\nEdge gate: simple, easy to trim, suitable for flat parts. Width = 1-2× wall thickness, depth = 50-80% of wall. Submarine (tunnel) gate: auto-degates on ejection. Pin gate: small round gate, self-degating with 3-plate mold. Fan gate: wide, thin gate for uniform flow front — excellent for flat parts. Diaphragm/disc gate: for cylindrical parts, fills uniformly around circumference. Cashew gate: curved tunnel gate to access underside. Hot tip: direct hot nozzle to part, no runner waste.", "gate_runner", "gate_types"),
        c("## Gate Location Guidelines\nBest practices: (1) Gate into thickest section — ensures packing reaches all areas. (2) Place at center of part for radial flow when possible. (3) Avoid gating near thin ribs or bosses. (4) Keep gate away from load-bearing areas (gate region has high stress). (5) Consider cosmetic requirements — gate leaves a mark. (6) For fiber-filled materials: gate location controls fiber orientation, which controls warpage. Use fill analysis to evaluate multiple gate locations.", "gate_runner", "location_guidelines"),
        c("## Gate Sizing Rules\nGate too small: high shear stress/rate, jetting, gate blush, premature gate freeze (poor packing), high pressure drop. Gate too large: long cycle time (gate freeze time), difficult trimming, large gate vestige. Sizing guidelines: Edge gate depth = 50-80% of wall thickness. Submarine gate diameter = 0.5-1× wall thickness. Gate freeze time should exceed packing time requirement. Calculate: gate freeze time ≈ gate_diameter² / (π² × thermal_diffusivity).", "gate_runner", "gate_sizing"),
        c("## Multi-Gate Design\nWhen single gate cannot fill the part (high L/t ratio, large flat parts, complex geometry), use multiple gates. Issues: weld lines form between gates, flow imbalance if not symmetric, packing complications. Solutions: sequential valve gating (open gates in sequence as flow front arrives), balanced runner system, adjust individual gate sizes for timing. Moldflow's gate location optimization can suggest optimal number and location of gates.", "gate_runner", "multi_gate"),
        c("## Hot Runner Systems\nAdvantages: no runner waste (5-30% material savings), shorter cycle time, lower injection pressure, consistent quality. Types: hot tip (thermal gate), valve gate (mechanical shut-off). Valve gate advantages: no gate vestige, precise fill control, sequential molding capability. Temperature control: each zone independently controlled. Balance: naturally balanced (all flow paths equal) or artificially balanced (different nozzle sizes). Key parameter: nozzle temperature within material processing range.", "gate_runner", "hot_runner"),
        c("## Runner System Design\nCold runner sizing: diameter based on part weight and material. Rule of thumb: sprue diameter ≥ maximum wall thickness + 1.5mm. Primary runner: 6-10mm diameter. Secondary runner: 4-8mm. Runner cross-section: full round (best), trapezoidal (acceptable, easier to machine). Runner length: minimize — each 100mm of runner adds 10-30 bar pressure drop. Cold slug wells: at every runner turn, minimum 1× runner diameter deep.", "gate_runner", "runner_design"),
        c("## Runner Balancing for Multi-Cavity\nNaturally balanced (H-pattern): all flow paths equal length — preferred for up to 32 cavities. Shear-induced imbalance: even in H-pattern, flow from inner and outer branch differs due to shear history in bends (Beaumont effect). Solution: MeltFlipper technology rotates melt stream at branch points. Artificially balanced: different runner diameters to compensate for different flow path lengths. Use simulation to verify balance — fill time difference should be <5% between cavities.", "gate_runner", "runner_balancing"),
        c("## Valve Gate Sequential Molding\nSequential valve gating (SVG) opens gates in timed sequence as melt front approaches each gate location. Benefits: eliminates weld lines, reduces pressure requirement, enables long flow paths, controls packing distribution. Moldflow simulation: set valve gate open/close times based on fill front arrival. Typical timing: open gate when melt front is 5-10mm from gate location. Close previous gate during packing phase. Used extensively in automotive bumpers, instrument panels.", "gate_runner", "sequential_valve"),
        c("## Gate Location Analysis in Simulation\nMoldflow's Gate Location Analysis: automatic optimization considering (1) maximum injection pressure, (2) fill time, (3) temperature difference at end of fill, (4) weld line locations, (5) air trap locations. Run with 'Best gate location' study type. Results show color contour — green=good, red=poor gate locations. For multiple gates: run iteratively — place first gate at best location, then find best second gate, etc.", "gate_runner", "gate_analysis"),
        c("## Pressure Drop Through Gate\nGate pressure drop typically 20-40% of total injection pressure. Calculate: ΔP = (8·η·Q)/(π·r⁴) for round gates (Hagen-Poiseuille for Newtonian approximation). For non-Newtonian polymer: use power law correction. Excessive gate pressure drop causes: high shear rate (degradation risk), shear heating (burning), jetting. Simulation result: check 'Pressure drop across gate' — should be <30% of maximum injection pressure.", "gate_runner", "pressure_drop"),
    ]


# ═══════════════════════════════════════════
# 6. DFM GUIDELINES (~20 chunks)
# ═══════════════════════════════════════════
def dfm_chunks():
    return [
        c("## Wall Thickness Design Rules\nUniform wall thickness is the single most important DFM rule for injection molding. Non-uniform walls cause: warpage (differential shrinkage), sink marks (thick areas), flow hesitation (thin areas), longer cycle time (thick areas control cooling). Recommended: keep variation within ±10% of nominal. Transitions: taper at 3:1 ratio minimum. Typical wall thickness: automotive 2.5-3.5mm, consumer electronics 1.5-2.5mm, thin-wall packaging 0.3-0.7mm.", "dfm", "wall_thickness"),
        c("## Rib Design Rules\nRibs add stiffness without increasing wall thickness. Rules: rib thickness = 50-60% of base wall (prevents sink marks opposite ribs). Rib height ≤ 3× base wall thickness. Draft angle ≥ 0.5° per side (1° preferred). Fillet at rib base = 0.25-0.5× base wall. Space ribs ≥ 2× base wall apart. For multiple ribs: stagger or offset to avoid creating thick sections. Maximum aspect ratio (height/thickness): 10:1.", "dfm", "ribs"),
        c("## Boss Design Rules\nBosses for screw fastening: OD = 2× ID (inner diameter). Wall thickness = 50-60% of base wall. Height ≤ 2.5× OD. Include gussets for tall bosses. Connect bosses to walls with ribs, not thick sections. For self-tapping screws: ID = screw major diameter - thread depth. For press-fit inserts: design for interference fit with proper tolerances. Avoid isolated thick bosses — they create sink marks.", "dfm", "bosses"),
        c("## Draft Angle Requirements\nMinimum draft for injection molding: 0.5° per side for untextured surfaces. Add 1° per 0.025mm of texture depth. Recommended: 1-2° for standard parts. Zero-draft possible with slides or lifters but adds tooling cost. Inside surfaces (core side) need more draft than outside (cavity side) because part shrinks onto core. Polished surfaces (SPI-A1): minimum 3° draft. Spark-eroded finish (EDM): 1-2° typically sufficient.", "dfm", "draft_angle"),
        c("## Undercut Solutions\nUndercuts require moving mold components: side actions (slides), lifters, collapsing cores, or unscrewing mechanisms. Cost impact: slides add $3K-15K per action. Design alternatives: redesign to eliminate undercut, use snap-fit (deflection during ejection), split part into two halves. Internal undercuts: use collapsing core or lifter. Threads: external = split cavity or slide, internal = unscrewing core or collapsing core.", "dfm", "undercuts"),
        c("## Corner and Fillet Design\nSharp corners cause: stress concentration (2-3× stress multiplier), flow restriction, cooling issues, difficult demolding. Rules: inside radius = 0.5-1× wall thickness minimum. Outside radius = inside radius + wall thickness. This maintains uniform wall thickness through the corner. Sharp corners in simulation: mesh refinement needed, stress analysis shows peak stress at corner, crack initiation site under fatigue loading.", "dfm", "corners"),
        c("## Snap-Fit Design Guidelines\nCantilever snap-fit: most common. Maximum strain during assembly: 2% for ductile materials (ABS, PP), 1% for brittle (PS, SAN). Deflection = (ε × L²)/(1.5 × t) where ε=strain, L=beam length, t=beam thickness. Retention force depends on return angle (typically 45°). Allowable deflection: calculate from material yield strain and safety factor. Include lead-in angle (30-45°) for easy assembly. Taper beam for uniform stress distribution.", "dfm", "snap_fits"),
        c("## Living Hinge Design\nLiving hinges connect two parts with a thin flexible section. Material: PP or PE only (high flex fatigue resistance). Hinge thickness: 0.25-0.5mm (0.3mm typical for PP). Hinge length (width): as wide as practical. Land length: 0.5-1.5mm. Include lead-in radii on both sides (R = 0.5-1mm). Gate on the cap side — flow through hinge aligns molecules for better flex life. PP living hinges can survive >1 million cycles if designed correctly.", "dfm", "living_hinge"),
        c("## Tolerance Specifications for Injection Molding\nGeneral tolerances: ±0.1mm per 25mm for commercial quality, ±0.05mm for precision, ±0.025mm for tight (requires process control). Factors affecting tolerances: material shrinkage variation, process repeatability, tool wear, temperature, moisture absorption. Semi-crystalline materials: wider tolerances needed (crystallization variation). Across parting line: add ±0.05mm for mold misalignment. Critical dimensions should be in same mold half when possible.", "dfm", "tolerances"),
        c("## Weld Line Placement Strategy\nWeld lines are inevitable in parts with holes, multiple gates, or variable thickness. Design strategy: (1) predict weld line locations with simulation before finalizing gate location, (2) move weld lines away from cosmetic surfaces, (3) move weld lines away from high-stress areas, (4) if weld lines must be in visible areas: use textured surface to minimize visibility. Testing: weld line strength = 60-90% of base material (amorphous), 40-70% (semi-crystalline), 30-60% (glass-filled).", "dfm", "weld_lines"),
        c("## Designing for Assembly\nSnap-fits reduce assembly time by 70-90% vs screws. Design consolidation: combine multiple parts into one injection molded part. Boss-and-rib integration: combine structural and fastening features. Alignment features: use pins, slots, or lips to ensure correct orientation. Tolerances for mating parts: consider worst-case stack-up. Design for robotic assembly: consistent part orientation, reliable ejection position, stable base for placement.", "dfm", "assembly"),
        c("## Surface Finish Specifications (SPI Standards)\nSPI A-1 (Mirror): diamond buff, Ra 0.012-0.025μm — for optical parts, lenses. Requires 3°+ draft. SPI A-3: 600 grit, Ra 0.05μm — standard high-gloss. SPI B-1 to B-3: 600-320 grit, semi-gloss, Ra 0.05-0.1μm. SPI C-1 to C-3: 600-320 stone, matte, Ra 0.35-0.7μm. SPI D-1 to D-3: bead blast/sandblast, textured, Ra 0.8-3.2μm. Each texture depth requires additional draft angle: 1° per 0.025mm depth.", "dfm", "surface_finish"),
    ]


# ═══════════════════════════════════════════
# 7. MESH & SIMULATION SETUP (~20 chunks)
# ═══════════════════════════════════════════
def mesh_chunks():
    return [
        c("## Mesh Types for Injection Molding Simulation\nMidplane mesh: 2D shell elements on midplane of part. Fastest to solve. Good for thin, simple parts. Limitations: cannot model 3D effects (fountain flow, fiber skin-core). Dual-domain (Fusion): 2D elements on outer surfaces, matched top/bottom. Better geometry representation. Most popular for production work. 3D mesh: tetrahedral elements filling the volume. Most accurate. Required for thick parts (>4mm), fiber-filled, gas-assist. Slowest to solve.", "mesh", "mesh_types"),
        c("## 3D Mesh Best Practices\nElement count: typically 500K-5M for production parts. Through-thickness layers: minimum 6 for standard parts, 10-12 for fiber-filled (to capture skin-core structure), 4 minimum for cooling analysis. Element quality: aspect ratio <20 (ideal <6), tet collapse ratio >0.1. Mesh density: higher at gates, thin sections, cooling channels, features of interest. Edge length: 1-3mm for automotive parts, 0.5-1mm for small connectors. Use local mesh refinement rather than globally fine mesh.", "mesh", "3d_best_practices"),
        c("## Dual-Domain (Fusion) Mesh Guidelines\nMatch ratio: >85% of elements should have a matched pair on opposite face. Global edge length: 2-3× wall thickness typical. Aspect ratio: <6 ideal, <20 acceptable. Connectivity check: no free edges (indicates gaps in mesh). Manifold check: no non-manifold edges. Intersection check: no self-intersecting triangles. Mesh count: typically 50K-500K triangles. Moldflow Mesh Doctor tool automatically repairs common issues.", "mesh", "dual_domain"),
        c("## Mesh Sensitivity Analysis\nAlways verify that results are mesh-independent. Approach: run same analysis with 2× finer mesh, compare key results (pressure, fill time, temperature, warpage). If results change >5-10%, mesh is too coarse. Start coarse (fast solve), refine until convergence. Critical areas needing fine mesh: gates, thin sections, weld line regions, cooling channel vicinity. Document mesh sensitivity in simulation reports.", "mesh", "sensitivity"),
        c("## Boundary Layer Mesh for Cooling\nCooling analysis requires adequate mesh resolution near cavity surface and cooling channels. Moldflow: boundary layer mesh (BLM) automatically adds thin prismatic layers at surface. Recommended: 3-5 boundary layers with first layer height = 0.1-0.3mm. BLM improves temperature gradient accuracy near surface. Without BLM: surface temperature prediction can be off by 5-15°C, affecting cooling time and warpage results.", "mesh", "boundary_layer"),
        c("## CAD Import and Geometry Preparation\nCommon CAD issues: sliver surfaces, gaps, overlaps, non-manifold edges, tiny features. Repair workflow: (1) import STEP/Parasolid (avoid STL for simulation), (2) check for problems using automatic diagnostics, (3) fill gaps and remove slivers, (4) defeaturing: remove features <2× mesh size (small holes, fillets, chamfers, logos), (5) identify parting line for dual-domain. Defeaturing saves 30-50% solving time with negligible accuracy impact.", "mesh", "cad_preparation"),
        c("## Simulation Workflow: Fill Analysis\nStep 1: Import and mesh geometry. Step 2: Select material from database. Step 3: Set process conditions (melt temp, mold temp, injection time or speed). Step 4: Place gate(s). Step 5: Run fill analysis. Key results: fill time, injection pressure, flow front temperature, shear rate, air traps, weld lines, clamp force. Validate: max pressure < machine capacity, clamp force < machine tonnage, no unfilled regions, weld lines in acceptable locations.", "mesh", "fill_analysis"),
        c("## Simulation Workflow: Pack + Cool + Warp\nAfter fill analysis: Pack analysis — set packing pressure profile (typically 3 stages: high-medium-low). Packing time: until gate freezes (check from fill results). Cool analysis — define cooling circuits, set coolant temperature and flow rate. Warp analysis — predicts final part deflection. Run sequence: Fill → Pack → Cool → Warp (each builds on previous). Total solve time: 30min - 8h for 3D mesh depending on complexity.", "mesh", "pack_cool_warp"),
        c("## Convergence Issues in Simulation\nCommon convergence problems: (1) Solver divergence during fill — often due to mesh quality issues, reduce time step or fix mesh. (2) Temperature oscillation during pack — reduce packing pressure increment size. (3) Warp solver fails — check for unconstrained rigid body motion, add 3-point constraints. (4) Cooling iteration not converging — increase maximum iterations, check for extreme boundary conditions. General fix: improve mesh quality, reduce time step, check material data for errors.", "mesh", "convergence"),
        c("## Material Database for Simulation\nMoldflow/Moldex3D have extensive material databases (10,000+ grades). Data includes: Cross-WLF viscosity, 2-domain Tait PVT, thermal conductivity vs temperature, specific heat vs temperature, mechanical properties. Custom material characterization: need rheology (capillary rheometer), pvT (dilatometer), DSC (crystallization), thermal conductivity (TPS or laser flash). Cost: $3K-8K per grade. Always validate: compare simulation pressure to machine pressure from actual molding.", "mesh", "material_database"),
    ]


# ═══════════════════════════════════════════
# 8. PROCESS OPTIMIZATION (~15 chunks)
# ═══════════════════════════════════════════
def process_chunks():
    return [
        c("## Injection Speed Optimization\nInjection speed affects: fill pattern, shear rate, pressure requirement, surface quality. Too slow: hesitation, cold flow fronts, visible flow marks, short shots. Too fast: jetting, burning (trapped air), flash, high clamp force. Optimal: depends on material and part. General approach: use speed profiling — start slow (prevent jetting at gate), accelerate (fill body), slow down at end (prevent air compression). Target fill time: typically 1-3 seconds for automotive parts.", "process", "injection_speed"),
        c("## Packing Pressure Optimization\nPacking compensates for volumetric shrinkage during cooling. Typical packing pressure: 50-80% of peak injection pressure. Packing profile: (1) initial high pressure for 0.5-1s, (2) medium hold pressure for most of packing, (3) taper to low or zero before gate freeze. Packing time: until gate freezes (check gate freeze time from simulation — when gate reaches no-flow temperature). Under-packing: sink marks, voids, dimensional issues. Over-packing: flash, increased stress, difficult ejection.", "process", "packing"),
        c("## V/P (Velocity-to-Pressure) Switchover\nThe transition from velocity-controlled filling to pressure-controlled packing is critical. Switchover too early: short shot during fill. Switchover too late: pressure spike, flash, overpacking near gate. Methods: position-based (most common — switch at 95-98% filled), pressure-based (switch when cavity pressure reaches threshold), time-based (least preferred). In simulation: check 'V/P switchover' position — at this point, ~95-98% of cavity volume should be filled.", "process", "vp_switchover"),
        c("## Melt Temperature Selection\nMelt temperature affects viscosity, fill pressure, crystallization, degradation. Too low: high viscosity, high pressure, poor surface, incomplete fill. Too high: degradation, long cooling, flash. Selection: use material datasheet recommended range. Start at midpoint. For thin-wall or long flow: use upper range. For thick parts or parts with long cycle time: use lower range (less cooling needed). Measure actual melt temperature with pyrometer, not barrel setpoint (barrel zones ≠ actual melt temp).", "process", "melt_temperature"),
        c("## Mold Temperature Effects\nMold temperature affects: surface quality, crystallization (semi-crystalline), cycle time, residual stress. Higher mold temp: better surface replication, more crystallization (higher shrinkage but better properties), longer cooling time, lower residual stress. Lower mold temp: faster cycle, less shrinkage, higher residual stress, potentially poor surface. Critical for semi-crystalline: PA needs 80-100°C for proper crystallization. PC needs 80-110°C for stress-free parts.", "process", "mold_temperature"),
        c("## Scientific Molding Methodology\nSystematic approach to process optimization: (1) Viscosity curve — establish injection speed vs pressure. (2) Cavity balance — verify uniform fill. (3) Pressure drop study — quantify pressure loss through system. (4) Gate seal study — determine packing time (increasing hold time until part weight stabilizes). (5) Cooling study — determine minimum cooling time. (6) Process window — DOE for robustness. (7) Document: fill-only short shots at increasing speeds to map fill pattern.", "process", "scientific_molding"),
        c("## Cycle Time Components\nTotal cycle = mold close + injection + packing + cooling + mold open + ejection + (robot). Typical breakdown: injection 1-3s (5-10%), packing 3-10s (10-20%), cooling 10-60s (60-80%), mold open/close/ejection 3-8s (10-15%). Optimization priorities: (1) cooling time (biggest component), (2) mold movements (machine speed, dry cycle), (3) packing time (only until gate freeze). Target cycle times: thin-wall packaging <5s, consumer products 15-30s, automotive 30-60s.", "process", "cycle_time"),
        c("## Process DOE (Design of Experiments)\nDOE factors for injection molding: melt temp, mold temp, injection speed, packing pressure, packing time, cooling time, VP switchover position. Responses: part weight, dimensions, warpage, appearance, mechanical properties. Methods: Taguchi L9/L18 (screening), full factorial 2^k (interaction effects), response surface (optimization). In simulation: Moldflow DOE study can evaluate 10-50 combinations automatically. Production DOE: use 3-5 parts per condition, measure responses.", "process", "doe"),
        c("## Process Window and Robustness\nProcess window = range of each parameter that produces acceptable parts. Wider window = more robust process = less scrap. Factors narrowing window: tight tolerances, complex geometry, sensitive material, thin walls. Moldflow's process window analysis shows green (robust), yellow (marginal), red (out of spec) regions. Six Sigma capability (Cpk > 1.33) requires process window > 8× natural process variation. Machine-to-machine transfer: verify window encompasses machine-to-machine variations.", "process", "process_window"),
    ]


# ═══════════════════════════════════════════
# 9. SOFTWARE — Moldflow (~25 chunks)
# ═══════════════════════════════════════════
def moldflow_chunks():
    return [
        c("## Moldflow Overview\nAutodesk Moldflow is the most widely used injection molding simulation software. Two products: Moldflow Adviser (basic fill/pack analysis) and Moldflow Insight (full suite: fill, pack, cool, warp, fiber, gas-assist, co-injection, etc.). Solver: finite element (FE) based. Available mesh types: midplane, dual-domain (Fusion), 3D. Material database: 10,000+ grades. Licensing: annual subscription ($15K-50K/year depending on tier). Cloud solving available since 2021.", "software", "moldflow_overview"),
        c("## Moldflow 2024 New Features\nKey additions in Moldflow 2024: (1) STAMP viscosity model — Stress and Temperature Adjustment of Moldability Parameters, improves shrinkage prediction accuracy by accounting for in-mold stress effects on crystallization. (2) Conformal cooling improvements — better pressure drop prediction for non-circular channels, support for lattice structures. (3) Enhanced 3D solver performance — 15-20% faster for large models. (4) Updated material database with latest grades from major suppliers.", "software", "moldflow_2024"),
        c("## Moldflow 2025 New Features\nMoldflow 2025 highlights: (1) Conformal cooling channel optimization — topology-based algorithm auto-generates optimized channel layout given design constraints (min wall thickness, max pressure drop, target temperature uniformity). (2) Assembly analysis — simulate multi-component assemblies (overmolding, insert molding) with component interaction. (3) Improved warpage prediction using CRIMS+ (enhanced corrected residual in-mold stress). (4) Python scripting API for automation. (5) Cloud API for headless batch runs.", "software", "moldflow_2025"),
        c("## Moldflow 2026 New Features\nMoldflow 2026 (latest release): (1) Multi-objective optimization — simultaneously optimize cycle time, warpage, and weld line quality. (2) Digital twin integration — export simulation model for process monitoring correlation. (3) Advanced conformal cooling — support for gyroid/TPMS lattice cooling structures. (4) Improved fiber breakage prediction for long-fiber composites. (5) Updated Co-injection analysis with improved interface tracking. (6) Performance: 25-30% faster 3D solver on multi-core systems.", "software", "moldflow_2026"),
        c("## Moldflow 2026.0.1 Updates\nMoldflow 2026.0.1 patch: (1) Bug fix for STAMP model convergence issues with POM materials. (2) Improved meshing robustness for thin-wall automotive parts. (3) Updated Dupont, BASF, and Covestro material data (2025 datasheets). (4) Fixed cloud solving authentication issues. (5) Memory optimization for models >5M elements. (6) New pre-defined analysis sequences for common workflows (fill-pack-warp in one click).", "software", "moldflow_2026_1"),
        c("## Moldflow Tips: Material Selection\nIn Moldflow material database: search by trade name (e.g., 'Ultramid A3WG6'), by family (e.g., 'PA66'), or by supplier (e.g., 'BASF'). Verify material data completeness: need Cross-WLF (viscosity), PVT (shrinkage), thermal (cooling). Missing data = lower accuracy. If exact grade not in database: use 'generic' version (e.g., 'Generic PA66-GF30') or characterize custom material ($3K-8K). Always check 'material data quality' indicator in Moldflow.", "software", "moldflow_material"),
        c("## Moldflow Tips: Results Interpretation\nCritical results to check: (1) Fill time — uniform fill pattern? (2) Pressure at V/P switchover — within machine capacity? (3) Flow front temperature — above no-flow temp everywhere? (4) Shear rate — within material limit? (5) Clamp force — below machine tonnage? (6) Weld lines — in acceptable locations? (7) Air traps — vent placement needed? (8) Volumetric shrinkage — uniform? (9) Warpage — within tolerance? Create a standard checklist for each project.", "software", "moldflow_results"),
        c("## Moldflow Cloud Solving\nMoldflow supports cloud solving for compute-intensive 3D analyses. Benefits: run multiple studies simultaneously, no local hardware needed, faster turnaround for DOE studies. Setup: Autodesk cloud credits (included in some subscriptions). Workflow: set up study locally → submit to cloud → results download when complete. Best for: DOE studies (10-50 runs), 3D mesh analyses >3M elements, overnight batch runs. Not ideal for quick single-run iterations.", "software", "moldflow_cloud"),
        c("## Moldflow Automation: Scripting\nMoldflow supports automation via: (1) Study Automation Wizard (built-in) — parameterize studies and run in sequence. (2) Moldflow API / COM interface — program custom workflows in Python or VB.NET. (3) Moldflow 2025+ Python scripting — direct Python API for model setup, running, and post-processing. Use cases: parametric studies, automated reporting, DOE, integration with optimization tools (modeFRONTIER, Optimus, HEEDS). Template-based approach: create master model, script varies parameters.", "software", "moldflow_automation"),
        c("## Moldflow vs Other Simulation Software\nMoldflow strengths: largest material database, proven accuracy, strong industry adoption, comprehensive analysis types. Weaknesses: expensive, slower solver than some competitors, learning curve. Moldex3D: faster 3D solver (GPU acceleration), better UI, strong in Asia. Sigmasoft: specialized in runner/mold thermal analysis, unique 'virtual molding' approach. Cadmould: European-focused, good for quick feasibility. SOLIDWORKS Plastics: integrated in SOLIDWORKS, limited but accessible for designers.", "software", "comparison"),
    ]


# ═══════════════════════════════════════════
# 10. SOFTWARE — Moldex3D (~15 chunks)
# ═══════════════════════════════════════════
def moldex3d_chunks():
    return [
        c("## Moldex3D Overview\nMoldex3D by CoreTech System is the second most popular injection molding simulation software globally, dominant in Asia-Pacific. True 3D-first solver (all analyses in 3D by default). Strong GPU acceleration. Products: Moldex3D Professional, Advanced, Enterprise. Material database: 8000+ grades. Competitive with Moldflow for most analysis types. Growing market share due to faster solve times and modern UI.", "software", "moldex3d_overview"),
        c("## Moldex3D 2024 New Features\nMoldex3D 2024R1/R2 highlights: (1) AI Optimization Wizard — machine learning-based process optimization, suggests optimal melt temp, mold temp, injection speed, packing based on target quality metrics. (2) Gate Design Discovery — AI-assisted gate location and sizing optimization. (3) iSLM (Intelligent Simulation Lifecycle Management) — cloud-based project management and data analytics for simulation teams. (4) Enhanced fiber orientation: pARD-RSC model for improved warpage prediction.", "software", "moldex3d_2024"),
        c("## Moldex3D 2025 New Features\nMoldex3D 2025R1 highlights: (1) MoldiBot — AI chatbot assistant for simulation setup guidance and troubleshooting. Answers questions about analysis setup, parameter selection, and results interpretation. (2) Dual Nakamura crystallization model — improved crystallization kinetics for semi-crystalline polymers, better shrinkage prediction. (3) Enhanced DOE with machine learning surrogate models. (4) Improved co-injection and overmolding analysis. (5) GPU solver improvements: 2-3× speedup for thermal analysis.", "software", "moldex3d_2025"),
        c("## Moldex3D Studio Interface\nMoldex3D Studio is the main pre/post-processing environment. Key features: integrated CAD import (STEP, IGES, Parasolid, Catia, NX), automatic mesh generation (BLM — Boundary Layer Mesh for 3D), process wizard for guided setup, result animation and export. Mesh: uses hybrid elements — prism layers at surface + tet in core. Auto-mesh quality typically sufficient for production analysis without manual intervention.", "software", "moldex3d_studio"),
        c("## Moldex3D Material Wizard\nMaterial data management: Moldex3D Material Wizard provides guided material characterization workflow. Lab data input: rheology (capillary), pvT, DSC, DMA, TGA. The wizard fits Cross-WLF, Tait, and crystallization model parameters automatically. Can also use generic materials from database. Material data exchange: supports CAMPUS format. Material Lab service available for custom characterization (through CoreTech partners).", "software", "moldex3d_material"),
        c("## Moldex3D Unique Capabilities\nMoldex3D advantages over Moldflow: (1) True 3D solver from the start (Moldflow historically midplane-first). (2) GPU acceleration — 3-5× speedup for large models. (3) Better co-injection modeling (interface tracking). (4) Compression molding: superior solver for compression and transfer molding. (5) IC packaging: specialized encapsulation analysis. (6) MCM (Multi-Component Molding): overmolding, 2-shot, insert molding with component interaction. (7) RIM/reaction injection molding simulation.", "software", "moldex3d_unique"),
        c("## Moldex3D DOE and Optimization\nDOE module: Taguchi, Latin Hypercube, full factorial. Response surface methodology for process optimization. Moldex3D 2024+: AI Optimization Wizard uses trained ML model to predict optimal process within seconds (after initial training runs). Process optimization targets: minimize warpage, cycle time, pressure. Constraints: maximum clamp force, shear rate limits, temperature limits. Integration with external optimization tools: modeFRONTIER, HEEDS, Optimus via API.", "software", "moldex3d_doe"),
    ]


# ═══════════════════════════════════════════
# 11. OPEN SOURCE SIMULATION (~10 chunks)
# ═══════════════════════════════════════════
def open_source_chunks():
    return [
        c("## openInjMoldSim — Open Source Injection Molding Simulation\nopenInjMoldSim is an OpenFOAM-based open-source injection molding simulation solver. Developed by Gregor Kosec and collaborators. Status: last major update ~2020, compatible with OpenFOAM 7. Capabilities: filling simulation with Cross-WLF viscosity, fountain flow, solidification. Limitations: no packing, no warpage, no cooling circuit analysis, no fiber orientation. Repository: github.com/krebeljk/openInjMoldSim. Good for research, not production simulation.", "software", "openinjmoldsim"),
        c("## OpenFOAM for Polymer Processing\nOpenFOAM can model polymer flows using custom solvers and material models. Relevant tools: rheoTool (viscoelastic flow solver), interFoam (multiphase for mold filling with VOF tracking), custom Cross-WLF viscosity implementations. Limitations for injection molding: no built-in injection molding workflow, no mold thermal analysis, no warpage prediction from shrinkage, manual setup required. Best suited for: research on flow behavior, custom rheology problems, academic studies.", "software", "openfoam"),
        c("## Free/Open Alternatives for Injection Molding\nFree simulation tools: (1) openInjMoldSim — filling only, OpenFOAM 7. (2) SOLIDWORKS Plastics Lite — free with SOLIDWORKS subscription, basic fill. (3) Autodesk Fusion 360 — includes basic mold fill simulation in Manufacturing workspace. (4) SimScale — cloud-based, has polymer flow capability (not injection-molding specific). (5) FreeCAD + CalculiX — structural analysis but no injection molding. Bottom line: no free tool matches Moldflow/Moldex3D for production use. For learning: openInjMoldSim gives insight into fill physics.", "software", "free_alternatives"),
        c("## PINN (Physics-Informed Neural Networks) for Injection Molding\nResearch trend: PINNs embed governing equations (Navier-Stokes, energy, crystallization) into neural network training. Applications: (1) real-time fill prediction (100-1000× faster than FEA), (2) process optimization surrogate, (3) digital twin inference from sensor data. Challenges: training data requirement, generalization to new geometries, accuracy vs speed tradeoff. State of art: lab demonstrations on simple geometries, not yet production-ready. Key researchers: groups at TU Munich, KU Leuven, University of Massachusetts.", "software", "pinn"),
        c("## Machine Learning Surrogates for Simulation\nML surrogate models replace expensive simulation with fast predictions. Workflow: (1) run 50-200 simulations varying parameters, (2) train ML model (random forest, neural network, or Gaussian process), (3) use model for rapid optimization or process monitoring. Applications: real-time process control, DOE optimization, material selection screening. Moldex3D 2024 AI Optimization Wizard is a commercial example. Academic: many papers on ML for warpage prediction, fill pattern classification, defect detection. Accuracy: within 5-15% of full simulation for trained parameter range.", "software", "ml_surrogates"),
    ]


# ═══════════════════════════════════════════
# 12. ADVANCED PROCESSES (~30 chunks)
# ═══════════════════════════════════════════
def advanced_process_chunks():
    return [
        c("## Overmolding Simulation\nOvermolding: injecting a second material over or around a first component (substrate). Types: insert molding (metal/plastic substrate), 2-shot molding (two plastic materials), soft-touch overmolding (TPE over rigid). Simulation challenges: heat transfer between substrate and overmold, bonding interface prediction, substrate deformation from overmold pressure and temperature. Moldflow 2025+: improved assembly analysis for overmolding. Moldex3D: MCM (Multi-Component Molding) module handles overmolding with thermal coupling.", "advanced", "overmolding"),
        c("## Overmolding Simulation Setup\nSetup steps: (1) Import substrate geometry (from CAD or previous molding simulation). (2) Define substrate material and initial temperature (typically room temp for insert, or hot from first shot for 2-shot). (3) Import overmold geometry. (4) Define overmold material. (5) Set interface conditions (bonded or contact). (6) Gate the overmold. (7) Run fill-pack-cool-warp. Key: substrate temperature at time of overmolding critically affects bonding and warpage. For 2-shot: minimize transfer time between shots.", "advanced", "overmolding_setup"),
        c("## Gas-Assist Injection Molding (GAIM)\nGas-assist: inject nitrogen gas into thick sections after partial fill. Gas hollows out core, saving material and cycle time. Benefits: eliminate sink marks in thick ribs/handles, reduce clamp force (25-50%), reduce weight (20-40%), reduce cycle time. Simulation: Moldflow and Moldex3D both support gas-assist. Key parameters: gas delay time, gas pressure profile, gas entry location. Design rules: gas channels should be 2-4× wall thickness diameter, avoid sharp turns, minimum 6mm channel diameter.", "advanced", "gas_assist"),
        c("## Gas-Assist Design Guidelines\nGas channel design: circular cross-section preferred. Channel diameter: 8-25mm typical. Length: up to 600mm. Avoid: sharp corners (<45°), T-intersections, thin sections between channels. Gas penetration depends on: melt temperature (higher = thinner walls), injection volume (short shot %), gas pressure and delay. Spillover cavity: collect excess melt displaced by gas. Simulation predicts: gas penetration length, wall thickness of hollow section, gas fingering risk.", "advanced", "gas_assist_design"),
        c("## MuCell Microcellular Foaming\nMuCell (Trexel technology): inject supercritical nitrogen or CO2 into melt to create uniform microcellular foam structure. Benefits: 5-15% weight reduction, elimination of sink marks, reduced clamp force, less warpage, shorter cycle time. Bubble size: 5-100 μm. Process: SCF (supercritical fluid) mixed with melt under pressure, nucleation occurs at pressure drop in cavity. Simulation: Moldflow supports MuCell with foam density prediction, bubble size distribution, and structural foam mechanical properties.", "advanced", "mucell"),
        c("## Thin-Wall Injection Molding\nThin-wall: wall thickness <1mm or flow-length/thickness ratio >200. Challenges: extremely high injection pressure (>200 MPa), high clamp force, fast injection (<0.5s fill time), rapid cooling. Materials: typically easy-flow grades (high MFI PP, thin-wall ABS). Machine requirements: high injection speed (>500 mm/s), high pressure capacity (>250 MPa), fast response hydraulics or electric drives. Simulation: 3D mesh mandatory, fine through-thickness resolution (≥6 layers), inertia effects may be important.", "advanced", "thin_wall"),
        c("## Thin-Wall Molding Process Tips\nInjection speed: 200-1000 mm/s (fast to prevent freeze-off). Melt temperature: upper end of range. Mold temperature: can be higher to prevent premature freezing. Gate: large gate to minimize pressure drop, valve gate preferred. Venting: critical — fast injection compresses air rapidly. Runner: short, large diameter. Hot runner: strongly recommended to eliminate cold runner pressure loss. Pack: short packing time (gate freezes quickly in thin wall). Cooling: fast cycle despite high mold temp due to thin wall.", "advanced", "thin_wall_process"),
        c("## Co-Injection (Sandwich Molding)\nCo-injection: two materials injected sequentially through same gate — skin material first, then core material. Core material pushes through center due to fountain flow. Applications: recycled material as core (hidden), structural foam core with solid skin, barrier layers for packaging. Simulation: Moldflow and Moldex3D both support co-injection with interface tracking. Key: skin-to-core ratio (typically 60-70% skin), breakthrough prediction (core reaching surface), interface position control.", "advanced", "co_injection"),
        c("## Compression Molding Simulation\nCompression molding: material placed in open mold, mold closes to shape part. Used for: thermosets (SMC, BMC), rubber, GMT (glass mat thermoplastic). Simulation: Moldex3D has dedicated compression solver. Moldflow has basic support. Key physics: non-isothermal flow of highly viscous material, cure kinetics (thermosets), fiber orientation in SMC. Charge placement optimization: simulation predicts where to place charge for complete fill with minimum pressure. Knit lines and air traps from charge placement are critical.", "advanced", "compression"),
        c("## Insert Molding Simulation\nInsert molding: metal or other inserts placed in mold before injection. Applications: threaded inserts, electrical contacts, structural reinforcement. Simulation concerns: heat transfer between insert and melt (metal insert acts as heat sink — melt freezes prematurely around insert), stress around insert (especially at sharp corners), potential for weld lines behind insert. Design: maintain minimum wall thickness around insert (≥0.5mm per side), use generous radii at insert-to-plastic transitions, preheat inserts to prevent premature freezing.", "advanced", "insert_molding"),
        c("## In-Mold Decoration (IMD/IML) Simulation\nIn-Mold Labeling (IML) and In-Mold Decoration (IMD): pre-printed film placed in mold, plastic injected behind it. Film deformation, washout (ink distortion), and bonding are key concerns. Simulation: predict flow over film, pressure on film, temperature at film-melt interface. Film may wrinkle if not properly held. Gate should be positioned to flow parallel to film, not perpendicular (prevents washout). Low injection speed near film surface recommended.", "advanced", "imd_iml"),
        c("## Recycled Material Simulation Challenges\nRecycled polymers (PCR — post-consumer recycled) present simulation challenges: (1) Variable viscosity — batch-to-batch variation in MFI. (2) Contamination — mixed polymer fractions affect flow and mechanical properties. (3) Degraded molecular weight — lower viscosity than virgin but also lower mechanical properties. (4) Moisture sensitivity — recycled PA/PET need aggressive drying. Simulation approach: use worst-case viscosity data, widen process window, test with ±20% viscosity variation. Material databases are adding recycled grades (Moldflow 2024+).", "advanced", "recycled_materials"),
        c("## Bioplastic Simulation Considerations\nBioplastics (PLA, PHA, PBS, bio-PE, bio-PA): growing use for sustainability. PLA: crystallization-sensitive, narrow processing window (190-220°C), brittle without modification, low HDT (55°C). PHA: very sensitive to shear degradation, narrow window. Bio-PE/PA: process like conventional PE/PA. Simulation: standard material models work but need accurate material data. PLA crystallization model important for shrinkage prediction. Material data availability: growing in Moldflow/Moldex3D databases but less coverage than conventional resins.", "advanced", "bioplastics"),
        c("## EV (Electric Vehicle) Molding Challenges\nEV-specific injection molding challenges: (1) Battery housings — large flat parts, tight dimensional tolerances, flame retardant materials (PA66-GF, PBT-GF). (2) High-voltage connectors — extremely tight tolerances, high creepage distance requirements, insert molding. (3) Motor components — high-temperature materials (PPS-GF, PPA), thermal management. (4) Lightweight structural parts — replacing metal with glass/carbon fiber reinforced plastics, structural simulation coupling needed. (5) EMI shielding — conductive fillers (carbon fiber, metal flakes) affecting flow.", "advanced", "ev_challenges"),
        c("## EV Battery Housing Simulation\nBattery housing (battery tray/enclosure) simulation: large structural part (up to 1.5m × 1m). Material: typically PA66-GF30/50 or PP-GF40. Challenges: (1) Flatness tolerance <0.3mm over 1m — requires extreme warpage control. (2) Sealing surface quality for IP67 rating. (3) Flame retardancy (UL94 V-0) affects material flow. (4) Multiple inserts and mounting points. Simulation approach: 3D mesh mandatory, conformal cooling for uniform temperature, multiple gates with SVG, fiber orientation optimization for warpage.", "advanced", "ev_battery"),
        c("## Variotherm (Rapid Heat-Cool Molding)\nVariotherm: rapidly cycle mold temperature between high (during fill) and low (during cool). Benefits: eliminate weld lines, improve surface quality, enable thin-wall filling, achieve high-gloss without painting. Methods: steam heating, induction heating, IR heating, electric cartridge heaters. Temperature swing: typically 60-120°C range in 10-30 seconds. Simulation: Moldflow and Moldex3D support variotherm with time-varying mold temperature boundary condition. Cycle time impact: +5-20s vs conventional.", "advanced", "variotherm"),
        c("## Digital Twin for Injection Molding\nDigital twin: simulation model connected to real-time process data from molding machine. Applications: (1) Virtual setup — predict optimal process before first shot. (2) Process monitoring — compare actual vs predicted values, detect drift. (3) Predictive quality — predict part quality from process signature without measurement. (4) Adaptive process control — adjust parameters in real-time based on material variation. Moldflow 2026: digital twin export capability. Commercial platforms: Sensxpert, iMFLUX (P&G), ENGEL iQ series.", "advanced", "digital_twin"),
    ]


# ═══════════════════════════════════════════
# 13. THEORY & FUNDAMENTALS (~25 chunks)
# ═══════════════════════════════════════════
def theory_chunks():
    return [
        c("## Cross-WLF Viscosity Model\nThe Cross-WLF model describes polymer melt viscosity as a function of shear rate and temperature:\nη(γ̇,T) = η₀(T) / (1 + (η₀·γ̇/τ*)^(1-n))\nwhere η₀(T) = D1·exp(-A1·(T-D2)/(A2+T-D2)) is the zero-shear viscosity (WLF equation), τ* is the critical stress at transition from Newtonian to shear-thinning, n is the power law index (0 = most shear-thinning, 1 = Newtonian). Parameters: D1, D2, A1, A2, n, τ*. Typical values: n=0.1-0.4, τ*=10,000-300,000 Pa. This is THE standard viscosity model for injection molding simulation.", "theory", "cross_wlf"),
        c("## WLF Parameters Physical Meaning\nD1: reference viscosity pre-exponential factor (Pa·s), typically 10^8 to 10^14. D2: reference temperature (K), often close to Tg for amorphous materials. A1: first WLF constant (dimensionless), typically 20-40. A2: second WLF constant (K), typically 50-200. Higher A1 = steeper viscosity drop with temperature. Higher A2 = broader transition region. For amorphous polymers: D2 ≈ Tg. For semi-crystalline: D2 is fitted parameter, may not equal Tg. Pressure dependence sometimes added: D3 coefficient shifts Tg with pressure.", "theory", "wlf_parameters"),
        c("## 2-Domain Tait PVT Equation\nThe 2-domain Tait equation models specific volume as function of temperature and pressure:\nV(T,P) = V₀(T) × (1 - C·ln(1 + P/B(T))) + V_trans(T,P)\nwhere C=0.0894 (universal constant), V₀ is zero-pressure volume, B(T) is pressure sensitivity. Two domains separated by transition temperature T_trans(P): solid (below Tg/Tm) and melt (above). Each domain has different b coefficients (b1-b4 for melt, b5-b8 for solid, b9 for crystallization). This model predicts shrinkage, density, and compressibility during packing and cooling.", "theory", "tait_pvt"),
        c("## Fountain Flow in Injection Molding\nFountain flow: the characteristic flow pattern at the advancing melt front during filling. Melt from the center of the flow channel is carried to the front, where it 'fountains' outward to contact the cold mold wall and freezes. Creates a layered structure: frozen skin (oriented in flow direction) → shear zone → core (oriented perpendicular or random). Important for: fiber orientation (skin-core structure), weld line formation, surface appearance. 3D mesh simulation captures fountain flow; midplane/dual-domain approximate it.", "theory", "fountain_flow"),
        c("## Skin-Core Structure in Injection Molding\nFountain flow creates a layered structure through the part thickness: (1) Frozen skin: first material to contact mold wall, high molecular orientation in flow direction. (2) Shear zone: high shear deformation, fibers aligned with flow. (3) Core: low shear, random or cross-flow orientation (from fountain flow stretching). For fiber-filled materials: skin has fibers in flow direction (low shrinkage), core has fibers perpendicular (high shrinkage in flow direction). This differential causes warpage. Understanding skin-core is essential for predicting fiber-filled part behavior.", "theory", "skin_core"),
        c("## Crystallization Kinetics in Simulation\nSemi-crystalline polymers crystallize during cooling, significantly affecting shrinkage and mechanical properties. Models: Nakamura (isothermal crystallization rate as function of temperature), Hoffman-Lauritzen (nucleation and growth), Dual Nakamura (Moldex3D 2025 — two crystallization phases). Crystallinity depends on: cooling rate (fast cool = low crystallinity = less shrinkage), nucleating agents, fiber reinforcement (heterogeneous nucleation). In simulation: crystallinity distribution through thickness predicted from thermal history.", "theory", "crystallization"),
        c("## Residual Stress in Injection Molded Parts\nThree sources of residual stress: (1) Flow-induced: molecular orientation frozen during cooling (tensile in flow direction, compressive perpendicular). (2) Thermally-induced: differential cooling through thickness creates parabolic stress profile (compressive at surface, tensile at core). (3) Pressure-induced: packing pressure gradients frozen in. Total residual stress = sum of all three. Effects: warpage, reduced impact strength, environmental stress cracking, dimensional instability. Annealing (heating to Tg-20°C for hours) reduces residual stress.", "theory", "residual_stress"),
        c("## Shear Rate in Injection Molding\nShear rate is the velocity gradient across the flow channel. Maximum shear rate occurs at the mold wall. Calculation: γ̇_wall = 6Q/(W·H²) for rectangular channel, γ̇_wall = 4Q/(π·R³) for round channel (Newtonian). For power-law fluids: multiply by (2n+1)/(3n) correction. Typical ranges: gate 5,000-50,000 1/s, runner 1,000-10,000 1/s, cavity wall 100-10,000 1/s. Exceeding material limit causes: degradation, splay marks, burning. Check material datasheet for maximum allowable shear rate.", "theory", "shear_rate"),
        c("## Heat Transfer in Injection Molding\nThree modes: (1) Conduction: primary mode — heat transfers from hot melt through mold wall to coolant. Rate depends on thermal conductivity of polymer (~0.1-0.4 W/m·K) and steel (~25-50 W/m·K). Polymer is the bottleneck. (2) Convection: coolant-side heat transfer. Turbulent flow (Re>10000) has 5-10× better heat transfer than laminar. (3) Radiation: negligible in closed mold. Total heat to remove per cycle = mass × (enthalpy at melt temp - enthalpy at ejection temp). For PP: ~500 kJ/kg.", "theory", "heat_transfer"),
        c("## Clamping Force Calculation\nClamp force must exceed force from cavity pressure pushing mold halves apart. F_clamp = P_cavity × A_projected × safety_factor. Projected area: part + runner projected onto parting plane. Cavity pressure: typically 30-80 MPa for thermoplastics. Rule of thumb: 3-5 tons/in² (46-77 MPa) of projected area for most resins. PC needs more (5-7 t/in²), PP needs less (2-4 t/in²). Safety factor: 1.1-1.2. From simulation: use maximum clamp force result — should be <80% of machine capacity.", "theory", "clamping_force"),
        c("## No-Flow Temperature\nNo-flow temperature (T_nf): temperature below which polymer stops flowing (viscosity too high). For amorphous materials: T_nf ≈ Tg + 10-30°C. For semi-crystalline: T_nf ≈ Tm - 10°C (crystallization freezes the melt). In simulation: when a mesh element reaches T_nf, it's treated as 'frozen' — no more flow. Gate freeze: when gate region reaches T_nf, packing stops. Frozen layer fraction: percentage of thickness that has reached T_nf. At ejection, typically >80% should be frozen.", "theory", "no_flow_temperature"),
        c("## Volumetric Shrinkage and Part Weight\nVolumetric shrinkage = (V_mold - V_part) / V_mold. Depends on: material PVT behavior, packing pressure, cooling rate. Higher packing pressure = less shrinkage. Faster cooling = less crystallinity = less shrinkage (semi-crystalline). Typical values: amorphous 0.4-0.8%, semi-crystalline 1-3%. Shrinkage is non-uniform: less near gate (high packing), more far from gate. Part weight correlates with shrinkage — heavier part = less shrinkage = better packed. Gate seal study: plot part weight vs hold time to find gate freeze time.", "theory", "shrinkage"),
        c("## Reynolds Number for Cooling Channels\nRe = ρ·v·D/μ where ρ=coolant density, v=velocity, D=channel diameter, μ=dynamic viscosity. For water at 25°C: ρ=997 kg/m³, μ=0.00089 Pa·s. Turbulent flow (Re>10000): much better heat transfer (Nusselt number scales with Re^0.8). Laminar flow (Re<2300): poor heat transfer, temperature gradient across channel. For 10mm channel with water: need flow rate > 0.7 L/min per channel for turbulent flow. Series circuits maintain higher velocity (better turbulence) than parallel.", "theory", "reynolds_number"),
        c("## Fiber Orientation Tensor\nFiber orientation described by second-order tensor A_ij (3×3 symmetric). Diagonal elements: A_11 = alignment in flow direction, A_22 = alignment in cross-flow, A_33 = alignment in thickness. A_11 = 1 means all fibers in flow direction. A_11 = 1/3, A_22 = 1/3, A_33 = 1/3 means random (isotropic). Typical injection molded part: skin layer A_11 ≈ 0.7-0.9 (highly aligned in flow), core A_22 ≈ 0.5-0.7 (cross-flow from fountain flow). This tensor directly feeds into anisotropic shrinkage and mechanical property prediction.", "theory", "fiber_tensor"),
        c("## Thermal Diffusivity and Cooling\nThermal diffusivity α = k/(ρ·Cp) where k=thermal conductivity, ρ=density, Cp=specific heat. This property controls how fast heat moves through the material. Typical values: polymers α ≈ 0.1-0.15 mm²/s, steel α ≈ 10-15 mm²/s, BeCu α ≈ 30-40 mm²/s. Cooling time scales with thickness² / α. That's why doubling wall thickness quadruples cooling time. This is the single most important thermal property for cycle time estimation.", "theory", "thermal_diffusivity"),
    ]


# ═══════════════════════════════════════════
# 14. BEST PRACTICES & WORKFLOWS (~15 chunks)
# ═══════════════════════════════════════════
def best_practice_chunks():
    return [
        c("## Simulation Project Workflow\n1. Define objectives (what questions to answer)\n2. Obtain and prepare CAD (defeaturing, parting line)\n3. Generate mesh (choose type based on part)\n4. Select material (verify data completeness)\n5. Set process conditions (melt temp, mold temp, injection time)\n6. Place gate(s) and runner\n7. Run fill analysis → validate\n8. Run pack analysis → optimize hold pressure\n9. Run cooling analysis → design cooling circuits\n10. Run warpage analysis → evaluate\n11. Iterate: modify design, gate, process, cooling\n12. Document and report findings", "best_practices", "workflow"),
        c("## Simulation Report Best Practices\nA good simulation report includes: (1) Executive summary with go/no-go recommendation. (2) Model description: geometry, mesh type and count, material. (3) Process conditions used. (4) Fill results: fill time, pressure, clamp force, weld lines, air traps. (5) Pack results: volumetric shrinkage, sink marks, holding pressure profile. (6) Cool results: cycle time, temperature uniformity, circuit performance. (7) Warp results: total deflection, breakdown by cause. (8) Recommendations: design changes, process optimization, gate/cooling modifications. Always include screenshots of key results with color legends.", "best_practices", "reporting"),
        c("## When to Use 3D vs Dual-Domain Mesh\nUse 3D mesh when: (1) wall thickness > 4mm, (2) glass-fiber filled material (need skin-core), (3) gas-assist or foam molding, (4) significant 3D flow effects (thick-to-thin transitions), (5) warpage accuracy is critical, (6) cooling analysis with conformal channels. Use dual-domain (Fusion) when: (1) thin-wall uniform thickness, (2) quick feasibility study needed, (3) many design iterations (faster solve), (4) unfilled materials. Never use midplane for production analysis — it's only for quick screening.", "best_practices", "mesh_selection"),
        c("## Common Simulation Mistakes\n1. Wrong material selection (generic vs actual grade)\n2. Incorrect gate location or size\n3. Too coarse mesh (results not converged)\n4. Ignoring cooling circuit design (using uniform mold temperature)\n5. Wrong packing profile (too short, wrong pressure)\n6. Not checking shear rate limits\n7. Not validating simulation against real molding data\n8. Over-interpreting results (treating simulation as exact)\n9. Not running mesh sensitivity study\n10. Using midplane mesh for fiber-filled materials", "best_practices", "common_mistakes"),
        c("## Simulation Validation\nValidation: compare simulation predictions to actual molding trial data. Key metrics to compare: (1) fill pressure vs machine peak pressure (should match within ±15%). (2) Fill pattern vs short shots (visual comparison). (3) Clamp force vs machine reading. (4) Warpage magnitude and direction. (5) Cycle time. If simulation and reality disagree by >20%: check material data accuracy, check actual process conditions match simulation inputs, verify mesh quality. Published validation studies show ±10-20% accuracy for pressure, ±20-30% for warpage.", "best_practices", "validation"),
        c("## Simulation for Mold Quoting\nUsing simulation in mold quoting: (1) Quick fill study to determine gate count and type. (2) Clamp force estimation for machine sizing. (3) Cooling analysis for cycle time estimate. (4) Warpage check to set dimensional expectations. (5) Runner sizing for material usage. Typical turnaround: 1-3 days for fill+pack+warp study. This allows mold makers to quote with confidence on process parameters, cycle time, and machine requirements. Reduces trial-and-error costs by 50-70% according to industry surveys.", "best_practices", "quoting"),
        c("## Simulation-Driven Mold Design Iteration\nTypical iteration loop: (1) Initial design → simulation shows problems (e.g., warpage, weld lines). (2) Modify gate location → re-run → check improvement. (3) Modify cooling → re-run → check cycle time and warpage. (4) Adjust process parameters → re-run → optimize window. (5) Final validation run with all optimizations. Average: 3-5 iterations to converge on acceptable design. Each iteration: 2-8 hours solve time for 3D analysis. Total project: 1-3 weeks for complex automotive parts.", "best_practices", "iteration"),
        c("## Material Testing for Simulation\nCustom material characterization for simulation: (1) Capillary rheometry — measures viscosity vs shear rate at multiple temperatures → fit Cross-WLF. (2) PVT measurement — specific volume vs temperature at multiple pressures → fit Tait equation. (3) DSC (Differential Scanning Calorimetry) — crystallization kinetics for semi-crystalline → fit Nakamura model. (4) Thermal conductivity (TPS or laser flash) vs temperature. (5) Specific heat vs temperature. Cost: $3,000-8,000 per grade. Lead time: 4-8 weeks. Required when exact grade not in simulation database.", "best_practices", "material_testing"),
    ]


# ═══════════════════════════════════════════
# 15. INDUSTRY-SPECIFIC (~20 chunks)
# ═══════════════════════════════════════════
def industry_chunks():
    return [
        c("## Automotive Interior Parts\nDashboard, door panels, console: typically PC/ABS or PP+EPDM. Large parts (up to 1.5m) require multiple gates with sequential valve gating. Grain texture needs adequate draft. Class A surface requirements: no sink marks, flow marks, or weld lines on visible surfaces. Simulation focus: warpage (tight fit requirements), weld line placement, gate vestige location, cycle time optimization. Material: low-gloss PC/ABS for premium, talc-filled PP for economy.", "industry", "automotive_interior"),
        c("## Automotive Exterior Parts (Bumpers)\nBumpers: PP+EPDM or PC/PBT blend. Length up to 2m. 4-8 valve gates with sequential opening. Key requirements: dimensional accuracy for body gap/flush, paintability, impact performance at -30°C. Simulation: critical for gate timing in SVG, warpage (must meet ±0.5mm gap/flush), weld line locations (mechanical performance), cooling for cycle time. Typical cycle time: 45-60s. Mold cost: $500K-2M.", "industry", "automotive_exterior"),
        c("## Automotive Under-Hood Components\nEngine covers, intake manifolds, radiator tanks: PA66-GF30/50, PPA-GF, PPS-GF. High temperature exposure (up to 200°C continuous). Requirements: dimensional stability at elevated temperature, chemical resistance (oils, coolant), vibration fatigue resistance. Simulation focus: fiber orientation for mechanical properties, warpage at elevated temperature (post-mold warpage from crystallization), insert molding for metal brackets.", "industry", "automotive_underhood"),
        c("## Medical Device Molding\nMedical parts: syringes, IV components, inhalers, diagnostic housings. Materials: medical-grade PP, PE, PC, PPSU, PEEK. Requirements: biocompatibility (ISO 10993), tight tolerances (±0.025mm), cleanroom production, lot traceability. Simulation concerns: cavity-to-cavity consistency in multi-cavity molds (32-128 cavities for syringes), dimensional accuracy, residual stress (affects long-term dimensional stability and chemical resistance). Material data: use exact medical grade, not generic.", "industry", "medical"),
        c("## Packaging (Thin-Wall)\nFood containers, lids, cups: PP, PS, PET. Wall thickness 0.3-0.7mm. Cycle time <5s. Multi-cavity (4-64 cavities). Extremely high injection speed (500-1000+ mm/s). Stack molds common for high cavities. Requirements: uniform wall distribution for stacking, FDA compliance, barrier properties. Simulation: 3D mesh required for thin-wall accuracy, high-speed filling dynamics, heat transfer during extremely short cooling time. Material: high-flow grades with MFI 50-100+ g/10min.", "industry", "packaging"),
        c("## Electronics Enclosures\nSmartphone cases, laptop housings, tablet frames: PC, PC/ABS, PA, magnesium die-cast alternatives. Requirements: tight dimensional tolerances (±0.05mm for snap-fits), EMI shielding (some applications), surface finish (high-gloss or textured), thin walls (0.8-1.5mm). Simulation focus: warpage for assembly fit, weld line strength (drop test performance), gate location for cosmetics, cooling for fast cycle. Multi-material: overmolded soft-touch grips, co-molded transparent windows.", "industry", "electronics"),
        c("## Consumer Goods and Appliances\nHousing, handles, knobs, internal frames: ABS, PP, PA, POM. Wide range of requirements. Cost-sensitive — optimize cycle time and minimize material usage. Simulation value: gate location for cosmetics (no gate blush on visible surfaces), warpage control, rib/boss optimization (sink marks), snap-fit design validation. Multi-cavity molds (2-16 cavities typical). Color matching: consistent melt temperature across cavities needed for uniform color.", "industry", "consumer_goods"),
        c("## Optical and Lighting Parts\nLenses, light guides, light pipes, headlamp housings: PMMA, PC (optical grades), COC, COP. Requirements: optical clarity (>90% transmission), minimal birefringence (low residual stress), tight surface accuracy (Ra <0.01μm), no flow marks or weld lines. Simulation: birefringence prediction from residual stress analysis, warpage affecting optical surface, gate location to avoid weld lines in optical path. Process: slow injection, high mold temp (120-140°C for PC), long pack time, gradual cooling.", "industry", "optical"),
        c("## Connector and Micro-Molding\nElectrical connectors, micro-parts: PBT-GF, PA-GF, LCP. Feature sizes <0.3mm, wall <0.5mm. Multi-cavity (32-128 cavities). Requirements: pin-to-pin accuracy ±0.01mm, flash-free (for electrical contact surfaces), consistent fill across all cavities. Simulation: 3D mesh with very fine resolution, runner balancing critical, venting for micro-features. LCP (Liquid Crystal Polymer): low viscosity, very fast fill, excellent for thin features but high anisotropy.", "industry", "connectors"),
        c("## Pipe and Fitting Molding\nPipes, elbows, tees, valves: PVC, PP-R, PE-RT, CPVC. Pressure-rated applications. Requirements: uniform wall thickness, no voids or porosity (pressure failure risk), proper weld knit strength. Simulation: fill balance in complex geometries (tees, crosses), warpage causing out-of-round (dimensional tolerance for sealing surfaces), packing uniformity for pressure rating. Large fittings: cycle time optimization important (thick walls, long cooling). PVC: sensitive to degradation — minimize residence time, avoid hot spots.", "industry", "pipes_fittings"),
    ]


# ═══════════════════════════════════════════
# 16. FIBER ORIENTATION DEEP DIVE (~10 chunks)
# ═══════════════════════════════════════════
def fiber_chunks():
    return [
        c("## Fiber Orientation in Injection Molding\nShort glass fiber reinforced plastics (10-50% GF by weight) are among the most widely used engineering materials. Fiber orientation during molding critically affects: mechanical properties (2-3× stronger in fiber direction), shrinkage (2-4× less in fiber direction), warpage (differential shrinkage). Understanding and predicting fiber orientation is essential for accurate structural simulation and warpage prediction. Key factors: gate location (determines flow pattern), part geometry, material (fiber loading, length, diameter), and process conditions.", "fiber", "overview"),
        c("## Folgar-Tucker Fiber Orientation Model\nThe Folgar-Tucker (FT) model is the standard computational model for predicting fiber orientation. Based on Jeffery's equation for single fiber in dilute suspension + interaction coefficient (Ci) for fiber-fiber interactions. The model predicts evolution of orientation tensor A_ij along flow path. Known limitation: over-predicts alignment speed (fibers reach steady state too quickly). Ci typically fitted from experimental data (0.001-0.01 for 30% GF). Despite limitations, FT is the baseline model in all commercial simulators.", "fiber", "folgar_tucker"),
        c("## RSC (Reduced Strain Closure) Model\nRSC model by Phelps and Tucker (2009) addresses the over-prediction of fiber alignment in the Folgar-Tucker model. Introduces a 'slowness factor' κ (0 < κ < 1) that reduces the rate of fiber orientation evolution. When κ = 1, RSC = FT. Typical κ = 0.1-0.3 for concentrated fiber suspensions. Result: core region retains more random orientation, matching experimental observations better. RSC is available in Moldflow and Moldex3D. Recommended as minimum model for fiber-filled warpage analysis.", "fiber", "rsc"),
        c("## ARD-RSC and MRD Models\nARD-RSC (Anisotropic Rotary Diffusion + RSC): extends RSC by making the fiber interaction anisotropic (direction-dependent). Five parameters (b1-b5) + κ. More accurate for complex flow fields but requires more fitting data. MRD (Moldflow Rotational Diffusion): Moldflow's proprietary model introduced in 2024. Simplified parameter set compared to ARD-RSC. pARD-RSC: accounts for fiber concentration gradients through thickness. These advanced models give 10-30% better warpage prediction compared to standard FT.", "fiber", "ard_mrd"),
        c("## Long Fiber Reinforcement (LFT)\nLong fiber thermoplastics (LFT): initial fiber length 10-25mm (vs 0.3-0.5mm for short fiber). During injection molding, fibers break down — final length distribution 1-5mm. Fiber breakage occurs in: screw plasticating, runner system, and gate. Simulation: Moldflow 2026 includes improved fiber breakage prediction model. Moldex3D: fiber breakage model predicts final length distribution. Mechanical properties depend on final fiber length (longer = stronger, but length varies through the part). Fiber breakage is worse at: narrow gates, sharp turns, high screw RPM.", "fiber", "long_fiber"),
        c("## Fiber Orientation Measurement\nExperimental methods to validate fiber orientation predictions: (1) Micro-CT scanning (X-ray tomography) — 3D fiber orientation without cutting, resolution ~5μm. (2) Optical microscopy of polished cross-sections — measure elliptical footprint of fiber cross-sections to determine angle. (3) Image analysis (CCD cameras + algorithms) for automated measurement. Standard: ASTM D5592 for fiber length distribution. Orientation tensor from micro-CT is directly comparable to simulation output. Cost: micro-CT analysis $1K-5K per sample.", "fiber", "measurement"),
    ]


# ═══════════════════════════════════════════
# 17. SHRINKAGE DEEP DIVE (~8 chunks)
# ═══════════════════════════════════════════
def shrinkage_chunks():
    return [
        c("## Shrinkage Mechanisms\nShrinkage has three main mechanisms: (1) Thermal contraction — all polymers contract as they cool. Coefficient of thermal expansion (CTE) determines magnitude. (2) Crystallization shrinkage — semi-crystalline polymers undergo additional volume reduction as crystalline phase forms. Can be 5-15% of total volume depending on crystallinity level. (3) Pressure relaxation — material at high packing pressure has compressed volume; as pressure releases, material expands slightly (but net effect is still shrinkage). Total shrinkage = thermal + crystallization - residual pressure effect.", "shrinkage", "mechanisms"),
        c("## Shrinkage Prediction in Simulation\nSimulation predicts shrinkage from PVT (pressure-volume-temperature) data. The 2-domain Tait equation models specific volume at any T and P. Shrinkage = 1 - V(T_eject, P_atm)/V_mold_cavity. Key insight: shrinkage varies through the part because: (1) packing pressure varies (less near gate, more far from gate), (2) cooling rate varies (surface vs core, cooling channel proximity), (3) fiber orientation varies (glass-filled). CRIMS data (Corrected Residual In-Mold Stress) improves shrinkage prediction by accounting for frozen-in stress effects.", "shrinkage", "prediction"),
        c("## Anisotropic Shrinkage in Fiber-Filled Materials\nGlass-fiber reinforced materials show highly anisotropic shrinkage: flow direction shrinkage 0.2-0.5%, cross-flow shrinkage 0.8-1.5% (for 30% GF). Ratio can be 3:1 or higher. Cause: fibers aligned in flow direction constrain shrinkage in that direction. Mold design must compensate differently in X, Y, Z. Simulation predicts directional shrinkage from fiber orientation tensor. For warpage: the differential shrinkage between skin (flow-aligned) and core (cross-aligned) creates bending. This is the primary warpage mechanism for GF parts.", "shrinkage", "anisotropic"),
        c("## Mold Scaling from Shrinkage\nMold cavity is oversized to compensate for part shrinkage. Scale factor = 1 / (1 - shrinkage). For 1% shrinkage: scale = 1.0101 (multiply all dimensions by 1.0101). Challenges: shrinkage is not uniform (varies by location, direction, and thickness). Approach: (1) Uniform scaling with nominal shrinkage — simple but approximate. (2) Non-uniform scaling from simulation — apply different scale factors to different regions. (3) Morphed cavity from warpage compensation — most advanced, modifies cavity shape based on inverse of predicted warpage.", "shrinkage", "mold_scaling"),
    ]


# ═══════════════════════════════════════════
# 18. HOT RUNNER DEEP DIVE (~8 chunks)
# ═══════════════════════════════════════════
def hot_runner_chunks():
    return [
        c("## Hot Runner System Types\nExternally heated: heaters on outside of manifold/nozzle. Large flow channels, low pressure drop, good for heat-sensitive materials (PVC, POM). Self-insulating melt in contact with channel walls. Internally heated: torpedo/probe inside flow channel heats melt from center. Smaller channels. Good for crystalline materials (prevents freeze-off). Insulated runner: large channel diameter (25-50mm) with frozen melt insulating outer wall. Simplest design, limited material compatibility, requires frequent purging.", "hot_runner", "types"),
        c("## Hot Runner Temperature Control\nEach zone independently controlled: manifold zones (2-8), nozzle zones (1 per drop), sometimes tip zones. Temperature uniformity: ±2°C target. Thermocouples: J-type or K-type, placed in melt channel for accuracy. Controller: PID with auto-tune, ramp-up protection (gradual heating prevents thermal shock). Power: 200-1000W per nozzle, 500-3000W per manifold zone. Start-up sequence: manifold first (lower temp), then nozzles. Monitor melt temperature at each drop — variation indicates blocked nozzle or failed heater.", "hot_runner", "temperature"),
        c("## Hot Runner Balancing\nNatural balance: all flow paths equal length and diameter — expensive but ideal. Artificial balance: different nozzle sizes or temperature offsets to equalize flow. Methods to diagnose imbalance: (1) short shots — check which cavities fill first, (2) weigh parts per cavity, (3) simulation — predict pressure/flow distribution. Causes of imbalance: unequal manifold channel lengths, thermal gradients in manifold, shear-induced imbalance at branch points, nozzle variation. Simulation: model hot runner geometry explicitly in Moldflow/Moldex3D for accurate balancing.", "hot_runner", "balancing"),
        c("## Valve Gate Technology\nValve gate: mechanical pin opens/closes gate to part. Actuated by: pneumatic (most common), hydraulic (high force), electric (precise position control). Benefits: no gate vestige (flush surface), precise flow control, enable sequential molding, no drool or stringing. Pin diameter: 2-8mm typical. Stroke: 5-15mm. Close timing: critical for gate quality (too early = mark, too late = pin pushes into part). Electric valve gates: enable partial opening (throttle flow) for speed control without changing machine speed.", "hot_runner", "valve_gate"),
    ]


# ═══════════════════════════════════════════
# MAIN: Assemble all chunks and upload
# ═══════════════════════════════════════════
def make_chunks():
    all_chunks = []
    all_chunks.extend(material_chunks())
    all_chunks.extend(troubleshooting_chunks())
    all_chunks.extend(warpage_chunks())
    all_chunks.extend(cooling_chunks())
    all_chunks.extend(gate_runner_chunks())
    all_chunks.extend(dfm_chunks())
    all_chunks.extend(mesh_chunks())
    all_chunks.extend(process_chunks())
    all_chunks.extend(moldflow_chunks())
    all_chunks.extend(moldex3d_chunks())
    all_chunks.extend(open_source_chunks())
    all_chunks.extend(advanced_process_chunks())
    all_chunks.extend(theory_chunks())
    all_chunks.extend(best_practice_chunks())
    all_chunks.extend(industry_chunks())
    all_chunks.extend(fiber_chunks())
    all_chunks.extend(shrinkage_chunks())
    all_chunks.extend(hot_runner_chunks())
    return all_chunks


def main():
    chunks = make_chunks()
    print(f"Total chunks: {len(chunks)}")

    # Embed all texts
    print(f"Loading embedding model: {MODEL}")
    embedder = TextEmbedding(MODEL)
    texts = [ch["text"] for ch in chunks]
    print("Embedding all chunks...")
    embeddings = list(embedder.embed(texts))
    print(f"Embedded {len(embeddings)} chunks, dim={len(embeddings[0])}")

    # Connect to Qdrant
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Recreate collection
    try:
        client.delete_collection(COLLECTION)
        print(f"Deleted existing collection '{COLLECTION}'")
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION}'")

    # Upload in batches
    BATCH = 100
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i+BATCH]
        batch_emb = embeddings[i:i+BATCH]
        points = []
        for ch, emb in zip(batch, batch_emb):
            payload = {"text": ch["text"], "category": ch["category"]}
            if "subcategory" in ch:
                payload["subcategory"] = ch["subcategory"]
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=emb.tolist(),
                payload=payload,
            ))
        client.upsert(collection_name=COLLECTION, points=points)
        print(f"  Uploaded batch {i//BATCH + 1} ({len(points)} points)")

    info = client.get_collection(COLLECTION)
    print(f"\nDone! Collection '{COLLECTION}' has {info.points_count} points.")

    # Quick test
    test_query = "How to fix warpage in glass-filled nylon?"
    test_emb = list(embedder.embed([test_query]))[0]
    results = client.query_points(
        collection_name=COLLECTION,
        query=test_emb.tolist(),
        limit=3,
        with_payload=True,
    )
    print(f"\nTest query: '{test_query}'")
    for r in results.points:
        print(f"  [{r.score:.3f}] {r.payload.get('category')}/{r.payload.get('subcategory', '-')}: {r.payload['text'][:80]}...")


if __name__ == "__main__":
    main()
