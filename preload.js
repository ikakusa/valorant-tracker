const { contextBridge } = require("electron");
const axios = require("axios");

contextBridge.exposeInMainWorld("api", {
    getGameState: async () => {
        const res = await axios.get("http://127.0.0.1:5000/get-game-state");
        return res.data.result;
    },
    getMatchData: async () => {
        const res = await axios.get("http://127.0.0.1:5000/get-match-data");
        return res.data.result;
    },
    getPregameData: async () => {
        const res = await axios.get("http://127.0.0.1:5000/get-pregame-data");
        return res.data.result;
    },
    getCurrentMatchID: async () => {
        const res = await axios.get("http://127.0.0.1:5000/get-current-match-id");
        return res.data.result;
    },
    getCurrentPregameID: async () => {
        const res = await axios.get("http://127.0.0.1:5000/get-current-pregame-id");
        return res.data.result;
    }
});