#!/usr/bin/env python3
"""Generate assets/banner.svg — the animated README banner.

Shares outlined wordmark geometry with make_wordmark.py so the wordmark never
suffers the font-fallback gap. The wordmark is centered on a 1280x420 dark
canvas with chart motifs and SMIL animations (which play in GitHub READMEs).
"""
import make_wordmark as wm

W, H = 1280, 420


def build_banner():
    # Light-on-dark wordmark geometry, built at x0=0 then centered.
    g = wm.build("#F8FAFC", light=True, x0=0)
    edge = g["right_edge"]
    wm_x = (W - edge) / 2  # center horizontally
    wm_y = 60              # top of the 130-tall wordmark band within the canvas

    tail_total = sum(
        ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        for (x1, y1), (x2, y2) in zip(g["tail_pts"], g["tail_pts"][1:])
    )

    wordmark = f'''
  <g transform="translate({wm_x:.1f},{wm_y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="0.5s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" additive="sum"
                      from="0 18" to="0 0" dur="0.7s" begin="0.5s" fill="freeze"
                      calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
    {g["axis"]}
    {g["anyv"]}
    {g["stem"]}
    <circle cx="{g["i_cx"]:.1f}" cy="33" r="11.5" fill="#4269d0" stroke="#03050C" stroke-width="3">
      <animate attributeName="r" from="11.5" to="13.5" dur="1.6s" begin="2.2s"
               repeatCount="indefinite" values="11.5;13.5;11.5" keyTimes="0;0.5;1"/>
    </circle>
    {g["z"]}
    <g stroke-dasharray="{tail_total:.1f}" stroke-dashoffset="{tail_total:.1f}">
      <animate attributeName="stroke-dashoffset" from="{tail_total:.1f}" to="0" dur="0.7s" begin="1.0s" fill="freeze"/>
      {g["tail_poly"]}
    </g>
    <circle cx="{g["tail_pts"][-1][0]:.1f}" cy="46" r="6.5" fill="#3ca951" stroke="#03050C" stroke-width="2.5" opacity="0">
      <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="1.6s" fill="freeze"/>
    </circle>
  </g>'''

    bars = '''
  <g transform="translate(96,0)">
    <rect x="0" y="270" width="34" height="0" rx="4" fill="#4269d0">
      <animate attributeName="height" from="0" to="70" dur="0.7s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
      <animate attributeName="y" from="270" to="200" dur="0.7s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
    </rect>
    <rect x="46" y="270" width="34" height="0" rx="4" fill="#6cc5b0">
      <animate attributeName="height" from="0" to="120" dur="0.7s" begin="0.32s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
      <animate attributeName="y" from="270" to="150" dur="0.7s" begin="0.32s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
    </rect>
    <rect x="92" y="270" width="34" height="0" rx="4" fill="#3ca951">
      <animate attributeName="height" from="0" to="92" dur="0.7s" begin="0.44s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
      <animate attributeName="y" from="270" to="178" dur="0.7s" begin="0.44s" fill="freeze" calcMode="spline" keySplines="0.2 0.7 0.2 1"/>
    </rect>
  </g>'''

    right = '''
  <g transform="translate(940,150)">
    <path d="M0 120 L40 95 L40 120 Z M40 95 L88 105 L88 120 L40 120 Z M88 105 L140 60 L140 120 L88 120 Z M140 60 L196 26 L196 120 L140 120 Z"
          fill="url(#b-area)" opacity="0">
      <animate attributeName="opacity" from="0" to="1" dur="0.8s" begin="1.1s" fill="freeze"/>
    </path>
    <polyline points="0,120 40,95 88,105 140,60 196,26" fill="none" stroke="url(#b-grad)"
              stroke-width="5" stroke-linecap="round" stroke-linejoin="round"
              stroke-dasharray="320" stroke-dashoffset="320">
      <animate attributeName="stroke-dashoffset" from="320" to="0" dur="1.1s" begin="0.9s" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
    </polyline>
    <g fill="#03050C" stroke-width="3">
      <circle cx="40" cy="95" r="6" stroke="#4269d0"><animate attributeName="r" from="0" to="6" dur="0.3s" begin="1.4s" fill="freeze"/></circle>
      <circle cx="88" cy="105" r="6" stroke="#6cc5b0"><animate attributeName="r" from="0" to="6" dur="0.3s" begin="1.55s" fill="freeze"/></circle>
      <circle cx="140" cy="60" r="6" stroke="#6cc5b0"><animate attributeName="r" from="0" to="6" dur="0.3s" begin="1.7s" fill="freeze"/></circle>
      <circle cx="196" cy="26" r="7" fill="#3ca951" stroke="#FFFFFF"><animate attributeName="r" from="0" to="7" dur="0.35s" begin="1.85s" fill="freeze"/></circle>
    </g>
  </g>'''

    tagline = '''
  <text x="640" y="362" text-anchor="middle" fill="#9696a0"
        font-family="'Helvetica Neue',Helvetica,Arial,sans-serif" font-size="22" font-weight="400" letter-spacing="3" opacity="0">
    AI-NATIVE DATA VISUALIZATION
    <animate attributeName="opacity" from="0" to="1" dur="0.8s" begin="1.8s" fill="freeze"/>
  </text>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="anyviz — AI-native data visualization spec and skill library">
  <title>anyviz</title>
  <desc>Animated banner: the anyviz wordmark with live chart motifs (bars, trend line, scatter, area) on a dark canvas.</desc>
  <defs>
    <linearGradient id="av-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4269d0"/><stop offset="55%" stop-color="#6cc5b0"/><stop offset="100%" stop-color="#3ca951"/>
    </linearGradient>
    <linearGradient id="b-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4269d0"/><stop offset="55%" stop-color="#6cc5b0"/><stop offset="100%" stop-color="#3ca951"/>
    </linearGradient>
    <radialGradient id="b-glow" cx="50%" cy="42%" r="60%">
      <stop offset="0%" stop-color="#4269d0" stop-opacity="0.16"/><stop offset="70%" stop-color="#03050C" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="b-area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#4269d0" stop-opacity="0.30"/><stop offset="100%" stop-color="#4269d0" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="#03050C"/>
  <rect width="{W}" height="{H}" fill="url(#b-glow)"/>
  <g stroke="#FFFFFF" stroke-opacity="0.04" stroke-width="1">
    <line x1="0" y1="105" x2="{W}" y2="105"/><line x1="0" y1="210" x2="{W}" y2="210"/><line x1="0" y1="315" x2="{W}" y2="315"/>
  </g>{bars}{right}{wordmark}{tagline}
</svg>
'''


if __name__ == "__main__":
    open("assets/banner.svg", "w").write(build_banner())
    print("wrote assets/banner.svg")
