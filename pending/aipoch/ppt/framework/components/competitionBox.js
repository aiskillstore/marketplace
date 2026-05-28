/**
 * PPT Framework - 竞争框组件
 * 
 * 展示竞争分析、关键要素
 */

const competitionBox = {
    meta: {
        name: 'competitionBox',
        description: '竞争分析框',
        defaultAnimation: { preset: 'slideUp', duration: 500 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        return `
            <div class="competition-box ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
                <h4><span class="icon-dot">●</span> ${data.title}</h4>
                <div class="competition-list-box">
                    ${data.items.map(item => `<div class="competition-item-box">${item}</div>`).join('')}
                </div>
                <p class="competition-conclusion">${data.conclusion}</p>
            </div>`;
    }
};

/**
 * 注册组件
 */
function registerCompetitionBox() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('competitionBox', competitionBox);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { competitionBox, registerCompetitionBox };
} else {
    window.CompetitionBoxComponent = { competitionBox, registerCompetitionBox };
}
