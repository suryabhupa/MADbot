# MADbot
MIT Pokerbots 2016 Submission for HU PLO

### MADbotv1.0
First submission; performed averagely when played with other bots during Casino Day 1; bot may have been too aggressive and not started to play less risky when bankroll is far too negative. MADbotv1.0 doesn't consider bets made by opponent and doesn't consider any history. Fixes to be made; consider bets in some way (unclear), and more strongly restrict actions when bankroll is very negative. 

### MADbotv1.1
Only minor tweaks to thresholds were made; MADbotv1.1 is less aggressive, but sufficient stops on behavior after bankroll is negative aren't enforced absolutely, but are stronger. 

### MADbotv1.2
Fixed bugs in both computation of maximum equity and if/else statements. 

### MADbotv1.3
New strategy to only fold or call based on thresholds of equity; if the bot plays the hand after flop comes out, it will play till completion. 

### MADbotv1.4
Same strategy as before; slightly less conserative bot with bounds (that don't seem to work). Uses ``utils.py``. 

### MADbotv1.5
Fixes the bug where bot doesn't initiate bet. Updates thresholds based on previous data. Adds potsize check on preflop and more (controlled) randomness in the strategy decision.
