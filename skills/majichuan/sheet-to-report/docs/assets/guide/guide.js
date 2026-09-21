(() => {
  const status = document.getElementById('copy-status');
  let timer;
  function announce(message) {
    status.textContent = message;
    clearTimeout(timer);
    timer = setTimeout(() => { status.textContent = ''; }, 7000);
  }
  function selectText(element) {
    const range = document.createRange();
    range.selectNodeContents(element);
    const selection = window.getSelection();
    selection.removeAllRanges(); selection.addRange(range);
  }
  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const source = document.getElementById(button.dataset.copy);
      const text = source.innerText.trim();
      let copied = false;
      try { await navigator.clipboard.writeText(text); copied = true; } catch (_) {
        selectText(source);
        try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
        if (!copied) source.focus({preventScroll:true});
      }
      const destination = button.dataset.copyDestination;
      const success = destination === 'terminal' ? '已复制安装命令。请在电脑终端中执行。' : destination === 'claude' ? '已复制。请在 Claude Code 中依次执行这两条命令。' : '已复制。回到刚才的 AI 对话中粘贴并发送。';
      announce(copied ? success : '自动复制不可用，已选中文字；请用系统复制功能复制。');
    });
  });
  document.querySelectorAll('[data-expand]').forEach(link => link.addEventListener('click', () => {
    document.getElementById(link.dataset.expand).open = true;
  }));
  function revealHash() {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target.matches('details')) target.open = true;
  }
  addEventListener('hashchange', revealHash);
  revealHash();
  {
    const navLinks = [...document.querySelectorAll('.contents a')];
    let pending = false;
    function updateLocation() {
      pending = false;
      const threshold = document.querySelector('.topbar').getBoundingClientRect().bottom + 48;
      const current = navLinks.filter(a => document.getElementById(a.hash.slice(1)).getBoundingClientRect().top <= threshold).pop() || navLinks[0];
      navLinks.forEach(a => {
        if (a === current) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
    }
    function queueUpdate() {
      if (!pending) { pending = true; requestAnimationFrame(updateLocation); }
    }
    addEventListener('scroll', queueUpdate, {passive:true});
    addEventListener('resize', queueUpdate);
    document.querySelectorAll('details').forEach(el => el.addEventListener('toggle', queueUpdate));
    addEventListener('load', queueUpdate);
    updateLocation();
  }
})();
