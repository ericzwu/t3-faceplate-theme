# Faceplate

A T3 Code theme styled like a piece of hardware: a satin plastic shell, the chat on a screen set behind a bezel, and
keys, faders and slide switches for controls. Light and dark modes follow the app's setting.

| Light | Dark |
|---|---|
| ![Light mode](preview/light.webp) | ![Dark mode](preview/dark.webp) |

## Install

Paste this into a T3 Code thread:

> Install the Faceplate theme from https://github.com/ericzwu/t3-faceplate-theme using the agent instructions in its README.

Or install it by hand: copy `theme/faceplate.json` and `theme/faceplate.png` into `~/.t3/userdata/themes`
(Windows: `%USERPROFILE%\.t3\userdata\themes`), then pick Faceplate in Settings → Appearance. You need both files; the
PNG is the bezel. If the bezel shows as a flat band, reload the window.

Tested on T3 Code 0.1.10.

### Agent instructions

1. Get `themesDir` from `t3_theme_read`. If the tool isn't available, use the folder above.
2. Download both files into it, keeping their names:
   - `https://raw.githubusercontent.com/ericzwu/t3-faceplate-theme/main/theme/faceplate.json`
   - `https://raw.githubusercontent.com/ericzwu/t3-faceplate-theme/main/theme/faceplate.png`

   Don't install the JSON through `t3_theme_set` with a `theme` object; that leaves out the image.
3. Switch to it with `t3_theme_set` and `themeId: "faceplate"`. Leave the user's light/dark setting alone.
4. Tell the user it's installed and that `t3-chat` switches back to the default theme.

## Limits

- Native menus and window buttons can't be styled. Terminal text, the file tree and diff contents only take the
  theme's colours.
- Parts of the theme depend on the app's current markup, so an update can break them. Anything that breaks falls
  back to the default look.

## Building

`node src/build.js` merges `src/dark.css` and `src/light.css` into `theme/faceplate.json`. Colour roles are in `src/roles.json`.

`python src/make-bezel.py theme/faceplate.png` re-renders the bezel. It needs Pillow.

Theme CSS is capped at 50,000 characters, and the build fails above that. Light mode reuses the dark
bezel image, flipped and tone-mapped in CSS, because a theme gets only one image.

## Licence

[MIT](LICENSE)
