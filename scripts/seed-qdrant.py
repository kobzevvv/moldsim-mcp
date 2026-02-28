#!/usr/bin/env python3
"""
Seed Qdrant Cloud with injection molding simulation knowledge.

Uses fastembed for local embeddings (all-MiniLM-L6-v2, 384 dims).
Chunks: materials, troubleshooting, DFM guidelines, mesh guidelines,
process bounds, plus comprehensive simulation domain knowledge.
"""

import json
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding

# ── Config ──
QDRANT_URL = "https://d072a605-3a1a-471a-aaf3-a6bdd11f07d2.us-west-2-0.aws.cloud.qdrant.io:6333"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.9tpiCCNFb9wWBzxVJkT21qcWDYqZ0PV1fu9siVlo3kY"
COLLECTION = "moldsim_knowledge"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dims
VECTOR_SIZE = 384

def make_chunks():
    """Generate all knowledge chunks with metadata."""
    chunks = []

    # ══════════════════════════════════════════════
    # MATERIALS — comprehensive entries per material
    # ══════════════════════════════════════════════
    materials = [
        {
            "id": "abs-generic", "name": "ABS Generic", "family": "ABS", "type": "amorphous",
            "melt_range": "220-260°C", "mold_range": "40-80°C", "rec_melt": "240°C", "rec_mold": "60°C",
            "shrinkage": "0.4-0.7%", "density": "1050 kg/m³",
            "notes": "General-purpose ABS. Good impact resistance and processability. Hygroscopic — must dry at 80°C for 3h before molding. Max shear rate 50000 1/s. Residence time max 8 min.",
            "cross_wlf": "n=0.2694, τ*=30820 Pa, D1=4.89e10 Pa·s, D2=373.15 K, A1=23.76, A2=51.6 K",
            "applications": "Consumer electronics housings, automotive interior trim, appliance housings, toys, luggage",
        },
        {
            "id": "pp-homo", "name": "PP Homopolymer", "family": "PP", "type": "semi-crystalline",
            "melt_range": "200-280°C", "mold_range": "20-80°C", "rec_melt": "230°C", "rec_mold": "40°C",
            "shrinkage": "1.0-2.5%", "density": "905 kg/m³",
            "notes": "Most widely used thermoplastic. High shrinkage and warpage tendency. Non-hygroscopic — no drying needed. Excellent chemical resistance. Max shear rate 100000 1/s.",
            "cross_wlf": "n=0.2853, τ*=25000 Pa, D1=2.87e11 Pa·s, D2=263.15 K, A1=27.8, A2=51.6 K",
            "applications": "Packaging, caps, automotive bumpers, battery cases, containers, living hinges",
        },
        {
            "id": "pp-copo", "name": "PP Copolymer (Impact)", "family": "PP", "type": "semi-crystalline",
            "melt_range": "200-270°C", "mold_range": "20-60°C", "rec_melt": "225°C", "rec_mold": "35°C",
            "shrinkage": "1.2-2.2%", "density": "900 kg/m³",
            "notes": "Better impact resistance than homopolymer especially at low temperatures. Used in automotive interiors. Non-hygroscopic.",
            "cross_wlf": "n=0.3012, τ*=24500 Pa, D1=1.95e11 Pa·s, D2=258.15 K, A1=26.9, A2=51.6 K",
            "applications": "Automotive interior panels, appliance housings, outdoor furniture, cold-storage containers",
        },
        {
            "id": "pa6", "name": "PA6 (Nylon 6)", "family": "PA", "type": "semi-crystalline",
            "melt_range": "240-290°C", "mold_range": "60-100°C", "rec_melt": "260°C", "rec_mold": "80°C",
            "shrinkage": "0.8-1.5%", "density": "1130 kg/m³",
            "notes": "Very hygroscopic — MUST dry to <0.2% moisture at 80°C for 6h. Good toughness and wear resistance. Sharp crystallization behavior. Max shear rate 60000 1/s. Residence time max 6 min.",
            "cross_wlf": "n=0.2563, τ*=85650 Pa, D1=1.51e12 Pa·s, D2=323.15 K, A1=30.63, A2=51.6 K",
            "applications": "Gears, bearings, bushings, cable ties, power tool housings, automotive under-hood",
        },
        {
            "id": "pa66", "name": "PA66 (Nylon 66)", "family": "PA", "type": "semi-crystalline",
            "melt_range": "270-300°C", "mold_range": "70-110°C", "rec_melt": "285°C", "rec_mold": "80°C",
            "shrinkage": "0.8-1.5%", "density": "1140 kg/m³",
            "notes": "Higher melting point than PA6. Very sensitive to moisture — dry to <0.1%. Narrow processing window. Max shear rate 60000 1/s. Max residence time 5 min.",
            "cross_wlf": "n=0.2618, τ*=91200 Pa, D1=4.42e12 Pa·s, D2=333.15 K, A1=32.15, A2=51.6 K",
            "applications": "Electrical connectors, automotive structural parts, zip ties, brush bristles",
        },
        {
            "id": "pa66-gf30", "name": "PA66-GF30 (30% Glass Fiber)", "family": "PA", "type": "semi-crystalline",
            "melt_range": "275-310°C", "mold_range": "80-120°C", "rec_melt": "290°C", "rec_mold": "90°C",
            "shrinkage": "0.3-1.0% (anisotropic)", "density": "1380 kg/m³",
            "notes": "Anisotropic shrinkage — flow direction vs cross-flow differ significantly. Fiber orientation critical for warpage prediction. Abrasive to tooling — hardened steel required. Very hygroscopic. 30% glass fiber content.",
            "cross_wlf": "n=0.3265, τ*=57340 Pa, D1=3.12e12 Pa·s, D2=333.15 K, A1=31.2, A2=51.6 K",
            "applications": "Structural automotive (engine brackets, pedals), electrical connectors, power tool housings",
        },
        {
            "id": "pc", "name": "PC (Polycarbonate)", "family": "PC", "type": "amorphous",
            "melt_range": "280-320°C", "mold_range": "80-120°C", "rec_melt": "300°C", "rec_mold": "90°C",
            "shrinkage": "0.5-0.7%", "density": "1200 kg/m³",
            "notes": "Excellent transparency and impact resistance. High viscosity — needs high injection pressure. Sensitive to stress cracking from chemicals. Must dry at 120°C for 4h. Max shear rate 40000 1/s.",
            "cross_wlf": "n=0.1816, τ*=307100 Pa, D1=5.73e14 Pa·s, D2=418.15 K, A1=35.5, A2=51.6 K",
            "applications": "Lenses, safety glasses, medical devices, automotive headlamp covers, phone cases",
        },
        {
            "id": "pc-abs", "name": "PC/ABS Blend", "family": "PC/ABS", "type": "amorphous",
            "melt_range": "250-290°C", "mold_range": "60-100°C", "rec_melt": "270°C", "rec_mold": "75°C",
            "shrinkage": "0.5-0.7%", "density": "1150 kg/m³",
            "notes": "Combines PC heat resistance with ABS processability. Easier to mold than pure PC. Must dry at 100°C for 3h. Common in automotive and electronics.",
            "cross_wlf": "n=0.2345, τ*=85000 Pa, D1=8.12e11 Pa·s, D2=393.15 K, A1=28.5, A2=51.6 K",
            "applications": "Automotive instrument panels, laptop housings, phone cases, printer parts",
        },
        {
            "id": "pom", "name": "POM (Acetal/Delrin)", "family": "POM", "type": "semi-crystalline",
            "melt_range": "190-230°C", "mold_range": "60-120°C", "rec_melt": "210°C", "rec_mold": "90°C",
            "shrinkage": "1.8-2.5%", "density": "1410 kg/m³",
            "notes": "Excellent dimensional stability and low friction. NARROW processing window — degrades above 230°C releasing formaldehyde gas. NEVER exceed 220°C. Purge with PE before shutdown. Non-hygroscopic.",
            "cross_wlf": "n=0.2958, τ*=62400 Pa, D1=5.42e10 Pa·s, D2=268.15 K, A1=25.1, A2=51.6 K",
            "applications": "Gears, bearings, clips, zippers, plumbing fittings, fuel system components",
        },
        {
            "id": "hdpe", "name": "HDPE (High Density Polyethylene)", "family": "PE", "type": "semi-crystalline",
            "melt_range": "200-280°C", "mold_range": "20-60°C", "rec_melt": "230°C", "rec_mold": "30°C",
            "shrinkage": "1.5-3.0%", "density": "955 kg/m³",
            "notes": "High shrinkage and warpage tendency. Non-hygroscopic. Excellent chemical resistance. High thermal conductivity for a polymer (0.44 W/mK).",
            "cross_wlf": "n=0.3856, τ*=28500 Pa, D1=1.82e10 Pa·s, D2=223.15 K, A1=22.5, A2=51.6 K",
            "applications": "Bottle caps, containers, crates, pipes, fuel tanks",
        },
        {
            "id": "pmma", "name": "PMMA (Acrylic)", "family": "PMMA", "type": "amorphous",
            "melt_range": "220-260°C", "mold_range": "50-80°C", "rec_melt": "240°C", "rec_mold": "65°C",
            "shrinkage": "0.3-0.6%", "density": "1190 kg/m³",
            "notes": "Excellent optical clarity — 92% light transmission. Brittle. Scratches easier than PC. Must dry at 80°C for 4h.",
            "cross_wlf": "n=0.2142, τ*=125000 Pa, D1=7.82e12 Pa·s, D2=378.15 K, A1=31.8, A2=51.6 K",
            "applications": "Automotive lighting lenses, displays, light guides, cosmetic packaging, aquariums",
        },
        {
            "id": "pbt", "name": "PBT (Polybutylene Terephthalate)", "family": "PBT", "type": "semi-crystalline",
            "melt_range": "240-275°C", "mold_range": "40-100°C", "rec_melt": "255°C", "rec_mold": "70°C",
            "shrinkage": "1.3-2.0%", "density": "1310 kg/m³",
            "notes": "Fast crystallization — enables short cycle times. Good electrical properties. Hygroscopic — dry at 120°C for 4h. Excellent for connectors and switches.",
            "cross_wlf": "n=0.2785, τ*=72500 Pa, D1=6.25e10 Pa·s, D2=318.15 K, A1=26.2, A2=51.6 K",
            "applications": "Electrical connectors, switches, relay housings, automotive sensors",
        },
        {
            "id": "pbt-gf30", "name": "PBT-GF30 (30% Glass Fiber)", "family": "PBT", "type": "semi-crystalline",
            "melt_range": "250-280°C", "mold_range": "60-110°C", "rec_melt": "265°C", "rec_mold": "80°C",
            "shrinkage": "0.3-1.2% (anisotropic)", "density": "1530 kg/m³",
            "notes": "Anisotropic shrinkage due to fiber orientation. Excellent creep resistance. Used for structural connectors. Dry at 120°C for 4h.",
            "cross_wlf": "n=0.3185, τ*=52800 Pa, D1=4.85e10 Pa·s, D2=318.15 K, A1=25.8, A2=51.6 K",
            "applications": "Structural electrical connectors, automotive housings, sensor enclosures",
        },
        {
            "id": "pet", "name": "PET (Polyethylene Terephthalate)", "family": "PET", "type": "semi-crystalline",
            "melt_range": "270-300°C", "mold_range": "20-140°C", "rec_melt": "285°C", "rec_mold": "30°C",
            "shrinkage": "1.0-2.5%", "density": "1340 kg/m³",
            "notes": "Unique dual behavior: Hot mold (140°C) = crystalline opaque with high shrinkage. Cold mold (30°C) = amorphous transparent with low shrinkage. Very hygroscopic — dry at 160°C for 4h.",
            "cross_wlf": "n=0.2385, τ*=95000 Pa, D1=2.15e12 Pa·s, D2=345.15 K, A1=30.2, A2=51.6 K",
            "applications": "Bottles (preforms), packaging trays, electrical connectors, automotive reflectors",
        },
        {
            "id": "tpu", "name": "TPU (Thermoplastic Polyurethane 85A)", "family": "TPU", "type": "semi-crystalline",
            "melt_range": "190-230°C", "mold_range": "20-50°C", "rec_melt": "210°C", "rec_mold": "35°C",
            "shrinkage": "0.8-2.0%", "density": "1200 kg/m³",
            "notes": "Elastomeric. Use LOW injection speed to avoid shear heating. Very hygroscopic — dry at 80°C for 3h. Flexible material. Max shear rate only 20000 1/s.",
            "cross_wlf": "n=0.3456, τ*=15000 Pa, D1=2.85e9 Pa·s, D2=253.15 K, A1=21.8, A2=51.6 K",
            "applications": "Shoe soles, phone cases, seals, gaskets, sports equipment, cable jackets",
        },
    ]

    for mat in materials:
        text = f"""Material: {mat['name']} ({mat['family']}, {mat['type']})
Melt temperature range: {mat['melt_range']}, recommended: {mat['rec_melt']}
Mold temperature range: {mat['mold_range']}, recommended: {mat['rec_mold']}
Shrinkage: {mat['shrinkage']}
Density: {mat['density']}
Cross-WLF viscosity model: {mat['cross_wlf']}
Notes: {mat['notes']}
Applications: {mat['applications']}"""
        chunks.append({
            "text": text,
            "category": "material",
            "material_id": mat["id"],
            "material_family": mat["family"],
        })

    # ══════════════════════════════════════════════
    # TROUBLESHOOTING — defects and simulation issues
    # ══════════════════════════════════════════════
    defects = [
        {
            "problem": "Short shot — part not fully filled",
            "symptoms": "Part missing material in thin sections or far from gate. Inconsistent fill across cavities.",
            "causes": "Insufficient injection pressure/speed. Melt temperature too low (high viscosity). Gate or runner too small. Trapped air (no venting). Wall too thin for flow length.",
            "solutions": "Increase injection speed/pressure. Raise melt temp within window. Enlarge gate/runner. Add vents (0.01-0.03mm). Increase wall thickness. Use higher MFI grade.",
            "sim_check": "Run fill analysis — check pressure at end of fill vs machine capacity. Check fill time contour for hesitation. Air trap analysis for vent locations.",
        },
        {
            "problem": "Flash — excess material at parting line",
            "symptoms": "Thin film of plastic at mold parting line or around inserts and ejector pins.",
            "causes": "Excessive injection/packing pressure. Insufficient clamp tonnage. Mold wear/damage. Melt temp too high. Excessive packing time.",
            "solutions": "Reduce injection and packing pressure. Verify clamp force (2-5 tons/in² projected area). Repair mold parting surfaces. Lower melt temp. Use gate-freeze-controlled packing.",
            "sim_check": "Check clamp force vs machine capacity with 10-20% safety margin. Run packing analysis. Pressure distribution at V/P switchover.",
        },
        {
            "problem": "Sink marks — surface depressions opposite thick features",
            "symptoms": "Visible depressions on part surface, typically opposite ribs or bosses. Cosmetically unacceptable.",
            "causes": "Insufficient packing pressure/time. Rib-to-wall ratio >60%. Excessive wall thickness. Gate freeze-off too early. Melt temp too high.",
            "solutions": "Increase packing pressure and duration. Reduce rib thickness to ≤60% of wall (50% preferred). Core out thick sections. Enlarge gate or relocate closer to thick sections. Lower melt temp. Consider gas-assist for thick sections.",
            "sim_check": "Volumetric shrinkage contour. Sink mark indicator in packing analysis. Gate freeze-off time vs packing hold time. Pressure at end-of-fill in thick sections.",
        },
        {
            "problem": "Warpage — part distortion after ejection",
            "symptoms": "Part doesn't meet dimensional tolerances. Bowing, twisting, or corner lifting.",
            "causes": "Non-uniform cooling (differential shrinkage). Fiber orientation effects (filled materials). Residual stress from packing gradient. Asymmetric geometry or wall thickness. Unbalanced runner. Premature ejection.",
            "solutions": "Balance cooling circuits (equalize core/cavity temps). Optimize gate for balanced fill and fiber orientation. Increase cooling time. Reduce packing pressure differential. Add stiffening ribs. For glass-filled: control fiber orientation via gate placement.",
            "sim_check": "Warpage analysis with all 3 contributors: differential shrinkage, differential cooling, fiber orientation. Deflection plot. Cooling analysis — core/cavity ΔT should be <5°C. Fiber orientation tensor.",
        },
        {
            "problem": "Weld lines / knit lines — visible lines where flow fronts meet",
            "symptoms": "Visible line on part surface where flow fronts merged. Reduced mechanical strength at weld location (can be <50% for filled materials).",
            "causes": "Multiple gates creating opposing flow fronts. Flow splitting around holes/cores. Low melt temperature at meeting point. Trapped air at confluence.",
            "solutions": "Relocate gates to move welds to non-critical areas. Increase melt temperature for better fusion. Increase injection speed to maintain front temperature. Add overflow well at weld. Vent at weld lines. Use sequential valve gating.",
            "sim_check": "Weld line location plot — overlay with stress areas. Temperature at flow front (TAFT) should be above no-flow temp. Pressure at weld formation.",
        },
        {
            "problem": "Burn marks / dieseling — brown or black marks",
            "symptoms": "Brown/black marks at end of fill or in corners. Characteristic burned plastic smell.",
            "causes": "Trapped air compressed adiabatically (diesel effect). Injection speed too high near end of fill. Insufficient venting. Excessive shear heating at gate.",
            "solutions": "Add/enlarge vents at burn locations. Reduce injection speed near end of fill (multi-stage). Lower melt temp. Reduce clamp force if over-clamped. Vacuum venting for deep ribs.",
            "sim_check": "Air trap analysis. Temperature at end of fill — regions above degradation temp. Shear rate plot vs material limits.",
        },
        {
            "problem": "Jetting — snake-like pattern on surface near gate",
            "symptoms": "Wavy snake-like marks starting from gate. Surface roughness near gate area.",
            "causes": "Material jets through gate without contacting wall. Gate too small relative to cavity. Injection speed too high at gate entry. Gate directed at open cavity.",
            "solutions": "Redesign gate to direct flow against wall (fan/tab gate). Reduce initial injection speed (slow-fast profile). Enlarge gate opening. Impinge on cavity wall at angle.",
            "sim_check": "Fill animation — look for free jet pattern in early fill. Gate shear rate vs material limits.",
        },
        {
            "problem": "Splay / silver streaks — radiating marks from gate",
            "symptoms": "Silver streaks radiating from gate. Surface appears rough or hazy.",
            "causes": "Moisture in material (steam creates bubbles). Material degradation (volatiles). Excessive shear heating at gate. Air entrainment in barrel.",
            "solutions": "Dry material properly (check specific requirements). Reduce melt temp if degradation suspected. Reduce injection speed at gate. Reduce screw RPM and back pressure. Use hopper dryer with dew point monitoring.",
            "sim_check": "Check if material is hygroscopic. Shear rate at gate vs max recommended. Bulk temperature vs degradation limit.",
        },
        {
            "problem": "Voids / internal bubbles — hollow spots inside part",
            "symptoms": "Internal bubbles in transparent parts or cut sections. Reduced mechanical properties.",
            "causes": "Thick sections shrink internally — packing can't compensate. Gate freezes before thick section solidifies. Insufficient packing. Moisture (gas bubbles vs vacuum voids).",
            "solutions": "Increase packing pressure and time. Enlarge gate for longer packing. Reduce wall thickness — core out. Move gate closer to thick sections. Consider gas-assist or structural foam.",
            "sim_check": "Volumetric shrinkage — voids where >8% shrinkage. Packing pressure transmission. Gate freeze time vs packing time.",
        },
        {
            "problem": "Flow marks / tiger stripes — surface waviness",
            "symptoms": "Wavy pattern or concentric rings on surface. Alternating dull/glossy bands (tiger stripes on PP).",
            "causes": "Fountain flow instability at low speeds. Melt front freezes and re-melts cyclically. Material sticking/slipping at surface. Mold temp too low.",
            "solutions": "Increase injection speed. Raise mold temperature. Increase melt temperature slightly. Use textured surface. For tiger stripes on PP: mold temp 50-60°C.",
            "sim_check": "Flow front velocity — deceleration zones. Melt front temperature vs no-flow temp.",
        },
    ]

    for d in defects:
        text = f"""Injection molding defect: {d['problem']}
Symptoms: {d['symptoms']}
Root causes: {d['causes']}
Solutions: {d['solutions']}
Simulation checks: {d['sim_check']}"""
        chunks.append({"text": text, "category": "troubleshooting", "subcategory": "defect"})

    # ── Simulation-specific issues ──
    sim_issues = [
        {
            "problem": "Mesh sensitivity — results change with mesh refinement",
            "detail": """Mesh too coarse — insufficient elements through thickness. Poor element quality (high aspect ratio, skewed). Thin sections with only 1-2 elements.
Solutions: Use at least 4 layers through thickness for midplane/dual-domain. For 3D: minimum 4 elements through wall, 8+ preferred. Refine at gates, thin sections, corners. Run convergence study until <2% change. Target aspect ratio <6:1, match ratio 85%+ for dual-domain."""
        },
        {
            "problem": "Race-tracking / preferential flow along thick sections",
            "detail": """Material flows along thick sections or ribs instead of thin areas. Thin areas fill last despite proximity to gate.
Causes: Thick-to-thin wall transitions. Unbalanced runner. Ribs acting as flow leaders.
Solutions: Redesign for uniform wall thickness. Use flow leaders/deflectors intentionally. Balance runner. Move gate. Sequential valve gating for large parts.
Simulation: Check fill time contour, pressure distribution at 25/50/75% fill, flow front velocity."""
        },
        {
            "problem": "Cooling imbalance / hot spots in mold",
            "detail": """Part surface temperature varies >10°C at end of cooling. Ejection marks or sticking on hot side.
Causes: Cooling lines too far from cavity. Uneven spacing. Core side lacks cooling. Hot runner heat interference.
Solutions: Place channels 1-2× diameter from surface. Spacing ≤3× diameter. Use baffles/bubblers/conformal cooling. Separate core/cavity circuits. Insulate hot runner.
Target: ΔT <5°C across part, circuit in-out ΔT <3°C, Reynolds >10000 (turbulent)."""
        },
        {
            "problem": "Overpacking near gate — high residual stress",
            "detail": """High residual stress near gate. Excessive clamp force during packing. Gate blush or vestige.
Solutions: Use multi-step packing: 80% → 60% → 40% of injection pressure. Start packing at 50% of injection pressure. Optimize gate size.
Simulation: Volumetric shrinkage <0 = overpacked. Check packing pressure distribution gradient."""
        },
        {
            "problem": "Shear rate exceeding material limit at gate",
            "detail": """Material degrades at gate due to excessive shear. Shows as splay, burn marks, or property loss.
Causes: Gate too small. Injection speed too high. Runner too small.
Solutions: Enlarge gate. Reduce speed (multi-stage). Increase runner diameter. Multiple gates.
Simulation: Compare shear rate result to material max. Check bulk temperature at gate."""
        },
    ]

    for si in sim_issues:
        chunks.append({
            "text": f"Simulation issue: {si['problem']}\n{si['detail']}",
            "category": "troubleshooting", "subcategory": "simulation"
        })

    # ══════════════════════════════════════════════
    # DFM GUIDELINES — Design for Manufacturability
    # ══════════════════════════════════════════════
    dfm_rules = [
        """DFM Rule: Uniform Wall Thickness
Maintain uniform wall thickness throughout the part. Variations cause differential cooling, uneven shrinkage, and warpage. Where changes are needed, use gradual transitions with 3:1 taper ratio minimum. Thick-to-thin transitions promote race tracking. Typical range: 1.0–4.0mm for most thermoplastics.""",

        """DFM Rule: Minimum Wall Thickness by Material
Thin walls increase pressure requirements and risk short shots. Maximum flow-length-to-thickness ratio by material: PP ~300:1, ABS ~200:1, PC ~100:1, PA ~150:1. Beyond these limits, consider multiple gates.
Typical values: ABS 1.2–3.5mm, PP 0.8–3.8mm, PC 1.2–4.0mm, PA 0.8–3.0mm.""",

        """DFM Rule: Rib Design
Rib thickness should be 50-60% of adjoining wall thickness. Thicker ribs cause sink marks. For cosmetic parts use 50% ratio.
Maximum rib height should not exceed 3× wall thickness. Taller ribs are hard to fill and eject, and act as flow leaders.
Rib spacing should be at least 2× wall thickness center-to-center. Closer spacing causes cooling problems between ribs.""",

        """DFM Rule: Draft Angles
Apply minimum 1° draft on all surfaces parallel to mold opening direction. Textured surfaces need extra: add 1° per 0.025mm texture depth. Polished (SPI A-1) can use 0.5° minimum. Deep ribs: 0.25-0.5° per side.""",

        """DFM Rule: Corner Radii
Use generous radii on all internal corners — minimum 0.5× wall thickness. Sharp corners create stress concentrations (factor 2-3×), impede flow, and cause cooling issues. Internal radius = 0.5-0.75× wall thickness. External radius = internal + wall thickness. Radius/thickness ratio of 0.6 reduces stress concentration to ~1.5×.""",

        """DFM Rule: Boss Design
Boss OD should not exceed 2× ID, connected to wall with gusset ribs. Standalone bosses with thick walls cause sink marks. Boss wall thickness should follow rib rules (50-60% of nominal wall).""",

        """DFM Rule: Gate Location
Gate into the thickest section — flow from thick to thin. Gate for balanced fill (equal flow length in all directions). Keep weld lines away from structural/cosmetic areas. Gate type cosmetic impact: edge < fan < tunnel < hot tip. Gate thickness: 50-80% of wall thickness.""",

        """DFM Rule: Tolerances for Injection Molding
Standard tolerance: ±0.1mm per 25mm + additional per material. Tighter tolerances increase cost exponentially. Amorphous plastics (ABS, PC) hold tighter tolerances than semi-crystalline (PP, PA). Across parting line: add ±0.1mm. Glass-filled: anisotropic tolerances.
Fine: ±0.05mm/25mm (amorphous), Standard: ±0.1mm/25mm, Commercial: ±0.2mm/25mm.""",

        """DFM Rule: Shrinkage Compensation
Mold cavity = part dimension × (1 + shrinkage rate). Amorphous materials: 0.4-0.8%. Semi-crystalline: 1.0-3.0%. Filled materials: 0.2-1.5% (anisotropic — lower in flow direction, higher cross-flow). Shrinkage varies with processing conditions.""",

        """DFM Rule: Venting
Vent depth depends on material viscosity. Land length 1-2mm, then relief to atmosphere.
Crystalline (PP, PA): 0.01-0.02mm depth. Amorphous (ABS, PC): 0.02-0.05mm. Filled materials: 0.01-0.015mm.
Place vents at parting line, end of fill, and at weld line locations. Too deep = flash.""",
    ]

    for rule in dfm_rules:
        chunks.append({"text": rule, "category": "guidelines", "subcategory": "dfm"})

    # ══════════════════════════════════════════════
    # MESH GUIDELINES
    # ══════════════════════════════════════════════
    mesh_guides = [
        """Mesh Type: Midplane Mesh
Best for thin, shell-like parts with uniform wall thickness. Fastest to solve. NOT suitable for thick parts, 3D flow features, or complex core/cavity geometry. Wall thickness assigned as property, not geometric. Use for early-stage gate location studies. Single layer of triangular elements at midplane.""",

        """Mesh Type: Dual-Domain (Fusion) Mesh
Best for most injection molded parts. Uses triangular elements on both surfaces with matched pairs. Good balance of accuracy and speed. Handles ribs, bosses, thickness variations. Match ratio should be >85%. NOT suitable for very thick parts (>5mm) or complex 3D flow.
Element size: 2-3× nominal wall thickness. Refine at gates (0.5× wall), thin sections (1× wall). Total elements: 50k-200k typical.""",

        """Mesh Type: 3D Mesh (Tetrahedral)
Required for: thick parts (wall >4mm), gas/water assist, co-injection, overmolding, insert molding, through-thickness effects. Most accurate but slowest.
Minimum 4 elements through wall thickness, 8+ for accurate thermal/fiber results. Gate region: 10+ layers. Total elements: 500k-5M typical. Use boundary layer meshing near walls.""",

        """Mesh Quality Metrics
Dual-domain targets: aspect ratio <6:1 (max 20:1), match ratio >85%, no free edges, no intersecting elements.
3D targets: aspect ratio <20:1, no inverted elements.
Fix mesh issues BEFORE running analysis — poor mesh = unreliable results.
Runner system: Use beam elements for cold runners. At least 6 elements around runner cross-section for 3D. Cooling channels: 8 elements around circumference.""",
    ]

    for guide in mesh_guides:
        chunks.append({"text": guide, "category": "guidelines", "subcategory": "mesh"})

    # ══════════════════════════════════════════════
    # PROCESS OPTIMIZATION KNOWLEDGE
    # ══════════════════════════════════════════════
    process_knowledge = [
        """Process Optimization: Cycle Time Reduction
Cooling time dominates cycle — driven by thickest section. Cooling time scales with wall_thickness².
Formula: t_cool ≈ (s²/π²α) × ln(8/π² × (T_melt-T_mold)/(T_eject-T_mold))
Solutions: Core out thick sections. Optimize cooling layout. Lower mold temp (check surface quality). Match packing time to gate freeze time. High-conductivity inserts (Cu-Be) for hot spots.
Cooling circuit: Reynolds number >10000 (turbulent flow), in-out ΔT <3°C per circuit.""",

        """Process Optimization: V/P Switchover (Velocity to Pressure Transfer)
Switch at 95-99% volumetric fill. Too early = short shot. Too late = pressure spike and flash.
Use cavity pressure sensor for consistent switchover. Pressure-based switchover more reliable than position-based.
Fill study method: short shots at increasing volumes to find exact fill point.
Simulation: Note exact fill volume and pressure at 98% fill. Pressure trace should show smooth transition.""",

        """Process Parameter: Injection Speed
Range: 10-500 mm/s. Thin walls need high speed. Thick walls and shear-sensitive materials (PVC, POM) need low speed.
Use multi-stage profile: slow at gate (avoid jetting) → fast through cavity → slow at end (avoid burn marks).
Speed affects: fill time, shear rate, shear heating, clamp force, molecular orientation.""",

        """Process Parameter: Packing Pressure
Typical: 30-80% of injection pressure. Use multi-step profile: start at 80% and step down to 40%.
Purpose: compensate volumetric shrinkage during solidification. Reduce overpacking near gate while maintaining packing at end-of-flow.
Duration should match gate freeze time — packing beyond gate freeze wastes cycle time.""",

        """Process Parameter: Melt and Mold Temperature
Melt temperature controls viscosity, molecular orientation, and degradation risk. Higher = easier flow but more shrinkage and longer cooling.
Mold temperature controls surface quality, crystallinity (semi-crystalline), residual stress, and cycle time. Higher = better surface, more crystalline, more shrinkage, longer cycle.
Always verify temperatures are within material's processing window.""",

        """Process Parameter: Clamp Force
Rule of thumb: 2-5 tons per square inch of projected area. Semi-crystalline materials (PP, PA): use higher multiplier (3-5). Amorphous (ABS, PC): 2-3.
Simulation provides accurate clamp force — add 10-20% safety margin.
Insufficient clamp force = flash. Excessive = mold wear, compressed vents.""",

        """Material Handling: Drying Requirements
Hygroscopic materials MUST be dried before molding. Moisture causes splay, bubbles, property loss.
PA6/PA66: 80°C for 6h, target <0.2% moisture. PC: 120°C for 4h. PBT/PET: 120-160°C for 4h. ABS: 80°C for 3h. TPU: 80°C for 3h.
Non-hygroscopic (no drying): PP, PE, PS, POM.
Use desiccant dryer with dew point monitoring, not hot air oven.""",

        """Crystallization Control for Semi-Crystalline Materials
Mold temperature controls final crystallinity: higher = more crystalline, more shrinkage, better properties.
PET is extreme: cold mold (30°C) = amorphous/transparent, hot mold (140°C) = crystalline/opaque.
Non-uniform cooling → different crystallinity → differential shrinkage → warpage.
Nucleating agents can accelerate crystallization and reduce sensitivity to cooling rate.""",

        """Fiber Orientation Effects in Glass-Filled Materials
Glass fibers align with flow direction during filling. Shrinkage is LOW in fiber direction, HIGH perpendicular.
Result: anisotropic shrinkage → warpage in unexpected directions. Weld lines have perpendicular fibers → very weak (<50% of bulk strength).
Gate placement controls fiber orientation in critical areas. Symmetrical gates for symmetrical parts.
Simulation outputs: fiber orientation tensor (a11, a22, a33), separate in-flow vs cross-flow shrinkage.""",
    ]

    for pk in process_knowledge:
        chunks.append({"text": pk, "category": "process", "subcategory": "optimization"})

    # ══════════════════════════════════════════════
    # SIMULATION SETUP — practical workflow knowledge
    # ══════════════════════════════════════════════
    sim_setup = [
        """Simulation Workflow: CAD Import and Preparation
1. Import CAD (STEP, IGES, Parasolid preferred). STL is geometry-only, loses feature info.
2. Defeature: remove logos, text, micro-features that don't affect flow.
3. Heal geometry: fix surface gaps, missing faces, sliver faces.
4. Verify wall thickness is captured correctly.
5. Define parting line for core/cavity assignment.
6. If using dual-domain mesh: both surfaces must be captured accurately.""",

        """Simulation Workflow: Analysis Sequence
Recommended sequence: Fill → Pack → Cool → Warp
- Fill analysis: gate location, fill pattern, pressure, air traps, weld lines
- Pack (holding) analysis: shrinkage compensation, sink marks, residual stress
- Cool analysis: circuit efficiency, cycle time, temperature distribution
- Warp analysis: total deflection, contributors (shrinkage, cooling, orientation)
For fiber-filled materials: add Fiber Orientation before Warp.
For structural: add Stress analysis after Warp.""",

        """Simulation Workflow: Material Selection in Software
Always use the specific grade from your supplier — not a generic material.
Material data quality levels: Gold (fully characterized, all models) > Silver (main models) > Bronze (minimum data, some estimated).
Critical material data: Cross-WLF viscosity model, 2-domain Tait PVT model, thermal properties (conductivity, specific heat, transition temperatures).
If exact grade not in database: use similar grade from same family, validate against datasheet, adjust processing window.""",

        """Simulation Workflow: Runner and Gate Design
Cold runner: model as beam elements (fast) or 3D (accurate). Include sprue, runners, sub-runners, gates.
Hot runner: model manifold with thermal properties. Key: nozzle tip temperature, manifold heat-up.
Gate types in simulation: edge gate, fan gate, submarine/tunnel gate, pin gate, hot tip, valve gate.
Runner balancing: naturally balanced (symmetrical layout) or artificially balanced (different runner diameters).
For multi-cavity: verify fill balance with fill-time difference <5% between cavities.""",

        """Simulation Workflow: Cooling System Design
Model actual cooling channels with correct diameter, position, and inlet/outlet.
Minimum: 8 elements around channel circumference.
Specify: coolant type (water, oil), inlet temperature, flow rate.
Target: Reynolds number >10000 (turbulent flow). Laminar flow = poor heat transfer.
Flow rate per circuit: typically 5-12 L/min.
Check: circuit efficiency (heat removed), temperature uniformity, time to ejection temp.""",

        """Simulation Results Interpretation: Fill Analysis
Key outputs:
- Fill time contour: should show balanced front advancement
- Pressure at V/P switchover: compare to machine capacity (should be <80%)
- Clamp force: compare to machine capacity + safety margin
- Air traps: need venting at these locations
- Weld line locations: avoid structural and cosmetic areas
- Temperature at flow front (TAFT): should stay above no-flow temp
- Shear rate: should be within material limits everywhere""",

        """Simulation Results Interpretation: Warpage Analysis
Total deflection is the sum of three contributors:
1. Differential shrinkage: caused by pressure gradient from gate to end-of-flow
2. Differential cooling: caused by temperature difference between core and cavity
3. Orientation effects: caused by molecular/fiber orientation frozen during cooling
Each contributor can be analyzed separately to identify dominant cause.
For glass-filled materials: orientation contribution is usually dominant.
For unfilled materials: differential cooling is often dominant.""",

        """Common Simulation Mistakes
1. Using generic material instead of specific grade
2. Not running mesh convergence study
3. Ignoring material drying requirements in real process
4. Setting unrealistic process conditions (temp outside window)
5. Not including runner system in fill analysis
6. Using midplane mesh for thick or complex parts
7. Ignoring fiber orientation in warpage for filled materials
8. Not validating clamp force against actual machine
9. Over-interpreting results from coarse mesh
10. Forgetting to check V/P switchover position""",
    ]

    for ss in sim_setup:
        chunks.append({"text": ss, "category": "simulation_setup", "subcategory": "workflow"})

    # ══════════════════════════════════════════════
    # MOLDFLOW-SPECIFIC KNOWLEDGE
    # ══════════════════════════════════════════════
    moldflow_knowledge = [
        """Autodesk Moldflow: Material Data System
Moldflow material database uses characterization levels:
- Gold (comprehensive): Full Cross-WLF, pvT, thermal, mechanical, all validated
- Silver: Main rheological + thermal data, some estimated properties
- Bronze: Minimum data, most properties estimated from family behavior
Gold-level data can improve warpage prediction accuracy by 30-50% compared to Bronze.
STAMP (Standard Testing for Accuracy in Moldflow Predictions) validates material data quality.
Material file format: .udb (Universal DataBase). Contains Cross-WLF, Tait PVT, thermal properties, processing window.""",

        """Autodesk Moldflow: Confidence of Fill
Moldflow provides a 'Confidence of Fill' result that indicates regions likely to fill successfully.
Green = high confidence, Yellow = possible hesitation, Red = likely short shot.
Based on: local pressure, temperature, shear rate, and wall thickness.
Useful for initial feasibility check before full analysis.""",

        """Autodesk Moldflow: Mesh Types
Moldflow supports three mesh technologies:
1. Midplane (fusion predecessor): 2D triangles at part midplane, wall thickness as property
2. Dual Domain (Fusion): matched triangles on inner/outer surfaces, fast 3D approximation
3. 3D: true tetrahedral volume mesh, most accurate but slowest
Dual Domain is the most commonly used — good accuracy for most parts.
3D required for: thick parts, gas assist, overmolding, insert molding, complex flow patterns.""",

        """Simulation File Formats in Injection Molding
Moldflow: .sdy (study file), .udm (model), .udb (material database), .pat (material)
Moldex3D: .mvl (project), .bdf (mesh), material XML
Cadmould: proprietary project format
Common exchange: STEP (.stp), IGES (.igs), Parasolid (.x_t), STL (.stl)
For geometry exchange, STEP AP214 or Parasolid recommended — preserves topology.
STL loses all feature/boundary information, only triangulated surface.""",
    ]

    for mk in moldflow_knowledge:
        chunks.append({"text": mk, "category": "software", "subcategory": "moldflow"})

    # ══════════════════════════════════════════════
    # ADVANCED TOPICS
    # ══════════════════════════════════════════════
    advanced = [
        """Cross-WLF Viscosity Model Explained
The Cross-WLF model describes how polymer viscosity depends on temperature, pressure, and shear rate.
η(T,γ̇) = η₀(T) / (1 + (η₀γ̇/τ*)^(1-n))
where η₀(T,p) = D1 × exp(-A1(T-T*)/(A2+(T-T*)))
and T* = D2 + D3×p

Parameters:
- n: power-law index (dimensionless, 0.1-0.5 typical, lower = more shear thinning)
- τ* (tau star): critical shear stress marking transition from Newtonian to shear-thinning (Pa)
- D1: reference viscosity (Pa·s)
- D2: glass transition temperature at zero pressure (K)
- D3: pressure dependence of Tg (K/Pa, often 0 for simplified model)
- A1, A2: WLF constants (A2 often fixed at 51.6 K)

This is the standard viscosity model used in all major injection molding simulation software.""",

        """2-Domain Tait PVT Model Explained
The Tait equation describes specific volume (inverse of density) as function of temperature and pressure.
V(T,p) = V₀(T) × (1 - C × ln(1 + p/B(T))) + V_t(T,p)
where C = 0.0894 (universal Tait constant)

Two domains separated by transition temperature (Tg for amorphous, Tm for semi-crystalline):
Melt domain (T > b5): V₀ = b1m + b2m(T-b5), B = b3m × exp(-b4m(T-b5))
Solid domain (T < b5): V₀ = b1s + b2s(T-b5), B = b3s × exp(-b4s(T-b5))

For semi-crystalline materials, additional crystallization term:
V_t = b7 × exp(b8(T-b5) - b9×p) for T < b5, else 0

Parameters b5 = transition temp at zero pressure, b6 = pressure dependence.
Critical for accurate shrinkage and warpage prediction.""",

        """Fountain Flow in Injection Molding
During filling, polymer melt exhibits fountain flow: material at the center of the channel flows forward, reaches the flow front, and fans outward to the mold walls where it freezes.
This creates the frozen layer (skin) and the flowing core.
Molecular orientation is highest at the skin layer (parallel to flow) and lowest at the core.
This affects: mechanical properties (anisotropic), residual stress, warpage.
3D simulation captures fountain flow; midplane and dual-domain approximate it.""",

        """Gate Freeze and Its Impact
Gate freeze occurs when the gate solidifies during packing. After gate freeze, no more material can enter the cavity — packing stops.
Gate freeze time depends on: gate thickness, mold temperature, material type.
Thin gates freeze faster → shorter packing → more shrinkage and sink marks.
Thick gates freeze slower → longer packing → better compensation but longer cycle time and bigger vestige.
Optimal: packing time ≈ gate freeze time. Packing beyond gate freeze wastes cycle time.
Simulation reports gate freeze time — match your packing duration to this value.""",

        """Residual Stress in Injection Molded Parts
Two types of residual stress:
1. Flow-induced: from molecular orientation frozen during filling. Higher near surface (frozen layer).
2. Thermally-induced: from differential cooling. Compressive at surface, tensile at core.
In-mold (before ejection): part is constrained, stresses are in equilibrium with mold.
After ejection: stresses redistribute → warpage, dimensional change.
Reducing residual stress: lower injection speed, higher mold temperature, longer cooling, annealing post-mold.
Simulation can predict both in-mold and post-ejection stress states.""",

        """Conformal Cooling
Traditional cooling channels are straight-drilled, limited to simple geometries.
Conformal cooling follows the part contour — possible with additive manufacturing (3D printed mold inserts).
Benefits: 40-70% reduction in cooling time for complex parts. More uniform cooling → less warpage.
Design rules: channel diameter 4-8mm, wall-to-channel distance 1.5-2× diameter, channel-to-channel spacing 2-3× diameter.
Model in simulation: same as conventional channels but with curved paths matching part geometry.""",
    ]

    for adv in advanced:
        chunks.append({"text": adv, "category": "theory", "subcategory": "advanced"})

    return chunks


def main():
    print("Initializing embedding model...")
    embed_model = TextEmbedding(MODEL)

    print("Generating knowledge chunks...")
    chunks = make_chunks()
    print(f"Total chunks: {len(chunks)}")

    print("Computing embeddings...")
    texts = [c["text"] for c in chunks]
    embeddings = list(embed_model.embed(texts))
    print(f"Embeddings computed: {len(embeddings)}, dim={len(embeddings[0])}")

    print("Connecting to Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Recreate collection
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION in collections:
        print(f"Deleting existing collection '{COLLECTION}'...")
        client.delete_collection(COLLECTION)

    print(f"Creating collection '{COLLECTION}' with {VECTOR_SIZE} dims...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    # Upsert points
    points = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        payload = {k: v for k, v in chunk.items() if k != "text"}
        payload["text"] = chunk["text"]
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=emb.tolist(),
            payload=payload,
        ))

    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=COLLECTION, points=batch)
        print(f"  Uploaded {min(i+batch_size, len(points))}/{len(points)} points")

    # Verify
    info = client.get_collection(COLLECTION)
    print(f"\nDone! Collection '{COLLECTION}': {info.points_count} points")

    # Test query
    print("\nTest query: 'How to fix warpage in glass-filled nylon?'")
    test_emb = list(embed_model.embed(["How to fix warpage in glass-filled nylon?"]))[0]
    results = client.query_points(
        collection_name=COLLECTION,
        query=test_emb.tolist(),
        limit=3,
    )
    for i, r in enumerate(results.points):
        print(f"\n--- Result {i+1} (score: {r.score:.3f}) ---")
        print(r.payload["text"][:200] + "...")


if __name__ == "__main__":
    main()
