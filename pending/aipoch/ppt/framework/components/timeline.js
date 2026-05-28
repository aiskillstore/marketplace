/**
 * PPT Framework - 时间线组件
 * 
 * 展示阶段、进度、演进路径，支持依次激活动画
 */

const timeline = {
    meta: {
        name: 'timeline',
        description: '时间线',
        defaultAnimation: { preset: 'fadeIn', duration: 500, stagger: 100 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="timeline ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${data.style || ''}">
                ${data.items.map((item, idx) => {
                    const delay = anim.stagger * idx;
                    const itemStyle = delay ? `--anim-delay: ${delay}ms` : '';
                    return `
                    <div class="timeline-item" data-active-step="${item.activeStep}" style="${itemStyle}">
                        <div class="timeline-badge${item.badgeCurrent ? ' current' : ''}">${item.badge}</div>
                        <div class="timeline-icon claude-icon${item.iconFilled ? ' filled' : ''}">${item.icon}</div>
                        <div class="timeline-title">${item.title}</div>
                        <div class="timeline-desc">${item.desc}</div>
                        <div class="timeline-case">${item.case}</div>
                    </div>`;
                }).join('')}
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerTimeline() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('timeline', timeline);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { timeline, registerTimeline };
} else {
    window.TimelineComponent = { timeline, registerTimeline };
}
