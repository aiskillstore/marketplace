# Japan clues

Entries use the shared format (`references/clues/README.md`). Cross-country clues that lead here (driving side, plate shape, script) are in `references/clues/global.md`.

## Clues

### Railway company names on level-crossing and station signs
- Look for: the company name printed on round "踏切 とまれ" (level crossing, stop) signs, warning signs, and crossing equipment boxes
- Points to: operating area. JR passenger service is split among six companies, each with its own territory (JR西日本 (JR West) = Kinki, the Chūgoku region, part of Hokuriku); private railway names can often pin the line directly
- Strength: medium (JR to the broad region, private railways to the line)
- Counterexamples: near company boundaries; old signs not replaced after a line was handed over to a third-party operator
- Sources: v003

### Telephone area codes (市外局番)
- Look for: TEL numbers on signs, construction notices, warning signs, vending machines
- Points to: the first digit after the 0 runs roughly north to south (01 Hokkaido … 09 Kyushu and Okinawa); look up the full area code in a table to get the city (e.g., 03 = Tokyo's 23 wards)
- Strength: medium
- Counterexamples: area codes vary from 2 to 5 digits; when only part of the number is visible, judge the length from the digit grouping; 0120, 0570, 050, 080, 090 don't map to a region
- Sources: v003

### Four parallel tracks at one level crossing
- Look for: the number of parallel tracks across the crossing, whether there is overhead catenary
- Points to: a quadruple-track section of a trunk line; adding conditions like "right on the coast" can narrow it to a few km (`osm.py crossings --kind level_crossing` estimates the track count from the node count)
- Strength: medium
- Counterexamples: station throats and two companies' lines running side by side also show 4 tracks; urban quadruple-track sections are mostly grade-separated, so places with level crossings are actually rare
- Sources: v003

### Issuing authority at the bottom of signs
- Look for: "〇〇警察署" (police station), "〇〇土木事務所" (civil engineering office), "〇〇区役所" (ward office) at the bottom of regulatory signs, construction signs, and notice boards
- Points to: ward, city
- Strength: medium
- Counterexamples: the name of a prefectural or cross-ward agency is not the ward you are in
- Sources: v003
