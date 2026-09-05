# ⚽ Football Club Manager — Community Data Packs

> Create, publish and share custom Data Packs for **Football Club Manager**.

---

## 🚀 Quick Start

### 1) Download the Starter Pack

[⬇️ Download Players Starter Pack](https://github.com/ugurcan1881/manager-sim-data-packs/releases/download/starter-v1.0/ManagerSim-Players-Starter.zip)

The starter pack currently includes:

- `manifest.json`
- `players.csv`

More files may be added later for:

- Clubs
- Competitions
- Stadiums
- Logos
- Other supported game data

---

## ✏️ Create Your Mod

Open `players.csv` with Excel, LibreOffice Calc, Google Sheets or another CSV editor.

### Important

- Edit the `name` column.
- **Do not change `playerId`.**
- `playerId` is the permanent ID used by the game.
- Other columns are there to help you identify the correct player.

Example:

```csv
playerId,name,position,nationality
1524,John Smith,ST,Nigeria
```

Change only the name:

```csv
playerId,name,position,nationality
1524,Victor Osimhen,ST,Nigeria
```

When finished, save the CSV.

---

## 📦 Create Your ZIP

Your ZIP should look like this:

```text
My-Data-Pack.zip
├── manifest.json
├── players.csv
├── clubs.csv
├── competitions.csv
├── stadiums.csv
└── images/
```

Not every file is required. Only include files supported by your Data Pack.

> Important: Do not put everything inside an extra folder inside the ZIP.

Correct:

```text
My-Data-Pack.zip
├── manifest.json
└── players.csv
```

Avoid:

```text
My-Data-Pack.zip
└── My-Data-Pack/
    ├── manifest.json
    └── players.csv
```

---

# 🌐 Publish Your Data Pack

Never used GitHub before? Follow these four steps.

### STEP 1 — Create a GitHub Account

Go to:

https://github.com

Create a free account.

---

### STEP 2 — Create a Repository

On GitHub:

**+ → New repository**

Recommended settings:

**Repository name**
```text
football-club-manager-data-pack
```

**Description**
```text
Unofficial community Data Pack for Football Club Manager.
```

Select:

- ✅ Public
- ✅ Add a README file

Then press:

**Create repository**

---

### STEP 3 — Create a Release

Inside your repository:

**Releases → Create a new release**

Example:

**Tag**
```text
v1.0.0
```

**Release title**
```text
2026/27 Data Pack v1.0.0
```

Then upload your Data Pack ZIP in the release assets section.

Press:

**Publish release**

---

### STEP 4 — Submit Your Mod

Copy the URL of your GitHub Release page.

Example:

```text
https://github.com/YourUsername/YourRepository/releases/tag/v1.0.0
```

Then submit it here:

## [📤 SUBMIT YOUR DATA PACK](https://github.com/ugurcan1881/manager-sim-data-packs/issues/new?template=data-pack-submission.yml)

You only need to enter:

- Mod Name
- Author
- Description
- GitHub Release URL

That’s it.

You do **not** need to calculate:

- SHA-256
- File size
- Direct ZIP URL
- Download metadata

Those details can be collected automatically from the GitHub Release.

---

# 🔎 In-Game Data Mod Browser

Approved Data Packs may appear in:

```text
DATA PACKS
→ SEARCH FOR DATA MODS
```

Players can see:

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

Some community Data Packs may appear under **Featured Mods**.

Featured only means the Data Pack is highlighted for easier discovery.

It does **not** mean Football Club Manager owns, licenses or created the third-party content inside that Data Pack.

---

# 🔄 Updating Your Mod

When you release an update:

```text
v1.0.0 → v1.1.0
```

Create a new GitHub Release and upload the new ZIP.

Do not overwrite the old release file.

---

# 🛡️ Community Rules

Data Packs must not contain:

- Malware
- Executable files
- Harmful scripts
- Intentionally misleading files
- Attempts to bypass Data Pack security

Data Packs may be removed if they are:

- Malicious
- Broken
- Misleading
- Abusive
- Incompatible
- Reported for a valid rights complaint
- In violation of community rules

---

# ⚠️ Community Content Disclaimer

Community Data Packs are independently created user-generated content.

Each Data Pack author is responsible for the content they create, upload and distribute.

Football Club Manager does not claim ownership of third-party names, trademarks, logos, images or other materials contained in independently created community Data Packs.

Unless specifically stated otherwise, community Data Packs are **not official Football Club Manager content**.

Listing or featuring a Data Pack does not imply ownership, sponsorship, affiliation, licensing or endorsement of third-party content.

Users choose whether to download and install community Data Packs.

---

# ©️ Copyright & Trademark Complaints

Football Club Manager respects copyright, trademark and other rights holders.

If you believe a listed Data Pack infringes your rights, please submit a report containing:

- Data Pack name
- Link to the affected Data Pack
- Description of the affected content
- Rights you represent
- Contact information
- Relevant supporting information

A reported Data Pack may be reviewed, hidden or removed where appropriate.

---

# 🚩 Report a Data Pack

Report a Data Pack if it is:

- Malicious
- Broken
- Misleading
- Impersonating another creator
- Violating community rules
- Infringing copyright or trademark rights

---

# 🎮 Default Game Data

Football Club Manager includes its own default game data.

Community Data Packs are optional override packages.

Selecting:

```text
NO DATA PACK
```

returns the game to its default data.

---

## ❤️ Community

Create your pack, publish it, submit it and share it with other Football Club Manager players.

**Have fun modding.**
