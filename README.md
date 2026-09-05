# Football Club Manager Data Packs

Community Data Pack registry for **Football Club Manager**.

This repository allows players to create, share and discover community-made Data Packs for Football Club Manager.

Data Packs are optional and are not required to play the game.

---

# 📥 Create a Player Name Data Pack

Download the official starter template:

## [⬇️ Download Players Starter Pack](https://github.com/ugurcan1881/manager-sim-data-packs/releases/download/starter-v1.0/ManagerSim-Players-Starter.zip)

The ZIP contains:

- `manifest.json`
- `players.csv`

The `players.csv` file contains the game's players together with their unique `playerId` and additional information that can help identify them.

---

## Editing `players.csv`

The CSV contains columns such as:

```text
playerId
name
position
secondaryPosition
birthDate
nationality
heightCm
overall
potential
```

### Important Rules

- Only edit the `name` column when creating a Player Name Data Pack.
- **Never modify `playerId`.**
- `playerId` is the permanent identifier used by the game.
- Other columns are provided to help identify players.
- Editing informational columns does not change those attributes in-game.
- Do not remove required columns.
- Keep `manifest.json` and `players.csv` inside the Data Pack ZIP.

---

## Example

Before:

```csv
playerId,name,position,nationality
1524,John Smith,ST,Nigeria
```

After:

```csv
playerId,name,position,nationality
1524,Victor Osimhen,ST,Nigeria
```

When you are finished, save the CSV and create the ZIP again.

You can test your Data Pack directly in the game:

**Data Packs → Import ZIP**

---

# 📤 Submit Your Mod

Finished your Data Pack and want to share it with other Football Club Manager players?

## [📤 SUBMIT YOUR DATA PACK](https://github.com/ugurcan1881/manager-sim-data-packs/issues/new?template=data-pack-submission.yml)

The submission form will ask for information such as:

- Data Pack name
- Author / creator name
- Version
- Description
- ZIP download URL
- Source page
- Game version
- Database version
- SHA-256 hash

Submissions may be reviewed before they are added to the public Data Pack catalog.

Submitting a Data Pack does **not** guarantee that it will be listed.

---

# 🔎 Community Data Packs

Approved Data Packs may appear in the in-game:

**Search Data Packs**

section.

Players may be able to:

- Search available Data Packs
- See the Data Pack name
- See the author
- View the original source
- View the version
- View the download size
- Inspect information about the package
- Download the package
- Install and use it in-game
- Delete installed packages
- Return to the default game database at any time

Community Data Packs are optional.

The default Football Club Manager database works without installing any Data Pack.

---

# ⭐ Featured Data Packs

Some community Data Packs may be marked as **Featured**.

Featured status only means that the package has been selected for easier discovery.

Featured status does **not** mean that Football Club Manager owns, created, licenses, sponsors or endorses third-party content contained inside the Data Pack.

Featured status may be removed at any time.

---

# 🔐 Data Pack Safety

Football Club Manager Data Packs are designed to contain data and supported image files only.

Data Packs must not contain executable code.

Unsupported or potentially dangerous file types may be rejected by the game.

Packages containing malicious content, executable files or attempts to bypass the Data Pack security system may be permanently removed from the catalog.

Data Packs may also be removed if they:

- Contain malicious files
- Attempt to execute code
- Contain intentionally misleading information
- Are corrupted or unusable
- Abuse the Data Pack system
- Violate community rules
- Impersonate another creator
- Receive a valid copyright, trademark or other rights complaint

---

# 👤 Data Pack Author Responsibility

Each Data Pack is created and distributed by its respective community author.

By submitting a Data Pack, the author confirms that they are responsible for the content they upload and distribute.

This includes, where applicable:

- Player names
- Club names
- Competition names
- Logos
- Images
- Trademarks
- Graphics
- Other third-party content

Authors should only distribute content they have the necessary rights or permission to distribute.

Football Club Manager may reject or remove any Data Pack at its discretion.

---

# ⚠️ Community Content Disclaimer

Community Data Packs are independently created user-generated content.

Football Club Manager does not claim ownership of third-party names, trademarks, logos, images or other materials contained in independently created community Data Packs.

Unless specifically stated otherwise, community Data Packs are not created by Football Club Manager and are not official game content.

The availability of a Data Pack in the community catalog does not imply ownership, sponsorship, affiliation, licensing or endorsement by Football Club Manager.

Users choose whether to download and install community Data Packs.

Data Pack authors are responsible for the content they distribute.

---

# ©️ Copyright & Trademark Complaints

Football Club Manager respects the rights of copyright owners, trademark owners and other rights holders.

If you are a rights holder or an authorized representative and believe that a community Data Pack contains material that infringes your rights, you may request that the package be reviewed.

Please provide:

- The name of the affected Data Pack
- The content you believe infringes your rights
- The rights you represent
- A link to the affected package
- Your contact information
- Any relevant supporting information

After receiving a valid complaint, the affected Data Pack may be reviewed, hidden or removed from the community catalog.

---

# 🚩 Report a Data Pack

If you find a Data Pack that is:

- Malicious
- Broken
- Misleading
- Impersonating another creator
- Infringing copyright or trademarks
- Violating the community rules

please report it through this repository.

Reported Data Packs may be investigated and removed when appropriate.

---

# 🗑️ Removal Policy

Football Club Manager reserves the right to remove a Data Pack from the public catalog at any time.

A package may be removed because of:

- Security concerns
- Technical problems
- Author request
- Valid rights-holder complaint
- Community guideline violations
- Abuse of the distribution system
- Compatibility problems
- Misleading information

Removing a Data Pack from the public catalog prevents new users from discovering it through the official Data Pack browser.

---

# 🔄 Updates

Data Pack authors may publish updated versions of their packages.

Updates should use the same Data Pack identity whenever possible so players can receive the correct update.

Authors should update:

- Version number
- Download URL
- File size
- SHA-256
- Supported game version
- Supported database version

when publishing a new package version.

---

# 🎮 Default Game Database

Football Club Manager includes its own default database.

Community Data Packs operate as an optional override layer and do not permanently modify the original game database.

Selecting:

**NO DATA PACK**

returns the game to its default data.

---

# ❤️ Community

The Data Pack system exists to allow Football Club Manager players to customize their game and share their creations with the community.

Thank you to everyone who creates, tests and shares Data Packs.
