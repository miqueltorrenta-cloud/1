import type {Caption} from '@remotion/captions';
import {interpolate, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/600.css';

type Page = {text: string; startMs: number; endMs: number};

// ~ two lines at 100px Montserrat SemiBold inside the 1560px text box.
const MAX_CHARS = 38;
const MAX_GAP_MS = 450;
const MIN_PAGE_MS = 700;

export const toPages = (captions: Caption[]): Page[] => {
  const pages: Page[] = [];
  let cur: Page | null = null;
  for (const c of captions) {
    const word = c.text.trim();
    if (!word) continue;
    const prevEndsSentence = cur !== null && /[.!?…]$/.test(cur.text);
    const breakHere =
      cur === null ||
      prevEndsSentence ||
      c.startMs - cur.endMs > MAX_GAP_MS ||
      (cur.text + ' ' + word).length > MAX_CHARS;
    if (breakHere) {
      if (cur) pages.push(cur);
      cur = {text: word, startMs: c.startMs, endMs: c.endMs};
    } else if (cur) {
      cur.text += ' ' + word;
      cur.endMs = c.endMs;
    }
  }
  if (cur) pages.push(cur);
  // Hold each page until the next one starts (when the gap is small) and
  // enforce a minimum on-screen time so short pages stay readable.
  return pages.map((p, i) => {
    const next = pages[i + 1];
    let end = Math.max(p.endMs, p.startMs + MIN_PAGE_MS);
    if (next && next.startMs - p.endMs <= MAX_GAP_MS) end = next.startMs;
    if (next) end = Math.min(end, next.startMs);
    return {...p, endMs: end};
  });
};

export const Captions: React.FC<{captions: Caption[]}> = ({captions}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const page = toPages(captions).find((p) => ms >= p.startMs && ms < p.endMs);
  if (!page) return null;

  const local = ms - page.startMs;
  const remaining = page.endMs - ms;
  const opacity = Math.min(
    interpolate(local, [0, 120], [0, 1], {extrapolateRight: 'clamp'}),
    interpolate(remaining, [0, 90], [0, 1], {extrapolateRight: 'clamp'}),
  );
  const rise = interpolate(local, [0, 180], [14, 0], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        // ~11.5% bottom margin: above the TikTok/Reels caption + UI band, never glued to the edge.
        bottom: '11.5%',
        display: 'flex',
        justifyContent: 'center',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          // 1560 / 2160 = 72%: keeps clear of the right-hand action rail.
          maxWidth: 1560,
          textAlign: 'center',
          fontFamily: 'Montserrat',
          fontWeight: 600,
          fontSize: 100,
          lineHeight: 1.22,
          letterSpacing: '0.005em',
          color: '#FFFFFF',
          textShadow: '0 3px 14px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.6)',
          WebkitTextStroke: '1px rgba(0,0,0,0.25)',
          opacity,
          transform: `translateY(${rise}px)`,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {page.text}
      </div>
    </div>
  );
};
