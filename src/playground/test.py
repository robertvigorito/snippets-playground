import nuke


original_knob_changed = nuke.callbacks.knobChangeds

nuke.callbacks.knobChangeds = []


# Do something without any knobChangeds being called

nuke.callbacks.knobChangeds = original_knob_changed
