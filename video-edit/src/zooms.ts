// Hand-placed micro-zooms. Each keyframe is [seconds, scale]; segments between
// keyframes are eased with a smooth in-out curve. Shots are split at the real
// cuts of the source (3.667 s, 9.267 s, 13.067 s) so a zoom never crosses a cut.
export type Shot = {
  from: number;
  to: number;
  origin: string; // transform-origin, aimed at the speaker's face
  keys: [number, number][];
};

export const SHOTS: Shot[] = [
  // Entrance: slow push-in on the hook, held through the line.
  {from: 0, to: 3.667, origin: '35% 40%', keys: [[0, 1.0], [0.4, 1.0], [2.6, 1.045], [3.667, 1.05]]},
  // Neon sign: open wide so the sign reads, push in when the new phrase
  // starts after the pause (4.79 s), give the frame back in the 8.7 s pause.
  {from: 3.667, to: 9.267, origin: '50% 45%', keys: [[3.667, 1.0], [4.75, 1.0], [6.4, 1.06], [7.9, 1.06], [9.1, 1.02], [9.267, 1.02]]},
  // Bar: let the shot breathe first, then a gentle drift in.
  {from: 9.267, to: 13.067, origin: '45% 45%', keys: [[9.267, 1.0], [10.2, 1.0], [12.9, 1.04], [13.067, 1.04]]},
  // EZE logo: the one accented push of the edit, then release to the original framing for the ending.
  {from: 13.067, to: 18.3, origin: '50% 40%', keys: [[13.067, 1.0], [13.35, 1.0], [14.6, 1.08], [15.6, 1.08], [17.6, 1.0], [18.3, 1.0]]},
];
