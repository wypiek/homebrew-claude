// Homebrew Channel look for the Claude app.
//
// Sets a dark palette and draws the HBC water and rising bubbles behind the
// conversation. The scene and palettes come from variants.ts, which
// scripts/build-claude-mod.py generates: edit that script, not variants.ts.
//
// The bubbles are translated from channel/channelapp/source/bubbles.c of
// The Homebrew Channel, https://github.com/fail0verflow/hbc, by Team
// Twiizers (fail0verflow), GPL-2.0-or-later, and redrawn as vector art.
// This file is also GPL-2.0-or-later. See LICENSE.

import type { EngineInterface, Register, ThemeSetArgs } from 'claude-code'

import { makeColors } from './make-colors.js'
import { SCENE, VARIANTS } from './variants'
import type { Variant } from './variants'

const PLUGIN = 'homebrew-channel'
const COMMAND = 'homebrew-color'

function pick(id: unknown): Variant {
  return VARIANTS.find(v => v.id === id) ?? (VARIANTS[0] as Variant)
}

function look(v: Variant): { args: ThemeSetArgs; unpainted?: string } {
  const { theme, problems } = makeColors({
    label: v.name,
    only: 'dark',
    roles: v.roles,
    dark: { gray: { anchors: v.anchors } },
  })

  return {
    args: {
      colors: theme,
      overrideColorScheme: 'dark',
      // No blur: the bubbles move behind the panels, so a blur would be
      // redrawn every frame. The tint is the T3 Code theme's sidebar glass.
      backdrop: { scene: v.id, glass: { blur: 0, tint: v.glass, opacity: 0.6 } },
    },
    unpainted: problems.find(line => line.startsWith("Desktop won't paint")),
  }
}

// A plugin's name, with or without its marketplace (`name@marketplace`).
function ownedByUs(plugin: string): boolean {
  return plugin === PLUGIN || plugin.startsWith(`${PLUGIN}@`)
}

function scene(v: Variant): string {
  return SCENE.replace(/\{([a-z]+)\}/g, (token, name: string) => v.tokens[name] ?? token)
}

async function apply($: EngineInterface, v: Variant): Promise<void> {
  const { args, unpainted } = look(v)

  if (unpainted !== undefined) {
    $.ui.toast(`Homebrew Channel: ${unpainted}`)
  }
  const set = await $.theme.set(args)

  if (!set.isDrawn) {
    $.ui.status(`Homebrew Channel: ${set.reason}`)
  }
}

export const register: Register = (on, options) => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: COMMAND,
      description: 'Change the Homebrew Channel color',
      argumentHint: `[${VARIANTS.map(v => v.id).join('|')}]`,
    })
    await apply($, pick(options.color))

    return next(e)
  })

  on('command.run', { command: COMMAND }, async ($, e) => {
    const names = VARIANTS.map(v => v.id).join(', ')
    const wanted = e.args.trim().toLowerCase()

    if (wanted === '') {
      return { text: `Homebrew Channel colors: ${names}. Pick one with /${COMMAND} <color>.` }
    }
    const v = VARIANTS.find(one => one.id === wanted)

    if (v === undefined) {
      return { text: `No color "${wanted}". Choose one of: ${names}.` }
    }
    await apply($, v)

    // Keep the choice for later sessions: it is the plugin's own setting.
    const row = (await $.config.list()).find(
      one => one.key.endsWith('.color') && ownedByUs(one.key.split('.')[0] ?? ''),
    )
    const saved = row === undefined ? undefined : await $.config.set({ key: row.key, value: v.id })

    if (saved === undefined || 'deny' in saved) {
      return { text: `${v.name} is on for this session. It could not be saved for later sessions.` }
    }

    return { text: `${v.name} is on.` }
  }).catch(() => ({ text: 'Homebrew Channel: the color could not be changed.' }))

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    const ours = ownedByUs(e.props.plugin)
    const v = VARIANTS.find(one => one.id === e.props.scene)

    if (!ours || v === undefined || (e.surface !== 'desktop' && e.surface !== 'mobile')) {
      return next(e)
    }
    const { Svg } = $.ui.resolve(e)

    return <Svg source={scene(v)} alt="Bubbles rising through deep blue water" isInteractive />
  })
}
