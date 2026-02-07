const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        resizable: false,
        maximizable: false,
        height: 575,
        title: "VALORANT Tracker",
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            devTools: false,
            contextIsolation: true,
            nodeIntegration: true
        },
        autoHideMenuBar: true
    });
    win.loadFile("index.html");
}

app.whenReady().then(() => {
    createWindow();
});