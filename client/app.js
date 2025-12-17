/**
 * Agent Assist Console - Frontend Application Logic
 * 
 * Handles:
 * - Chat interface
 * - API communication
 * - Media panel rendering
 * - Freshdesk export
 */

// Configuration
const CONFIG = {
    apiBaseUrl: window.location.origin.includes('localhost') 
        ? 'http://localhost:8000' 
        : window.location.origin,
    endpoints: {
        chat: '/api/chat',
        freshdesk: '/api/freshdesk',
        health: '/health'
    }
};

// Application State
const AppState = {
    config: {
        modelMode: 'flash'
    },
    chat: {
        messages: [],
        isLoading: false
    },
    context: {
        currentAssets: null,
        matchedProduct: null,
        sources: [],
        latestResponse: null
    },
    freshdesk: {
        ticketId: null
    }
};

// Configure marked to open all links in new tabs
marked.use({
    renderer: {
        link(href, title, text) {
            const link = marked.Renderer.prototype.link.call(this, href, title, text);
            return link.replace('<a', '<a target="_blank" rel="noopener noreferrer"');
        }
    }
});

// DOM Elements
const elements = {
    chatContainer: document.getElementById('chat-container'),
    chatForm: document.getElementById('chat-form'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    mediaPanel: document.getElementById('media-panel'),
    ticketIdInput: document.getElementById('ticket-id'),
    exportBtn: document.getElementById('export-btn'),
    loadingOverlay: document.getElementById('loading-overlay'),
    statusIndicator: document.getElementById('status-indicator')
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    console.log('🚀 Initializing Agent Assist Console...');
    
    // Check backend health
    await checkHealth();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load model preference
    loadModelPreference();
    
    console.log('✅ Application ready');
}

async function checkHealth() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.health}`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('connected', true);
            console.log('✓ Backend connected', data);
        } else {
            updateStatus('disconnected', false);
            console.warn('⚠ Backend unhealthy', data);
        }
    } catch (error) {
        updateStatus('error', false);
        console.error('✗ Failed to connect to backend', error);
    }
}

function setupEventListeners() {
    // Chat form submission
    elements.chatForm.addEventListener('submit', handleChatSubmit);
    
    // Model selection
    document.querySelectorAll('input[name="model"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            AppState.config.modelMode = e.target.value;
            localStorage.setItem('preferredModel', e.target.value);
            console.log(`Model changed to: ${e.target.value}`);
        });
    });
    
    // Ticket ID input
    elements.ticketIdInput.addEventListener('input', (e) => {
        AppState.freshdesk.ticketId = e.target.value.trim();
        elements.exportBtn.disabled = !AppState.freshdesk.ticketId || !AppState.context.latestResponse;
    });
    
    // Export button
    elements.exportBtn.addEventListener('click', handleFreshdeskExport);
    
    // Enter key for input
    elements.userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            elements.chatForm.dispatchEvent(new Event('submit'));
        }
    });
}

function loadModelPreference() {
    const preferred = localStorage.getItem('preferredModel');
    if (preferred) {
        AppState.config.modelMode = preferred;
        const radio = document.querySelector(`input[name="model"][value="${preferred}"]`);
        if (radio) radio.checked = true;
    }
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const query = elements.userInput.value.trim();
    if (!query || AppState.chat.isLoading) return;
    
    // Clear input
    elements.userInput.value = '';
    
    // Add user message to chat
    addMessage('user', query);
    
    // Show loading
    setLoading(true);
    addTypingIndicator();
    
    try {
        // Send query to backend
        const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.chat}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                model_mode: AppState.config.modelMode
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add AI response
        addMessage('assistant', data.markdown_response, data);
        
        // Update context
        AppState.context.currentAssets = data.media_assets;
        AppState.context.matchedProduct = data.matched_product;
        AppState.context.sources = data.sources;
        AppState.context.latestResponse = data;
        
        // Update media panel
        if (data.media_assets) {
            renderMediaPanel(data.media_assets, data.matched_product);
        }
        
        // Enable export button if ticket ID is set
        if (AppState.freshdesk.ticketId) {
            elements.exportBtn.disabled = false;
        }
        
        console.log('✓ Response received', data);
        
    } catch (error) {
        console.error('✗ Error processing query:', error);
        removeTypingIndicator();
        addMessage('system', `❌ Error: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

function addMessage(role, content, metadata = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="flex justify-end">
                <div class="user-message">
                    ${escapeHtml(content)}
                </div>
            </div>
        `;
    } else if (role === 'assistant') {
        const markdownHtml = marked.parse(content);
        
        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                </div>
                <div class="flex-1">
                    <div class="ai-message">
                        <div class="markdown-content">
                            ${markdownHtml}
                        </div>
                        ${metadata && metadata.matched_product ? `
                            <div class="mt-3 pt-3 border-t border-gray-200">
                                <span class="badge badge-blue">
                                    📦 ${metadata.matched_product}
                                </span>
                                <span class="badge badge-green ml-2">
                                    ${Math.round(metadata.confidence * 100)}% match
                                </span>
                            </div>
                        ` : ''}
                        ${metadata && metadata.sources && metadata.sources.length > 0 ? `
                            <div class="mt-3 pt-3 border-t border-gray-200">
                                <p class="text-xs font-medium text-gray-500 mb-1">Sources:</p>
                                <div class="text-xs text-gray-600 space-y-1">
                                    ${metadata.sources.map(source => `
                                        <div>📄 ${escapeHtml(source)}</div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="text-xs text-gray-500 mt-2 ml-4">
                        ${new Date().toLocaleTimeString()} • ${metadata?.model_used || 'AI'}
                    </div>
                </div>
            </div>
        `;
    } else if (role === 'system') {
        messageDiv.innerHTML = `
            <div class="flex justify-center">
                <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 rounded-lg text-sm">
                    ${content}
                </div>
            </div>
        `;
    }
    
    // Remove welcome message if it exists
    const welcomeMsg = elements.chatContainer.querySelector('.text-center.py-12');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    elements.chatContainer.appendChild(messageDiv);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    
    AppState.chat.messages.push({ role, content, metadata });
}

function addTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'message';
    indicator.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            </div>
            <div class="ai-message">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    elements.chatContainer.appendChild(indicator);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function renderMediaPanel(assets, productName) {
    const { specs, videos, images, documents } = assets;
    
    let html = `
        <div class="p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">
                📦 ${productName || 'Product Resources'}
            </h2>
    `;
    
    // Specifications
    if (specs && Object.keys(specs).length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Specifications
                </h3>
                <div class="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
                    <table class="spec-table w-full">
                        <tbody>
                            ${Object.entries(specs)
                                .filter(([key]) => !key.startsWith('_') && key !== 'Model_NO' && key !== 'Product_Name')
                                .slice(0, 10)
                                .map(([key, value]) => `
                                    <tr class="border-b border-gray-200 last:border-b-0">
                                        <td class="px-3 py-2 font-medium text-gray-600">${formatKey(key)}</td>
                                        <td class="px-3 py-2 text-gray-900">${formatValue(value)}</td>
                                    </tr>
                                `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    // Videos
    if (videos && videos.length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Videos
                </h3>
                <div class="space-y-3">
                    ${videos.map(video => `
                        <a href="${video.url}" target="_blank" 
                           class="media-card block bg-white border border-gray-200 rounded-lg p-3 hover:border-blue-500">
                            <div class="flex items-center space-x-3">
                                <div class="flex-shrink-0 w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                                    <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                                    </svg>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm font-medium text-gray-900 truncate">${video.title}</p>
                                    <p class="text-xs text-gray-500">${video.type || 'Video'}</p>
                                </div>
                                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                            </div>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Documents
    if (documents && documents.length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    Documents
                </h3>
                <div class="space-y-2">
                    ${documents.map(doc => `
                        <a href="${doc.url}" target="_blank" 
                           class="media-card block bg-white border border-gray-200 rounded-lg p-3 hover:border-blue-500">
                            <div class="flex items-center space-x-3">
                                <div class="flex-shrink-0">
                                    <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm font-medium text-gray-900">${doc.title}</p>
                                    <p class="text-xs text-gray-500">${doc.type || 'PDF'} ${doc.file_size ? '• ' + doc.file_size : ''}</p>
                                </div>
                                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                            </div>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Images
    if (images && images.length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Images
                </h3>
                <div class="grid grid-cols-2 gap-2">
                    ${images.map(image => `
                        <a href="${image.url}" target="_blank" class="media-card block">
                            <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden border border-gray-200 hover:border-blue-500">
                                <img src="${image.url}" alt="${image.title}" 
                                     class="w-full h-full object-cover"
                                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 24 24\\' fill=\\'%239ca3af\\'%3E%3Cpath d=\\'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z\\'/%3E%3C/svg%3E'">
                            </div>
                            <p class="text-xs text-gray-600 mt-1 text-center truncate">${image.title}</p>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    
    elements.mediaPanel.innerHTML = html;
}

async function handleFreshdeskExport() {
    if (!AppState.freshdesk.ticketId || !AppState.context.latestResponse) {
        return;
    }
    
    elements.exportBtn.disabled = true;
    elements.exportBtn.innerHTML = '<span class="flex items-center justify-center">Exporting...</span>';
    
    try {
        // Format note for Freshdesk
        const formattedNote = formatFreshdeskNote(
            AppState.chat.messages[AppState.chat.messages.length - 2].content, // User query
            AppState.context.latestResponse.markdown_response,
            AppState.context.latestResponse.model_used,
            AppState.context.sources
        );
        
        const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.freshdesk}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticket_id: AppState.freshdesk.ticketId,
                formatted_note: formattedNote
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Successfully exported to ticket #${data.ticket_id}`);
            console.log('✓ Exported to Freshdesk', data);
        } else {
            throw new Error(data.error || 'Export failed');
        }
        
    } catch (error) {
        console.error('✗ Freshdesk export error:', error);
        alert(`❌ Export failed: ${error.message}`);
    } finally {
        elements.exportBtn.disabled = false;
        elements.exportBtn.innerHTML = `
            <span class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                Export to Ticket
            </span>
        `;
    }
}

function formatFreshdeskNote(query, response, model, sources) {
    return `
<div style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #f9f9f9;">
    <h3 style="color: #2c3e50; margin-top: 0;">🤖 Agent Assist Console Research</h3>
    
    <div style="margin-bottom: 15px;">
        <strong>Query:</strong> ${escapeHtml(query)}
    </div>
    
    <div style="background-color: white; padding: 15px; border-radius: 3px; margin-bottom: 15px;">
        <strong>Research Results:</strong>
        <div style="margin-top: 10px;">
            ${marked.parse(response)}
        </div>
    </div>
    
    ${sources && sources.length > 0 ? `
    <div style="margin-bottom: 10px;">
        <strong>Sources:</strong>
        <ul>
            ${sources.map(source => `<li>${escapeHtml(source)}</li>`).join('')}
        </ul>
    </div>
    ` : ''}
    
    <div style="font-size: 0.85em; color: #7f8c8d; margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0;">
        Generated by Agent Assist Console | Model: ${model}
    </div>
</div>
    `.trim();
}

// Utility functions
function setLoading(loading) {
    AppState.chat.isLoading = loading;
    elements.sendBtn.disabled = loading;
    elements.userInput.disabled = loading;
    elements.loadingOverlay.classList.toggle('hidden', !loading);
}

function updateStatus(status, healthy) {
    const indicator = elements.statusIndicator;
    const dot = indicator.querySelector('.w-2');
    const text = indicator.querySelector('span');
    
    if (healthy) {
        dot.className = 'w-2 h-2 bg-green-400 rounded-full animate-pulse';
        text.textContent = 'Connected';
    } else {
        dot.className = 'w-2 h-2 bg-red-400 rounded-full';
        text.textContent = status === 'error' ? 'Error' : 'Disconnected';
    }
}

function insertSample(text) {
    elements.userInput.value = text;
    elements.userInput.focus();
}

function clearChat() {
    if (confirm('Clear all messages?')) {
        AppState.chat.messages = [];
        elements.chatContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="inline-block p-4 bg-blue-100 rounded-full mb-4">
                    <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                </div>
                <h2 class="text-2xl font-bold text-gray-800 mb-2">Welcome to Agent Assist Console</h2>
                <p class="text-gray-600 max-w-md mx-auto">
                    Ask questions about products, specifications, installation, or troubleshooting. 
                    I'll search through all available resources to help you.
                </p>
            </div>
        `;
        
        // Clear media panel
        elements.mediaPanel.innerHTML = `
            <div class="p-6">
                <h2 class="text-lg font-semibold text-gray-800 mb-4">📎 Resources & Media</h2>
                <div class="text-center py-12 text-gray-400">
                    <svg class="w-16 h-16 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    <p>Media assets will appear here when you search for a product</p>
                </div>
            </div>
        `;
        
        AppState.context.currentAssets = null;
        AppState.context.latestResponse = null;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatKey(key) {
    return key.replace(/_/g, ' ')
              .replace(/\b\w/g, l => l.toUpperCase());
}

function formatValue(value) {
    if (value === null || value === undefined || value === '') {
        return '—';
    }
    if (typeof value === 'number') {
        return value.toLocaleString();
    }
    return String(value);
}

// Export to window for HTML onclick handlers
window.insertSample = insertSample;
window.clearChat = clearChat;
