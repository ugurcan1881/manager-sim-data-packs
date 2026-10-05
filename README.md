# ⚽ Football Club Manager — Community Data Packs

Create, customize and share community Data Packs for **Football Club Manager**.

Data Packs allow players to replace supported default game data with custom names, images and other supported content without modifying the original game database.

---

# 🚀 Quick Start

## 1. Download the Full Starter Pack

[⬇️ DOWNLOAD FULL STARTER PACK](https://github.com/ugurcan1881/manager-sim-data-packs/releases/download/starter-v1.0/Football.Club.Manager.Full-Starter-Pack.zip)

The Full Starter Pack contains the files needed to create a Football Club Manager Data Pack.

It includes supported data such as:

- `manifest.json`
- `players.csv`
- `clubs.csv`
- `competitions.csv`
- `stadiums.csv`
- `images/`

The starter files contain the IDs used by the game so you can easily identify and edit supported game data.

---

# ✏️ Creating Your Data Pack

Extract the Starter Pack ZIP to a folder.

You can edit CSV files using:

- Microsoft Excel
- LibreOffice Calc
- Google Sheets
- Any compatible CSV editor

You only need to change the information you want to customize.

---

## 👤 Players

Player data is stored in:

`players.csv`

Example:

playerId,name,position,nationality
1524,John Smith,ST,Nigeria

You may change supported fields such as the player name.

Example:

playerId,name,position,nationality
1524,Victor Osimhen,ST,Nigeria

### Important

Do **not** change:

`playerId`

The ID is used by the game to identify the correct player.

---

## 🏟️ Clubs

Club data is stored in:

`clubs.csv`

You can use this file to customize supported club information.

### Important

Do **not** change the club ID.

The club ID connects your changes to the correct club inside the game.

---

## 🏆 Competitions

Competition data is stored in:

`competitions.csv`

This may include supported leagues, cups and other competitions.

You may change supported competition information while keeping the original competition ID unchanged.

---

## 🏟 Stadiums

Stadium data is stored in:

`stadiums.csv`

You may customize supported stadium information.

Do **not** change stadium IDs.

---

# 🖼️ Images and Logos

Supported images can be placed inside:

`images/`

Depending on the supported Data Pack structure, images may be used for things such as:

- Club logos
- Competition logos
- Player images
- Stadium images
- Other supported graphics

Follow the file structure included in the Starter Pack.

Do not change IDs or image references unless you know they are supported by the game.

---

# ⚠️ IDs Are Important

Football Club Manager uses permanent IDs to connect Data Pack changes to the correct game data.

Examples include:

playerId
clubId
competitionId
stadiumId

### Never change these IDs.

You should normally change only the editable values connected to those IDs.

For example:

ID = identifies the object
Name = the value your Data Pack overrides

Changing an ID may cause your Data Pack to modify the wrong object or fail to load correctly.

---

# 📄 manifest.json

Every Data Pack must contain:

`manifest.json`

The manifest contains information used by Football Club Manager to identify and load the Data Pack.

Keep the manifest inside the root of your ZIP.

---

# 📦 Creating Your Data Pack ZIP

When you finish editing your Data Pack, create a ZIP file.

Your ZIP should look similar to this:

My-Data-Pack.zip
├── manifest.json
├── players.csv
├── clubs.csv
├── competitions.csv
├── stadiums.csv
└── images/

You do not need to modify every file.

Your Data Pack can contain only the supported files you actually use.

---

## ✅ Correct ZIP Structure

My-Data-Pack.zip
├── manifest.json
├── players.csv
└── clubs.csv

---

## ❌ Incorrect ZIP Structure

Do not place the Data Pack inside another folder inside the ZIP.

Avoid:

My-Data-Pack.zip
└── My-Data-Pack/
    ├── manifest.json
    ├── players.csv
    └── clubs.csv

The Data Pack files should be directly inside the ZIP.

---

# 🌐 Publishing Your Data Pack

Community Data Packs are hosted by their creators.

GitHub Releases are recommended because they provide a public source page and downloadable ZIP file.

If you have never used GitHub before, follow the steps below.

---

# STEP 1 — Create a GitHub Account

Go to:

https://github.com

Create a free GitHub account.

---

# STEP 2 — Create a Repository

On GitHub:

+ → New repository

Example repository name:

football-club-manager-data-pack

Example description:

Unofficial community Data Pack for Football Club Manager.

Recommended settings:

- Public
- Add a README file

Then press:

Create repository

---

# STEP 3 — Create a Release

Inside your repository open:

Releases

Then select:

Create a new release

Example tag:

v1.0.0

Example release title:

2026/27 Data Pack v1.0.0

Upload your finished Data Pack ZIP to the Release assets section.

Example:

My-Football-Data-Pack-v1.0.0.zip

Then press:

Publish release

---

# STEP 4 — Submit Your Data Pack

After publishing your Release, copy the URL of the Release page.

Example:

https://github.com/YourUsername/YourRepository/releases/tag/v1.0.0

Then submit your Data Pack here:

https://github.com/ugurcan1881/manager-sim-data-packs/issues/new?template=data-pack-submission.yml

The submission form asks for:

- Mod Name
- Author
- Description
- GitHub Release URL

The Author field is the display name or nickname that will appear for your Data Pack.

It does not need to be identical to your GitHub username.

---

# 🤖 Automatic Processing

You do not need to manually provide technical download information.

The Football Club Manager Data Pack system can automatically collect and validate information from your GitHub Release, including:

- Release version
- ZIP download URL
- File size
- SHA-256
- Other supported metadata

The submitted ZIP may also be checked for compatibility and unsafe file types before being added to the catalog.

---

# 🔎 In-Game Data Mod Browser

Published community Data Packs may appear inside the Football Club Manager Data Mod Browser.

Players can browse available packs and view information such as:

- Mod name
- Author
- Description
- Version
- File size
- Download count
- Source page

Available actions may include:

- Download
- Update
- Use
- Delete
- View Source

---

# ⭐ Featured Mods

Some community Data Packs may be highlighted under:

Featured Mods

Featured status only means that the Data Pack has been highlighted for easier discovery.

It does not mean Football Club Manager owns, created, licensed or officially endorses third-party content contained inside the Data Pack.

---

# 🔄 Updating Your Data Pack

When you create a new version of your Data Pack, use a new version number.

Example:

v1.0.0
↓
v1.1.0

Create a new GitHub Release for the update.

Example:

v1.1.0

Upload the updated ZIP to that Release.

Whenever possible, keep the version numbers consistent.

Example:

Tag:
v1.1.0

Release title:
2026/27 Data Pack v1.1.0

ZIP:
2026-27-Data-Pack-v1.1.0.zip

This makes updates easier to identify.

---

# 🛡️ Community Rules

Data Packs must not contain:

- Malware
- Executable files
- Harmful scripts
- Malicious code
- Intentionally misleading files
- Files designed to bypass Data Pack security
- Content intended to damage the game or user's device

Data Packs may be removed from the community catalog if they are:

- Malicious
- Broken
- Misleading
- Abusive
- Incompatible
- Impersonating another creator
- Violating community rules
- Subject to a valid copyright, trademark or other rights complaint

---

# ⚠️ Community Content Disclaimer

Community Data Packs are independently created user-generated content.

Each Data Pack author is responsible for the content they create, upload and distribute.

Football Club Manager does not claim ownership of third-party names, trademarks, logos, images or other materials contained in independently created community Data Packs.

Unless specifically stated otherwise, community Data Packs are not official Football Club Manager content.

Listing, displaying or featuring a Data Pack does not imply ownership, sponsorship, affiliation, licensing or endorsement of third-party content.

Players choose whether to download and install community Data Packs.

---

# ©️ Copyright & Trademark Complaints

Football Club Manager respects copyright, trademark and other rights holders.

If you believe a listed Data Pack infringes your rights, a report should include relevant information such as:

- Data Pack name
- Link to the affected Data Pack
- Description of the affected content
- Rights you represent
- Contact information
- Relevant supporting information

A reported Data Pack may be reviewed, hidden or removed where appropriate.

---

# 🚩 Reporting a Data Pack

A Data Pack may be reported if it is:

- Malicious
- Broken
- Misleading
- Impersonating another creator
- Violating community rules
- Infringing copyright or trademark rights
- Distributing content without the necessary rights or permissions

---

# 🎮 Default Game Data

Football Club Manager includes its own default game data.

Community Data Packs are optional override packages.

Installing a Data Pack does not permanently replace the original game database.

Selecting:

NO DATA PACK

returns the game to its default data.

---

# 🔗 Source Transparency

Community Data Packs remain hosted by their creators.

Football Club Manager may provide a link to the original GitHub Release or repository so players can view the source of the Data Pack.

Data Pack authors remain responsible for maintaining their own hosted files and releases.

---

# ❤️ Community

Create your Data Pack.

Customize your football world.

Publish it.

Submit it.

Share it with other Football Club Manager players.

Have fun modding. ⚽
