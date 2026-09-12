/* ==================== TIMER & NOTIFICATION SYSTEM ==================== */

/**
 * Timer Management for Gaming Sessions
 * Handles countdown timers, alerts, and session expiry notifications
 */

const TimerSystem = (() => {
    const timers = new Map();
    const ALERT_THRESHOLD = 5 * 60; // 5 minutes in seconds
    
    /**
     * Start a countdown timer for a session
     * @param {number} sessionId - Session ID
     * @param {number} endTime - Unix timestamp of session end time
     * @param {function} onTick - Callback for each tick
     * @param {function} onExpire - Callback when time expires
     */
    function startTimer(sessionId, endTime, onTick, onExpire) {
        // Clear existing timer if any
        if (timers.has(sessionId)) {
            clearInterval(timers.get(sessionId).interval);
        }
        
        const timerData = {
            sessionId,
            endTime,
            onTick,
            onExpire,
            alerted5min: false,
            interval: null
        };
        
        const updateTimer = () => {
            const now = Date.now();
            const remaining = Math.max(0, endTime - now);
            const remainingSeconds = Math.floor(remaining / 1000);
            
            // Call tick callback
            if (onTick) {
                onTick(remainingSeconds);
            }
            
            // Alert at 5 minutes remaining
            if (remainingSeconds === ALERT_THRESHOLD && !timerData.alerted5min) {
                timerData.alerted5min = true;
                triggerAlert(sessionId, '5 minutes remaining!');
            }
            
            // Expire
            if (remainingSeconds === 0) {
                clearInterval(timerData.interval);
                timers.delete(sessionId);
                if (onExpire) {
                    onExpire();
                }
                triggerAlert(sessionId, 'Session expired!');
            }
        };
        
        updateTimer(); // First call
        timerData.interval = setInterval(updateTimer, 1000);
        timers.set(sessionId, timerData);
    }
    
    /**
     * Stop a timer
     * @param {number} sessionId
     */
    function stopTimer(sessionId) {
        if (timers.has(sessionId)) {
            clearInterval(timers.get(sessionId).interval);
            timers.delete(sessionId);
        }
    }
    
    /**
     * Stop all timers
     */
    function stopAllTimers() {
        timers.forEach((timerData) => {
            clearInterval(timerData.interval);
        });
        timers.clear();
    }
    
    /**
     * Format seconds to human readable time
     * @param {number} seconds
     * @returns {string} Formatted time string
     */
    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    }
    
    /**
     * Get formatted time for display
     * @param {number} seconds
     * @returns {string}
     */
    function getDisplayTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    
    return {
        startTimer,
        stopTimer,
        stopAllTimers,
        formatTime,
        getDisplayTime
    };
})();

/**
 * Notification System
 * Handles alerts, sounds, and visual notifications
 */
function triggerAlert(sessionId, message) {
    // Play alert sound
    playAlertSound();
    
    // Show visual notification
    showNotification(message);
    
    // Optional: Show browser notification if permission granted
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Gaming Center Alert', {
            body: message,
            icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="%2300ff41"/></svg>'
        });
    }
}

/**
 * Play alert sound
 */
function playAlertSound() {
    // Create a simple beep sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // Hz
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

/**
 * Show toast notification
 */
function showNotification(message, type = 'warning') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = `
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    `;
    alertDiv.innerHTML = `
        <i class="fas fa-bell me-2"></i>
        <strong>${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Request notification permission
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Request notification permission on page load
window.addEventListener('load', () => {
    requestNotificationPermission();
});

/**
 * Session Timer Widget
 * Creates and manages timer display for active sessions
 */
class SessionTimer {
    constructor(sessionId, elementId, endTime) {
        this.sessionId = sessionId;
        this.elementId = elementId;
        this.endTime = new Date(endTime).getTime();
        this.element = document.getElementById(elementId);
        
        if (this.element) {
            this.start();
        }
    }
    
    start() {
        TimerSystem.startTimer(
            this.sessionId,
            this.endTime,
            (seconds) => this.updateDisplay(seconds),
            () => this.onExpire()
        );
    }
    
    updateDisplay(seconds) {
        if (this.element) {
            const displayTime = TimerSystem.getDisplayTime(seconds);
            this.element.textContent = displayTime;
            
            // Change color based on time remaining
            if (seconds <= 300) { // 5 minutes or less
                this.element.className = 'text-danger fw-bold';
            } else if (seconds <= 600) { // 10 minutes or less
                this.element.className = 'text-warning fw-bold';
            } else {
                this.element.className = 'text-success fw-bold';
            }
        }
    }
    
    onExpire() {
        if (this.element) {
            this.element.textContent = 'EXPIRED';
            this.element.className = 'text-danger fw-bold';
        }
    }
    
    stop() {
        TimerSystem.stopTimer(this.sessionId);
    }
}

/**
 * Utility: Format duration in minutes to readable format
 */
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    } else {
        return `${mins}m`;
    }
}

/**
 * Utility: Calculate bill amount
 */
function calculateBill(durationMinutes, hourlyRate) {
    return (durationMinutes / 60) * hourlyRate;
}

/**
 * Utility: Get elapsed time since a start time
 */
function getElapsedTime(startTime) {
    const now = new Date();
    const start = new Date(startTime);
    const diffSeconds = Math.floor((now - start) / 1000);
    return TimerSystem.formatTime(diffSeconds);
}

/**
 * Export functions for global use
 */
window.TimerSystem = TimerSystem;
window.SessionTimer = SessionTimer;
window.triggerAlert = triggerAlert;
window.playAlertSound = playAlertSound;
window.showNotification = showNotification;
window.formatDuration = formatDuration;
window.calculateBill = calculateBill;
window.getElapsedTime = getElapsedTime;
