/**
 * PPT Framework - 导航和交互控制
 * 
 * 处理键盘快捷键、鼠标点击、触摸手势、全屏、帮助面板等
 */

const Navigation = {
    // 触摸起始位置
    touchStartX: 0,

    /**
     * 初始化导航
     */
    init() {
        this.bindKeyboardEvents();
        this.bindMouseEvents();
        this.bindTouchEvents();
        this.bindFullscreenEvents();
        this.bindUIEvents();
        
        console.log('Navigation: Initialized');
    },

    /**
     * 绑定键盘事件
     */
    bindKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            // ESC 关闭所有模式
            if (e.key === 'Escape') {
                e.preventDefault();
                this.closeAllModes();
                return;
            }
            
            // 帮助模式下不响应其他按键
            if (Engine.state.mode === 'help') return;
            
            // 黑屏/白屏模式下任意键关闭
            if (Engine.state.mode === 'blank') {
                e.preventDefault();
                this.closeBlank();
                return;
            }
            
            // 概览模式
            if (Engine.state.mode === 'overview') {
                this.handleOverviewKeydown(e);
                return;
            }
            
            // 演示模式
            this.handlePresentationKeydown(e);
        });
    },

    /**
     * 处理概览模式按键
     * @param {KeyboardEvent} e
     */
    handleOverviewKeydown(e) {
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                this.navigateOverview('left');
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.navigateOverview('right');
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateOverview('up');
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.navigateOverview('down');
                break;
            case 'Enter':
                e.preventDefault();
                this.selectOverviewItem();
                break;
            case 'g':
            case 'G':
                e.preventDefault();
                this.closeOverview();
                break;
        }
    },

    /**
     * 处理演示模式按键
     * @param {KeyboardEvent} e
     */
    handlePresentationKeydown(e) {
        switch (e.key) {
            case 'ArrowRight':
            case ' ':
                e.preventDefault();
                Engine.state.jumpBuffer ? this.executeJump() : Engine.next();
                break;
            case 'ArrowLeft':
            case 'Backspace':
                e.preventDefault();
                Engine.prev();
                break;
            case 'Home':
                e.preventDefault();
                Engine.goToSlide(0);
                break;
            case 'End':
                e.preventDefault();
                Engine.goToSlide(Engine.state.totalSlides - 1);
                break;
            case 'Enter':
                e.preventDefault();
                Engine.state.jumpBuffer ? this.executeJump() : Engine.next();
                break;
            case 'f':
            case 'F':
            case 'F11':
                e.preventDefault();
                this.toggleFullscreen();
                break;
            case '?':
            case 'h':
            case 'H':
                e.preventDefault();
                this.toggleHelp();
                break;
            case 'g':
            case 'G':
                e.preventDefault();
                this.toggleOverview();
                break;
            case 'b':
            case 'B':
                e.preventDefault();
                this.toggleBlank('black');
                break;
            case 'w':
            case 'W':
                e.preventDefault();
                this.toggleBlank('white');
                break;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                e.preventDefault();
                this.handleNumberInput(e.key);
                break;
        }
    },

    /**
     * 绑定鼠标事件
     */
    bindMouseEvents() {
        const presentation = Engine.elements.presentation;
        if (!presentation) return;
        
        presentation.addEventListener('click', (e) => {
            if (Engine.state.mode !== 'presentation') return;
            if (e.target.closest('.progress-dots, .fullscreen-btn')) return;
            Engine.next();
        });
    },

    /**
     * 绑定触摸事件
     */
    bindTouchEvents() {
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', (e) => {
            if (Engine.state.mode !== 'presentation') return;
            
            const diff = this.touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                diff > 0 ? Engine.next() : Engine.prev();
            }
        });
    },

    /**
     * 绑定全屏事件
     */
    bindFullscreenEvents() {
        document.addEventListener('fullscreenchange', () => {
            document.body.classList.toggle('fullscreen-mode', !!document.fullscreenElement);
        });
    },

    /**
     * 绑定 UI 事件
     */
    bindUIEvents() {
        const { fullscreenBtn, helpClose, helpOverlay, blankOverlay } = Engine.elements;
        
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFullscreen();
            });
        }
        
        if (helpClose) {
            helpClose.addEventListener('click', () => this.closeHelp());
        }
        
        if (helpOverlay) {
            helpOverlay.addEventListener('click', () => this.closeHelp());
        }
        
        if (blankOverlay) {
            blankOverlay.addEventListener('click', () => this.closeBlank());
        }
    },

    // ========== 全屏 ==========
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {
                Engine.showToast('无法进入全屏模式', true);
            });
        } else {
            document.exitFullscreen();
        }
    },

    // ========== 帮助面板 ==========
    
    openHelp() {
        Engine.state.mode = 'help';
        Engine.elements.helpOverlay?.classList.add('active');
        Engine.elements.helpPanel?.classList.add('active');
    },
    
    closeHelp() {
        Engine.state.mode = 'presentation';
        Engine.elements.helpOverlay?.classList.remove('active');
        Engine.elements.helpPanel?.classList.remove('active');
    },
    
    toggleHelp() {
        Engine.state.mode === 'help' ? this.closeHelp() : this.openHelp();
    },

    // ========== 黑屏/白屏 ==========
    
    toggleBlank(color) {
        if (Engine.state.mode === 'blank' && Engine.state.blankColor === color) {
            this.closeBlank();
        } else {
            this.openBlank(color);
        }
    },
    
    openBlank(color) {
        Engine.state.mode = 'blank';
        Engine.state.blankColor = color;
        if (Engine.elements.blankOverlay) {
            Engine.elements.blankOverlay.className = `blank-overlay active ${color}`;
        }
    },
    
    closeBlank() {
        Engine.state.mode = 'presentation';
        Engine.state.blankColor = null;
        if (Engine.elements.blankOverlay) {
            Engine.elements.blankOverlay.className = 'blank-overlay';
        }
    },

    // ========== 概览模式 ==========
    
    openOverview() {
        Engine.state.mode = 'overview';
        Engine.state.overviewSelected = Engine.state.currentSlide;
        this.updateOverviewSelection();
        Engine.elements.overviewContainer?.classList.add('active');
    },
    
    closeOverview() {
        Engine.state.mode = 'presentation';
        Engine.elements.overviewContainer?.classList.remove('active');
    },
    
    toggleOverview() {
        Engine.state.mode === 'overview' ? this.closeOverview() : this.openOverview();
    },
    
    updateOverviewSelection() {
        document.querySelectorAll('.overview-item').forEach((item, idx) => {
            item.classList.toggle('selected', idx === Engine.state.overviewSelected);
        });
    },
    
    navigateOverview(direction) {
        const cols = Math.floor((Engine.elements.overviewGrid?.offsetWidth || 600) / 300) || 2;
        
        switch (direction) {
            case 'left':
                if (Engine.state.overviewSelected > 0) Engine.state.overviewSelected--;
                break;
            case 'right':
                if (Engine.state.overviewSelected < Engine.state.totalSlides - 1) Engine.state.overviewSelected++;
                break;
            case 'up':
                if (Engine.state.overviewSelected >= cols) Engine.state.overviewSelected -= cols;
                break;
            case 'down':
                if (Engine.state.overviewSelected + cols < Engine.state.totalSlides) Engine.state.overviewSelected += cols;
                break;
        }
        
        this.updateOverviewSelection();
    },
    
    selectOverviewItem() {
        Engine.goToSlide(Engine.state.overviewSelected);
        this.closeOverview();
    },

    // ========== 页码跳转 ==========
    
    handleNumberInput(num) {
        Engine.state.jumpBuffer += num;
        
        if (Engine.elements.jumpNumber) {
            Engine.elements.jumpNumber.textContent = Engine.state.jumpBuffer;
        }
        Engine.elements.jumpIndicator?.classList.add('active');
        
        clearTimeout(Engine.state.jumpTimeout);
        Engine.state.jumpTimeout = setTimeout(() => this.clearJumpBuffer(), 3000);
    },
    
    executeJump() {
        if (Engine.state.jumpBuffer) {
            Engine.goToSlide(parseInt(Engine.state.jumpBuffer) - 1);
            this.clearJumpBuffer();
        }
    },
    
    clearJumpBuffer() {
        Engine.state.jumpBuffer = '';
        Engine.elements.jumpIndicator?.classList.remove('active');
        clearTimeout(Engine.state.jumpTimeout);
    },

    // ========== 关闭所有模式 ==========
    
    closeAllModes() {
        if (Engine.state.mode === 'help') {
            this.closeHelp();
        } else if (Engine.state.mode === 'blank') {
            this.closeBlank();
        } else if (Engine.state.mode === 'overview') {
            this.closeOverview();
        }
        this.clearJumpBuffer();
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Navigation;
} else {
    window.Navigation = Navigation;
}
