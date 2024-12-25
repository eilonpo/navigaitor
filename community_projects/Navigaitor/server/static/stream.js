const hlsUrl = "http://localhost:8000/hls/playlist.m3u8";

const video = document.getElementById('video');

if (Hls.isSupported()) {
  // Use hls.js for browsers without native HLS support
  const hls = new Hls();
  hls.loadSource(hlsUrl);
  hls.attachMedia(video);
  hls.on(Hls.Events.MANIFEST_PARSED, () => {
      console.log("HLS Manifest loaded, starting playback.");
      video.play();
  });
  hls.on(Hls.Events.ERROR, (event, data) => {
      console.error("HLS Error:", data);
  });
} else if (video.canPlayType('application/vnd.apple.mpegurl')) {
  // Native HLS support (Safari)
  video.src = hlsUrl;
  video.addEventListener('loadedmetadata', () => {
      console.log("HLS Metadata loaded, starting playback.");
      video.play();
  });
} else {
  // No HLS support
  alert("Your browser does not support HLS playback.");
}
