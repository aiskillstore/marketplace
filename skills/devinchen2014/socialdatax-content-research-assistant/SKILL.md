---
name: "socialdatax-content-research-assistant"
description: "面向内容运营、品牌调研和创作者的跨平台社媒内容研究助手。适用于小红书、抖音、快手、Bilibili、知乎、Instagram、X / Twitter、YouTube、TikTok、微博、今日头条、好看视频和视频号的选题策划、竞品观察、趋势判断、评论洞察和创作者资料整理，也支持公众号文章链接详情、内容整理和互动统计，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "socialdatax-content-research-assistant"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📌","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 社媒内容研究助手

## 适用场景

面向内容运营、品牌调研和创作者的跨平台社媒内容研究助手。适用于小红书、抖音、快手、Bilibili、知乎、Instagram、X / Twitter、YouTube、TikTok、微博、今日头条、好看视频和视频号的选题策划、竞品观察、趋势判断、评论洞察和创作者资料整理，也支持公众号文章链接详情、内容整理和互动统计，来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、要观察的平台热榜、内容链接或内容 ID、账号关键词、达人名称或赛道方向、账号用户名、频道链接、账号主页、账号分享文本或平台账号 ID、互动对象 ID 或链接。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：榜单排名和热度信号、相关标题、作者或账号、链接或内容 ID、单条内容正文、作者、发布时间和互动指标、评论文本、回复线索和用户反馈主题、候选账号、昵称、平台账号 ID 和粉丝信号、账号资料、认证、粉丝或互动信号、近期内容列表、发布时间和互动信号、点赞或转发记录，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs detail --note-id "<note_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs comments --note-id "<note_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin detail --aweme-id "<aweme_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin comments --aweme-id "<aweme_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-info --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-posts --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-search --keyword "<creator_keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou detail --photo-id "<photo_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou comments --photo-id "<photo_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili search-videos --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili search-articles --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili detail --content-id "<content_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili comments --content-id "<content_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-videos --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-articles --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu hot-list --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu detail --content-url "<zhihu_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu comments --content-url "<zhihu_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram detail --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram comments --post-url "<instagram_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram user-info --username "<username>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram user-posts --username "<username>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x detail --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x comments --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-info --username "<username>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-posts --username "<username>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube detail --url "<youtube_video_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube comments --url "<youtube_video_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube channel-info --channel-url "<youtube_channel_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube user-posts --channel-url "<youtube_channel_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok detail --url "<tiktok_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok comments --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok user-info --tiktok-id "<tiktok_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok user-posts --tiktok-id "<tiktok_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo detail --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo comments --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao detail --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao comments --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat detail --encrypted-object-id "<encrypted_object_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat article --url "<mp_article_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat article-stats --url "<mp_article_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat comments --object-id "<object_id>" --object-nonce-id "<object_nonce_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat user-info --user-id "<v2_finder_user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat user-posts --user-id "<v2_finder_user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-info --douyin-id "<douyin_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo likers --url "<post_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo reposts --url "<post_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs search-suggestions --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-detail --sku-id "<sku_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-detail --url "<url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-reviews --sku-id "<sku_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-review-replies --review-id "<review_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs product-review-reply-replies --review-id "<review_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs topic-notes --url "<topic_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs topic-notes --page-id "<page_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin product-search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin product-detail --product-id "<product_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin product-detail --url "<url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat share-link --object-id "<object_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan user-search --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan search-suggestions --keyword "<keyword>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan hot-search --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan detail --video-id "<video_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan detail --url "<video_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan comments --video-id "<video_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan comments --url "<video_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan replies --video-id "<video_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan replies --url "<video_url>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan user-info --profile-url "<profile_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest haokan user-posts --profile-url "<profile_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-replies --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-replies --username "<username>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-replies --profile-url "<profile_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest xhs detail --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs comments --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin detail --url "<douyin_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin share-link --aweme-id "<aweme_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin share-link --url "<douyin_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin comments --url "<douyin_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-series --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-series --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs sub-comments --note-id "<note_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin replies --aweme-id "<aweme_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou detail --url "<kuaishou_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou comments --url "<kuaishou_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou replies --photo-id "<photo_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili detail --url "<bilibili_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili comments --url "<bilibili_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili replies --comment-object-id "<comment_object_id>" --comment-object-type "<comment_object_type_integer>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili reactions --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili reactions --url "<bilibili_opus_or_dynamic_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-videos --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-articles --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-dynamics --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest bilibili user-dynamics --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest zhihu replies --content-url "<zhihu_content_url_or_share_text>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram detail --post-url "<instagram_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram replies --post-id "<post_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest instagram user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x detail --post-url "<x_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x comments --post-url "<x_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x replies --post-id "<post_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-info --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-posts --user-id "<user_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest x user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest youtube replies --reply-token "<reply_token>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok comments --url "<tiktok_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok replies --post-id "<post_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest tiktok user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo detail --post-url "<weibo_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo comments --post-url "<weibo_post_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo likers --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo reposts --post-id "<post_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo user-info --profile-url "<profile_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo user-posts --profile-url "<profile_url>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo replies --post-id "<post_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao detail --url "<toutiao_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao comments --url "<toutiao_content_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao user-info --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao user-posts --profile-url "<profile_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest toutiao replies --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat detail --url "<wechat_work_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat comments --url "<wechat_video_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat replies --object-id "<object_id>" --object-nonce-id "<object_nonce_id>" --comment-id "<comment_id>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat user-info --url "<wechat_work_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat user-posts --url "<wechat_work_url_or_share_text>" --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs search --keyword "<keyword>" --since-days 7 --pages 2 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin search --keyword "<keyword>" --since-days 7 --pages 2 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou search --keyword "<keyword>" --since-days 7 --pages 2 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo search --keyword "<keyword>" --since-days 7 --pages 2 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat search --keyword "<keyword>" --since-days 7 --pages 2 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest xhs user-posts --user-id "<user_id>" --since-days 30 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest douyin user-posts --sec-user-id "<sec_user_id>" --since-days 30 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest kuaishou user-posts --user-id "<user_id>" --since-days 30 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest weibo user-posts --user-id "<user_id>" --since-days 30 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
npx -y socialdatax-skills@latest wechat user-posts --user-id "<v2_finder_user_id>" --since-days 30 --pretty --source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant
```

遇到热榜、内容链接、主页链接、评论分析、Bilibili 互动分析、微博点赞/转发分析、创作者资料、创作者内容列表或短剧合集这类任务时，直接调用对应平台的 `socialdatax-skills` 子命令，不要一律退回关键词搜索。

## 参数说明

热榜：
- 说明：用户要看当前小红书热榜时，使用 `xhs hot-search`，这个命令不需要 `--keyword`。
- 说明：用户要看当前抖音热榜时，使用 `douyin hot-search`，这个命令不需要 `--keyword`。
- 说明：用户要看当前快手热榜时，使用 `kuaishou hot-search`，这个命令不需要 `--keyword`。
- 说明：用户要看当前知乎热榜时，使用 `zhihu hot-list`，这个命令不需要 `--keyword`。
- 说明：用户要看当前微博热搜时，使用 `weibo hot-search`；用户要看当前今日头条热榜时，使用 `toutiao hot-search`；用户要看当前视频号热榜时，使用 `wechat hot-search`；这些命令都不需要 `--keyword`。

搜索：
- 说明：做关键词研究时，根据平台使用 `xhs search`、`douyin search`、`kuaishou search`、`bilibili search-videos` / `search-articles`、`zhihu search`、`instagram search`、`x search`、`youtube search`、`tiktok search`、`weibo search`、`toutiao search` 或 `wechat search`。
- 说明：做快手关键词研究时，使用 `kuaishou search --keyword <text>`。
- 说明：搜索翻页时，如果返回了 `next_page_token`，再使用 `--page-token <next_page_token>`；第一页不要传。继续翻页时只能原样使用同一链路返回的完整 token。
- 可选：`--since-days <1-365>`：仅适用于 XHS、抖音、快手、微博和视频号搜索；Bilibili 视频、知乎和 YouTube 搜索请改用对应发布时间筛选，不要传给 Bilibili 文章、Instagram、X / Twitter 或 TikTok 搜索。
- 说明：关键词研究筛选：不同平台支持的 `--sort-type`、`--note-type`、`--publish-time-range`、`--duration-range`、`--content-type`、`--video-type` 不完全相同，只使用对应 direct CLI 帮助里列出的参数。

详情 / 评论：
- 说明：做详情、评论、回复命令时，使用示例里的内容 ID 参数，或者用对应的 URL 入口，两种方式不要混用。
- 说明：已知抖音作品 aweme_id 时，用 `douyin share-link --aweme-id <aweme_id>` 生成分享链接；用户提供作品链接、短链或分享文案时，用 `douyin share-link --url <douyin_content_url_or_share_text>`。
- 说明：YouTube 评论回复使用返回的 `reply_token`，运行 `youtube replies --reply-token <reply_token>`；不要把 YouTube 回复写成 `--comment-id`。
- 说明：XHS 评论 `--sort-type <default|time_descending|like_count_descending>`：可选一级评论排序；不传就使用平台默认排序。
- 条件必填：`--comment-id <comment_id>`：仅在 CLI 示例使用评论 ID 的回复 / 子评论命令中必填；YouTube 回复改用返回的 `--reply-token <reply_token>`。

创作者 / 账号：
- 说明：做创作者资料、内容列表或合集列表命令时，使用示例里的账号 ID 参数，或者用对应的 profile-url 入口，两种方式不要混用。
- 说明：快手 `user-search` 支持用 `--pages <n>` 和 `--max-items <n>` 控制候选账号数量，但不支持 `--since-days`，因为它返回的是账号，不是作品。
- 可选：`--since-days <1-365>`：仅适用于 XHS、抖音、快手、微博和视频号创作者内容列表；不要传给 Bilibili、知乎、Instagram、X / Twitter、YouTube、TikTok 或抖音 `user-series`。

通用：
- 可选：`--page-token <next_page_token>`：用于各平台支持 token 翻页的搜索、评论、回复和创作者内容列表。翻页时要保持原始主题、内容对象、创作者搜索词或目标账号不变，并且必须原样传回完整 token，不能截断、改写、脱敏或用省略号替换中间部分。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-content-research-assistant`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

## 平台选择

- 小红书 / XHS / RedNote：适合笔记、评论、博主资料和博主笔记列表研究。
- 抖音、快手、微博、今日头条、视频号：适合热点、评论、创作者和近期内容研究。
- Bilibili、知乎：适合视频 / 图文 / 问答内容研究；公众号文章：适合文章链接详情和内容整理。
- Instagram、X / Twitter、YouTube、TikTok：适合跨平台社媒选题、竞品观察、评论洞察、账号和内容研究。
- 用户同时看多个平台时，先按平台分开证据，再比较共性和差异。

## 如何选入口

优先使用最贴近用户任务的 direct CLI 命令，不要把所有需求都塞回关键词搜索。命令返回 JSON，通常包含 `platform`、`tool`、`arguments` 和 `data`。
- 好看视频 / Haokan：用 `search` 找视频、`user-search` 找账号，`search-suggestions` 返回联想词，`hot-search` 返回热词而非热门视频。可读取详情、评论、用户资料和作品列表。视频 ID 与视频链接二选一，用户 ID 与主页链接二选一。视频搜索用有限 `--pages`，不支持 `--all`；联想词、热词、详情和用户资料不分页。评论中的回复只是预览，完整回复用 `replies` 加一级 `comment_id` 分页读取。不支持 `--include-replies`、`--since-days` 或口播转文字。
- X 博主发出的回复（含自回复）使用 `x user-replies`；帖子下的评论使用 `x comments` / `x replies`。用户 ID、用户名和主页链接三选一；翻页保持定位方式和完整令牌不变，不混用 `user-posts` 令牌。空页有令牌时可继续，不支持 `--since-days`。

## 输出建议

优先输出可直接复盘的结果：榜单信号、相关样本和主要角度、单条内容事实、评论主题和反馈线索、候选账号、创作者资料、创作者内容证据、互动记录，并标出下一步可继续追问的问题。

做综合研究时，先按平台分开整理事实证据，再补充你的判断；建议按内容角度、受众需求、趋势信号、评论主题、创作者定位和下一步动作来组织结果。
对于 XHS 搜索或详情结果里的 `note_url`，无论是在最终回答、展示、引用、存储、输出还是转发时，都要保留完整原始 URL，包括其中的 `xsec_token` 查询参数；不要改写、截断、脱敏、重建，也不要只根据 `note_id` 去拼链接。如果详情里的 `note_url` 为空，就展示 `note_id`，或者明确说明当前没有可直接打开的完整链接。
对于 XHS `note_id`，要原样复制返回的完整 `note_id`；不要只传或只展示前缀。
做评论分析时，先归纳可见主题，再判断情绪、需求或风险点。
做创作者研究时，把账号资料和内容列表证据分开写；如果用了抖音短剧合集命令，要单独写合集事实；如果用了微博账号内容命令，要保留微博博文列表证据；如果用了今日头条账号内容命令，要保留今日头条博文列表证据；如果用了视频号账号内容命令，要保留视频号作品列表证据；如果用了对应平台账号或频道内容命令，要保留创作者帖子、频道视频或 Shorts 列表证据。
如果同时用了热榜和关键词搜索，请把热榜信号和关键词搜索结果分开写。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- XHS: `xhs_get_search_hot_list`, `xhs_search_notes`, `xhs_get_note_detail_by_note_id`, `xhs_get_note_comments_by_note_id`, `xhs_get_user_info_by_user_id`, `xhs_get_user_posted_notes_by_user_id`, `xhs_search_suggestions`, `xhs_search_users`, `xhs_search_products`, `xhs_get_product_detail_by_sku_id`, `xhs_get_product_detail_by_url`, `xhs_get_product_reviews`, `xhs_get_product_review_replies`, `xhs_get_product_review_reply_replies`, `xhs_get_topic_notes_by_topic_url`, `xhs_get_topic_notes_by_page_id`, `xhs_get_note_detail_by_note_url`, `xhs_get_note_comments_by_note_url`, `xhs_get_user_info_by_profile_url`, `xhs_get_user_posted_notes_by_profile_url`, `xhs_get_note_sub_comments_by_comment_id`
- DOUYIN: `douyin_get_hot_search_list`, `douyin_search_videos`, `douyin_get_video_detail_by_aweme_id`, `douyin_get_video_comments_by_aweme_id`, `douyin_get_user_info_by_sec_user_id`, `douyin_get_user_posted_videos_by_sec_user_id`, `douyin_search_users`, `douyin_get_user_info_by_douyin_id`, `douyin_search_products`, `douyin_get_product_detail_by_product_id`, `douyin_get_product_detail_by_url`, `douyin_get_video_detail_by_url`, `douyin_get_video_share_link_by_aweme_id`, `douyin_get_video_share_link_by_url`, `douyin_get_video_comments_by_url`, `douyin_get_user_info_by_profile_url`, `douyin_get_user_posted_videos_by_profile_url`, `douyin_get_user_series_by_sec_user_id`, `douyin_get_user_series_by_profile_url`, `douyin_get_video_comment_replies_by_comment_id`
- KUAISHOU: `kuaishou_get_hot_search_list`, `kuaishou_search_videos`, `kuaishou_search_users`, `kuaishou_get_video_detail_by_photo_id`, `kuaishou_get_video_comments_by_photo_id`, `kuaishou_get_user_info_by_user_id`, `kuaishou_get_user_posted_videos_by_user_id`, `kuaishou_get_video_detail_by_url`, `kuaishou_get_video_comments_by_url`, `kuaishou_get_user_info_by_profile_url`, `kuaishou_get_user_posted_videos_by_profile_url`, `kuaishou_get_video_comment_replies_by_comment_id`
- BILIBILI: `bilibili_search_videos`, `bilibili_search_articles`, `bilibili_get_content_detail_by_id`, `bilibili_get_content_comments_by_id`, `bilibili_get_user_info_by_user_id`, `bilibili_get_user_posted_videos_by_user_id`, `bilibili_get_user_posted_articles_by_user_id`, `bilibili_get_content_detail_by_url`, `bilibili_get_content_comments_by_url`, `bilibili_get_content_comment_replies_by_comment_id`, `bilibili_get_content_likes_and_reposts_by_post_id`, `bilibili_get_content_likes_and_reposts_by_url`, `bilibili_get_user_info_by_profile_url`, `bilibili_get_user_posted_videos_by_profile_url`, `bilibili_get_user_posted_articles_by_profile_url`, `bilibili_get_user_posted_dynamics_by_user_id`, `bilibili_get_user_posted_dynamics_by_profile_url`
- ZHIHU: `zhihu_get_hot_list`, `zhihu_search_content`, `zhihu_get_content_detail_by_url`, `zhihu_get_content_comments_by_url`, `zhihu_get_user_info_by_profile_url`, `zhihu_get_user_posted_articles_by_profile_url`, `zhihu_get_comment_replies_by_url`
- INSTAGRAM: `instagram_search_posts`, `instagram_get_post_detail_by_post_id`, `instagram_get_post_comments_by_post_url`, `instagram_get_user_info_by_username`, `instagram_get_user_posts_by_username`, `instagram_get_post_detail_by_post_url`, `instagram_get_post_comment_replies_by_comment_id`, `instagram_get_user_info_by_profile_url`, `instagram_get_user_posts_by_profile_url`
- X: `x_search_posts`, `x_get_post_detail_by_post_id`, `x_get_post_comments_by_post_id`, `x_get_user_info_by_username`, `x_get_user_posts_by_username`, `x_get_user_replies_by_user_id`, `x_get_user_replies_by_username`, `x_get_user_replies_by_profile_url`, `x_get_post_detail_by_post_url`, `x_get_post_comments_by_post_url`, `x_get_post_comment_replies_by_comment_id`, `x_get_user_info_by_user_id`, `x_get_user_info_by_profile_url`, `x_get_user_posts_by_user_id`, `x_get_user_posts_by_profile_url`
- YOUTUBE: `youtube_search_videos`, `youtube_get_video_detail_by_url`, `youtube_get_video_comments_by_url`, `youtube_get_channel_info_by_url`, `youtube_get_user_posted_videos_by_channel_url`, `youtube_get_video_comment_replies`
- TIKTOK: `tiktok_search_posts`, `tiktok_get_post_detail_by_url`, `tiktok_get_post_comments_by_post_id`, `tiktok_get_user_info_by_tiktok_id`, `tiktok_get_user_posts_by_tiktok_id`, `tiktok_get_post_comments_by_url`, `tiktok_get_post_comment_replies`, `tiktok_get_user_info_by_profile_url`, `tiktok_get_user_posts_by_profile_url`
- WEIBO: `weibo_get_hot_search_list`, `weibo_search_posts`, `weibo_get_post_detail_by_post_id`, `weibo_get_post_comments_by_post_id`, `weibo_get_user_info_by_user_id`, `weibo_get_user_posts_by_user_id`, `weibo_get_post_liker_list_by_post_url`, `weibo_get_post_repost_list_by_post_url`, `weibo_get_post_detail_by_post_url`, `weibo_get_post_comments_by_post_url`, `weibo_get_post_liker_list_by_post_id`, `weibo_get_post_repost_list_by_post_id`, `weibo_get_user_info_by_profile_url`, `weibo_get_user_posts_by_profile_url`, `weibo_get_post_comment_replies_by_comment_id`
- TOUTIAO: `toutiao_get_hot_search_list`, `toutiao_search_posts`, `toutiao_get_post_detail_by_post_id`, `toutiao_get_post_comments_by_post_id`, `toutiao_get_user_info_by_user_id`, `toutiao_get_user_posts_by_user_id`, `toutiao_get_post_detail_by_url`, `toutiao_get_post_comments_by_url`, `toutiao_get_user_info_by_profile_url`, `toutiao_get_user_posts_by_profile_url`, `toutiao_get_post_comment_replies_by_comment_id`
- WECHAT: `wechat_get_hot_search_list`, `wechat_search_videos`, `wechat_get_video_detail_by_encrypted_object_id`, `wechat_get_mp_article_detail_by_url`, `wechat_get_mp_article_stats_by_url`, `wechat_get_video_comments_by_object_id`, `wechat_get_user_info_by_user_id`, `wechat_get_user_posted_videos_by_user_id`, `wechat_get_video_share_url_by_object_id`, `wechat_get_video_detail_by_url`, `wechat_get_video_comments_by_url`, `wechat_get_video_comment_replies_by_comment_id`, `wechat_get_user_info_by_url`, `wechat_get_user_posted_videos_by_url`
- HAOKAN: `haokan_search_videos`, `haokan_search_users`, `haokan_search_suggestions`, `haokan_get_hot_search_list`, `haokan_get_video_detail_by_video_id`, `haokan_get_video_detail_by_url`, `haokan_get_video_comments_by_video_id`, `haokan_get_video_comments_by_url`, `haokan_get_comment_replies_by_video_id`, `haokan_get_comment_replies_by_url`, `haokan_get_user_info_by_user_id`, `haokan_get_user_info_by_url`, `haokan_get_user_posted_videos_by_user_id`, `haokan_get_user_posted_videos_by_profile_url`

上面自动列出的 MCP 工具名就是事实源；根据用户的平台和任务，优先选择最贴近的那个工具。
搜索翻页时，第一页不要传 `page_token`；继续同一条链路时，只能传完整返回的 `next_page_token`，后续续页都继续用 `page_token`。
补全小红书搜索词时使用 `xhs_search_suggestions`；用户要笔记或商品结果时，分别使用 `xhs_search_notes` 或 `xhs_search_products`。
做小红书博主、商品或话题页研究时，分别使用 `xhs_search_users`、`xhs_search_products` 或 `xhs_get_topic_notes_by_topic_url` / `xhs_get_topic_notes_by_page_id`；已知 sku_id 时用 `xhs_get_product_detail_by_sku_id`，商品链接用 `xhs_get_product_detail_by_url`，商品评价、回复及回复下的嵌套回复用 `xhs_get_product_reviews`、`xhs_get_product_review_replies` 和 `xhs_get_product_review_reply_replies`。
做抖音商品研究时，关键词使用 `douyin_search_products`；已知 product_id 时用 `douyin_get_product_detail_by_product_id`，商品链接用 `douyin_get_product_detail_by_url`。

小红书搜索参数命名提醒：direct CLI 使用 `--sort-type`、`--publish-time-range`、`--note-type`；MCP 工具 `xhs_search_notes` 使用 `sort_type`、`publish_time_range`、`note_type`。不要传 `sortType`、`publishTimeRange` 或 `noteType`。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：热榜=排名/话题/热度信号、内容样本=标题/作者/链接或 ID、详情=正文/作者/发布时间/互动指标、评论=内容/用户/时间/回复线索、候选账号=昵称/ID/粉丝信号、账号=昵称/ID/简介/粉丝信号、账号内容=标题/发布时间/互动信号、互动记录=用户/时间/动作；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 使用 `--include-replies` 时，`replies_partial` 表示该评论回复不完整，`replies_pending` 表示尚未展开。先用该平台回复命令、对应评论标识及可用的 `replies_next_page_token` 补齐；尚未展开或首个回复请求失败时，修正错误后从该评论的首批回复开始，重复令牌错误则先排查。仅在主评论仍有剩余额度时，才用外层 `data.next_page_token` 继续；补齐已取得评论的回复不增加主评论页数；两类令牌不能混用，不把回复预览当成完整回复。
- 非余额不足且非限流的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 批量处理：默认按队列逐条处理；用户明确需要批量效率时，最多同时处理 3 条。每完成 1 条，就继续处理下一条，不要一次性发起大量请求。遇到 `rate_limited` 或“请求过于频繁”时，不要放弃任务；先停止发起新的请求，按返回的等待时间等待，没有等待时间就先等待 2 秒，然后继续处理当前队列。等待期间已完成的结果要保留；恢复后继续从未完成的位置处理。遇到 `insufficient_balance` 或“积分不足”时，立即停止后续请求，输出已获得结果，并提示充值或切换有余额的 API Key 后继续。

## 常见问题

- 没结果：放宽关键词、减少限定，或换成更贴近用户表达的词。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
