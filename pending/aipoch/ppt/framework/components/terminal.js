/**
 * PPT Framework - 终端组件
 * 
 * 模拟终端界面，适合展示命令、公式、代码片段
 */

const terminal = {
    meta: {
        name: 'terminal',
        description: '终端代码块',
        defaultAnimation: { preset: 'scaleIn', duration: 500 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="terminal ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <div class="terminal-header">
                    <div class="terminal-dot red"></div>
                    <div class="terminal-dot yellow"></div>
                    <div class="terminal-dot green"></div>
                </div>
                <div class="terminal-body">
                    <div class="terminal-line">
                        ${data.content.map(item => {
                            switch(item.type) {
                                case 'prompt': return `<span class="terminal-prompt">${item.text}</span>`;
                                case 'highlight': return `<span class="terminal-highlight">${item.text}</span>`;
                                case 'success': return `<span class="terminal-success">${item.text}</span>`;
                                case 'cursor': return `<span class="terminal-cursor"></span>`;
                                default: return `<span>${item.text}</span>`;
                            }
                        }).join('')}
                    </div>
                </div>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerTerminal() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('terminal', terminal);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { terminal, registerTerminal };
} else {
    window.TerminalComponent = { terminal, registerTerminal };
}
