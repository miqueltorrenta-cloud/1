import {Config} from '@remotion/cli/config';

// Quality first: lossless frame capture, high-quality x264, BT.709 tagging.
Config.setVideoImageFormat('png');
Config.setCodec('h264');
Config.setCrf(12);
Config.setX264Preset('slow');
Config.setPixelFormat('yuv420p');
Config.setColorSpace('bt709');
Config.setAudioCodec('aac');
Config.setAudioBitrate('320k');
Config.setConcurrency(2);
Config.setBrowserExecutable(process.env.REMOTION_BROWSER ?? null);
