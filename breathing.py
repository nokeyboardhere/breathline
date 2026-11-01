"""Breathline breathing pattern calculations."""

from dataclasses import dataclass


@dataclass
class BreathingPattern:
    inhale: float
    exhale: float

    @property
    def cycle_duration(self) -> float:
        return self.inhale + self.exhale

    @property
    def breaths_per_minute(self) -> float:
        return 60 / self.cycle_duration


def calculate_pattern(regulation: float, tempo: float) -> BreathingPattern:
    """Calculate breathing durations from two normalized controls."""

    regulation = max(-1.0, min(1.0, regulation))
    tempo = max(-1.0, min(1.0, tempo))

    # Interpolate between calm, balance and energizing patterns.
    if regulation <= 0:
        position = regulation + 1
        inhale = 4.0 + position * -0.5
        exhale = 6.0 + position * -2.5
    else:
        inhale = 3.5 - regulation
        exhale = 3.5 - regulation

    # Scale both phases proportionally.
    multiplier = 1.25 ** (-tempo)

    inhale *= multiplier
    exhale *= multiplier

    # Keep breathing within conservative rate limits.
    cycle = inhale + exhale

    if cycle < 5.0:
        scale = 5.0 / cycle
        inhale *= scale
        exhale *= scale

    if cycle > 15.0:
        scale = 15.0 / cycle
        inhale *= scale
        exhale *= scale

    return BreathingPattern(inhale, exhale)
