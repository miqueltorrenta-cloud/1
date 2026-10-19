import type {Caption} from '@remotion/captions';
import {
  AbsoluteFill,
  Audio,
  Easing,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Captions} from './Captions';
import {SHOTS} from './zooms';
import captions from './data/captions.json';
import ducking from './data/ducking.json';

const smooth = Easing.bezier(0.45, 0, 0.25, 1);

const zoomAt = (t: number) => {
  const shot = SHOTS.find((s) => t >= s.from && t < s.to) ?? SHOTS[SHOTS.length - 1];
  const keys = shot.keys;
  let scale = keys[keys.length - 1][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [t0, s0] = keys[i];
    const [t1, s1] = keys[i + 1];
    if (t >= t0 && t <= t1) {
      scale = interpolate(t, [t0, t1], [s0, s1], {easing: smooth});
      break;
    }
  }
  return {scale, origin: shot.origin};
};

export const EzeEdit: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scale, origin} = zoomAt(frame / fps);

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: origin}}>
        {/* Original picture and voice, untouched (volume 1, PNG frame extraction). */}
        <OffthreadVideo src={staticFile('source.mp4')} transparent style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
      <Audio
        src={staticFile('music_original.wav')}
        volume={(f) => ducking.gain[Math.min(f, ducking.gain.length - 1)]}
      />
      <Captions captions={captions as Caption[]} />
    </AbsoluteFill>
  );
};
