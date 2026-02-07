from pyvaloapi import ValorantClient
import time
from threading import Thread
import requests as req
import valorant_defs as defs
from concurrent.futures import ThreadPoolExecutor
import json
import traceback
import re


class Utils:
    def __init__(self):
        while True:
            try:
                self.api = ValorantClient().unofficial_api()
                self.current_user = self.api.get_current_player()
                self.current_user_puuid = self.api.get_current_player_puuid()
                self.weapons = req.get("https://valorant-api.com/v1/weapons").json()[
                    "data"
                ]
                self.player_skin = {}
                self.presence = None
                self.game_state = "MENUS"
                self.pregame_data = {}
                self.match_data = {}
                Thread(target=self.update_presence, daemon=True).start()
                print("Valorant Client has been initialized")
                break
            except:
                print("Init failed retrying in 3 seconds")
                time.sleep(3)

    @staticmethod
    def get_filtered(func, obj):
        return list(filter(func, obj))

    @staticmethod
    def div(a, b, default=0):
        return a / b if b else default

    def get_weapon_by_name(self, name: str):
        return self.get_filtered(
            lambda x: x["displayName"].lower() == name.lower(), self.weapons
        )[0]

    # match detailからkdrとかいろいろだすにda
    def parse_detail(self, puuid: str):
        _histories = self.api.get_match_history(puuid, "competitive", end=5)
        _histories2 = self.api.get_match_history(puuid, None, end=1)
        histories = []
        histories2 = []
        if _histories.get("History") is not None:
            histories = _histories["History"]
        if _histories2.get("History") is not None:
            histories2 = _histories2["History"]
        kills = 0
        deaths = 0
        assists = 0
        total_rounds = 0
        damages = 0
        total_hit = 0
        head_hit = 0
        body_hit = 0
        leg_hit = 0
        level = 0
        set_level = False
        match_count = len(histories)
        playerName = None
        for hist2 in histories2:
            matchID = hist2["MatchID"]
            detail = self.api.get_match_details(matchID)
            if detail.get("players") is None:
                continue
            player = self.get_filtered(
                lambda x: x["subject"] == puuid, detail["players"]
            )[0]
            if not set_level:
                level = player["accountLevel"]
                set_level = True
            if playerName is None:
                playerName = player["gameName"] + "#" + player["tagLine"]
        for hist in histories:
            matchID = hist["MatchID"]
            detail = self.api.get_match_details(matchID)
            if detail.get("players") is None:
                continue
            player = self.get_filtered(
                lambda x: x["subject"] == puuid, detail["players"]
            )[0]
            stats = player["stats"]
            kills += stats["kills"]
            deaths += stats["deaths"]
            assists += stats["assists"]
            round_damage = player["roundDamage"]
            total_rounds += len(round_damage) if round_damage is not None else 0
            damages += sum(d.get("damage") for d in round_damage)
            round_results = detail["roundResults"]
            for result in round_results:
                player_stats = self.get_filtered(
                    lambda x: x["subject"] == puuid, result["playerStats"]
                )[0]
                damages_data = player_stats["damage"]
                for damage in damages_data:
                    head_hit += damage["headshots"]
                    body_hit += damage["bodyshots"]
                    leg_hit += damage["legshots"]
            total_hit = sum([head_hit, body_hit, leg_hit])
            time.sleep(2)

        kd = self.div(kills, deaths, 0)

        print(playerName)
        return {
            "kills": kills,
            "deaths": deaths,
            "name": playerName,
            "assists": assists,
            "kdr": kd,
            "account_level": level,
            "total_rounds": total_rounds,
            "total_damage": damages,
            "average_damage": self.div(damages, total_rounds),
            "total_matches": match_count,
            "head_shots": head_hit,
            "body_shosts": body_hit,
            "leg_shots": leg_hit,
            "total_shots": total_hit,
            "hs": round(self.div(head_hit, total_hit) * 100),
        }

    def parse_mmr(self, puuid):
        mmr = self.api.get_player_mmr(puuid)
        active_season = self.api.get_active_season()[0]
        current_season = active_season["uuid"]
        queue_skills = mmr["QueueSkills"]["competitive"]
        competitive_seasons = queue_skills.get("SeasonalInfoBySeasonID")
        current_competitive_season = None

        peak_tier = 0
        peak_season = current_season
        peak_season_name = active_season["displayName"]
        peak_rank_name = "UNRANKED"
        peak_rank_icon = "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/0/largeicon.png"

        if competitive_seasons is not None:
            current_competitive_season = competitive_seasons.get(current_season)
            sorted_competitive_seasons = sorted(
                competitive_seasons.items(),
                key=lambda x: x[1]["CompetitiveTier"],
                reverse=True,
            )
            peak_competitive_season = sorted_competitive_seasons[0][1]
            peak_season = peak_competitive_season["SeasonID"]
            peak_season_name = re.sub(
                r"EpisodeV(\d+)-\d+",
                r"V\1",
                re.search(
                    r"CompetitiveSeason_(.*?)_DataAsset",
                    self.api.get_competitive_season(peak_season)["assetPath"],
                ).group(1),
            ).replace("_", " ")

            peak_tier = peak_competitive_season["CompetitiveTier"]
            peak_rank_name = defs.competitive_tiers_data[peak_tier]["tierName"]
            peak_rank_icon = defs.competitive_tiers_data[peak_tier]["largeIcon"]

        win_rate = 0
        total_games = 0
        wins = 0
        tier = 0
        rr = 0
        derank_protect_shield = 0
        derank_protect_status = "Empty"
        rank_icon = "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/0/largeicon.png"
        display_name = "UNRANKED"

        if current_competitive_season is not None:
            total_games = current_competitive_season["NumberOfGames"]
            wins = current_competitive_season["NumberOfWins"]
            tier = current_competitive_season["CompetitiveTier"]
            rr = current_competitive_season["RankedRating"]
            win_rate = round(self.div(wins, total_games) * 100)
            rank_icon = defs.competitive_tiers_data[tier]["largeIcon"]
            display_name = defs.competitive_tiers_data[tier]["tierName"]
            derank_protect_status = mmr["DerankProtectedStatus"]
            derank_protect_shield = mmr["DerankProtectedGamesRemaining"]

        return {
            "derank_shield": derank_protect_shield,
            "derank_shield_status": derank_protect_status,
            "display_name": display_name,
            "rank_icon": rank_icon,
            "total_games": total_games,
            "wins": wins,
            "tier": tier,
            "rr": rr,
            "win_rate": win_rate,
            "peak_tier": peak_tier,
            "peak_rank_name": peak_rank_name,
            "peak_rank_icon": peak_rank_icon,
            "peak_season_id": peak_season,
            "peak_season_name": peak_season_name,
        }

    def load_pregame_data(self, gameID, teamID, item):
        try:
            game_data = self.pregame_data[gameID]
            players = game_data["players"]
            i, player = item
            uid = player["Subject"]
            player_data = players.get(uid) if players is not None else None
            stats = player_data.get("stats") if player_data is not None else None
            player_stats = self.parse_detail(uid) if stats is None else stats
            mmr = player_data.get("mmr") if player_data is not None else None
            player_mmr = self.parse_mmr(uid) if mmr is None else mmr
            agentID = player["CharacterID"].lower()
            playerIdentify = player["PlayerIdentity"]
            accountLevel = player_stats["account_level"]
            hideLevel = playerIdentify["HideAccountLevel"]
            hideName = playerIdentify["Incognito"]
            playerName = player_stats["name"]
            agent = defs.agent_data.get(agentID)
            agentObj = (
                agent
                if agent is not None
                else {"displayName": None, "displayIcon": None}
            )
            character_selection_state = player["CharacterSelectionState"]
            self.pregame_data[gameID]["players"].setdefault(uid, {}).update(
                {
                    "uid": uid,
                    "agent_select_status": character_selection_state,
                    "agent_locked": character_selection_state == "locked",
                    "any_agent_selected": character_selection_state != "",
                    "teamID": teamID,
                    "agentID": agentID,
                    "agent_name": agentObj["displayName"],
                    "agent_image": agentObj["displayIcon"],
                    "index": i,
                    "name": playerName,
                    "accountLevel": accountLevel,
                    "hideName": hideName,
                    "hideLevel": hideLevel,
                    "stats": player_stats,
                    "mmr": player_mmr,
                }
            )
            print(f"Loaded {uid}")
        except:
            traceback.print_exc()

    def load_data(self, gameID, item):
        try:
            i, player = item
            uid = player["Subject"]
            player_stats = self.parse_detail(uid)
            player_mmr = self.parse_mmr(uid)
            teamID = player["TeamID"]
            agentID = player["CharacterID"].lower()
            playerIdentify = player["PlayerIdentity"]
            accountLevel = player_stats["account_level"]
            hideLevel = playerIdentify["HideAccountLevel"]
            hideName = playerIdentify["Incognito"]
            playerName = player_stats["name"] if player_stats["name"] is not None else "None"
            agentObj = defs.agent_data[agentID]
            self.match_data[gameID]["players"].setdefault(uid, {}).update(
                {
                    "uid": uid,
                    "teamID": teamID,
                    "agentID": agentID,
                    "agent_name": agentObj["displayName"],
                    "agent_image": agentObj["displayIcon"],
                    "index": i,
                    "name": playerName,
                    "accountLevel": accountLevel,
                    "hideName": hideName,
                    "hideLevel": hideLevel,
                    "skin": self.player_skin[uid],
                    "stats": player_stats,
                    "mmr": player_mmr,
                }
            )
            print(f"Loaded {uid}")
        except:
            traceback.print_exc()

    # ４秒ごとにpresenceあぷで ついでにpregameのデータとingameのデータもとる
    def update_presence(self):
        while True:
            try:
                self.presence = self.api.wait_presence()
                self.game_state = self.api.get_game_state(self.presence)
                state = self.game_state

                if state == "MENUS":
                    pass
                elif state == "INGAME":
                    gameID = self.api.get_current_match_id()
                    if self.match_data.get(gameID) is not None:
                        continue
                    game = self.api.get_current_match_info(gameID)
                    if game.get("MatchID") is None:
                        continue
                    players = game["Players"]
                    # { playerID: "name#1234" }
                    self.match_data.setdefault(gameID, {})
                    self.match_data[gameID].setdefault("players", {})
                    print("Loading players skin...")
                    self.update_skin(self.api.get_current_match_loadout(gameID))
                    print("Loaded skins")
                    print("Loading player data")
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        for item in enumerate(players):
                            executor.submit(self.load_data, gameID, item)
                    print("Loaded player data")
                elif state == "PREGAME":
                    gameID = self.api.get_current_pregame_id()
                    game = self.api.get_pregame_status(gameID)
                    if game.get("ID") is None:
                        continue
                    players = game["AllyTeam"]["Players"]
                    teamID = game["AllyTeam"]["TeamID"]
                    # { playerID: "name#1234" }
                    self.pregame_data.setdefault(gameID, {})
                    self.pregame_data[gameID].setdefault("players", {})
                    print("Loading player data")
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        for item in enumerate(players):
                            executor.submit(
                                self.load_pregame_data,
                                gameID,
                                teamID,
                                item,
                            )
                    print("Loaded player data")
                    pass
            except:
                traceback.print_exc()
            time.sleep(4 if state != "PREGAME" else 2)

    # プレイヤーのスキン取得
    def update_skin(self, loadout):
        for weapon in loadout["Loadouts"]:
            p_loadout = weapon["Loadout"]
            pid = p_loadout["Subject"]
            if len(pid) > 0:
                for d in defs.weaponID_maps:
                    for k, v in d.items():
                        skinID = p_loadout["Items"][v]["Sockets"][
                            "bcef87d6-209b-46c6-8b19-fbe40bd95abc"
                        ]["Item"]["ID"]
                        chromaID = p_loadout["Items"][v]["Sockets"][
                            "3ad1b2b2-acdb-4524-852f-954a76ddae0a"
                        ]["Item"]["ID"]
                        skinObj = {
                            "displayName": "Vandal"
                        }
                        hasSkin = False
                        try:
                            skinObj = self.get_filtered(
                                lambda x: x["uuid"] == skinID, defs.weapon_data[v]["skins"]
                            )[0]
                            hasSkin = True
                        except:
                            pass

                        chromaObj = {
                            "fullRender": "https://media.valorant-api.com/weaponskinchromas/19629ae1-4996-ae98-7742-24a240d41f99/fullrender.png",
                            "displayName": "Vandal",
                        }
                        if hasSkin:
                            try:
                                chromaObj = self.get_filtered(
                                    lambda x: x["uuid"] == chromaID, skinObj["chromas"]
                                )[0]
                            except:
                                pass

                        self.player_skin.setdefault(pid, {}).setdefault(k, {}).update(
                            {
                                "chroma": chromaID,
                                "skinId": skinID,
                                "skinName": skinObj["displayName"],
                                "displayName": chromaObj["displayName"],
                                "skinImage": chromaObj["fullRender"],
                            }
                        )

# we
utils = Utils()
