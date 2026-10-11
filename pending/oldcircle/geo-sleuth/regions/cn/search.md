# Searching for places in mainland China

Region-specific half of `references/search.md`: which Chinese platforms to search and how to phrase queries. The general method (variants, engines, vote counting, after a hit) stays in `references/search.md`.

## Chinese keyword search

General web search tools are often ineffective for Chinese content inside China. Use the script:

```bash
uv run scripts/revimg.py --query "蓝色拱形顶棚 人行天桥 高架" --query "<city> 出租车 颜色" --out-dir q/
```

(Queries in Chinese: "blue arched canopy, pedestrian bridge, elevated road"; "<city> taxi color".)

Bing China gives web results (title + link); Baidu Images and Sogou Images give result-page screenshots (look at photos of similar scenes). For long descriptive queries ("楼顶操场 学校" rooftop playground school, "黄色公交" yellow bus) Bing mostly returns travel-guide pages; look directly at the Baidu Images screenshot. Baidu web search pops up a verification challenge, so it isn't done.

## Where to search by object type (China)

| Object | Where to search | Source |
|---|---|---|
| Scenic-area buildings, viral check-in spots | Douyin, Xiaohongshu, Weibo keyword and image search; official scenic-area accounts post videos from the same angle | v010-2, v009 |
| Statues, small park features | User photos in Ctrip reviews | v010-6 |
| New residential developments, commercial complexes | Housing-development albums on property sites (Anjuke, Fang.com, Loupan.com, etc.): the "周边配套" (nearby amenities) and "实景图" (real photos) sections; page all the way to the signboard | v010-5 |
| Old buildings, historic sites | Local culture-and-tourism and protected-heritage-site pages; Visual China Group captions carry place names and years | v004 |
| Ordinary streets, when even the city isn't fixed | Sample one page of arterial-road street view per candidate city and compare municipal fixtures (`baidu_pano.py sample`) | — |
| Vehicle livery (bus, taxi, school bus) | `revimg.py --query "<city> <color description> 公交"` (query in Chinese: <city> <color description> bus), and read route signs and company names from the result images; first resolve any place name you read to a district (county) with `poi.py` before using it; don't treat a vehicle from district A as a clue for district B | v014 |

## Social media

- Viral scenery: search `<city> + <scenery>` on Douyin, Xiaohongshu and Weibo, in both Chinese and English.
- Locals' photos of the same mountains or the same river: look in the candidate township's "同城" (local) feed or its place page (the v010-1 creator spoofed the device location to the candidate township to browse local content).
- IP location labels on posts and comments are covered in `clues.md` (Platform and metadata).
