/**
 * PPT Framework - 图片组件
 * 
 * 支持单图、带说明图片、图片网格展示
 * 
 * 使用示例：
 * 
 * 1. 单图展示：
 *    { step: 1, type: "image", src: "path/to/image.png", alt: "描述" }
 * 
 * 2. 带标题和说明：
 *    { step: 1, type: "image", src: "...", title: "标题", caption: "说明文字" }
 * 
 * 3. 图片网格（多图）：
 *    { step: 1, type: "image", layout: "grid", images: [
 *        { src: "1.png", title: "图1" },
 *        { src: "2.png", title: "图2" }
 *    ]}
 * 
 * 4. 图文并排：
 *    { step: 1, type: "image", layout: "side", src: "...", content: "右侧文字内容" }
 */

// 单图展示
function renderImageSingle(data, anim, combinedStyle, hideStepAttr) {
    const titleHtml = data.title ? `<div class="image-title">${data.title}</div>` : '';
    const captionHtml = data.caption ? `<div class="image-caption">${data.caption}</div>` : '';
    const imgStyle = data.imgStyle || '';
    const rounded = data.rounded !== false ? 'rounded' : '';
    const shadow = data.shadow !== false ? 'shadow' : '';
    
    return `
        <div class="image-container ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
            ${titleHtml}
            <img src="${data.src}" alt="${data.alt || data.title || ''}" class="image-single ${rounded} ${shadow}" style="${imgStyle}">
            ${captionHtml}
        </div>`;
}

// 图片网格
function renderImageGrid(data, anim, combinedStyle, hideStepAttr) {
    const columns = data.columns || Math.min(data.images.length, 3);
    const gridStyle = `grid-template-columns: repeat(${columns}, 1fr);`;
    
    return `
        <div class="image-grid ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${gridStyle} ${combinedStyle}">
            ${data.images.map((img, idx) => {
                const delay = (anim.stagger || 100) * idx;
                const itemStyle = delay ? `--anim-delay: ${delay}ms` : '';
                const hasOverlay = img.title || img.caption;
                return `
                <div class="image-grid-item" style="${itemStyle}">
                    <img src="${img.src}" alt="${img.alt || img.title || ''}" class="image-grid-img">
                    ${hasOverlay ? `<div class="image-grid-overlay">
                        ${img.title ? `<div class="image-grid-title">${img.title}</div>` : ''}
                        ${img.caption ? `<div class="image-grid-caption">${img.caption}</div>` : ''}
                    </div>` : ''}
                </div>`;
            }).join('')}
        </div>`;
}

// 图文并排
function renderImageSide(data, anim, combinedStyle, hideStepAttr) {
    const imgPosition = data.imgPosition || 'left';
    const imgWidth = data.imgWidth || '50%';
    
    const imgHtml = `
        <div class="image-side-img" style="width: ${imgWidth};">
            <img src="${data.src}" alt="${data.alt || ''}" class="rounded shadow">
            ${data.imgCaption ? `<div class="image-caption">${data.imgCaption}</div>` : ''}
        </div>`;
    
    const contentHtml = `
        <div class="image-side-content">
            ${data.title ? `<h4 class="image-side-title">${data.title}</h4>` : ''}
            <div class="image-side-text">${data.content || ''}</div>
        </div>`;
    
    const orderClass = imgPosition === 'right' ? 'img-right' : 'img-left';
    
    return `
        <div class="image-side ${orderClass} ${anim.className}" data-step="${data.step}"${hideStepAttr} style="${combinedStyle}">
            ${imgPosition === 'left' ? imgHtml + contentHtml : contentHtml + imgHtml}
        </div>`;
}

const image = {
    meta: {
        name: 'image',
        description: '图片展示',
        defaultAnimation: { preset: 'fadeIn', duration: 500 }
    },

    render(data, slideData = {}) {
        const anim = Registry.resolveAnimation(data, slideData);
        const combinedStyle = [anim.style, data.style].filter(Boolean).join('; ');
        const hideStepAttr = data.hideStep ? ` data-hide-step="${data.hideStep}"` : '';
        
        // 根据 layout 类型选择渲染方式
        const layout = data.layout || 'single';
        
        switch (layout) {
            case 'grid':
                return renderImageGrid(data, anim, combinedStyle, hideStepAttr);
            case 'side':
                return renderImageSide(data, anim, combinedStyle, hideStepAttr);
            default:
                return renderImageSingle(data, anim, combinedStyle, hideStepAttr);
        }
    }
};

/**
 * 注册组件
 */
function registerImage() {
    if (typeof Registry !== 'undefined') {
        Registry.registerComponent('image', image);
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { image, registerImage };
} else {
    window.ImageComponent = { image, registerImage };
}
