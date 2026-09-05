# Football Club Manager Data Packs

Community Data Pack registry for **Football Club Manager**.

Here you can download the official starter files, create your own Data Pack and submit it to be listed in the community Data Pack browser.

---

## Create a Player Name Data Pack

Download the starter pack:

### [⬇ Download Players Starter Pack](https://github.com/ugurcan1881/manager-sim-data-packs/releases/download/starter-v1.0/ManagerSim-Players-Starter.zip)

The ZIP contains:

- `manifest.json`
- `players.csv`

The `players.csv` file contains all players with their unique `playerId`.

### Rules

- Only edit the `name` column.
- Do **not** modify `playerId`.
- `playerId` is used by the game to identify each player.
- Other columns are provided to help identify players.
- Editing other informational columns will not change those player attributes in-game.
- Keep `manifest.json` and `players.csv` inside the Data Pack ZIP.

Example:

Before:

```csv
playerId,name,position,nationality
1524,John Smith,ST,Nigeria
