/**
 * PPT Framework - 渲染引擎和状态管理
 * 
 * 负责幻灯片渲染、状态管理、UI 更新
 */

const Engine = {
    // 设计尺寸
    DESIGN_WIDTH: 1280,
    DESIGN_HEIGHT: 720,

    // 状态
    state: {
        currentSlide: 0,
        totalSlides: 0,
        currentStep: 0,
        slideSteps: [],
        mode: 'presentation',  // presentation | help | blank | overview
        blankColor: null,
        jumpBuffer: '',
        jumpTimeout: null,
        overviewSelected: 0
    },

    // DOM 元素缓存
    elements: {},

    // 幻灯片数据（从外部注入）
    slidesData: [],

    /**
     * 初始化引擎
     * @param {Array} slides - 幻灯片数据数组
     */
    init(slides) {
        if (!slides || !Array.isArray(slides)) {
            console.error('Engine: slides data must be an array');
            return;
        }
        
        this.slidesData = slides;
        this.state.totalSlides = slides.length;
        
        this.renderAllSlides();
        this.cacheElements();
        this.calculateSlideSteps();
        this.createProgressDots();
        this.createStepIndicators();
        this.createOverviewItems();
        this.updateUI();
        
        // 更新跳转指示器
        if (this.elements.jumpTotal) {
            this.elements.jumpTotal.textContent = `/ ${this.state.totalSlides}`;
        }
        
        // 初始缩放
        this.updateScale();
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => this.updateScale());
        
        console.log('Engine: Initialized with', this.state.totalSlides, 'slides');
    },

    /**
     * 缓存 DOM 元素
     */
    cacheElements() {
        this.elements = {
            presentation: document.getElementById('presentation'),
            slidesContainer: document.getElementById('slides-container'),
            progressDots: document.getElementById('progress-dots'),
            pageNumber: document.getElementById('page-number'),
            navHint: document.getElementById('nav-hint'),
            fullscreenBtn: document.getElementById('fullscreen-btn'),
            helpOverlay: document.getElementById('help-overlay'),
            helpPanel: document.getElementById('help-panel'),
            helpClose: document.getElementById('help-close'),
            blankOverlay: document.getElementById('blank-overlay'),
            jumpIndicator: document.getElementById('jump-indicator'),
            jumpNumber: document.getElementById('jump-number-display'),
            jumpTotal: document.getElementById('jump-total'),
            overviewContainer: document.getElementById('overview-container'),
            overviewGrid: document.getElementById('overview-grid'),
            toast: document.getElementById('toast')
        };
    },

    /**
     * 渲染所有幻灯片
     */
    renderAllSlides() {
        const container = document.getElementById('slides-container');
        if (!container) {
            console.error('Engine: slides-container not found');
            return;
        }
        container.innerHTML = this.slidesData.map((slide, idx) => this.renderSlide(slide, idx)).join('');
    },

    /**
     * 渲染单个幻灯片
     * @param {Object} slideData - 幻灯片数据
     * @param {number} index - 幻灯片索引
     * @returns {string} HTML 字符串
     */
    renderSlide(slideData, index) {
        const slideId = `slide-${index + 1}`;
        
        // 计算该页最大步骤数
        let maxStep = 0;
        slideData.elements.forEach(el => {
            if (el.step > maxStep) maxStep = el.step;
            if (el.type === 'timeline' && el.items) {
                el.items.forEach(item => {
                    if (item.activeStep > maxStep) maxStep = item.activeStep;
                });
            }
            if (el.type === 'valueCards' && el.items) {
                el.items.forEach(item => {
                    if (item.activeStep > maxStep) maxStep = item.activeStep;
                });
            }
            if (el.revealStep && el.revealStep > maxStep) maxStep = el.revealStep;
        });

        // 渲染元素
        const elementsHtml = slideData.elements.map(el => {
            const renderer = Registry.getComponent(el.type);
            return renderer ? renderer(el, slideData) : '';
        }).join('');

        // 渲染头部组件
        const badgeRenderer = Registry.getComponent('badge');
        const titleRenderer = Registry.getComponent('title');
        const subtitleRenderer = Registry.getComponent('subtitle');
        const authorRenderer = Registry.getComponent('author');
        const clickHintRenderer = Registry.getComponent('clickHint');

        return `
            <div class="slide${index === 0 ? ' active' : ''}" id="${slideId}" data-steps="${maxStep + 1}" data-mode="hero">
                <div class="slide-content">
                    <div class="slide-spacer"></div>
                    <div class="slide-header-group">
                        ${badgeRenderer ? badgeRenderer(slideData.badge) : ''}
                        ${titleRenderer ? titleRenderer(slideData.title) : ''}
                        ${slideData.subtitle && subtitleRenderer ? subtitleRenderer(slideData.subtitle) : ''}
                        ${slideData.author && authorRenderer ? authorRenderer(slideData.author) : ''}
                    </div>
                    <div class="slide-content-wrapper">
                        ${elementsHtml}
                        ${slideData.clickHint && clickHintRenderer ? clickHintRenderer(slideData.clickHint) : ''}
                    </div>
                    <div class="slide-spacer"></div>
                </div>
                <div class="step-indicator" id="step-indicator-${index + 1}"></div>
            </div>`;
    },

    /**
     * 计算每页步骤数
     */
    calculateSlideSteps() {
        this.state.slideSteps = this.slidesData.map((slide, idx) => {
            const slideEl = document.getElementById(`slide-${idx + 1}`);
            return slideEl ? parseInt(slideEl.dataset.steps) || 1 : 1;
        });
    },

    /**
     * 更新缩放
     */
    updateScale() {
        const container = this.elements.presentation;
        if (!container) return;
        
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        
        const scaleX = containerWidth / this.DESIGN_WIDTH;
        const scaleY = containerHeight / this.DESIGN_HEIGHT;
        const scale = Math.min(scaleX, scaleY);
        
        const offsetX = (containerWidth - this.DESIGN_WIDTH * scale) / 2;
        const offsetY = (containerHeight - this.DESIGN_HEIGHT * scale) / 2;
        
        document.querySelectorAll('.slide').forEach(slide => {
            slide.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
        });
    },

    /**
     * 创建进度点
     */
    createProgressDots() {
        if (!this.elements.progressDots) return;
        
        this.elements.progressDots.innerHTML = '';
        for (let i = 0; i < this.state.totalSlides; i++) {
            const dot = document.createElement('div');
            dot.className = 'progress-dot';
            dot.addEventListener('click', (e) => {
                e.stopPropagation();
                this.goToSlide(i);
            });
            this.elements.progressDots.appendChild(dot);
        }
    },

    /**
     * 创建步骤指示器
     */
    createStepIndicators() {
        for (let i = 0; i < this.state.totalSlides; i++) {
            const container = document.getElementById(`step-indicator-${i + 1}`);
            if (container) {
                container.innerHTML = '';
                const steps = this.state.slideSteps[i];
                for (let j = 0; j < steps; j++) {
                    const dot = document.createElement('div');
                    dot.className = 'step-dot';
                    container.appendChild(dot);
                }
            }
        }
    },

    /**
     * 创建概览项
     */
    createOverviewItems() {
        if (!this.elements.overviewGrid) return;
        
        this.elements.overviewGrid.innerHTML = '';
        const slides = document.querySelectorAll('.slide');
        slides.forEach((slide, idx) => {
            const item = document.createElement('div');
            item.className = 'overview-item';
            item.dataset.index = idx;
            
            const number = document.createElement('div');
            number.className = 'overview-item-number';
            number.textContent = idx + 1;
            item.appendChild(number);
            
            const preview = slide.cloneNode(true);
            preview.className = 'overview-item-preview';
            preview.style.width = '400%';
            preview.style.height = '400%';
            preview.style.opacity = '1';
            preview.style.visibility = 'visible';
            item.appendChild(preview);
            
            item.addEventListener('click', () => {
                this.goToSlide(idx);
                Navigation.closeOverview();
            });
            this.elements.overviewGrid.appendChild(item);
        });
    },

    /**
     * 更新 UI
     */
    updateUI() {
        // 更新幻灯片激活状态
        document.querySelectorAll('.slide').forEach((slide, idx) => {
            slide.classList.toggle('active', idx === this.state.currentSlide);
        });
        
        // 更新进度点
        document.querySelectorAll('.progress-dot').forEach((dot, idx) => {
            dot.classList.toggle('active', idx === this.state.currentSlide);
        });
        
        // 更新页码
        if (this.elements.pageNumber) {
            this.elements.pageNumber.textContent = `${this.state.currentSlide + 1} / ${this.state.totalSlides}`;
        }
        
        // 更新概览选中状态
        document.querySelectorAll('.overview-item').forEach((item, idx) => {
            item.classList.toggle('current', idx === this.state.currentSlide);
        });
        
        this.updateStepAnimations();
    },

    /**
     * 更新步骤动画
     */
    updateStepAnimations() {
        const currentSlideEl = document.getElementById(`slide-${this.state.currentSlide + 1}`);
        if (!currentSlideEl) return;

        const currentStep = this.state.currentStep;

        // 更新 Hero/Content 模式
        currentSlideEl.dataset.mode = currentStep === 0 ? 'hero' : 'content';

        // 更新步骤指示器
        const stepIndicator = document.getElementById(`step-indicator-${this.state.currentSlide + 1}`);
        if (stepIndicator) {
            const dots = stepIndicator.querySelectorAll('.step-dot');
            dots.forEach((dot, idx) => {
                dot.classList.remove('active', 'passed');
                if (idx === currentStep) dot.classList.add('active');
                else if (idx < currentStep) dot.classList.add('passed');
            });
        }

        // 更新动画元素
        currentSlideEl.querySelectorAll('[data-step]').forEach(el => {
            const showStep = parseInt(el.dataset.step);
            const hideStep = el.dataset.hideStep ? parseInt(el.dataset.hideStep) : null;
            const struckStep = el.dataset.struckStep ? parseInt(el.dataset.struckStep) : null;

            if (hideStep !== null && currentStep >= hideStep) {
                el.classList.remove('visible');
                el.classList.add('fade-out');
            } else if (currentStep >= showStep) {
                el.classList.add('visible');
                el.classList.remove('fade-out');
            } else {
                el.classList.remove('visible', 'fade-out');
            }

            if (struckStep !== null) {
                el.classList.toggle('struck', currentStep >= struckStep);
            }
        });

        // 时间线项
        currentSlideEl.querySelectorAll('.timeline-item').forEach(el => {
            const activeStep = parseInt(el.dataset.activeStep);
            el.classList.remove('active', 'passed');
            if (currentStep >= activeStep) {
                el.classList.add(currentStep === activeStep ? 'active' : 'passed');
            }
        });

        // 价值卡片
        currentSlideEl.querySelectorAll('.value-card').forEach(el => {
            const activeStep = parseInt(el.dataset.activeStep);
            el.classList.toggle('active', currentStep >= activeStep);
        });
    },

    /**
     * 下一步
     */
    next() {
        if (this.state.mode !== 'presentation') return;
        
        const maxSteps = this.state.slideSteps[this.state.currentSlide];
        if (this.state.currentStep < maxSteps - 1) {
            this.state.currentStep++;
            this.updateStepAnimations();
        } else if (this.state.currentSlide < this.state.totalSlides - 1) {
            this.state.currentSlide++;
            this.state.currentStep = 0;
            this.updateUI();
        }
    },

    /**
     * 上一步
     */
    prev() {
        if (this.state.mode !== 'presentation') return;
        
        if (this.state.currentStep > 0) {
            this.state.currentStep--;
            this.updateStepAnimations();
        } else if (this.state.currentSlide > 0) {
            this.state.currentSlide--;
            this.state.currentStep = this.state.slideSteps[this.state.currentSlide] - 1;
            this.updateUI();
        }
    },

    /**
     * 跳转到指定幻灯片
     * @param {number} index - 幻灯片索引（从0开始）
     */
    goToSlide(index) {
        if (index < 0 || index >= this.state.totalSlides) {
            this.showToast(`页码范围: 1-${this.state.totalSlides}`, true);
            return;
        }
        this.state.currentSlide = index;
        this.state.currentStep = 0;
        this.updateUI();
    },

    /**
     * 显示 Toast 消息
     * @param {string} message - 消息内容
     * @param {boolean} isError - 是否为错误消息
     */
    showToast(message, isError = false) {
        if (!this.elements.toast) return;
        
        this.elements.toast.textContent = message;
        this.elements.toast.className = `toast active ${isError ? 'error' : ''}`;
        setTimeout(() => this.elements.toast.classList.remove('active'), 2000);
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Engine;
} else {
    window.Engine = Engine;
}
