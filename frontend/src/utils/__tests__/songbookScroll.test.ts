import { describe, expect, it } from 'vitest'
import {
    getContainerScrollTop,
    shouldAutoScrollToLyric,
} from '../songbookScroll'

describe('shouldAutoScrollToLyric', () => {
    it('scrolls when a lyric is active and focus mode is off', () => {
        expect(shouldAutoScrollToLyric(2, false)).toBe(true)
    })

    it('does not scroll when no lyric is active', () => {
        expect(shouldAutoScrollToLyric(-1, false)).toBe(false)
    })

    it('does not scroll in focus mode', () => {
        expect(shouldAutoScrollToLyric(2, true)).toBe(false)
    })
})

describe('getContainerScrollTop', () => {
    it('centers the active lyric in the container', () => {
        // element at 400px, height 100, container 300 → center at 400 - 150 + 50 = 300
        expect(getContainerScrollTop(400, 100, 300)).toBe(300)
    })

    it('never scrolls above the top of the container', () => {
        expect(getContainerScrollTop(10, 40, 300)).toBe(0)
    })
})
