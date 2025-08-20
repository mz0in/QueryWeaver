/**
 * Main application entry point - coordinates all modules
 */

import { DOM } from './modules/config.js';
import { initChat } from './modules/messages.js';
import { sendMessage, pauseRequest } from './modules/chat.js';
import { loadGraphs, handleFileUpload, onGraphChange } from './modules/graphs.js';
import { 
    toggleContainer, 
    showResetConfirmation, 
    hideResetConfirmation, 
    handleResetConfirmation,
    setupUserProfileDropdown,
    setupThemeToggle,
    setupToolbar,
    handleWindowResize,
} from './modules/ui.js';
import { setupAuthenticationModal, setupDatabaseModal } from './modules/modals.js';

// Initialize the application
function initializeApp() {
    // Initialize chat
    initChat();
    
    // Set up event listeners
    setupEventListeners();
    
    // Set up UI components
    setupUIComponents();
    
    // Load initial data
    loadInitialData();
}

function setupEventListeners() {
    // Chat functionality
    DOM.submitButton.addEventListener('click', sendMessage);
    DOM.pauseButton.addEventListener('click', pauseRequest);
    DOM.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Menu functionality
    DOM.menuButton.addEventListener('click', () => toggleContainer(DOM.menuContainer));

    // Schema functionality
    DOM.schemaButton.addEventListener('click', () => toggleContainer(DOM.schemaContainer));

    // Reset functionality
    DOM.newChatButton.addEventListener('click', showResetConfirmation);
    DOM.resetConfirmBtn.addEventListener('click', handleResetConfirmation);
    DOM.resetCancelBtn.addEventListener('click', hideResetConfirmation);

    // Modal interactions
    DOM.resetConfirmationModal.addEventListener('click', (e) => {
        if (e.target === DOM.resetConfirmationModal) {
            hideResetConfirmation();
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.resetConfirmationModal.style.display === 'flex') {
            hideResetConfirmation();
        }
    });

    // Graph management
    DOM.graphSelect.addEventListener("change", onGraphChange);
    DOM.fileUpload.addEventListener('change', handleFileUpload);

    // Window resize handling
    window.addEventListener('resize', handleWindowResize);
}

function setupUIComponents() {
    setupUserProfileDropdown();
    setupThemeToggle();
    setupAuthenticationModal();
    setupDatabaseModal();
    setupToolbar();
}

function loadInitialData() {
    loadGraphs();
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", initializeApp);
