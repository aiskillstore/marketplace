const fs = require('fs');
const cheerio = require('cheerio');
const TurndownService = require('turndown');
const { resolve } = require('path');

const readStdin = () => {
    return new Promise((resolve, reject) => {
        let data = '';
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', chunk => data += chunk);
        process.stdin.on('end', () => resolve(data));
        process.stdin.on('error', error => reject(error));
    });
};
(async () => {
    try {
        const html = await readStdin();
        if (!html) {
            console.error('No input provided via stdin');
            process.exit(1);
        }
        const $ = cheerio.load(html);
        const noiseSelectors = [
            'script', 'style', 'noscript', 'iframe', 'svg',
            'nav', 'footer', 'header',
            '.ad', '.ads', '.advertisement',
            '#sidebar', '.sidebar',
            '.comment', '.comments',
            '[role="alert"]', '[role="banner"]', '[role="navigation"]'
        ];
        $(noiseSelectors.join(',')).remove();

        const turndownService = new TurndownService({
            headingStyle: 'atx',
            codeBlockStyle: 'fenced'
        });

        let contentHtml = $('article').html() || $('main').html() || $('body').html();
        const markdown = turndownService.turndown(contentHtml || '');

        console.log(markdown);

    } catch (error) {
        console.error('Error cleaning HTML:', error.message);
        process.exit(1);
    }
})();