/**
 * Background Service Worker
 *
 * RESPONSIBILITIES:
 * - Handle extension lifecycle events
 * - Manage settings/storage
 * - Badge updates (show hint count)
 */

console.log('HintAI Background Service Worker Started');

// Default settings
const DEFAULT_SETTINGS = {
    backendUrl: 'ws://localhost:8000/ws/hints',
    autoAnalyze: true,
    debounceTime: 2000,
    enabled: true
};

// Initialize settings on install
chrome.runtime.onInstalled.addListener(() => {
    console.log('HintAI Extension Installed');
    chrome.storage.sync.set(DEFAULT_SETTINGS);
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'updateBadge') {
        // Update extension badge with hint count
        chrome.action.setBadgeText({
            text: message.count.toString(),
            tabId: sender.tab.id
        });
        chrome.action.setBadgeBackgroundColor({
            color: '#3b82f6'
        });
    }

    if (message.type === 'getSettings') {
        chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
            sendResponse(settings);
        });
        return true; // Keep message channel open
    }
});
