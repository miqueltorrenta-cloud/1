import {Composition} from 'remotion';
import {EzeEdit} from './EzeEdit';

// Matches the source exactly: 2160x3840, 30 fps, 18.267 s (548 frames).
export const RemotionRoot: React.FC = () => (
  <Composition
    id="EzeEdit"
    component={EzeEdit}
    durationInFrames={548}
    fps={30}
    width={2160}
    height={3840}
  />
);
