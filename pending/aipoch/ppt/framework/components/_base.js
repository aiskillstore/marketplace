/**
 * PPT Framework - 基础组件
 * 
 * 包含通用的头部组件：badge, title, subtitle, clickHint
 */

// ========== 徽章组件 ==========
const badge = {
    meta: {
        name: 'badge',
        description: '顶部徽章',
        defaultAnimation: null  // 始终可见
    },
    
    render(data, step = 0) {
        return `
            <div class="slide-badge anim visible" data-step="${step}">
                <span class="claude-icon">${data.icon}</span>
                <span>${data.text}</span>
            </div>`;
    }
};

// ========== 标题组件 ==========
const title = {
    meta: {
        name: 'title',
        description: '幻灯片标题',
        defaultAnimation: null
    },
    
    render(data, step = 0) {
        return `
            <h1 class="slide-title anim visible" data-step="${step}">
                ${data.gradient ? `<span class="gradient-text">${data.text}</span>` : data.text}
            </h1>`;
    }
};

// ========== 副标题组件 ==========
const subtitle = {
    meta: {
        name: 'subtitle',
        description: '幻灯片副标题',
        defaultAnimation: null
    },
    
    render(text, step = 0) {
        return `
            <p class="slide-subtitle anim visible" data-step="${step}">${text}</p>`;
    }
};

// ========== 作者信息组件 ==========
const author = {
    meta: {
        name: 'author',
        description: '作者署名',
        defaultAnimation: null
    },
    
    render(text, hideStep = 1) {
        return `
            <p class="slide-author anim visible" data-step="0" data-hide-step="${hideStep}">${text}</p>`;
    }
};

// ========== 点击提示组件 ==========
const clickHint = {
    meta: {
        name: 'clickHint',
        description: '底部点击提示',
        defaultAnimation: null
    },
    
    render(text, hideStep = 1) {
        return `
            <div class="click-hint anim visible" data-step="0" data-hide-step="${hideStep}">
                <span>${text}</span>
                <span>↓</span>
            </div>`;
    }
};

/**
 * 注册基础组件
 */
function registerBaseComponents() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('badge', badge);
        Registry.registerComponent('title', title);
        Registry.registerComponent('subtitle', subtitle);
        Registry.registerComponent('author', author);
        Registry.registerComponent('clickHint', clickHint);
        console.log('BaseComponents: Registered 5 base components');
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { badge, title, subtitle, author, clickHint, registerBaseComponents };
} else {
    window.BaseComponents = { badge, title, subtitle, author, clickHint, registerBaseComponents };
}
