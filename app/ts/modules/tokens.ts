/**
 * Token management functionality (TypeScript)
 */

interface Token {
    token_id: string;
    created_at: number;
    last_4_digits: string;
}

interface TokenResponse {
    token: string;
    token_id: string;
    created_at: number;
    last_4_digits: string;
}

interface TokenListResponse {
    tokens: Token[];
}

let currentDeleteTokenId: string | null = null;

export function setupTokenManagement() {
    const apiTokensBtn = document.getElementById('api-tokens-btn');
    const tokensModal = document.getElementById('tokens-modal');
    const closeTokensModal = document.getElementById('close-tokens-modal');
    const generateTokenBtn = document.getElementById('generate-token-btn');
    const copyTokenBtn = document.getElementById('copy-token-btn');
    const deleteTokenModal = document.getElementById('delete-token-modal');
    const closeDeleteTokenModal = document.getElementById('close-delete-token-modal');
    const confirmDeleteToken = document.getElementById('confirm-delete-token');
    const cancelDeleteToken = document.getElementById('cancel-delete-token');

    if (!apiTokensBtn || !tokensModal) return;

    // Open tokens modal
    apiTokensBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Close user profile dropdown
        const userProfileDropdown = document.getElementById('user-profile-dropdown');
        if (userProfileDropdown) {
            userProfileDropdown.classList.remove('show');
        }
        
        tokensModal.style.display = 'block';
        await loadTokens();
    });

    // Close tokens modal
    closeTokensModal?.addEventListener('click', function() {
        tokensModal.style.display = 'none';
        hideTokenGenerated();
    });

    // Close modal when clicking outside
    tokensModal.addEventListener('click', function(e) {
        if (e.target === tokensModal) {
            tokensModal.style.display = 'none';
            hideTokenGenerated();
        }
    });

    // Generate new token
    generateTokenBtn?.addEventListener('click', async function() {
        await generateToken();
    });

    // Copy token to clipboard
    copyTokenBtn?.addEventListener('click', function() {
        const tokenInput = document.getElementById('new-token-value') as HTMLInputElement;
        if (tokenInput) {
            tokenInput.select();
            document.execCommand('copy');
            
            // Show feedback
            const originalText = copyTokenBtn.textContent;
            copyTokenBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyTokenBtn.textContent = originalText;
            }, 2000);
        }
    });

    // Delete token modal handlers
    closeDeleteTokenModal?.addEventListener('click', function() {
        if (deleteTokenModal) {
            deleteTokenModal.style.display = 'none';
        }
        currentDeleteTokenId = null;
    });

    cancelDeleteToken?.addEventListener('click', function() {
        if (deleteTokenModal) {
            deleteTokenModal.style.display = 'none';
        }
        currentDeleteTokenId = null;
    });

    confirmDeleteToken?.addEventListener('click', async function() {
        if (currentDeleteTokenId) {
            await deleteToken(currentDeleteTokenId);
        }
    });

    // Close delete modal when clicking outside
    deleteTokenModal?.addEventListener('click', function(e) {
        if (e.target === deleteTokenModal) {
            deleteTokenModal.style.display = 'none';
            currentDeleteTokenId = null;
        }
    });

    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (tokensModal && tokensModal.style.display === 'block') {
                tokensModal.style.display = 'none';
                hideTokenGenerated();
            }
            if (deleteTokenModal && deleteTokenModal.style.display === 'block') {
                deleteTokenModal.style.display = 'none';
                currentDeleteTokenId = null;
            }
        }
    });
}

async function loadTokens(): Promise<void> {
    try {
        const response = await fetch('/api/tokens/list', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: TokenListResponse = await response.json();
        displayTokens(data.tokens);
    } catch (error) {
        console.error('Error loading tokens:', error);
        showError('Failed to load tokens. Please try again.');
    }
}

function displayTokens(tokens: Token[]): void {
    const noTokensMessage = document.getElementById('no-tokens-message');
    const tokensTable = document.getElementById('tokens-table');
    const tokensTbody = document.getElementById('tokens-tbody');

    if (!noTokensMessage || !tokensTable || !tokensTbody) return;

    if (tokens.length === 0) {
        noTokensMessage.style.display = 'block';
        tokensTable.style.display = 'none';
    } else {
        noTokensMessage.style.display = 'none';
        tokensTable.style.display = 'block';

        tokensTbody.innerHTML = '';
        tokens.forEach(token => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>****${token.last_4_digits}</td>
                <td>${formatDate(token.created_at)}</td>
                <td>
                    <button class="btn btn-danger btn-sm delete-token-btn" data-token-id="${token.token_id}" data-last4="${token.last_4_digits}">
                        Delete
                    </button>
                </td>
            `;
            tokensTbody.appendChild(row);
        });

        // Add event listeners to delete buttons
        const deleteButtons = tokensTbody.querySelectorAll('.delete-token-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tokenId = (this as HTMLElement).getAttribute('data-token-id');
                const last4 = (this as HTMLElement).getAttribute('data-last4');
                if (tokenId && last4) {
                    showDeleteTokenModal(tokenId, last4);
                }
            });
        });
    }
}

async function generateToken(): Promise<void> {
    const generateBtn = document.getElementById('generate-token-btn') as HTMLButtonElement;
    if (!generateBtn) return;

    try {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        const response = await fetch('/api/tokens/generate', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: TokenResponse = await response.json();
        showTokenGenerated(data.token);
        await loadTokens(); // Refresh the tokens list
    } catch (error) {
        console.error('Error generating token:', error);
        showError('Failed to generate token. Please try again.');
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate New Token';
    }
}

function showTokenGenerated(token: string): void {
    const tokenGenerated = document.getElementById('token-generated');
    const tokenInput = document.getElementById('new-token-value') as HTMLInputElement;

    if (tokenGenerated && tokenInput) {
        tokenInput.value = token;
        tokenGenerated.style.display = 'block';
        
        // Auto-select the token for easy copying
        setTimeout(() => {
            tokenInput.select();
        }, 100);
    }
}

function hideTokenGenerated(): void {
    const tokenGenerated = document.getElementById('token-generated');
    const tokenInput = document.getElementById('new-token-value') as HTMLInputElement;

    if (tokenGenerated) {
        tokenGenerated.style.display = 'none';
    }
    if (tokenInput) {
        tokenInput.value = '';
    }
}

function showDeleteTokenModal(tokenId: string, last4: string): void {
    const deleteTokenModal = document.getElementById('delete-token-modal');
    const deleteTokenLast4 = document.getElementById('delete-token-last4');

    if (deleteTokenModal && deleteTokenLast4) {
        currentDeleteTokenId = tokenId;
        deleteTokenLast4.textContent = last4;
        deleteTokenModal.style.display = 'block';
    }
}

async function deleteToken(tokenId: string): Promise<void> {
    const confirmBtn = document.getElementById('confirm-delete-token') as HTMLButtonElement;
    if (!confirmBtn) return;

    try {
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Deleting...';

        const response = await fetch(`/api/tokens/${tokenId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        // Close modal and refresh tokens
        const deleteTokenModal = document.getElementById('delete-token-modal');
        if (deleteTokenModal) {
            deleteTokenModal.style.display = 'none';
        }
        currentDeleteTokenId = null;

        await loadTokens(); // Refresh the tokens list
        showSuccess('Token deleted successfully.');
    } catch (error) {
        console.error('Error deleting token:', error);
        showError('Failed to delete token. Please try again.');
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Delete Token';
    }
}

function formatDate(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showError(message: string): void {
    // You can implement a proper notification system here
    // For now, just use alert
    alert('Error: ' + message);
}

function showSuccess(message: string): void {
    // You can implement a proper notification system here
    // For now, just use alert
    alert(message);
}