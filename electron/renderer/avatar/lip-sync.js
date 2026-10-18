/**
 * LipSyncProcessor — Real-time Web Audio API frequency analysis and mouth openness animation.
 */

class LipSyncProcessor {
  constructor() {
    this.audioContext = null;
    this.analyser = null;
    this.source = null;
    this.dataArray = null;
    this.isPlaying = false;
    this.currentAudio = null;
    this.volume = 1.0;
    this.gainNode = null;

    // Smooth interpolated values
    this.mouthOpen = 0.0;
    this.mouthWidth = 1.0;
  }

  initContext() {
    if (!this.audioContext) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.audioContext = new AudioCtx();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.gainNode = this.audioContext.createGain();
        this.gainNode.gain.value = this.volume;
      }
    }
  }

  setVolume(vol) {
    this.volume = Math.max(0.0, Math.min(1.0, vol));
    if (this.gainNode && this.audioContext) {
      this.gainNode.gain.setValueAtTime(this.volume, this.audioContext.currentTime);
    }
  }

  /**
   * Play audio buffer/url and process lip-sync data.
   * @param {string|Blob} audioSource URL or Blob of synthesized audio
   * @param {Function} onEnded Callback when playback finishes
   */
  async playAudio(audioSource, onEnded = null) {
    this.initContext();
    if (!this.audioContext) return;

    if (this.audioContext.state === "suspended") {
      await this.audioContext.resume();
    }

    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }

    const audioUrl = typeof audioSource === "string" ? audioSource : URL.createObjectURL(audioSource);
    const audio = new Audio(audioUrl);
    this.currentAudio = audio;

    const source = this.audioContext.createMediaElementSource(audio);
    source.connect(this.analyser);
    this.analyser.connect(this.gainNode);
    this.gainNode.connect(this.audioContext.destination);

    this.isPlaying = true;

    audio.onended = () => {
      this.isPlaying = false;
      this.mouthOpen = 0.0;
      if (onEnded) onEnded();
    };

    audio.onerror = (e) => {
      console.warn('[lip-sync] Audio element error:', audio.error ? `code ${audio.error.code} (${audio.error.message || 'unknown'})` : e);
      this.isPlaying = false;
      this.mouthOpen = 0.0;
      if (onEnded) onEnded();
    };

    try {
      await audio.play();
    } catch (playErr) {
      console.warn('[lip-sync] audio.play() rejected:', playErr.message || playErr);
      this.isPlaying = false;
      this.mouthOpen = 0.0;
      if (onEnded) onEnded();
    }
  }

  /**
   * Update and return current mouth metrics at 60 FPS.
   * @returns {{open: number, width: number, isSpeaking: boolean}}
   */
  update() {
    if (!this.isPlaying || !this.analyser) {
      this.mouthOpen += (0.0 - this.mouthOpen) * 0.2;
      return { open: this.mouthOpen, width: 1.0, isSpeaking: false };
    }

    this.analyser.getByteFrequencyData(this.dataArray);

    // Compute RMS volume in voice formant frequencies (bins 2 to 32, ~200Hz - 2500Hz)
    let sum = 0;
    const lowBin = 2;
    const highBin = Math.min(32, this.dataArray.length);
    for (let i = lowBin; i < highBin; i++) {
      sum += this.dataArray[i];
    }
    const avg = sum / (highBin - lowBin);
    const rawOpen = Math.min(1.0, (avg / 128.0) * 1.6);

    // Exponential smoothing for natural speech articulation
    this.mouthOpen += (rawOpen - this.mouthOpen) * 0.35;
    this.mouthWidth = 1.0 + this.mouthOpen * 0.2;

    return {
      open: this.mouthOpen,
      width: this.mouthWidth,
      isSpeaking: this.mouthOpen > 0.08,
    };
  }

  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    this.isPlaying = false;
    this.mouthOpen = 0.0;
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { LipSyncProcessor };
}
