param(
  [string]$ManifestPath
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$jsonText = [System.IO.File]::ReadAllText($ManifestPath, [System.Text.Encoding]::UTF8)
$manifest = $jsonText | ConvertFrom-Json
$rawDir = $manifest.rawDir
$rootDir = $manifest.rootDir

function New-Color([int]$r, [int]$g, [int]$b, [int]$a = 255) {
  return [System.Drawing.Color]::FromArgb($a, $r, $g, $b)
}

function Add-RoundedRectPath($path, [float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
  $d = $r * 2
  $path.AddArc($x, $y, $d, $d, 180, 90)
  $path.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
  $path.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
  $path.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
  $path.CloseFigure()
}

function Fill-RoundedRect($g, $brush, [float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
  $p = New-Object System.Drawing.Drawing2D.GraphicsPath
  Add-RoundedRectPath $p $x $y $w $h $r
  $g.FillPath($brush, $p)
  $p.Dispose()
}

function Draw-RoundedRect($g, $pen, [float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
  $p = New-Object System.Drawing.Drawing2D.GraphicsPath
  Add-RoundedRectPath $p $x $y $w $h $r
  $g.DrawPath($pen, $p)
  $p.Dispose()
}

$fLabelZh = New-Object System.Drawing.Font("Microsoft YaHei UI", 11.5, [System.Drawing.FontStyle]::Bold)
$fLabelEn = New-Object System.Drawing.Font("Segoe UI", 11.5, [System.Drawing.FontStyle]::Bold)
$fBubbleZh = New-Object System.Drawing.Font("Microsoft YaHei UI", 10, [System.Drawing.FontStyle]::Bold)
$fBubbleEn = New-Object System.Drawing.Font("Consolas", 10, [System.Drawing.FontStyle]::Bold)

$bBg = New-Object System.Drawing.SolidBrush((New-Color 244 246 250))
$bCard = New-Object System.Drawing.SolidBrush((New-Color 255 255 255))
$bDarkText = New-Object System.Drawing.SolidBrush((New-Color 30 41 59))
$bWhite = New-Object System.Drawing.SolidBrush((New-Color 255 255 255))
$pCardBorder = New-Object System.Drawing.Pen((New-Color 226 232 240), 1.5)

# Authentic Minecraft In-Game Chat Bar Strip (top-left translucent charcoal bar, no cyan sci-fi border!)
$bMcChatBg = New-Object System.Drawing.SolidBrush((New-Color 14 18 24 178))
$bMcBracket = New-Object System.Drawing.SolidBrush((New-Color 163 230 53))

function Draw-MinecraftTagBubble($g, [float]$cx, [float]$topY, [string]$text, $font, [float]$leftX = 14, [float]$barY = 14) {
  if (-not $text) { return }
  $chatLine = "> " + $text
  $sz = $g.MeasureString($chatLine, $font)
  $bw = [Math]::Ceiling($sz.Width) + 16
  $bh = 24
  $g.FillRectangle($bMcChatBg, $leftX, $barY, $bw, $bh)
  $g.DrawString(">", $font, $bMcBracket, ($leftX + 6), ($barY + 3))
  $g.DrawString($text, $font, $bWhite, ($leftX + 19), ($barY + 3))
}

if (-not $manifest.loopsOnly) {
# 1. Clean 3-View Turnaround Sheet (.zh.png and .en.png)
$tInfo = $manifest.turnaround
foreach ($lang in @("zh", "en")) {
  $bmp = New-Object System.Drawing.Bitmap(1344, 596)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $g.FillRectangle($bBg, 0, 0, 1344, 596)

  $font = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }
  for ($i = 0; $i -lt 3; $i++) {
    $v = $tInfo.views[$i]
    $vx = 24 + $i * 436
    $vy = 20
    Fill-RoundedRect $g $bCard $vx $vy 424 556 14
    Draw-RoundedRect $g $pCardBorder $vx $vy 424 556 14

    $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $v.file))
    $g.DrawImage($img, ($vx + 6), ($vy + 6), 412, 502)
    $img.Dispose()

    $label = if ($lang -eq "zh") { $v.labelZh } else { $v.labelEn }
    $lsz = $g.MeasureString($label, $font)
    $g.DrawString($label, $font, $bDarkText, ($vx + (424 - $lsz.Width) / 2), ($vy + 518))
  }

  $outFile = if ($lang -eq "zh") { $tInfo.outZh } else { $tInfo.outEn }
  $bmp.Save($outFile, [System.Drawing.Imaging.ImageFormat]::Png)
  if ($lang -eq "en") {
    foreach ($defPath in $tInfo.outDefault) {
      $bmp.Save($defPath, [System.Drawing.Imaging.ImageFormat]::Png)
    }
  }
  $g.Dispose()
  $bmp.Dispose()
}

# 2. Clean 4-Panel Voxel Blocks, Tools & Mobs Showcase (.zh.png and .en.png)
$oInfo = $manifest.objects
foreach ($lang in @("zh", "en")) {
  $bmp = New-Object System.Drawing.Bitmap(1384, 500)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $g.FillRectangle($bBg, 0, 0, 1384, 500)

  $font = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }
  for ($i = 0; $i -lt 4; $i++) {
    $p = $oInfo.panels[$i]
    $px = 20 + $i * 340
    $py = 18
    Fill-RoundedRect $g $bCard $px $py 324 464 14
    $pCol = New-Color $p.r $p.g $p.b
    $pen = New-Object System.Drawing.Pen($pCol, 2)
    Draw-RoundedRect $g $pen $px $py 324 464 14
    $pen.Dispose()

    $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $p.file))
    $g.DrawImage($img, ($px + 6), ($py + 6), 312, 408)
    $img.Dispose()

    $label = if ($lang -eq "zh") { $p.labelZh } else { $p.labelEn }
    $bBadge = New-Object System.Drawing.SolidBrush($pCol)
    Fill-RoundedRect $g $bBadge ($px + 14) ($py + 422) 296 32 8
    $lsz = $g.MeasureString($label, $font)
    $g.DrawString($label, $font, $bWhite, ($px + 14 + (296 - $lsz.Width) / 2), ($py + 427))
    $bBadge.Dispose()
  }

  $outFile = if ($lang -eq "zh") { $oInfo.outZh } else { $oInfo.outEn }
  $bmp.Save($outFile, [System.Drawing.Imaging.ImageFormat]::Png)
  if ($lang -eq "en") {
    $bmp.Save($oInfo.outDefault, [System.Drawing.Imaging.ImageFormat]::Png)
  }
  $g.Dispose()
  $bmp.Dispose()
}

# 3. Clean 4-Way Anti-Drift Comparison (.zh.png and .en.png)
$dInfo = $manifest.drift
foreach ($lang in @("zh", "en")) {
  $bmp = New-Object System.Drawing.Bitmap(1384, 500)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
  $g.FillRectangle($bBg, 0, 0, 1384, 500)

  $font = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }
  for ($i = 0; $i -lt 4; $i++) {
    $p = $dInfo.panels[$i]
    $px = 20 + $i * 340
    $py = 18
    Fill-RoundedRect $g $bCard $px $py 324 464 14
    $pCol = New-Color $p.r $p.g $p.b
    $pen = New-Object System.Drawing.Pen($pCol, 2)
    Draw-RoundedRect $g $pen $px $py 324 464 14
    $pen.Dispose()

    $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $p.file))
    $g.DrawImage($img, ($px + 6), ($py + 6), 312, 408)
    $img.Dispose()

    $label = if ($lang -eq "zh") { $p.labelZh } else { $p.labelEn }
    $bBadge = New-Object System.Drawing.SolidBrush($pCol)
    Fill-RoundedRect $g $bBadge ($px + 14) ($py + 422) 296 32 8
    $lsz = $g.MeasureString($label, $font)
    $g.DrawString($label, $font, $bWhite, ($px + 14 + (296 - $lsz.Width) / 2), ($py + 427))
    $bBadge.Dispose()
  }

  $outFile = if ($lang -eq "zh") { $dInfo.outZh } else { $dInfo.outEn }
  $bmp.Save($outFile, [System.Drawing.Imaging.ImageFormat]::Png)
  if ($lang -eq "en") {
    $bmp.Save($dInfo.outDefault, [System.Drawing.Imaging.ImageFormat]::Png)
  }
  $g.Dispose()
  $bmp.Dispose()
}

# 3b. Classic Minecraft Asset Library Thumbnails + Lineup Sheets (.zh.png and .en.png)
$libInfo = $manifest.library
if ($libInfo) {
  foreach ($c in $libInfo.characters) {
    Copy-Item -Force (Join-Path $rawDir $c.raw) $c.out
  }
  foreach ($o in $libInfo.objects) {
    Copy-Item -Force (Join-Path $rawDir $o.raw) $o.out
  }

  foreach ($lang in @("zh", "en")) {
    $font = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }

    # 6-Character Lineup Sheet (1420 x 360)
    $cbmp = New-Object System.Drawing.Bitmap(1420, 360)
    $cg = [System.Drawing.Graphics]::FromImage($cbmp)
    $cg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $cg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $cg.FillRectangle($bBg, 0, 0, 1420, 360)

    for ($i = 0; $i -lt 6; $i++) {
      $item = $libInfo.characters[$i]
      $cx = 16 + $i * 232
      $cy = 16
      Fill-RoundedRect $cg $bCard $cx $cy 220 328 12
      Draw-RoundedRect $cg $pCardBorder $cx $cy 220 328 12
      $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $item.raw))
      $cg.DrawImage($img, ($cx + 6), ($cy + 6), 208, 276)
      $img.Dispose()
      $lbl = if ($lang -eq "zh") { $item.labelZh } else { $item.labelEn }
      $lsz = $cg.MeasureString($lbl, $font)
      $cg.DrawString($lbl, $font, $bDarkText, ($cx + (220 - $lsz.Width) / 2), ($cy + 292))
    }
    $cOut = if ($lang -eq "zh") { $libInfo.charSheetZh } else { $libInfo.charSheetEn }
    $cbmp.Save($cOut, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en") { $cbmp.Save($libInfo.charSheetDefault, [System.Drawing.Imaging.ImageFormat]::Png) }
    $cg.Dispose()
    $cbmp.Dispose()

    # 8-Object Atlas Sheet (4x2 grid: 1000 x 560)
    $obmp = New-Object System.Drawing.Bitmap(1000, 560)
    $og = [System.Drawing.Graphics]::FromImage($obmp)
    $og.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $og.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $og.FillRectangle($bBg, 0, 0, 1000, 560)

    for ($i = 0; $i -lt 8; $i++) {
      $item = $libInfo.objects[$i]
      $col = $i % 4
      $row = [Math]::Floor($i / 4)
      $ox = 16 + $col * 244
      $oy = 16 + $row * 268
      Fill-RoundedRect $og $bCard $ox $oy 232 256 12
      Draw-RoundedRect $og $pCardBorder $ox $oy 232 256 12
      $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $item.raw))
      $og.DrawImage($img, ($ox + 6), ($oy + 6), 220, 210)
      $img.Dispose()
      $lbl = if ($lang -eq "zh") { $item.labelZh } else { $item.labelEn }
      $lsz = $og.MeasureString($lbl, $font)
      $og.DrawString($lbl, $font, $bDarkText, ($ox + (232 - $lsz.Width) / 2), ($oy + 222))
    }
    $oOut = if ($lang -eq "zh") { $libInfo.objSheetZh } else { $libInfo.objSheetEn }
    $obmp.Save($oOut, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en") { $obmp.Save($libInfo.objSheetDefault, [System.Drawing.Imaging.ImageFormat]::Png) }
    $og.Dispose()
    $obmp.Dispose()
  }
}

# 4. Clean 4-Shot 9:16 Storyboard Contact Sheets (.zh.png and .en.png) + Keyframes + GIF + MP4
foreach ($case in $manifest.cases) {
  foreach ($lang in @("zh", "en")) {
    $bmp = New-Object System.Drawing.Bitmap(1384, 648)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.FillRectangle($bBg, 0, 0, 1384, 648)

    $fontLabel = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }
    $fontBub = if ($lang -eq "zh") { $fBubbleZh } else { $fBubbleEn }

    for ($s = 0; $s -lt 4; $s++) {
      $sh = $case.shots[$s]
      $sx = 20 + $s * 340
      $sy = 18
      Fill-RoundedRect $g $bCard $sx $sy 324 612 14
      Draw-RoundedRect $g $pCardBorder $sx $sy 324 612 14

      $rawShotPath = Join-Path $rawDir ($case.prefix + "_shot_" + $s + ".png")
      $img = [System.Drawing.Image]::FromFile($rawShotPath)
      $chatText = if ($lang -eq "zh") { $sh.chatZh } else { $sh.chatEn }

      if ($lang -eq "zh" -and $sh.savePath) {
        $shotBmp = New-Object System.Drawing.Bitmap(360, 640)
        $sg = [System.Drawing.Graphics]::FromImage($shotBmp)
        $sg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
        $sg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
        $sg.DrawImage($img, 0, 0, 360, 640)
        Draw-MinecraftTagBubble $sg 0 0 $chatText $fontBub 14 14
        $shotBmp.Save($sh.savePath, [System.Drawing.Imaging.ImageFormat]::Png)
        $sg.Dispose()
        $shotBmp.Dispose()
      }

      $g.DrawImage($img, ($sx + 6), ($sy + 6), 312, 554)
      $img.Dispose()

      Draw-MinecraftTagBubble $g 0 0 $chatText $fontBub ($sx + 16) ($sy + 16)

      $label = if ($lang -eq "zh") { $sh.labelZh } else { $sh.labelEn }
      $lsz = $g.MeasureString($label, $fontLabel)
      $g.DrawString($label, $fontLabel, $bDarkText, ($sx + (324 - $lsz.Width) / 2), ($sy + 570))
    }

    $outSheet = if ($lang -eq "zh") { $case.sheetZh } else { $case.sheetEn }
    $bmp.Save($outSheet, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en") {
      $bmp.Save($case.sheetDefault, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $g.Dispose()
    $bmp.Dispose()
  }

  # Render clean 24-frame animation
  $hudDir = Join-Path $rootDir ("tmp\hud_" + $case.prefix)
  New-Item -ItemType Directory -Force -Path $hudDir | Out-Null

  for ($f = 0; $f -lt 24; $f++) {
    $sIdx = [Math]::Floor($f / 6)
    $sh = $case.shots[$sIdx]
    $fname = $case.prefix + "_anim_" + $f.ToString("00") + ".png"
    $srcImg = [System.Drawing.Image]::FromFile((Join-Path $rawDir $fname))
    $frameBmp = New-Object System.Drawing.Bitmap(270, 480)
    $fg = [System.Drawing.Graphics]::FromImage($frameBmp)
    $fg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $fg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $fg.DrawImage($srcImg, 0, 0, 270, 480)
    $srcImg.Dispose()

    Draw-MinecraftTagBubble $fg 0 0 $sh.chatEn $fBubbleEn 10 10

    $outFrame = Join-Path $hudDir ("frame_" + $f.ToString("00") + ".png")
    $frameBmp.Save($outFrame, [System.Drawing.Imaging.ImageFormat]::Png)
    $fg.Dispose()
    $frameBmp.Dispose()
  }

  $inPattern = Join-Path $hudDir "frame_%02d.png"
  $palPath = Join-Path $hudDir "palette.png"
  & ffmpeg -y -loglevel error -framerate 6 -i $inPattern -vf "palettegen=max_colors=128" $palPath
  & ffmpeg -y -loglevel error -framerate 6 -i $inPattern -i $palPath -lavfi "paletteuse=dither=bayer" $case.gifPath
  & ffmpeg -y -loglevel error -framerate 6 -i $inPattern -f lavfi -i "sine=frequency=440:beep_factor=3:duration=4" -c:v libx264 -pix_fmt yuv420p -vf "fps=24" -c:a aac -b:a 96k -shortest $case.mp4Path
}
} # end if (-not $manifest.loopsOnly)

# 5. Pure Voxel Block & Item Seamless Loops (GIF + MP4)
if ($manifest.objectLoops) {
  foreach ($lp in $manifest.objectLoops) {
    $inPat = Join-Path $rawDir ($lp.prefix + "_%02d.png")
    $pal = Join-Path $rawDir ($lp.prefix + "_pal.png")
    & ffmpeg -y -loglevel error -framerate 8 -i $inPat -vf "palettegen=max_colors=192" $pal
    & ffmpeg -y -loglevel error -framerate 8 -i $inPat -i $pal -lavfi "paletteuse=dither=bayer" $lp.gifPath
    & ffmpeg -y -loglevel error -framerate 8 -i $inPat -f lavfi -i "sine=frequency=520:beep_factor=2:duration=2" -c:v libx264 -pix_fmt yuv420p -vf "fps=24" -c:a aac -b:a 96k -shortest $lp.mp4Path
  }
}

# 6. Hero Widescreen 4-Up Synchronized Animated Showreel (GIF + MP4)
if ($manifest.heroReel -and $manifest.heroReel.sources.Count -eq 4) {
  $hr = $manifest.heroReel
  $s0 = $hr.sources[0]
  $s1 = $hr.sources[1]
  $s2 = $hr.sources[2]
  $s3 = $hr.sources[3]
  $reelPal = Join-Path $rawDir "hero_reel_pal.png"
  $stackFilter = "[0:v]scale=220:392,pad=232:412:6:10:color=#0f172a[v0];[1:v]scale=220:392,pad=232:412:6:10:color=#0f172a[v1];[2:v]scale=220:392,pad=232:412:6:10:color=#0f172a[v2];[3:v]scale=220:392,pad=232:412:6:10:color=#0f172a[v3];[v0][v1][v2][v3]hstack=inputs=4,fps=24[vmp4]"
  & ffmpeg -y -loglevel error -i $s0 -i $s1 -i $s2 -i $s3 -filter_complex $stackFilter -map "[vmp4]" -map 0:a -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 96k -shortest $hr.mp4Path
  & ffmpeg -y -loglevel error -i $hr.mp4Path -vf "fps=8,palettegen=max_colors=192" $reelPal
  & ffmpeg -y -loglevel error -i $hr.mp4Path -i $reelPal -lavfi "fps=8[x];[x][1:v]paletteuse=dither=bayer" $hr.gifPath
}

Write-Output "All bilingual .zh.png / .en.png boards, object loops, hero reel, GIFs, and MP4s generated!"
