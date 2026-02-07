const weaponSelect = document.getElementById("weapon-select");
let selectedWeapon = null;

// Ally: #19e0a4 | Enemy: #c91e3e

async function updateTracker() {
    const state = await api.getGameState();
    if (state === "MENUS") return;

    const matchData = state === "INGAME" ? await api.getMatchData() : await api.getPregameData();
    const currentMatchID = state === "INGAME" ? await api.getCurrentMatchID() : await api.getCurrentPregameID();
    const match = matchData[currentMatchID];

    const container = document.getElementById("players-container");
    container.innerHTML = "";
    const players = match.players;

    if (state === "INGAME") {
        const weapons = Object.values(players)[0].skin;

        if (weaponSelect.options.length === 0) {
            Object.keys(weapons).forEach(weapon => {
                const option = document.createElement("option");
                option.value = weapon;
                option.textContent = weapon.charAt(0).toUpperCase() + weapon.slice(1);
                weaponSelect.appendChild(option);
            });
        }

        if (!selectedWeapon) {
            selectedWeapon = Object.keys(weapons)[0];
            weaponSelect.value = selectedWeapon;
        }

        weaponSelect.value = selectedWeapon;

        weaponSelect.onchange = (e) => {
            selectedWeapon = e.target.value;
            updateWeaponImages();
        };
    }

    const sorted_players = Object.values(players).sort((a, b) => {
        if (a.teamID === b.teamID) return 0;
        if (a.teamID === "Blue") return -1;
        return 1;
    });

    Object.values(sorted_players).forEach(player => {
        const teamID = player.teamID;
        const any_agent_selected = state === "PREGAME" ? player.any_agent_selected : true;
        const agent_locked = state === "PREGAME" ? player.agent_locked : false;
        const color = state === "PREGAME" ? agent_locked ? "#19e0a4" : "#2e2e2e" : teamID === "Red" ? "#c91e3e" : "#19e0a4";
        const card = document.createElement("div");
        card.className = "player-card";

        const leftDiv = document.createElement("div");
        leftDiv.className = "player-left";

        const agentDiv = document.createElement("div");
        agentDiv.className = "agent-icon-container";
        agentDiv.style.backgroundColor = color;
        const agentImg = document.createElement("img");
        agentImg.src = player.agent_image;

        const tooltipAgent = document.createElement("div");
        tooltipAgent.className = "tooltip";
        tooltipAgent.textContent = player.agent_name;

        if (any_agent_selected) {
            agentDiv.appendChild(agentImg);
            agentDiv.appendChild(tooltipAgent);
        }
        const levelDiv = document.createElement("div");
        levelDiv.className = "agent-level";
        levelDiv.textContent = player.stats.account_level === 0 ? "-" : player.stats.account_level;
        agentDiv.appendChild(levelDiv);

        const nameContainer = document.createElement("div");
        nameContainer.className = "name-container";

        const rankDiv = document.createElement("div");
        rankDiv.className = "rank-icon-container";

        const rankInfoContainer = document.createElement("div");
        rankInfoContainer.className = "rank-info-container";

        const rankImgDiv = document.createElement("div");
        rankImgDiv.className = "rank-icon-div";
        const rankImg = document.createElement("img");
        rankImg.className = "rank-icon"
        rankImg.src = player.mmr.rank_icon;
        rankImgDiv.appendChild(rankImg);

        const tooltipRank = document.createElement("div");
        tooltipRank.className = "tooltip";
        tooltipRank.textContent = player.mmr.display_name;
        rankImgDiv.appendChild(tooltipRank);

        const playerName = document.createElement("span");
        playerName.className = "player-name";
        playerName.innerHTML = player.name;

        const rankInfo = document.createElement("div");
        rankInfo.className = "rank-rr-info";

        const rrText = document.createElement("span");
        rrText.className = "rr-text";
        rrText.innerHTML = `${player.mmr.rr} RR`;

        const peakContainer = document.createElement("div");
        peakContainer.className = "peak-rank-container";

        const peakText = document.createElement("span");
        peakText.className = "peak-text";
        peakText.innerHTML = "Peak ";

        const peakRankIconDiv = document.createElement("div");
        peakRankIconDiv.className = "peak-rank-icon-div";
        const peakRankIcon = document.createElement("img");
        peakRankIcon.src = player.mmr.peak_rank_icon;
        const tooltipPeakRank = document.createElement("div");
        tooltipPeakRank.className = "tooltip";
        tooltipPeakRank.textContent = `${player.mmr.peak_rank_name} // ${player.mmr.peak_season_name}`;
        peakRankIconDiv.appendChild(peakRankIcon);
        peakRankIconDiv.appendChild(tooltipPeakRank);

        peakContainer.appendChild(peakText);
        peakContainer.appendChild(peakRankIconDiv);

        rankInfo.appendChild(rrText);
        rankInfo.appendChild(peakContainer);

        nameContainer.appendChild(playerName);

        const rankInfoWrapper = document.createElement("div");
        rankInfoWrapper.className = "rank-info-wrapper";

        rankInfoWrapper.appendChild(rankImgDiv);
        rankInfoWrapper.appendChild(rankInfo);
        rankInfoContainer.appendChild(rankInfoWrapper);

        const kdr = (player.stats.kdr).toFixed(2);
        const kills = player.stats.kills;
        const deaths = player.stats.deaths;
        const total_games = player.stats.total_matches;
        const hsPct = player.stats.hs
        const winRate = player.mmr.win_rate;
        const total_competitive = player.mmr.total_games;
        const total_wins = player.mmr.wins;
        const total_loses = total_competitive - total_wins;

        const statsDiv = document.createElement("div");
        statsDiv.className = "player-stats";

        const kdDiv = document.createElement("div");
        kdDiv.className = "kd-div";
        const kdText = document.createElement("span");
        kdText.textContent = `K/D: ${kdr}`;
        const kdInfoText = document.createElement("span");
        kdInfoText.style.fontSize = "18.5px";
        kdInfoText.textContent = `${kills} / ${deaths}`;
        kdDiv.appendChild(kdText);
        kdDiv.appendChild(kdInfoText);

        const tooltipKD = document.createElement("div");
        tooltipKD.className = "tooltip";
        tooltipKD.textContent = `Last ${total_games} games`;
        kdDiv.appendChild(tooltipKD);

        statsDiv.appendChild(kdDiv);

        const statsDiv2 = document.createElement("div");
        statsDiv2.className = "player-stats2";

        const winDiv = document.createElement("div");
        winDiv.className = "win-div";
        const winText = document.createElement("span");
        winText.textContent = `Win%: ${winRate}%`;
        const winInfoText = document.createElement("span");
        winInfoText.style.fontSize = "18.5px";
        winInfoText.textContent = `${total_wins} / ${total_loses}`;
        winDiv.appendChild(winText);
        winDiv.appendChild(winInfoText);

        const tooltipWin = document.createElement("div");
        tooltipWin.className = "tooltip";
        tooltipWin.textContent = `${total_wins} Wins ${total_loses} Loses`;
        winDiv.appendChild(tooltipWin);

        statsDiv2.appendChild(winDiv);

        const statsDiv3 = document.createElement("div");
        statsDiv3.className = "player-stats2";

        const hsDiv = document.createElement("div");
        hsDiv.className = "hs-div";
        const hsText = document.createElement("span");
        hsText.textContent = `HS%: ${hsPct}%`;
        const hsInfoText = document.createElement("span");
        hsInfoText.style.fontSize = "18.5px";
        hsInfoText.textContent = `${player.stats.head_shots} / ${player.stats.total_shots}`;
        hsDiv.appendChild(hsText);
        hsDiv.appendChild(hsInfoText);

        const tooltipHS = document.createElement("div");
        tooltipHS.className = "tooltip";
        tooltipHS.textContent = `${player.stats.head_shots} Head shots / ${player.stats.total_shots} Shots`;
        hsDiv.appendChild(tooltipHS);

        statsDiv3.appendChild(hsDiv);

        //`K/D ${kdr} | HS%: ${hsPct}% | Win%: ${winRate}%`;

        rankInfoContainer.appendChild(statsDiv);
        rankInfoContainer.appendChild(statsDiv2);
        rankInfoContainer.appendChild(statsDiv3);

        rankDiv.appendChild(nameContainer);
        rankDiv.appendChild(rankInfoContainer);

        leftDiv.appendChild(agentDiv);
        leftDiv.appendChild(rankDiv);

        card.appendChild(leftDiv);

        if (state === "INGAME") {
            const weaponWrapper = document.createElement("div");
            weaponWrapper.className = "weapon-wrapper";

            const weaponImg = document.createElement("img");
            weaponImg.className = "weapon-skin";
            const weaponKey = selectedWeapon || Object.keys(player.skin)[0];
            weaponImg.src = player.skin[weaponKey].skinImage;

            const tooltipSkin = document.createElement("div");
            tooltipSkin.className = "tooltip";
            tooltipSkin.textContent = player.skin[weaponKey].displayName;

            weaponWrapper.appendChild(weaponImg);
            weaponWrapper.appendChild(tooltipSkin);

            const infoDiv = document.createElement("div");
            infoDiv.className = "player-info";

            infoDiv.appendChild(weaponWrapper);
            card.appendChild(infoDiv);
        }

        container.appendChild(card);
    });
}

function updateWeaponImages() {
    const cards = document.querySelectorAll(".player-card");
    const players = Object.values(matchData[Object.keys(matchData)[0]].players);

    cards.forEach((card, idx) => {
        const img = card.querySelector(".weapon-skin");
        if (img && players[idx].skin[selectedWeapon]) {
            img.src = players[idx].skin[selectedWeapon].skinImage;
        }
    });
}

setInterval(updateTracker, 5000);
updateTracker();