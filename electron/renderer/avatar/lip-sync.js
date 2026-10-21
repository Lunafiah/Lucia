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

    this._sessionSeq = 0;
    this._activeSession = null;
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
   * @param {Function|object} callbacks Callback when playback finishes, or lifecycle handlers
   */
  async playAudio(audioSource, callbacks = null) {
    this.initContext();

    // Normalizing callbacks: supports function or object { onStart, onEnded, onError, onCancel }
    const onStart = typeof callbacks === 'function' ? callbacks.onStart : callbacks?.onStart;
    const onEnded = typeof callbacks === 'function' ? (callbacks.onEnded || callbacks) : callbacks?.onEnded;
    const onError = typeof callbacks === 'function' ? callbacks.onError : callbacks?.onError;
    const onCancel = typeof callbacks === 'function' ? callbacks.onCancel : callbacks?.onCancel;

    // Graceful fallback if Web Audio is unsupported
    if (!this.audioContext) {
      if (typeof callbacks === 'function') callbacks();
      else if (onEnded) onEnded();
      return;
    }

    if (this.audioContext.state === "suspended") {
      try {
        await this.audioContext.resume();
      } catch (e) {
        console.warn('[lip-sync] audioContext.resume() failed:', e);
      }
    }

    if (this._activeSession) {
      this._activeSession.cancel();
      this._activeSession = null;
    }

    if (this.currentAudio) {
      try {
        this.currentAudio.pause();
      } catch (_) {}
      this.currentAudio = null;
    }

    let createdUrl = null;
    let audioUrl = audioSource;
    if (typeof audioSource !== "string") {
      try {
        createdUrl = URL.createObjectURL(audioSource);
        audioUrl = createdUrl;
      } catch (_) {
        audioUrl = "";
      }
    }

    const audio = new Audio(audioUrl);
    this.currentAudio = audio;

    try {
      const source = this.audioContext.createMediaElementSource(audio);
      source.connect(this.analyser);
      this.analyser.connect(this.gainNode);
      this.gainNode.connect(this.audioContext.destination);
    } catch (e) {
      console.warn('[lip-sync] MediaElementSource connection warning:', e);
    }

    this.isPlaying = true;

    let completed = false;
    let started = false;

    const cleanup = () => {
      this.isPlaying = false;
      this.mouthOpen = 0.0;
      if (this.currentAudio === audio) {
        this.currentAudio = null;
      }
      if (this._activeSession === session) {
        this._activeSession = null;
      }
      if (createdUrl) {
        try {
          URL.revokeObjectURL(createdUrl);
        } catch (_) {}
        createdUrl = null;
      }
    };

    const triggerStart = () => {
      if (!started && !completed) {
        started = true;
        if (onStart) onStart();
      }
    };

    const session = {
      id: ++this._sessionSeq,
      start: triggerStart,
      end: () => {
        if (!completed) {
          completed = true;
          cleanup();
          if (onEnded) onEnded();
        }
      },
      error: (err) => {
        if (!completed) {
          completed = true;
          cleanup();
          if (onError) onError(err);
          else if (onEnded) onEnded(err);
        }
      },
      cancel: () => {
        if (!completed) {
          completed = true;
          try {
            audio.pause();
          } catch (_) {}
          cleanup();
          if (onCancel) onCancel();
        }
      }
    };
    this._activeSession = session;

    audio.onplay = triggerStart;
    audio.onplaying = triggerStart;

    audio.onended = () => {
      session.end();
    };

    audio.onerror = (e) => {
      console.warn('[lip-sync] Audio element error:', audio.error ? `code ${audio.error.code} (${audio.error.message || 'unknown'})` : e);
      session.error(audio.error || e);
    };

    try {
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        await playPromise;
      }
      triggerStart();
    } catch (playErr) {
      console.warn('[lip-sync] audio.play() rejected:', playErr.message || playErr);
      session.error(playErr);
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
    if (this._activeSession) {
      this._activeSession.cancel();
      this._activeSession = null;
    }
    if (this.currentAudio) {
      try {
        this.currentAudio.pause();
      } catch (_) {}
      this.currentAudio = null;
    }
    this.isPlaying = false;
    this.mouthOpen = 0.0;
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { LipSyncProcessor };
}
