/**
 * Audio Hardware Router & Output Device Selector (audio-router.js)
 * Manages audio output sink routing and master gain.
 */

class AudioRouter {
  constructor() {
    this.volume = 1.0;
    this.selectedDeviceId = 'default';
  }

  /**
   * Enumerate available audio output devices.
   * @returns {Promise<Array<{ deviceId: string, label: string }>>}
   */
  async getOutputDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      return [{ deviceId: 'default', label: 'Default Audio Output' }];
    }

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const outputDevices = devices
        .filter((d) => d.kind === 'audiooutput')
        .map((d, index) => ({
          deviceId: d.deviceId,
          label: d.label || `Speaker / Headphone ${index + 1}`,
        }));

      return outputDevices.length > 0
        ? outputDevices
        : [{ deviceId: 'default', label: 'Default Audio Output' }];
    } catch (e) {
      console.warn('[audio-router] Failed to enumerate audio devices:', e);
      return [{ deviceId: 'default', label: 'Default Audio Output' }];
    }
  }

  /**
   * Set output device sink on an HTMLAudioElement or AudioContext if supported.
   * @param {HTMLAudioElement} audioElement
   * @param {string} deviceId
   */
  async setSinkId(audioElement, deviceId) {
    this.selectedDeviceId = deviceId;
    if (audioElement && typeof audioElement.setSinkId === 'function') {
      try {
        await audioElement.setSinkId(deviceId);
        console.log(`[audio-router] Audio sink set to: ${deviceId}`);
      } catch (err) {
        console.warn('[audio-router] setSinkId failed:', err);
      }
    }
  }

  /**
   * Set master volume level (0.0 to 1.0).
   * @param {number} vol
   */
  setVolume(vol) {
    this.volume = Math.max(0.0, Math.min(1.0, vol));
    if (window.avatarRenderer && typeof window.avatarRenderer.setVolume === 'function') {
      window.avatarRenderer.setVolume(this.volume);
    }
  }
}

if (typeof window !== 'undefined') {
  window.AudioRouter = AudioRouter;
  window.audioRouter = new AudioRouter();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AudioRouter };
}
