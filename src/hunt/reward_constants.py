# Entry categories for rewards
_BOSS_NAMES: tuple[str, ...] = ("spider", "butcher", "assassin", "scrapbeak")

BOUNTY_CATEGORIES: tuple[str, ...] = (
    "accolade_bad_luck",
    "accolade_clues_found",
    *(f"accolade_found_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_killed_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_killed_{boss_name}_solo" for boss_name in _BOSS_NAMES),
    *(f"accolade_contract_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_clean_sweep_{boss_name}" for boss_name in _BOSS_NAMES),
    "accolade_trophy_extraction_bonus",
    "accolade_quickplay_found_final_clue",
    "accolade_quickplay_wellsprings_found",
    "accolade_quickplay_extracted_artifact")

XP_CATEGORIES: tuple[str, ...] = (
    "accolade_reviver",
    *(f"accolade_banished_{boss_name}" for boss_name in _BOSS_NAMES),
    "accolade_partner_killed",
    "accolade_players_killed",
    "accolade_monsters_killed")

HUNT_DOLLARS_CATEGORY: str = "accolade_found_gold"
BLOODBONDS_CATEGORY: str = "accolade_found_gems"
HUNTER_XP_DESCRIPTOR_NAME: str = "loot hunter xp"
HUNTER_XP_REWARD_TYPE: int = 10
HUNTER_LEVELS_CATEGORY: str = "accolade_hunter_points"
UPGRADE_POINTS_DESCRIPTOR_NAME: str = "loot upgrade points"
BLOODLINE_DESCRIPTOR_NAME: str = "loot bloodline xp"
ASSISTS_CATEGORY: str = "accolade_players_killed_assist"
