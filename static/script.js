// Simple Kata Platform JavaScript

class KataPlatform {
    constructor() {
        this.currentKata = null;
        this.init();
    }

    init() {
        // Bind event listeners
        document.getElementById('back-btn').addEventListener('click', () => this.showKataList());
        document.getElementById('submit-btn').addEventListener('click', () => this.submitSolution());
        document.getElementById('reset-btn').addEventListener('click', () => this.resetCode());
        
        // Load katas on page load
        this.loadKatas();
    }

    async loadKatas() {
        try {
            const response = await fetch('/katas');
            const katas = await response.json();
            this.renderKataList(katas);
        } catch (error) {
            console.error('Failed to load katas:', error);
            document.getElementById('katas-container').innerHTML = 
                '<div class="error">Failed to load katas. Please try again.</div>';
        }
    }

    renderKataList(katas) {
        const container = document.getElementById('katas-container');
        
        if (katas.length === 0) {
            container.innerHTML = '<div class="no-katas">No katas available</div>';
            return;
        }

        const html = katas.map(kata => `
            <div class="kata-card" onclick="app.selectKata('${kata.id}')">
                <h3>${kata.title}</h3>
                <p>Click to start solving this kata</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async selectKata(kataId) {
        try {
            const response = await fetch(`/katas/${kataId}`);
            if (!response.ok) {
                throw new Error('Kata not found');
            }
            
            const kata = await response.json();
            this.currentKata = kata;
            this.showKataDetail(kata);
        } catch (error) {
            console.error('Failed to load kata:', error);
            alert('Failed to load kata. Please try again.');
        }
    }

    showKataDetail(kata) {
        // Hide kata list, show detail
        document.getElementById('kata-list').style.display = 'none';
        document.getElementById('kata-detail').style.display = 'block';
        
        // Populate kata information
        document.getElementById('kata-title').textContent = kata.title;
        document.getElementById('kata-description').textContent = kata.description;
        document.getElementById('code-editor').value = kata.starter_code;
        
        // Hide any previous results
        document.getElementById('result').style.display = 'none';
    }

    showKataList() {
        document.getElementById('kata-detail').style.display = 'none';
        document.getElementById('kata-list').style.display = 'block';
        this.currentKata = null;
    }

    async submitSolution() {
        if (!this.currentKata) {
            alert('No kata selected');
            return;
        }

        const code = document.getElementById('code-editor').value.trim();
        if (!code) {
            alert('Please write some code before submitting');
            return;
        }

        const submitBtn = document.getElementById('submit-btn');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Running...';

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    kata_id: this.currentKata.id,
                    code: code
                })
            });

            const result = await response.json();
            this.showResult(result);

        } catch (error) {
            console.error('Submission failed:', error);
            this.showResult({
                status: 'ERROR',
                message: 'Failed to submit code. Please try again.'
            });
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    showResult(result) {
        const resultDiv = document.getElementById('result');
        
        // Remove previous result classes
        resultDiv.classList.remove('pass', 'fail', 'error');
        
        // Add appropriate class and content
        const statusClass = result.status.toLowerCase();
        resultDiv.classList.add(statusClass);
        
        let icon = '';
        switch(result.status) {
            case 'PASS':
                icon = '✅';
                break;
            case 'FAIL':
                icon = '❌';
                break;
            case 'ERROR':
                icon = '⚠️';
                break;
        }
        
        resultDiv.innerHTML = `
            <div><strong>${icon} ${result.status}</strong></div>
            <div>${result.message}</div>
        `;
        
        resultDiv.style.display = 'block';
        
        // Scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    resetCode() {
        if (this.currentKata && confirm('Are you sure you want to reset your code?')) {
            document.getElementById('code-editor').value = this.currentKata.starter_code;
            document.getElementById('result').style.display = 'none';
        }
    }
}

// Initialize the application when page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new KataPlatform();
});