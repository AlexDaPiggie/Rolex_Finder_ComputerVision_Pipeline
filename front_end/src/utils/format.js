// Display names for the trained families (backend keys use snake_case)
const NAMES = {
  airking: "Air-King",
  cellini: "Cellini",
  date: "Date",
  datejust: "Datejust",
  daytona: "Daytona",
  explorer: "Explorer",
  gmt_master: "GMT-Master",
  land_dweller: "Land-Dweller",
  milgauss: "Milgauss",
  oyster_perpetual: "Oyster Perpetual",
  oysterquartz: "Oysterquartz",
  president: "President",
  sea_dweller: "Sea-Dweller",
  submariner: "Submariner",
  turn_o_graph: "Turn-O-Graph",
  yacht_master: "Yacht-Master",
};

export function displayName(key = "") {
  const k = String(key).toLowerCase().replaceAll("-", "_").replaceAll(" ", "_");
  if (NAMES[k]) return NAMES[k];
  return k.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// 0-1 -> "93%", "4.9%", "<0.1%". No fake 4-decimal precision.
export function formatPct(value) {
  const pct = value * 100;
  if (pct < 0.1) return "<0.1%";
  if (pct >= 99.5) return ">99%";
  if (pct >= 10) return `${Math.round(pct)}%`;
  return `${pct.toFixed(1)}%`;
}

export function confidenceLevel(confidence) {
  if (confidence >= 0.8) return "high";
  if (confidence >= 0.5) return "medium";
  return "low";
}

export const NO_WATCH = "No Watch Detected";

// Words instead of percentages: the model gives an estimate, not a measured accuracy.
export const VERDICT = {
  high: "Strong match",
  medium: "Likely",
  low: "Possible",
};

// When the top two families are close, say so. Pairs the model mixes up get a hint on how to tell them apart.
const HINTS = {
  "sea_dweller|submariner": "the Sea-Dweller has SEA-DWELLER text on the dial and a thicker case",
  "datejust|president": "the President (Day-Date) shows the day of the week and comes only in precious metal",
  "datejust|land_dweller": "the Land-Dweller says LAND-DWELLER on the dial, which has a honeycomb pattern, and has flat links on the bracelet",
  "datejust|oyster_perpetual": "the Oyster Perpetual has no date window",
};

export function closeCall(rows) {
  if (rows.length < 2) return null;
  const [a, b] = rows;
  if (b.raw < 0.2 || a.raw - b.raw > 0.3) return null;
  const key = [a.key, b.key].sort().join("|");
  const hint = HINTS[key] ? `, ${HINTS[key]}` : "";
  return `${a.name} or ${b.name}${hint}.`;
}
