import Exa from 'exa-js';
import 'dotenv/config';

async function search(query) {
    const apiKey = process.env.EXA_API_KEY;
    if (!apiKey) {
        console.error("错误: EXA_API_KEY 环境变量未设置。");
        process.exit(1);
    }
    const exa = new Exa(apiKey);
    try {
        const results = await exa.search(query, {
            numResults: 5,
            type: 'neural'
        });
        console.log(JSON.stringify(results.results, null, 2));
    } catch (error) {
        console.error("Exa 搜索失败:", error.message);
        process.exit(1);
    }
}

const query = process.argv.slice(2).join(' ');
if (!query) {
    console.error("用法: node exa.js <query>");
    process.exit(1);
}

search(query);
