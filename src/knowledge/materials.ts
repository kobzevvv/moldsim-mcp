/**
 * Material database for injection molding simulation.
 *
 * Data sources: published material datasheets, Moldflow material DB references,
 * and standard processing guides. Values are representative for simulation setup —
 * always verify against your specific grade's datasheet.
 *
 * Cross-WLF viscosity model: η(T,p) = D1 * exp(-A1*(T-T*) / (A2+(T-T*)))
 *   where T* = D2 + D3*p, valid above transition temperature
 *
 * Tait PVT (2-domain): V(T,p) = V0*(1 - C*ln(1 + p/B(T))) + Vt(T,p)
 *   C = 0.0894 (universal constant)
 */

export interface CrossWLF {
  n: number;          // power-law index (dimensionless)
  tau_star_Pa: number; // critical shear stress (Pa)
  D1_Pa_s: number;    // viscosity at reference (Pa·s)
  D2_K: number;       // glass transition at zero pressure (K)
  D3_K_Pa: number;    // pressure dependence of Tg (K/Pa)
  A1: number;         // WLF constant 1
  A2_K: number;       // WLF constant 2 (K)
}

export interface TaitPVT {
  // Melt domain (T > Tt)
  b1m_m3_kg: number;
  b2m_m3_kg_K: number;
  b3m_Pa: number;
  b4m_1_K: number;
  // Solid domain (T < Tt)
  b1s_m3_kg: number;
  b2s_m3_kg_K: number;
  b3s_Pa: number;
  b4s_1_K: number;
  // Transition
  b5_K: number;       // transition temp at zero pressure
  b6_K_Pa: number;    // pressure dependence of transition temp
  b7_m3_kg: number;   // crystallization amplitude (0 for amorphous)
  b8_1_K: number;
  b9_1_Pa: number;
}

export interface ThermalProperties {
  thermal_conductivity_W_mK: number;
  specific_heat_J_kgK: number;
  density_kg_m3: number;
  ejection_temp_C: number;
  no_flow_temp_C: number;
}

export interface ProcessingWindow {
  melt_temp_min_C: number;
  melt_temp_max_C: number;
  melt_temp_recommended_C: number;
  mold_temp_min_C: number;
  mold_temp_max_C: number;
  mold_temp_recommended_C: number;
  max_shear_rate_1_s: number;
  drying_temp_C: number | null;
  drying_time_hr: number | null;
  max_residence_time_min: number;
}

export interface MechanicalProperties {
  tensile_strength_MPa: number;
  flexural_modulus_MPa: number;
  elongation_at_break_pct: number;
  HDT_at_1_8MPa_C: number;
  shrinkage_pct_min: number;
  shrinkage_pct_max: number;
}

export interface Material {
  id: string;
  name: string;
  family: string;
  type: 'amorphous' | 'semi-crystalline';
  filler?: string;
  filler_pct?: number;
  mfi_g_10min?: number;
  mfi_condition?: string;
  cross_wlf: CrossWLF;
  tait_pvt: TaitPVT;
  thermal: ThermalProperties;
  processing: ProcessingWindow;
  mechanical: MechanicalProperties;
  notes: string;
}

export const MATERIALS: Material[] = [
  // ──── ABS ────
  {
    id: 'abs-generic',
    name: 'ABS Generic',
    family: 'ABS',
    type: 'amorphous',
    mfi_g_10min: 20,
    mfi_condition: '220°C / 10 kg',
    cross_wlf: {
      n: 0.2694,
      tau_star_Pa: 30820,
      D1_Pa_s: 4.89e+10,
      D2_K: 373.15,
      D3_K_Pa: 0,
      A1: 23.76,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 1.042e-3, b2m_m3_kg_K: 5.56e-7,
      b3m_Pa: 1.77e+8, b4m_1_K: 3.29e-3,
      b1s_m3_kg: 1.042e-3, b2s_m3_kg_K: 2.33e-7,
      b3s_Pa: 2.95e+8, b4s_1_K: 1.87e-3,
      b5_K: 373.15, b6_K_Pa: 3.18e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.17,
      specific_heat_J_kgK: 2050,
      density_kg_m3: 1050,
      ejection_temp_C: 90,
      no_flow_temp_C: 110,
    },
    processing: {
      melt_temp_min_C: 220, melt_temp_max_C: 260, melt_temp_recommended_C: 240,
      mold_temp_min_C: 40, mold_temp_max_C: 80, mold_temp_recommended_C: 60,
      max_shear_rate_1_s: 50000,
      drying_temp_C: 80, drying_time_hr: 3,
      max_residence_time_min: 8,
    },
    mechanical: {
      tensile_strength_MPa: 42,
      flexural_modulus_MPa: 2300,
      elongation_at_break_pct: 25,
      HDT_at_1_8MPa_C: 96,
      shrinkage_pct_min: 0.4, shrinkage_pct_max: 0.7,
    },
    notes: 'General-purpose ABS. Good impact, processability. Hygroscopic — must dry before molding.',
  },

  // ──── PP Homopolymer ────
  {
    id: 'pp-homo',
    name: 'PP Homopolymer',
    family: 'PP',
    type: 'semi-crystalline',
    mfi_g_10min: 12,
    mfi_condition: '230°C / 2.16 kg',
    cross_wlf: {
      n: 0.2853,
      tau_star_Pa: 25000,
      D1_Pa_s: 2.87e+11,
      D2_K: 263.15,
      D3_K_Pa: 0,
      A1: 27.8,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 1.274e-3, b2m_m3_kg_K: 8.95e-7,
      b3m_Pa: 8.82e+7, b4m_1_K: 4.72e-3,
      b1s_m3_kg: 1.160e-3, b2s_m3_kg_K: 3.55e-7,
      b3s_Pa: 1.78e+8, b4s_1_K: 3.58e-3,
      b5_K: 434.15, b6_K_Pa: 3.63e-7,
      b7_m3_kg: 8.63e-5, b8_1_K: 4.73e-2, b9_1_Pa: 8.37e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.15,
      specific_heat_J_kgK: 2400,
      density_kg_m3: 905,
      ejection_temp_C: 90,
      no_flow_temp_C: 140,
    },
    processing: {
      melt_temp_min_C: 200, melt_temp_max_C: 280, melt_temp_recommended_C: 230,
      mold_temp_min_C: 20, mold_temp_max_C: 80, mold_temp_recommended_C: 40,
      max_shear_rate_1_s: 100000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 10,
    },
    mechanical: {
      tensile_strength_MPa: 35,
      flexural_modulus_MPa: 1500,
      elongation_at_break_pct: 150,
      HDT_at_1_8MPa_C: 60,
      shrinkage_pct_min: 1.0, shrinkage_pct_max: 2.5,
    },
    notes: 'Most widely used thermoplastic. High shrinkage, good chemical resistance. Non-hygroscopic.',
  },

  // ──── PP Copolymer ────
  {
    id: 'pp-copo',
    name: 'PP Copolymer (Impact)',
    family: 'PP',
    type: 'semi-crystalline',
    mfi_g_10min: 10,
    mfi_condition: '230°C / 2.16 kg',
    cross_wlf: {
      n: 0.3012,
      tau_star_Pa: 24500,
      D1_Pa_s: 1.95e+11,
      D2_K: 258.15,
      D3_K_Pa: 0,
      A1: 26.9,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 1.289e-3, b2m_m3_kg_K: 9.12e-7,
      b3m_Pa: 8.45e+7, b4m_1_K: 4.55e-3,
      b1s_m3_kg: 1.170e-3, b2s_m3_kg_K: 3.72e-7,
      b3s_Pa: 1.69e+8, b4s_1_K: 3.42e-3,
      b5_K: 424.15, b6_K_Pa: 3.58e-7,
      b7_m3_kg: 7.82e-5, b8_1_K: 4.52e-2, b9_1_Pa: 8.12e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.15,
      specific_heat_J_kgK: 2350,
      density_kg_m3: 900,
      ejection_temp_C: 85,
      no_flow_temp_C: 135,
    },
    processing: {
      melt_temp_min_C: 200, melt_temp_max_C: 270, melt_temp_recommended_C: 225,
      mold_temp_min_C: 20, mold_temp_max_C: 60, mold_temp_recommended_C: 35,
      max_shear_rate_1_s: 100000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 10,
    },
    mechanical: {
      tensile_strength_MPa: 28,
      flexural_modulus_MPa: 1200,
      elongation_at_break_pct: 300,
      HDT_at_1_8MPa_C: 52,
      shrinkage_pct_min: 1.2, shrinkage_pct_max: 2.2,
    },
    notes: 'Better impact resistance than homopolymer, especially at low temps. Automotive interiors.',
  },

  // ──── PA6 (Nylon 6) ────
  {
    id: 'pa6',
    name: 'PA6 (Nylon 6)',
    family: 'PA',
    type: 'semi-crystalline',
    mfi_g_10min: 35,
    mfi_condition: '275°C / 5 kg',
    cross_wlf: {
      n: 0.2563,
      tau_star_Pa: 85650,
      D1_Pa_s: 1.51e+12,
      D2_K: 323.15,
      D3_K_Pa: 0,
      A1: 30.63,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.46e-4, b2m_m3_kg_K: 5.34e-7,
      b3m_Pa: 1.31e+8, b4m_1_K: 4.70e-3,
      b1s_m3_kg: 8.54e-4, b2s_m3_kg_K: 2.33e-7,
      b3s_Pa: 2.62e+8, b4s_1_K: 2.56e-3,
      b5_K: 494.15, b6_K_Pa: 1.18e-7,
      b7_m3_kg: 6.86e-5, b8_1_K: 8.72e-2, b9_1_Pa: 1.12e-8,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.25,
      specific_heat_J_kgK: 2100,
      density_kg_m3: 1130,
      ejection_temp_C: 160,
      no_flow_temp_C: 200,
    },
    processing: {
      melt_temp_min_C: 240, melt_temp_max_C: 290, melt_temp_recommended_C: 260,
      mold_temp_min_C: 60, mold_temp_max_C: 100, mold_temp_recommended_C: 80,
      max_shear_rate_1_s: 60000,
      drying_temp_C: 80, drying_time_hr: 6,
      max_residence_time_min: 6,
    },
    mechanical: {
      tensile_strength_MPa: 70,
      flexural_modulus_MPa: 2700,
      elongation_at_break_pct: 60,
      HDT_at_1_8MPa_C: 65,
      shrinkage_pct_min: 0.8, shrinkage_pct_max: 1.5,
    },
    notes: 'Very hygroscopic — dry to <0.2% moisture. Good toughness and wear resistance. Sharp crystallization.',
  },

  // ──── PA66 ────
  {
    id: 'pa66',
    name: 'PA66 (Nylon 66)',
    family: 'PA',
    type: 'semi-crystalline',
    mfi_g_10min: 40,
    mfi_condition: '275°C / 5 kg',
    cross_wlf: {
      n: 0.2618,
      tau_star_Pa: 91200,
      D1_Pa_s: 4.42e+12,
      D2_K: 333.15,
      D3_K_Pa: 0,
      A1: 32.15,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.32e-4, b2m_m3_kg_K: 5.21e-7,
      b3m_Pa: 1.42e+8, b4m_1_K: 4.85e-3,
      b1s_m3_kg: 8.42e-4, b2s_m3_kg_K: 2.21e-7,
      b3s_Pa: 2.81e+8, b4s_1_K: 2.72e-3,
      b5_K: 535.15, b6_K_Pa: 1.22e-7,
      b7_m3_kg: 7.12e-5, b8_1_K: 9.15e-2, b9_1_Pa: 1.08e-8,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.26,
      specific_heat_J_kgK: 2000,
      density_kg_m3: 1140,
      ejection_temp_C: 180,
      no_flow_temp_C: 230,
    },
    processing: {
      melt_temp_min_C: 270, melt_temp_max_C: 300, melt_temp_recommended_C: 285,
      mold_temp_min_C: 70, mold_temp_max_C: 110, mold_temp_recommended_C: 80,
      max_shear_rate_1_s: 60000,
      drying_temp_C: 80, drying_time_hr: 6,
      max_residence_time_min: 5,
    },
    mechanical: {
      tensile_strength_MPa: 80,
      flexural_modulus_MPa: 2800,
      elongation_at_break_pct: 40,
      HDT_at_1_8MPa_C: 75,
      shrinkage_pct_min: 0.8, shrinkage_pct_max: 1.5,
    },
    notes: 'Higher melting point than PA6. Very sensitive to moisture — dry to <0.1%. Narrow processing window.',
  },

  // ──── PA66-GF30 ────
  {
    id: 'pa66-gf30',
    name: 'PA66-GF30',
    family: 'PA',
    type: 'semi-crystalline',
    filler: 'glass fiber',
    filler_pct: 30,
    cross_wlf: {
      n: 0.3265,
      tau_star_Pa: 57340,
      D1_Pa_s: 3.12e+12,
      D2_K: 333.15,
      D3_K_Pa: 0,
      A1: 31.2,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 7.21e-4, b2m_m3_kg_K: 3.82e-7,
      b3m_Pa: 1.55e+8, b4m_1_K: 4.62e-3,
      b1s_m3_kg: 6.72e-4, b2s_m3_kg_K: 1.85e-7,
      b3s_Pa: 2.95e+8, b4s_1_K: 2.45e-3,
      b5_K: 535.15, b6_K_Pa: 1.18e-7,
      b7_m3_kg: 4.82e-5, b8_1_K: 8.65e-2, b9_1_Pa: 1.05e-8,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.37,
      specific_heat_J_kgK: 1600,
      density_kg_m3: 1380,
      ejection_temp_C: 190,
      no_flow_temp_C: 235,
    },
    processing: {
      melt_temp_min_C: 275, melt_temp_max_C: 310, melt_temp_recommended_C: 290,
      mold_temp_min_C: 80, mold_temp_max_C: 120, mold_temp_recommended_C: 90,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 80, drying_time_hr: 6,
      max_residence_time_min: 5,
    },
    mechanical: {
      tensile_strength_MPa: 185,
      flexural_modulus_MPa: 9500,
      elongation_at_break_pct: 4,
      HDT_at_1_8MPa_C: 250,
      shrinkage_pct_min: 0.3, shrinkage_pct_max: 1.0,
    },
    notes: 'Anisotropic shrinkage (flow vs cross-flow). Fiber orientation critical for warpage prediction. Abrasive to tooling.',
  },

  // ──── PC (Polycarbonate) ────
  {
    id: 'pc',
    name: 'PC (Polycarbonate)',
    family: 'PC',
    type: 'amorphous',
    mfi_g_10min: 10,
    mfi_condition: '300°C / 1.2 kg',
    cross_wlf: {
      n: 0.1816,
      tau_star_Pa: 307100,
      D1_Pa_s: 5.73e+14,
      D2_K: 418.15,
      D3_K_Pa: 0,
      A1: 35.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 8.63e-4, b2m_m3_kg_K: 4.02e-7,
      b3m_Pa: 2.22e+8, b4m_1_K: 4.12e-3,
      b1s_m3_kg: 8.27e-4, b2s_m3_kg_K: 1.18e-7,
      b3s_Pa: 3.68e+8, b4s_1_K: 2.15e-3,
      b5_K: 418.15, b6_K_Pa: 3.27e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.20,
      specific_heat_J_kgK: 1900,
      density_kg_m3: 1200,
      ejection_temp_C: 120,
      no_flow_temp_C: 160,
    },
    processing: {
      melt_temp_min_C: 280, melt_temp_max_C: 320, melt_temp_recommended_C: 300,
      mold_temp_min_C: 80, mold_temp_max_C: 120, mold_temp_recommended_C: 90,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 120, drying_time_hr: 4,
      max_residence_time_min: 6,
    },
    mechanical: {
      tensile_strength_MPa: 65,
      flexural_modulus_MPa: 2400,
      elongation_at_break_pct: 110,
      HDT_at_1_8MPa_C: 132,
      shrinkage_pct_min: 0.5, shrinkage_pct_max: 0.7,
    },
    notes: 'Excellent transparency and impact. High viscosity — needs high injection pressure. Sensitive to stress cracking from chemicals.',
  },

  // ──── PC/ABS Blend ────
  {
    id: 'pc-abs',
    name: 'PC/ABS Blend',
    family: 'PC/ABS',
    type: 'amorphous',
    cross_wlf: {
      n: 0.2345,
      tau_star_Pa: 85000,
      D1_Pa_s: 8.12e+11,
      D2_K: 393.15,
      D3_K_Pa: 0,
      A1: 28.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.12e-4, b2m_m3_kg_K: 4.82e-7,
      b3m_Pa: 1.95e+8, b4m_1_K: 3.85e-3,
      b1s_m3_kg: 8.82e-4, b2s_m3_kg_K: 1.72e-7,
      b3s_Pa: 3.15e+8, b4s_1_K: 2.05e-3,
      b5_K: 393.15, b6_K_Pa: 3.22e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.19,
      specific_heat_J_kgK: 1950,
      density_kg_m3: 1150,
      ejection_temp_C: 100,
      no_flow_temp_C: 135,
    },
    processing: {
      melt_temp_min_C: 250, melt_temp_max_C: 290, melt_temp_recommended_C: 270,
      mold_temp_min_C: 60, mold_temp_max_C: 100, mold_temp_recommended_C: 75,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 100, drying_time_hr: 3,
      max_residence_time_min: 7,
    },
    mechanical: {
      tensile_strength_MPa: 55,
      flexural_modulus_MPa: 2200,
      elongation_at_break_pct: 80,
      HDT_at_1_8MPa_C: 110,
      shrinkage_pct_min: 0.5, shrinkage_pct_max: 0.7,
    },
    notes: 'Combines PC heat resistance with ABS processability. Easier to mold than pure PC. Common in automotive and electronics.',
  },

  // ──── POM (Acetal / Delrin) ────
  {
    id: 'pom',
    name: 'POM (Acetal Homopolymer)',
    family: 'POM',
    type: 'semi-crystalline',
    mfi_g_10min: 9,
    mfi_condition: '190°C / 2.16 kg',
    cross_wlf: {
      n: 0.2958,
      tau_star_Pa: 62400,
      D1_Pa_s: 5.42e+10,
      D2_K: 268.15,
      D3_K_Pa: 0,
      A1: 25.1,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 8.12e-4, b2m_m3_kg_K: 4.85e-7,
      b3m_Pa: 1.18e+8, b4m_1_K: 5.12e-3,
      b1s_m3_kg: 7.22e-4, b2s_m3_kg_K: 2.05e-7,
      b3s_Pa: 2.45e+8, b4s_1_K: 2.82e-3,
      b5_K: 449.15, b6_K_Pa: 3.42e-7,
      b7_m3_kg: 7.45e-5, b8_1_K: 6.85e-2, b9_1_Pa: 9.82e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.31,
      specific_heat_J_kgK: 1900,
      density_kg_m3: 1410,
      ejection_temp_C: 130,
      no_flow_temp_C: 165,
    },
    processing: {
      melt_temp_min_C: 190, melt_temp_max_C: 230, melt_temp_recommended_C: 210,
      mold_temp_min_C: 60, mold_temp_max_C: 120, mold_temp_recommended_C: 90,
      max_shear_rate_1_s: 40000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 5,
    },
    mechanical: {
      tensile_strength_MPa: 70,
      flexural_modulus_MPa: 2900,
      elongation_at_break_pct: 25,
      HDT_at_1_8MPa_C: 110,
      shrinkage_pct_min: 1.8, shrinkage_pct_max: 2.5,
    },
    notes: 'Excellent dimensional stability and low friction. Narrow processing window — degrades with formaldehyde gas above 230°C. Non-hygroscopic.',
  },

  // ──── HDPE ────
  {
    id: 'hdpe',
    name: 'HDPE (High Density Polyethylene)',
    family: 'PE',
    type: 'semi-crystalline',
    mfi_g_10min: 8,
    mfi_condition: '190°C / 2.16 kg',
    cross_wlf: {
      n: 0.3856,
      tau_star_Pa: 28500,
      D1_Pa_s: 1.82e+10,
      D2_K: 223.15,
      D3_K_Pa: 0,
      A1: 22.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 1.262e-3, b2m_m3_kg_K: 8.32e-7,
      b3m_Pa: 8.15e+7, b4m_1_K: 5.02e-3,
      b1s_m3_kg: 1.092e-3, b2s_m3_kg_K: 2.85e-7,
      b3s_Pa: 2.12e+8, b4s_1_K: 2.55e-3,
      b5_K: 404.15, b6_K_Pa: 3.82e-7,
      b7_m3_kg: 1.12e-4, b8_1_K: 5.25e-2, b9_1_Pa: 7.85e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.44,
      specific_heat_J_kgK: 2600,
      density_kg_m3: 955,
      ejection_temp_C: 70,
      no_flow_temp_C: 120,
    },
    processing: {
      melt_temp_min_C: 200, melt_temp_max_C: 280, melt_temp_recommended_C: 230,
      mold_temp_min_C: 20, mold_temp_max_C: 60, mold_temp_recommended_C: 30,
      max_shear_rate_1_s: 60000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 12,
    },
    mechanical: {
      tensile_strength_MPa: 28,
      flexural_modulus_MPa: 1200,
      elongation_at_break_pct: 700,
      HDT_at_1_8MPa_C: 50,
      shrinkage_pct_min: 1.5, shrinkage_pct_max: 3.0,
    },
    notes: 'High shrinkage and warpage tendency. Non-hygroscopic. Excellent chemical resistance. Caps, containers.',
  },

  // ──── LDPE ────
  {
    id: 'ldpe',
    name: 'LDPE (Low Density Polyethylene)',
    family: 'PE',
    type: 'semi-crystalline',
    mfi_g_10min: 25,
    mfi_condition: '190°C / 2.16 kg',
    cross_wlf: {
      n: 0.4125,
      tau_star_Pa: 22000,
      D1_Pa_s: 8.72e+9,
      D2_K: 213.15,
      D3_K_Pa: 0,
      A1: 21.2,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 1.315e-3, b2m_m3_kg_K: 9.85e-7,
      b3m_Pa: 6.82e+7, b4m_1_K: 5.35e-3,
      b1s_m3_kg: 1.125e-3, b2s_m3_kg_K: 3.15e-7,
      b3s_Pa: 1.85e+8, b4s_1_K: 2.42e-3,
      b5_K: 385.15, b6_K_Pa: 3.92e-7,
      b7_m3_kg: 1.25e-4, b8_1_K: 4.85e-2, b9_1_Pa: 8.12e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.33,
      specific_heat_J_kgK: 2700,
      density_kg_m3: 920,
      ejection_temp_C: 55,
      no_flow_temp_C: 100,
    },
    processing: {
      melt_temp_min_C: 160, melt_temp_max_C: 240, melt_temp_recommended_C: 200,
      mold_temp_min_C: 15, mold_temp_max_C: 50, mold_temp_recommended_C: 30,
      max_shear_rate_1_s: 60000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 15,
    },
    mechanical: {
      tensile_strength_MPa: 12,
      flexural_modulus_MPa: 300,
      elongation_at_break_pct: 500,
      HDT_at_1_8MPa_C: 40,
      shrinkage_pct_min: 1.5, shrinkage_pct_max: 3.5,
    },
    notes: 'Very flexible, high shrinkage. Easy flow. Used for flexible lids, squeeze bottles.',
  },

  // ──── PMMA (Acrylic) ────
  {
    id: 'pmma',
    name: 'PMMA (Acrylic)',
    family: 'PMMA',
    type: 'amorphous',
    mfi_g_10min: 6,
    mfi_condition: '230°C / 3.8 kg',
    cross_wlf: {
      n: 0.2142,
      tau_star_Pa: 125000,
      D1_Pa_s: 7.82e+12,
      D2_K: 378.15,
      D3_K_Pa: 0,
      A1: 31.8,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 8.72e-4, b2m_m3_kg_K: 4.55e-7,
      b3m_Pa: 2.05e+8, b4m_1_K: 3.92e-3,
      b1s_m3_kg: 8.42e-4, b2s_m3_kg_K: 1.52e-7,
      b3s_Pa: 3.42e+8, b4s_1_K: 2.08e-3,
      b5_K: 378.15, b6_K_Pa: 3.35e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.19,
      specific_heat_J_kgK: 1800,
      density_kg_m3: 1190,
      ejection_temp_C: 85,
      no_flow_temp_C: 130,
    },
    processing: {
      melt_temp_min_C: 220, melt_temp_max_C: 260, melt_temp_recommended_C: 240,
      mold_temp_min_C: 50, mold_temp_max_C: 80, mold_temp_recommended_C: 65,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 80, drying_time_hr: 4,
      max_residence_time_min: 8,
    },
    mechanical: {
      tensile_strength_MPa: 72,
      flexural_modulus_MPa: 3200,
      elongation_at_break_pct: 5,
      HDT_at_1_8MPa_C: 95,
      shrinkage_pct_min: 0.3, shrinkage_pct_max: 0.6,
    },
    notes: 'Excellent optical clarity (92% light transmission). Brittle. Scratches easier than PC. Automotive lighting, displays.',
  },

  // ──── PBT ────
  {
    id: 'pbt',
    name: 'PBT (Polybutylene Terephthalate)',
    family: 'PBT',
    type: 'semi-crystalline',
    mfi_g_10min: 20,
    mfi_condition: '250°C / 2.16 kg',
    cross_wlf: {
      n: 0.2785,
      tau_star_Pa: 72500,
      D1_Pa_s: 6.25e+10,
      D2_K: 318.15,
      D3_K_Pa: 0,
      A1: 26.2,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 8.05e-4, b2m_m3_kg_K: 4.12e-7,
      b3m_Pa: 1.52e+8, b4m_1_K: 4.52e-3,
      b1s_m3_kg: 7.42e-4, b2s_m3_kg_K: 2.12e-7,
      b3s_Pa: 2.72e+8, b4s_1_K: 2.62e-3,
      b5_K: 498.15, b6_K_Pa: 2.85e-7,
      b7_m3_kg: 5.62e-5, b8_1_K: 7.25e-2, b9_1_Pa: 9.42e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.21,
      specific_heat_J_kgK: 1750,
      density_kg_m3: 1310,
      ejection_temp_C: 140,
      no_flow_temp_C: 200,
    },
    processing: {
      melt_temp_min_C: 240, melt_temp_max_C: 275, melt_temp_recommended_C: 255,
      mold_temp_min_C: 40, mold_temp_max_C: 100, mold_temp_recommended_C: 70,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 120, drying_time_hr: 4,
      max_residence_time_min: 6,
    },
    mechanical: {
      tensile_strength_MPa: 56,
      flexural_modulus_MPa: 2500,
      elongation_at_break_pct: 50,
      HDT_at_1_8MPa_C: 60,
      shrinkage_pct_min: 1.3, shrinkage_pct_max: 2.0,
    },
    notes: 'Fast crystallization — short cycle times. Good electrical properties. Hygroscopic. Connectors, switches.',
  },

  // ──── PBT-GF30 ────
  {
    id: 'pbt-gf30',
    name: 'PBT-GF30',
    family: 'PBT',
    type: 'semi-crystalline',
    filler: 'glass fiber',
    filler_pct: 30,
    cross_wlf: {
      n: 0.3185,
      tau_star_Pa: 52800,
      D1_Pa_s: 4.85e+10,
      D2_K: 318.15,
      D3_K_Pa: 0,
      A1: 25.8,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 6.42e-4, b2m_m3_kg_K: 3.15e-7,
      b3m_Pa: 1.75e+8, b4m_1_K: 4.25e-3,
      b1s_m3_kg: 6.02e-4, b2s_m3_kg_K: 1.62e-7,
      b3s_Pa: 3.05e+8, b4s_1_K: 2.35e-3,
      b5_K: 498.15, b6_K_Pa: 2.82e-7,
      b7_m3_kg: 3.85e-5, b8_1_K: 6.95e-2, b9_1_Pa: 9.15e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.35,
      specific_heat_J_kgK: 1400,
      density_kg_m3: 1530,
      ejection_temp_C: 150,
      no_flow_temp_C: 210,
    },
    processing: {
      melt_temp_min_C: 250, melt_temp_max_C: 280, melt_temp_recommended_C: 265,
      mold_temp_min_C: 60, mold_temp_max_C: 110, mold_temp_recommended_C: 80,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 120, drying_time_hr: 4,
      max_residence_time_min: 6,
    },
    mechanical: {
      tensile_strength_MPa: 145,
      flexural_modulus_MPa: 9800,
      elongation_at_break_pct: 3,
      HDT_at_1_8MPa_C: 215,
      shrinkage_pct_min: 0.3, shrinkage_pct_max: 1.2,
    },
    notes: 'Anisotropic shrinkage. Fiber orientation critical. Excellent creep resistance. Structural connectors.',
  },

  // ──── PET ────
  {
    id: 'pet',
    name: 'PET (Polyethylene Terephthalate)',
    family: 'PET',
    type: 'semi-crystalline',
    mfi_g_10min: 15,
    mfi_condition: '285°C / 2.16 kg',
    cross_wlf: {
      n: 0.2385,
      tau_star_Pa: 95000,
      D1_Pa_s: 2.15e+12,
      D2_K: 345.15,
      D3_K_Pa: 0,
      A1: 30.2,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 7.85e-4, b2m_m3_kg_K: 3.92e-7,
      b3m_Pa: 1.62e+8, b4m_1_K: 4.72e-3,
      b1s_m3_kg: 7.15e-4, b2s_m3_kg_K: 1.95e-7,
      b3s_Pa: 2.85e+8, b4s_1_K: 2.55e-3,
      b5_K: 525.15, b6_K_Pa: 2.55e-7,
      b7_m3_kg: 5.85e-5, b8_1_K: 7.82e-2, b9_1_Pa: 9.62e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.24,
      specific_heat_J_kgK: 1800,
      density_kg_m3: 1340,
      ejection_temp_C: 140,
      no_flow_temp_C: 220,
    },
    processing: {
      melt_temp_min_C: 270, melt_temp_max_C: 300, melt_temp_recommended_C: 285,
      mold_temp_min_C: 20, mold_temp_max_C: 140, mold_temp_recommended_C: 30,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 160, drying_time_hr: 4,
      max_residence_time_min: 5,
    },
    mechanical: {
      tensile_strength_MPa: 55,
      flexural_modulus_MPa: 2400,
      elongation_at_break_pct: 200,
      HDT_at_1_8MPa_C: 70,
      shrinkage_pct_min: 1.0, shrinkage_pct_max: 2.5,
    },
    notes: 'Hot mold = crystalline (opaque, high shrinkage). Cold mold = amorphous (transparent, low shrinkage). Very hygroscopic.',
  },

  // ──── PS (Polystyrene) ────
  {
    id: 'ps',
    name: 'PS (General Purpose Polystyrene)',
    family: 'PS',
    type: 'amorphous',
    mfi_g_10min: 8,
    mfi_condition: '200°C / 5 kg',
    cross_wlf: {
      n: 0.2542,
      tau_star_Pa: 28000,
      D1_Pa_s: 1.22e+11,
      D2_K: 373.15,
      D3_K_Pa: 0,
      A1: 26.4,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.82e-4, b2m_m3_kg_K: 5.05e-7,
      b3m_Pa: 1.82e+8, b4m_1_K: 3.45e-3,
      b1s_m3_kg: 9.52e-4, b2s_m3_kg_K: 1.85e-7,
      b3s_Pa: 3.18e+8, b4s_1_K: 1.95e-3,
      b5_K: 373.15, b6_K_Pa: 3.12e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.14,
      specific_heat_J_kgK: 1800,
      density_kg_m3: 1050,
      ejection_temp_C: 75,
      no_flow_temp_C: 100,
    },
    processing: {
      melt_temp_min_C: 180, melt_temp_max_C: 260, melt_temp_recommended_C: 220,
      mold_temp_min_C: 20, mold_temp_max_C: 60, mold_temp_recommended_C: 40,
      max_shear_rate_1_s: 40000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 10,
    },
    mechanical: {
      tensile_strength_MPa: 45,
      flexural_modulus_MPa: 3200,
      elongation_at_break_pct: 2,
      HDT_at_1_8MPa_C: 80,
      shrinkage_pct_min: 0.3, shrinkage_pct_max: 0.6,
    },
    notes: 'Easy to mold, low cost. Very brittle. Crystal clear when unstressed. Packaging, disposable items.',
  },

  // ──── HIPS ────
  {
    id: 'hips',
    name: 'HIPS (High Impact Polystyrene)',
    family: 'PS',
    type: 'amorphous',
    mfi_g_10min: 6,
    mfi_condition: '200°C / 5 kg',
    cross_wlf: {
      n: 0.2685,
      tau_star_Pa: 32000,
      D1_Pa_s: 1.55e+11,
      D2_K: 368.15,
      D3_K_Pa: 0,
      A1: 27.1,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.92e-4, b2m_m3_kg_K: 5.22e-7,
      b3m_Pa: 1.72e+8, b4m_1_K: 3.52e-3,
      b1s_m3_kg: 9.62e-4, b2s_m3_kg_K: 1.92e-7,
      b3s_Pa: 3.02e+8, b4s_1_K: 2.02e-3,
      b5_K: 368.15, b6_K_Pa: 3.15e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.16,
      specific_heat_J_kgK: 1850,
      density_kg_m3: 1040,
      ejection_temp_C: 75,
      no_flow_temp_C: 100,
    },
    processing: {
      melt_temp_min_C: 190, melt_temp_max_C: 260, melt_temp_recommended_C: 220,
      mold_temp_min_C: 20, mold_temp_max_C: 60, mold_temp_recommended_C: 40,
      max_shear_rate_1_s: 40000,
      drying_temp_C: null, drying_time_hr: null,
      max_residence_time_min: 10,
    },
    mechanical: {
      tensile_strength_MPa: 25,
      flexural_modulus_MPa: 1800,
      elongation_at_break_pct: 40,
      HDT_at_1_8MPa_C: 75,
      shrinkage_pct_min: 0.4, shrinkage_pct_max: 0.7,
    },
    notes: 'Rubber-modified PS for impact. Opaque. Refrigerator liners, food packaging. Non-hygroscopic.',
  },

  // ──── TPU ────
  {
    id: 'tpu',
    name: 'TPU (Thermoplastic Polyurethane, 85A)',
    family: 'TPU',
    type: 'semi-crystalline',
    cross_wlf: {
      n: 0.3456,
      tau_star_Pa: 15000,
      D1_Pa_s: 2.85e+9,
      D2_K: 253.15,
      D3_K_Pa: 0,
      A1: 21.8,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.15e-4, b2m_m3_kg_K: 5.82e-7,
      b3m_Pa: 1.12e+8, b4m_1_K: 4.82e-3,
      b1s_m3_kg: 8.52e-4, b2s_m3_kg_K: 2.52e-7,
      b3s_Pa: 2.15e+8, b4s_1_K: 2.72e-3,
      b5_K: 435.15, b6_K_Pa: 3.52e-7,
      b7_m3_kg: 3.25e-5, b8_1_K: 5.15e-2, b9_1_Pa: 7.52e-9,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.22,
      specific_heat_J_kgK: 1800,
      density_kg_m3: 1200,
      ejection_temp_C: 40,
      no_flow_temp_C: 120,
    },
    processing: {
      melt_temp_min_C: 190, melt_temp_max_C: 230, melt_temp_recommended_C: 210,
      mold_temp_min_C: 20, mold_temp_max_C: 50, mold_temp_recommended_C: 35,
      max_shear_rate_1_s: 20000,
      drying_temp_C: 80, drying_time_hr: 3,
      max_residence_time_min: 5,
    },
    mechanical: {
      tensile_strength_MPa: 35,
      flexural_modulus_MPa: 25,
      elongation_at_break_pct: 500,
      HDT_at_1_8MPa_C: 50,
      shrinkage_pct_min: 0.8, shrinkage_pct_max: 2.0,
    },
    notes: 'Elastomeric. Low injection speed to avoid shear heating. Very hygroscopic. Shoe soles, seals, phone cases.',
  },

  // ──── SAN ────
  {
    id: 'san',
    name: 'SAN (Styrene Acrylonitrile)',
    family: 'SAN',
    type: 'amorphous',
    mfi_g_10min: 10,
    mfi_condition: '220°C / 10 kg',
    cross_wlf: {
      n: 0.2456,
      tau_star_Pa: 42000,
      D1_Pa_s: 3.52e+11,
      D2_K: 383.15,
      D3_K_Pa: 0,
      A1: 27.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.42e-4, b2m_m3_kg_K: 4.72e-7,
      b3m_Pa: 1.92e+8, b4m_1_K: 3.62e-3,
      b1s_m3_kg: 9.12e-4, b2s_m3_kg_K: 1.75e-7,
      b3s_Pa: 3.22e+8, b4s_1_K: 2.02e-3,
      b5_K: 383.15, b6_K_Pa: 3.18e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.17,
      specific_heat_J_kgK: 1850,
      density_kg_m3: 1080,
      ejection_temp_C: 85,
      no_flow_temp_C: 110,
    },
    processing: {
      melt_temp_min_C: 220, melt_temp_max_C: 270, melt_temp_recommended_C: 240,
      mold_temp_min_C: 40, mold_temp_max_C: 80, mold_temp_recommended_C: 55,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 80, drying_time_hr: 3,
      max_residence_time_min: 8,
    },
    mechanical: {
      tensile_strength_MPa: 72,
      flexural_modulus_MPa: 3800,
      elongation_at_break_pct: 3,
      HDT_at_1_8MPa_C: 100,
      shrinkage_pct_min: 0.3, shrinkage_pct_max: 0.5,
    },
    notes: 'Transparent with better chemical resistance than PS. Brittle. Cosmetic packaging, kitchenware.',
  },

  // ──── ASA ────
  {
    id: 'asa',
    name: 'ASA (Acrylonitrile Styrene Acrylate)',
    family: 'ASA',
    type: 'amorphous',
    mfi_g_10min: 15,
    mfi_condition: '220°C / 10 kg',
    cross_wlf: {
      n: 0.2752,
      tau_star_Pa: 35000,
      D1_Pa_s: 5.15e+10,
      D2_K: 378.15,
      D3_K_Pa: 0,
      A1: 24.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.52e-4, b2m_m3_kg_K: 5.12e-7,
      b3m_Pa: 1.82e+8, b4m_1_K: 3.42e-3,
      b1s_m3_kg: 9.22e-4, b2s_m3_kg_K: 2.12e-7,
      b3s_Pa: 2.98e+8, b4s_1_K: 1.92e-3,
      b5_K: 378.15, b6_K_Pa: 3.22e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.18,
      specific_heat_J_kgK: 2000,
      density_kg_m3: 1070,
      ejection_temp_C: 85,
      no_flow_temp_C: 108,
    },
    processing: {
      melt_temp_min_C: 230, melt_temp_max_C: 270, melt_temp_recommended_C: 250,
      mold_temp_min_C: 50, mold_temp_max_C: 80, mold_temp_recommended_C: 65,
      max_shear_rate_1_s: 50000,
      drying_temp_C: 80, drying_time_hr: 3,
      max_residence_time_min: 8,
    },
    mechanical: {
      tensile_strength_MPa: 45,
      flexural_modulus_MPa: 2300,
      elongation_at_break_pct: 20,
      HDT_at_1_8MPa_C: 98,
      shrinkage_pct_min: 0.4, shrinkage_pct_max: 0.7,
    },
    notes: 'UV-stable alternative to ABS. Outdoor applications. Weather-resistant. Hygroscopic.',
  },

  // ──── PPE/PS (Noryl) ────
  {
    id: 'ppe-ps',
    name: 'PPE/PS (Modified PPO / Noryl)',
    family: 'PPE',
    type: 'amorphous',
    cross_wlf: {
      n: 0.2285,
      tau_star_Pa: 65000,
      D1_Pa_s: 1.85e+12,
      D2_K: 408.15,
      D3_K_Pa: 0,
      A1: 30.5,
      A2_K: 51.6,
    },
    tait_pvt: {
      b1m_m3_kg: 9.32e-4, b2m_m3_kg_K: 4.62e-7,
      b3m_Pa: 2.02e+8, b4m_1_K: 3.72e-3,
      b1s_m3_kg: 9.02e-4, b2s_m3_kg_K: 1.62e-7,
      b3s_Pa: 3.35e+8, b4s_1_K: 2.12e-3,
      b5_K: 408.15, b6_K_Pa: 3.28e-7,
      b7_m3_kg: 0, b8_1_K: 0, b9_1_Pa: 0,
    },
    thermal: {
      thermal_conductivity_W_mK: 0.22,
      specific_heat_J_kgK: 1700,
      density_kg_m3: 1060,
      ejection_temp_C: 120,
      no_flow_temp_C: 160,
    },
    processing: {
      melt_temp_min_C: 260, melt_temp_max_C: 310, melt_temp_recommended_C: 280,
      mold_temp_min_C: 60, mold_temp_max_C: 110, mold_temp_recommended_C: 85,
      max_shear_rate_1_s: 40000,
      drying_temp_C: 100, drying_time_hr: 2,
      max_residence_time_min: 8,
    },
    mechanical: {
      tensile_strength_MPa: 55,
      flexural_modulus_MPa: 2500,
      elongation_at_break_pct: 50,
      HDT_at_1_8MPa_C: 130,
      shrinkage_pct_min: 0.5, shrinkage_pct_max: 0.8,
    },
    notes: 'Very low moisture absorption, good dimensional stability. Excellent electrical properties. Water meter housings, EV connectors.',
  },
];

/** Lookup material by ID, name, or family (case-insensitive fuzzy match). */
export function findMaterial(query: string): Material[] {
  const q = query.toLowerCase().replace(/[^a-z0-9]/g, '');
  return MATERIALS.filter(m => {
    const targets = [m.id, m.name, m.family, m.filler ?? ''].map(
      s => s.toLowerCase().replace(/[^a-z0-9]/g, '')
    );
    return targets.some(t => t.includes(q) || q.includes(t));
  });
}

/** List all material IDs and names. */
export function listMaterials(): { id: string; name: string; family: string }[] {
  return MATERIALS.map(m => ({ id: m.id, name: m.name, family: m.family }));
}

export function formatMaterialProperties(
  mat: Material,
  requestedProps?: string[]
): string {
  const sections: string[] = [];
  sections.push(`# ${mat.name}`);
  sections.push(`Family: ${mat.family} | Type: ${mat.type}${mat.filler ? ` | Filler: ${mat.filler} (${mat.filler_pct}%)` : ''}`);

  const show = (key: string) => !requestedProps || requestedProps.length === 0 ||
    requestedProps.some(p => key.toLowerCase().includes(p.toLowerCase()));

  if (show('cross_wlf') || show('viscosity') || show('rheol')) {
    const w = mat.cross_wlf;
    sections.push(`\n## Cross-WLF Viscosity Model`);
    sections.push(`  n (power law index): ${w.n}`);
    sections.push(`  τ* (critical shear stress): ${w.tau_star_Pa} Pa`);
    sections.push(`  D1: ${w.D1_Pa_s} Pa·s`);
    sections.push(`  D2: ${w.D2_K} K (${(w.D2_K - 273.15).toFixed(1)}°C)`);
    sections.push(`  D3: ${w.D3_K_Pa} K/Pa`);
    sections.push(`  A1: ${w.A1}`);
    sections.push(`  A2: ${w.A2_K} K`);
  }

  if (show('pvt') || show('tait') || show('density') || show('shrink')) {
    const t = mat.tait_pvt;
    sections.push(`\n## 2-Domain Tait PVT Model`);
    sections.push(`  Melt domain: b1m=${t.b1m_m3_kg}, b2m=${t.b2m_m3_kg_K}, b3m=${t.b3m_Pa}, b4m=${t.b4m_1_K}`);
    sections.push(`  Solid domain: b1s=${t.b1s_m3_kg}, b2s=${t.b2s_m3_kg_K}, b3s=${t.b3s_Pa}, b4s=${t.b4s_1_K}`);
    sections.push(`  Transition: b5=${t.b5_K} K (${(t.b5_K - 273.15).toFixed(1)}°C), b6=${t.b6_K_Pa} K/Pa`);
    if (mat.type === 'semi-crystalline') {
      sections.push(`  Crystallization: b7=${t.b7_m3_kg}, b8=${t.b8_1_K}, b9=${t.b9_1_Pa}`);
    }
  }

  if (show('thermal') || show('conductiv') || show('heat') || show('temperature')) {
    const th = mat.thermal;
    sections.push(`\n## Thermal Properties`);
    sections.push(`  Thermal conductivity: ${th.thermal_conductivity_W_mK} W/(m·K)`);
    sections.push(`  Specific heat: ${th.specific_heat_J_kgK} J/(kg·K)`);
    sections.push(`  Solid density: ${th.density_kg_m3} kg/m³`);
    sections.push(`  Ejection temperature: ${th.ejection_temp_C}°C`);
    sections.push(`  No-flow temperature: ${th.no_flow_temp_C}°C`);
  }

  if (show('process') || show('melt') || show('mold') || show('dry') || show('window')) {
    const p = mat.processing;
    sections.push(`\n## Processing Window`);
    sections.push(`  Melt temp: ${p.melt_temp_min_C}–${p.melt_temp_max_C}°C (recommended: ${p.melt_temp_recommended_C}°C)`);
    sections.push(`  Mold temp: ${p.mold_temp_min_C}–${p.mold_temp_max_C}°C (recommended: ${p.mold_temp_recommended_C}°C)`);
    sections.push(`  Max shear rate: ${p.max_shear_rate_1_s} 1/s`);
    if (p.drying_temp_C != null) {
      sections.push(`  Drying: ${p.drying_temp_C}°C for ${p.drying_time_hr}h`);
    } else {
      sections.push(`  Drying: not required (non-hygroscopic)`);
    }
    sections.push(`  Max barrel residence time: ${p.max_residence_time_min} min`);
  }

  if (show('mechan') || show('strength') || show('modulus') || show('shrink') || show('HDT')) {
    const me = mat.mechanical;
    sections.push(`\n## Mechanical Properties`);
    sections.push(`  Tensile strength: ${me.tensile_strength_MPa} MPa`);
    sections.push(`  Flexural modulus: ${me.flexural_modulus_MPa} MPa`);
    sections.push(`  Elongation at break: ${me.elongation_at_break_pct}%`);
    sections.push(`  HDT @ 1.8 MPa: ${me.HDT_at_1_8MPa_C}°C`);
    sections.push(`  Mold shrinkage: ${me.shrinkage_pct_min}–${me.shrinkage_pct_max}%`);
  }

  sections.push(`\n## Notes\n${mat.notes}`);
  return sections.join('\n');
}
