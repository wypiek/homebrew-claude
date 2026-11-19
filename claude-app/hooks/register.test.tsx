import { expect, test } from 'claude-code/testing'
import type { TestBody } from 'claude-code/testing'

import { VARIANTS } from './variants'

// The hooks here stand for the engine beneath the plugin.
function engine(on: Parameters<TestBody>[1], sets: unknown[]) {
  on('command.register', () => ({ value: { command: 'homebrew-color' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('theme.set', (_, e) => {
    sets.push(e)

    return { value: { isDrawn: true, requestId: 't' } }
  })
}

test('the session starts with the default look, dark, with a scene', async ($, on) => {
  const sets: any[] = []
  engine(on, sets)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  expect(sets.length).toBe(1)
  expect(sets[0].overrideColorScheme).toBe('dark')
  expect(sets[0].backdrop.scene).toBe('default')
  expect(sets[0].backdrop.glass.blur).toBe(0)
})

test('the color setting picks the variant', { options: { color: 'pink' } }, async ($, on) => {
  const sets: any[] = []
  engine(on, sets)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  expect(sets[0].backdrop.scene).toBe('pink')
})

test('every variant draws its scene on desktop and mobile', async $ => {
  for (const v of VARIANTS) {
    for (const surface of ['desktop', 'mobile'] as const) {
      const ui = await $.ui.mount({
        plugin: 'homebrew-channel',
        component: 'Backdrop',
        surface,
        props: { scene: v.id, plugin: 'homebrew-channel', glass: { blur: 0, opacity: 0.6 } },
      })
      const svg = await ui.find({ type: 'Svg' })

      expect(svg).toBeTruthy()
      expect(String((svg as any).props?.source ?? '')).not.toMatch(/\{[a-z]+\}/)
      await ui.unmount()
    }
  }
})
