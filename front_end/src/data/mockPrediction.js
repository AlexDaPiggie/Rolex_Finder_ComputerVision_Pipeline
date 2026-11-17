const mockPrediction = {
  prediction: {
    model: "Cellini",
    confidence: 99.82,
  },

  matches: [
    {
      rank: 1,
      model: "Rolex Cellini Danaos",
      score: 28.92,
      references: ["4233", "4233", "4238"],
    },
    {
      rank: 2,
      model: "Rolex Cellini Time",
      score: 21.84,
      references: ["5050", "50505", "50509"],
    },
    {
      rank: 3,
      model: "Rolex Cellini Dual Time",
      score: 16.77,
      references: ["5052", "50525", "50529"],
    },
  ],

  probabilities: [
    { name: "Cellini", value: "99.8166%" },
    { name: "Daytona", value: "0.0608%" },
    { name: "Date", value: "0.0513%" },
    { name: "Explorer", value: "0.0311%" },
    { name: "GMT Master", value: "0.0194%" },
    { name: "Oyster Perpetual", value: "0.0078%" },
    { name: "Submariner", value: "0.0041%" },
  ],

  summary:
    "Among known variants, the closest match is Rolex Cellini Danaos, with possible reference IDs 4233, 4243, and 6229.",
};

export default mockPrediction;