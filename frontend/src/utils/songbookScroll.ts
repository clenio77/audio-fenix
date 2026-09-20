/**
 * Helpers for Songbook lyric auto-scroll.
 *
 * Auto-scroll must only run when the active lyric changes, and must scroll
 * the lyrics container — not the document (scrollIntoView would thrash the
 * page / fixed player on every currentTime tick).
 */

export function getContainerScrollTop(
  elementOffsetTop: number,
  elementHeight: number,
  containerClientHeight: number,
): number {
  return Math.max(
    0,
    elementOffsetTop - containerClientHeight / 2 + elementHeight / 2,
  )
}

export function shouldAutoScrollToLyric(
  activeIndex: number,
  focusMode: boolean,
): boolean {
  return !focusMode && activeIndex >= 0
}
