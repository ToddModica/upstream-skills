---
name: playwright-browser
description: Drive a real browser through Microsoft's Playwright MCP server. Use when a task needs a page opened or read in a browser, form filling, clicking through a logged-in or JavaScript-heavy site, checking console errors or network requests, or capturing screenshots of a live page. Firefox is the default browser.
---

# Playwright Browser

The `playwright` MCP server exposes Microsoft's Playwright MCP over stdio. It drives a real browser window, not a headless HTTP client, so JavaScript sites, logins, and visual layout behave as they do for a person.

## Loop

1. `browser_navigate` to the URL.
2. `browser_snapshot` to read the accessibility tree. Element references (`e12`, ...) come from this snapshot.
3. Act with `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option`, `browser_press_key`, or `browser_hover`.
4. Re-snapshot after anything that changes the DOM. Old references stop resolving, and a stale one fails instead of clicking the wrong node.
5. Verify the result with `browser_snapshot`, `browser_wait_for`, or `browser_take_screenshot`.

`browser_find` locates an element without capturing the whole tree and is cheaper when only one control is needed. `browser_evaluate` runs JavaScript for values the tree does not expose; prefer the tree first.

## Tools

| Need | Tool |
|---|---|
| Load, go back, switch tabs | `browser_navigate`, `browser_navigate_back`, `browser_tabs` |
| Inspect the page | `browser_snapshot`, `browser_find`, `browser_console_messages`, `browser_network_requests`, `browser_network_request` |
| Interact | `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option`, `browser_press_key`, `browser_hover`, `browser_drag`, `browser_file_upload`, `browser_drop` |
| Wait and confirm | `browser_wait_for`, `browser_take_screenshot` |
| Page control | `browser_resize`, `browser_emulate_media`, `browser_handle_dialog`, `browser_evaluate`, `browser_run_code_unsafe` |

## Settings

`.mcp.json` pins the npm version and selects the browser:

```json
"args": ["-y", "@playwright/mcp@0.0.85", "--browser=firefox"]
```

- Change `--browser=firefox` to `chromium`, `webkit`, or `msedge` to switch engines. Playwright drives its own browser builds; a system-installed Firefox or Chrome is not reused.
- Add `--headless` for unattended runs, or `--isolated` to discard the profile after each session.
- The profile persists between sessions, so cookies and logins survive a restart of the server. Add `--isolated` when a task must start clean.
- `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright` routes the browser download through a mirror when the default CDN is slow or blocked.

## Notes

- Screenshots and downloads are written under the server's working directory. Pass an explicit path in `browser_take_screenshot`, and never assume a path is writable outside it.
- Report the page state from the snapshot, not from what the URL suggests. If a navigation times out, say which URL failed and what the snapshot showed.
- Keep credentials out of prompts and out of screenshots; ask the user to type passwords into the browser window instead of filling them from a value in the conversation.
