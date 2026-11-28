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

$fLabelZh = New-Object System.Drawing.Font("Microsoft YaHei UI", 12, [System.Drawing.FontStyle]::Bold)
$fLabelEn = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$fBubbleZh = New-Object System.Drawing.Font("Microsoft YaHei UI", 10, [System.Drawing.FontStyle]::Bold)
$fBubbleEn = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)

$bBg = New-Object System.Drawing.SolidBrush((New-Color 244 246 250))
$bCard = New-Object System.Drawing.SolidBrush((New-Color 255 255 255))
$bDarkText = New-Object System.Drawing.SolidBrush((New-Color 30 41 59))
$bWhite = New-Object System.Drawing.SolidBrush((New-Color 255 255 255))
$pCardBorder = New-Object System.Drawing.Pen((New-Color 226 232 240), 1.5)
$bBubbleFill = New-Object System.Drawing.SolidBrush((New-Color 255 255 255 248))
$pBubbleBorder = New-Object System.Drawing.Pen((New-Color 203 213 225), 1.5)

function Draw-CleanChatBubble($g, [float]$cx, [float]$topY, [string]$text, $font) {
  if (-not $text) { return }
  $sz = $g.MeasureString($text, $font)
  $bw = [Math]::Max(68, [Math]::Ceiling($sz.Width) + 20)
  $bh = 28
  $bx = $cx - ($bw / 2)
  $by = $topY

  Fill-RoundedRect $g $bBubbleFill $bx $by $bw $bh 10
  Draw-RoundedRect $g $pBubbleBorder $bx $by $bw $bh 10

  $pts = @(
    (New-Object System.Drawing.PointF(($cx - 5), ($by + $bh - 1))),
    (New-Object System.Drawing.PointF(($cx + 5), ($by + $bh - 1))),
    (New-Object System.Drawing.PointF($cx, ($by + $bh + 6)))
  )
  $g.FillPolygon($bBubbleFill, $pts)
  $tx = $bx + ($bw - $sz.Width) / 2
  $g.DrawString($text, $font, $bDarkText, $tx, ($by + 4))
}

# 1. Clean 3-View Turnaround Sheet (.zh.png and .en.png)
$tInfo = $manifest.turnaround
if (Test-Path (Join-Path $rawDir $tInfo.views[0].file)) {
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
}

# 1b. Cast Acting Reference Sheet (.zh.png and .en.png — Identity + Signature Acting Moment)
if ($manifest.castActingSheet -and $manifest.castActingSheet.panels.Count -gt 0 -and (Test-Path (Join-Path $rawDir $manifest.castActingSheet.panels[0].file))) {
  $ca = $manifest.castActingSheet
  $pCount = $ca.panels.Count
  $cols = [Math]::Min(4, [Math]::Max(1, $pCount))
  $rows = [Math]::Ceiling($pCount / [double]$cols)
  $sheetW = 24 + $cols * 412
  $sheetH = 20 + $rows * 564
  $fSubZh = New-Object System.Drawing.Font("Microsoft YaHei UI", 9.0, [System.Drawing.FontStyle]::Regular)
  $fSubEn = New-Object System.Drawing.Font("Segoe UI", 9.0, [System.Drawing.FontStyle]::Regular)
  $bSubText = New-Object System.Drawing.SolidBrush((New-Color 71 85 105))
  $sfCenter = New-Object System.Drawing.StringFormat
  $sfCenter.Alignment = [System.Drawing.StringAlignment]::Center
  $sfCenter.LineAlignment = [System.Drawing.StringAlignment]::Near

  foreach ($lang in @("zh", "en")) {
    $bmp = New-Object System.Drawing.Bitmap([int]$sheetW, [int]$sheetH)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.FillRectangle($bBg, 0, 0, [int]$sheetW, [int]$sheetH)

    $fontTitle = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }
    $fontSub = if ($lang -eq "zh") { $fSubZh } else { $fSubEn }

    for ($i = 0; $i -lt $pCount; $i++) {
      $pn = $ca.panels[$i]
      $cIdx = $i % $cols
      $rIdx = [Math]::Floor($i / [double]$cols)
      $px = 20 + $cIdx * 412
      $py = 18 + $rIdx * 548
      Fill-RoundedRect $g $bCard $px $py 396 534 14
      Draw-RoundedRect $g $pCardBorder $px $py 396 534 14

      $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $pn.file))
      $g.DrawImage($img, ($px + 8), ($py + 8), 380, 460)
      $img.Dispose()

      $tStr = if ($lang -eq "zh") { $pn.titleZh } else { $pn.titleEn }
      $mStr = if ($lang -eq "zh") { $pn.momentZh } else { $pn.momentEn }
      $tsz = $g.MeasureString($tStr, $fontTitle)
      $g.DrawString($tStr, $fontTitle, $bDarkText, ($px + (396 - $tsz.Width) / 2), ($py + 471))
      $subRect = New-Object System.Drawing.RectangleF(($px + 14), ($py + 495), 368, 36)
      $g.DrawString($mStr, $fontSub, $bSubText, $subRect, $sfCenter)
    }

    $outPath = if ($lang -eq "zh") { $ca.outZh } else { $ca.outEn }
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en" -and $ca.outDefault) {
      $bmp.Save($ca.outDefault, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $g.Dispose()
    $bmp.Dispose()
  }
  $sfCenter.Dispose()
  $fSubZh.Dispose()
  $fSubEn.Dispose()
  $bSubText.Dispose()
}

# 2. Clean 4-Way Anti-Drift Comparison (.zh.png and .en.png)
$dInfo = $manifest.drift
if (Test-Path (Join-Path $rawDir $dInfo.panels[0].file)) {
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
}

# 2b. Classic Roblox Avatars Lineup (3x2 grid) & Classic Roblox Face Decal Atlas (4x2 grid)
if ($manifest.classicAssetSheet -and (Test-Path (Join-Path $rawDir "avatar_theo.png")) -and (Test-Path (Join-Path $rawDir "face_dizzy.png"))) {
  $cInfo = $manifest.classicAssetSheet
  $libAvDir = Join-Path $rootDir "assets\library\avatars"
  $libFaceDir = Join-Path $rootDir "assets\library\faces"
  New-Item -ItemType Directory -Force -Path $libAvDir, $libFaceDir | Out-Null

  foreach ($av in $cInfo.avatars) {
    $src = Join-Path $rawDir $av.file
    if (Test-Path $src) { Copy-Item $src (Join-Path $libAvDir $av.file) -Force }
  }
  foreach ($fc in $cInfo.faces) {
    $src = Join-Path $rawDir $fc.file
    if (Test-Path $src) { Copy-Item $src (Join-Path $libFaceDir $fc.file) -Force }
  }

  foreach ($lang in @("zh", "en")) {
    $font = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }

    # Avatars 3x2 sheet (1384 x 836)
    $bmpA = New-Object System.Drawing.Bitmap(1384, 836)
    $gA = [System.Drawing.Graphics]::FromImage($bmpA)
    $gA.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $gA.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $gA.FillRectangle($bBg, 0, 0, 1384, 836)

    for ($i = 0; $i -lt $cInfo.avatars.Count; $i++) {
      $av = $cInfo.avatars[$i]
      $col = $i % 3
      $row = [Math]::Floor($i / 3)
      $ax = 24 + $col * 452
      $ay = 18 + $row * 404
      Fill-RoundedRect $gA $bCard $ax $ay 432 388 14
      Draw-RoundedRect $gA $pCardBorder $ax $ay 432 388 14

      $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $av.file))
      $gA.DrawImage($img, ($ax + 86), ($ay + 8), 260, 332)
      $img.Dispose()

      $label = if ($lang -eq "zh") { $av.labelZh } else { $av.labelEn }
      $lsz = $gA.MeasureString($label, $font)
      $gA.DrawString($label, $font, $bDarkText, ($ax + (432 - $lsz.Width) / 2), ($ay + 348))
    }

    $outA = if ($lang -eq "zh") { $cInfo.avatarsOutZh } else { $cInfo.avatarsOutEn }
    $bmpA.Save($outA, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en") { $bmpA.Save($cInfo.avatarsOutDefault, [System.Drawing.Imaging.ImageFormat]::Png) }
    $gA.Dispose()
    $bmpA.Dispose()

    # Faces 4x2 sheet (1384 x 564)
    $bmpF = New-Object System.Drawing.Bitmap(1384, 564)
    $gF = [System.Drawing.Graphics]::FromImage($bmpF)
    $gF.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $gF.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $gF.FillRectangle($bBg, 0, 0, 1384, 564)

    for ($i = 0; $i -lt $cInfo.faces.Count; $i++) {
      $fc = $cInfo.faces[$i]
      $col = $i % 4
      $row = [Math]::Floor($i / 4)
      $fx = 20 + $col * 340
      $fy = 16 + $row * 268
      Fill-RoundedRect $gF $bCard $fx $fy 324 252 14
      Draw-RoundedRect $gF $pCardBorder $fx $fy 324 252 14

      $img = [System.Drawing.Image]::FromFile((Join-Path $rawDir $fc.file))
      $gF.DrawImage($img, ($fx + 62), ($fy + 8), 200, 200)
      $img.Dispose()

      $label = if ($lang -eq "zh") { $fc.labelZh } else { $fc.labelEn }
      $lsz = $gF.MeasureString($label, $font)
      $gF.DrawString($label, $font, $bDarkText, ($fx + (324 - $lsz.Width) / 2), ($fy + 214))
    }

    $outF = if ($lang -eq "zh") { $cInfo.facesOutZh } else { $cInfo.facesOutEn }
    $bmpF.Save($outF, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en") { $bmpF.Save($cInfo.facesOutDefault, [System.Drawing.Imaging.ImageFormat]::Png) }
    $gF.Dispose()
    $bmpF.Dispose()
  }
}

# 3. Clean Multi-Shot 9:16 Storyboard Contact Sheets (.zh.png and .en.png) + Keyframes + GIF + MP4
foreach ($case in $manifest.cases) {
  $shotCount = $case.shots.Count
  if ($shotCount -lt 1) { continue }
  $lastShotIdx = $shotCount - 1
  if (-not (Test-Path (Join-Path $rawDir ($case.prefix + "_shot_" + $lastShotIdx + ".png")))) { continue }

  $cols = [Math]::Min(4, $shotCount)
  $rows = [Math]::Ceiling($shotCount / 4.0)
  $boardW = 24 + $cols * 340
  $boardH = 20 + $rows * 628

  foreach ($lang in @("zh", "en")) {
    if ($lang -eq "zh" -and -not $case.sheetZh) { continue }
    if ($lang -eq "en" -and -not $case.sheetEn) { continue }

    $bmp = New-Object System.Drawing.Bitmap([int]$boardW, [int]$boardH)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.FillRectangle($bBg, 0, 0, [int]$boardW, [int]$boardH)

    $fontLabel = if ($lang -eq "zh") { $fLabelZh } else { $fLabelEn }

    for ($s = 0; $s -lt $shotCount; $s++) {
      $sh = $case.shots[$s]
      $cIdx = $s % 4
      $rIdx = [Math]::Floor($s / 4)
      $sx = 20 + $cIdx * 340
      $sy = 18 + $rIdx * 626
      Fill-RoundedRect $g $bCard $sx $sy 324 612 14
      Draw-RoundedRect $g $pCardBorder $sx $sy 324 612 14

      $rawShotPath = Join-Path $rawDir ($case.prefix + "_shot_" + $s + ".png")
      $img = [System.Drawing.Image]::FromFile($rawShotPath)
      # Speech bubbles inside all storyboard frames are always in English
      $chatText = $sh.chatEn
      $bx = if ($sh.bubbleX) { [float]$sh.bubbleX } else { 160.0 }
      $by = if ($sh.bubbleY) { [float]$sh.bubbleY } else { 38.0 }

      if ($lang -eq "en" -and $sh.savePath) {
        $shotBmp = New-Object System.Drawing.Bitmap(360, 640)
        $sg = [System.Drawing.Graphics]::FromImage($shotBmp)
        $sg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
        $sg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
        $sg.DrawImage($img, 0, 0, 360, 640)
        Draw-CleanChatBubble $sg ($bx * 1.1) ($by * 1.1) $chatText $fBubbleEn
        $shotBmp.Save($sh.savePath, [System.Drawing.Imaging.ImageFormat]::Png)
        $sg.Dispose()
        $shotBmp.Dispose()
      }

      $g.DrawImage($img, ($sx + 6), ($sy + 6), 312, 554)
      $img.Dispose()

      Draw-CleanChatBubble $g ($sx + $bx) ($sy + $by) $chatText $fBubbleEn

      $label = if ($lang -eq "zh") { $sh.labelZh } else { $sh.labelEn }
      $lsz = $g.MeasureString($label, $fontLabel)
      $g.DrawString($label, $fontLabel, $bDarkText, ($sx + (324 - $lsz.Width) / 2), ($sy + 570))
    }

    $outSheet = if ($lang -eq "zh") { $case.sheetZh } else { $case.sheetEn }
    $bmp.Save($outSheet, [System.Drawing.Imaging.ImageFormat]::Png)
    if ($lang -eq "en" -and $case.sheetDefault) {
      $bmp.Save($case.sheetDefault, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    $g.Dispose()
    $bmp.Dispose()
  }

  $framesPerShot = if ($case.framesPerShot) { [int]$case.framesPerShot } else { 6 }
  $padWidth = if ($case.framePadWidth) { [int]$case.framePadWidth } else { 2 }
  $padFmt = "0" * $padWidth
  $totalFrames = if ($case.totalFrames) { [int]$case.totalFrames } else { $shotCount * $framesPerShot }
  $lastAnimName = $case.prefix + "_anim_" + ($totalFrames - 1).ToString($padFmt) + ".png"

  if (Test-Path (Join-Path $rawDir $lastAnimName)) {
    # Isolate HUD frame staging inside $rawDir so parallel sessions never collide
    $hudDir = Join-Path $rawDir ("hud_" + $case.prefix)
    New-Item -ItemType Directory -Force -Path $hudDir | Out-Null

    # Build per-frame shot lookup supporting variable per-shot frameCount
    $shotIndexByFrame = New-Object int[] $totalFrames
    $cursorF = 0
    for ($si = 0; $si -lt $shotCount; $si++) {
      $fc = if ($case.shots[$si].frameCount) { [int]$case.shots[$si].frameCount } else { $framesPerShot }
      for ($k = 0; $k -lt $fc -and $cursorF -lt $totalFrames; $k++) {
        $shotIndexByFrame[$cursorF] = $si
        $cursorF++
      }
    }
    while ($cursorF -lt $totalFrames) {
      $shotIndexByFrame[$cursorF] = $shotCount - 1
      $cursorF++
    }

    for ($f = 0; $f -lt $totalFrames; $f++) {
      $sIdx = $shotIndexByFrame[$f]
      $sh = $case.shots[$sIdx]
      $bx = if ($sh.bubbleX) { [float]$sh.bubbleX } else { 160.0 }
      $by = if ($sh.bubbleY) { [float]$sh.bubbleY } else { 38.0 }
      $fname = $case.prefix + "_anim_" + $f.ToString($padFmt) + ".png"
      $srcImg = [System.Drawing.Image]::FromFile((Join-Path $rawDir $fname))
      $frameBmp = New-Object System.Drawing.Bitmap(270, 480)
      $fg = [System.Drawing.Graphics]::FromImage($frameBmp)
      $fg.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
      $fg.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
      $fg.DrawImage($srcImg, 0, 0, 270, 480)
      $srcImg.Dispose()

      Draw-CleanChatBubble $fg ($bx * 0.84) ($by * 0.84) $sh.chatEn $fBubbleEn

      $outFrame = Join-Path $hudDir ("frame_" + $f.ToString($padFmt) + ".png")
      $frameBmp.Save($outFrame, [System.Drawing.Imaging.ImageFormat]::Png)
      $fg.Dispose()
      $frameBmp.Dispose()
    }

    $inFps = if ($case.inFps) { [string]$case.inFps } else { "6" }
    $inPattern = Join-Path $hudDir ("frame_%0" + $padWidth + "d.png")
    $palPath = Join-Path $hudDir "palette.png"
    & ffmpeg -y -loglevel error -framerate $inFps -i $inPattern -vf "palettegen=max_colors=128" $palPath
    & ffmpeg -y -loglevel error -framerate $inFps -i $inPattern -i $palPath -lavfi "paletteuse=dither=bayer" $case.gifPath
    if ($case.wavPath -and (Test-Path $case.wavPath)) {
      & ffmpeg -y -loglevel error -framerate $inFps -i $inPattern -i $case.wavPath -c:v libx264 -pix_fmt yuv420p -vf "scale=540:960:flags=lanczos,fps=24" -c:a aac -b:a 128k -shortest $case.mp4Path
    } else {
      $durSec = [Math]::Max(4, [Math]::Round($totalFrames / [double]$inFps))
      & ffmpeg -y -loglevel error -framerate $inFps -i $inPattern -f lavfi -i ("sine=frequency=520:beep_factor=4:duration=" + $durSec) -c:v libx264 -pix_fmt yuv420p -vf "fps=24" -c:a aac -b:a 96k -shortest $case.mp4Path
    }
  }
}
Write-Output "All bilingual .zh.png / .en.png boards, keyframes, GIFs, and MP4s generated!"
