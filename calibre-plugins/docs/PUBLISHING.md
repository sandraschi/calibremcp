# Publishing Guide

How to publish Calibre plugins to the community.

---

## Distribution channel

The canonical channel is **MobileRead Forums**, specifically:
https://www.mobileread.com/forums/forumdisplay.php?f=237

There is no plugin registry, no npm-style index, no review gate.
You create a thread in that subforum, post the ZIP as an attachment, and maintain it there.

GitHub is source hosting and secondary distribution — tag the repo with `calibre-plugin`
so it's discoverable. But the MobileRead thread is the authoritative release channel.

---

## ZIP packaging

The ZIP must be built clean — no .git, no __pycache__, no .pyc, no dev files.
See `docs/LOCAL_TESTING.md` for the `build.py` script.

Naming convention: `PluginName_vX_Y_Z.zip`
Example: `CalibreOpsBridge_v0_1_0.zip`

---

## Version scheme

Calibre uses a tuple: `version = (major, minor, patch)` in `__init__.py`.
There is no semver enforcement — it's just a tuple compared numerically.

Bump strategy:
- Patch: bug fixes, no new features
- Minor: new features, backward-compatible
- Major: breaking change to config/behaviour or minimum_calibre_version bump

---

## MobileRead thread format

A good thread structure:

```
[Thread title]: CalibreOps Bridge — Surface your MCP library AI in Calibre

[SHORT DESCRIPTION]
One paragraph: what does it do, who is it for.

[REQUIREMENTS]
- Calibre 6.0+
- calibreops MCP server running on localhost (sandraschi/calibre-mcp)

[INSTALLATION]
1. Download CalibreOpsBridge_v0_1_0.zip (attached)
2. Calibre → Preferences → Plugins → Load plugin from file
3. Select the ZIP
4. Restart Calibre
5. Toolbar button "CalibreOps" appears

[CONFIGURATION]
Preferences → Plugins → CalibreOps Bridge → Customize
- Server URL (default: http://localhost:10720)
- Result limit
- Timeout

[CHANGELOG]
v0.1.0 (2026-04-xx): Initial release

[ATTACHMENT]
CalibreOpsBridge_v0_1_0.zip
```

---

## License

GPL v3 is the standard for Calibre plugins (consistent with Calibre itself).
Add a `LICENSE` file to the repo and note it in the thread.

---

## Updates

When you release a new version:
1. Edit the first post of the MobileRead thread — update changelog, replace attachment
2. Push the new tagged release to GitHub

There is no auto-update mechanism in Calibre for third-party plugins.
Users re-download and re-install manually (or use the MobileRead forum's notification system).

Some authors add a version-check that pings a GitHub releases API endpoint on startup
and shows a notification if a newer version is available. Optional but appreciated.
