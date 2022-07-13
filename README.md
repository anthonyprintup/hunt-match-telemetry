[![Run Tests CI](https://github.com/anthonyprintup/hunt-match-telemetry/actions/workflows/run-tests.yaml/badge.svg)](https://github.com/anthonyprintup/hunt-match-telemetry/actions/workflows/run-tests.yaml)

# Hunt Match Telemetry
This tool is intended to be used for automatically logging match data provided by the game.

# Installation
- Create a new Python 3.10 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it, <sup><sub>(optional)<sub/></sup>
- run `pip install hunt-match-telemetry` to install the package,
- download the [Steamworks SDK](https://partner.steamgames.com/downloads/steamworks_sdk.zip) and place it in `./resources/steam` as `steamworks_sdk.zip`.

# Instructions
- Run the CLI version of the package by executing `hunt-match-telemetry-cli` in your preferred terminal,
- join a match from the game,
- finish the game (extract, die, etc.),
- return to the lobby screen (or any UI element that updates the last match information).

# Screenshots
<!--suppress CheckImageSize, HtmlDeprecatedAttribute -->
<p align="center">
    Console log:
    <br/>
    <img alt="Console Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/console_log_example.png?raw=true" />
</p>
<p align="center">
    Match log:
    <br/>
    <img alt="Match Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/match_log_example.png?raw=true" />
</p>
<p align="center">
    Player log:
    <br/>
    <img alt="Player Log" src="https://github.com/anthonyprintup/hunt-match-telemetry/blob/main/assets/player_log_example.png?raw=true" width="715"/>
</p>

# Notice of Non-Affiliation and Disclaimer
We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with Crytek GmbH, or any of its subsidiaries or its affiliates.

The official Crytek GmbH website can be found at https://www.crytek.com/.
The official Hunt: Showdown website can be found at https://www.huntshowdown.com/.

All product and company names are the registered trademarks of their original owners. The use of any trade name or trademark is for identification and reference purposes only and does not imply any association with the trademark holder of their product brand.
