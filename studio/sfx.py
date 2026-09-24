"""Original interface and cinematic sound effects, synthesised with FFmpeg: no licence, no cost.

Writes WAV files into media/<folder>/audio/sfx/. Storyboard shots reference them via `sfx: [...]`.
"""
from __future__ import annotations

from . import config
from .media_tools import run

# name -> aevalsrc expression and duration (seconds). t = time, all mono at 48 kHz.
RECIPES = {
    # two short buzzy error tones
    "ui_error.wav": ("0.35*sgn(sin(2*PI*196*t))*(lt(t,0.12)+between(t,0.2,0.32))*exp(-6*mod(t,0.2))", 0.45),
    # descending two-note "access denied"
    "ui_deny.wav": ("0.4*sin(2*PI*(if(lt(t,0.18),660,440))*t)*exp(-5*mod(t,0.18))", 0.5),
    # soft scan chime (rising)
    "ui_scan.wav": ("0.3*sin(2*PI*(520+900*t)*t)*exp(-4*t)", 0.6),
    # bright two-note unlock chime
    "ui_unlock.wav": ("0.35*(sin(2*PI*784*t)*lt(t,0.16)+sin(2*PI*1175*t)*gte(t,0.16))*exp(-3.5*mod(t,0.16))", 0.9),
    # door latch click
    "door_click.wav": ("0.8*(random(0)-0.5)*exp(-120*t)+0.4*sin(2*PI*140*t)*exp(-40*t)", 0.15),
    # electrical crackle for the lens flicker
    "lens_crackle.wav": ("0.5*(random(0)-0.5)*gt(sin(2*PI*23*t),0.6)*exp(-1.5*t)+0.05*sin(2*PI*7000*t)*exp(-2*t)", 1.4),
    # rising digital hum as a new lens powers on
    "lens_boot.wav": ("0.3*sin(2*PI*(260*t+450*t*t))*min(1,t*3)*exp(-0.8*t)+0.08*sin(2*PI*3520*t)*gt(t,1.1)*exp(-4*(t-1.1))", 1.8),
    # elevator arrival ding
    "elevator_ding.wav": ("0.35*(sin(2*PI*880*t)+0.6*sin(2*PI*1320*t))*exp(-2.2*t)", 1.6),
    # low cinematic hit for the reveal (the Twist Villa sting)
    "sting.wav": ("0.9*sin(2*PI*(55-20*t)*t)*exp(-1.6*t)+0.25*(random(0)-0.5)*exp(-8*t)", 2.8),
    # glass shimmer for the mirror flash
    "mirror_shimmer.wav": ("0.25*(sin(2*PI*2093*t)+sin(2*PI*2637*t)+sin(2*PI*3136*t))*exp(-3*t)", 1.2),
}


def make_sfx(slug: str) -> list[str]:
    out = config.media_dir(slug) / "audio" / "sfx"
    out.mkdir(parents=True, exist_ok=True)
    made = []
    for name, (expr, dur) in RECIPES.items():
        run(["-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={dur}", "-af", "afade=t=out:st="
             f"{max(dur - 0.05, 0):.2f}:d=0.05", "-ac", "1", str(out / name)])
        made.append(name)
    return made
