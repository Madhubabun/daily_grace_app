package com.dailygrace.app.image

import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.data.VerseLayout

/** Typography and placement rules shared by the screen, the share image and the wallpaper. */
object VerseStyle {

    /** Scripture font size as a fraction of the canvas width, shrinking gently for long verses. */
    fun verseSizeFraction(verse: String): Float {
        val n = verse.length
        return when {
            n <= 45 -> 0.083f
            n <= 80 -> 0.074f
            n <= 120 -> 0.066f
            n <= 160 -> 0.059f
            else -> 0.053f
        }
    }

    const val REFERENCE_SIZE_FRACTION = 0.034f
    const val TEXT_WIDTH_FRACTION = 0.80f

    /** Vertical centre of the verse block inside the app (below the header, above the actions). */
    fun screenBandCenter(layout: VerseLayout): Float = when (layout) {
        VerseLayout.TOP -> 0.29f
        VerseLayout.CENTER -> 0.5f
        VerseLayout.BOTTOM -> 0.68f
    }

    /**
     * On the phone's wallpaper the top is taken by the lock-screen clock and the bottom by the
     * dock and shortcuts, so the bands are pulled toward the middle.
     */
    fun wallpaperBandCenter(layout: VerseLayout): Float = when (layout) {
        VerseLayout.TOP -> 0.37f
        VerseLayout.CENTER -> 0.5f
        VerseLayout.BOTTOM -> 0.64f
    }

    /** Share images are 9:16, slightly shorter than the art, so keep a little more breathing room. */
    fun shareBandCenter(layout: VerseLayout): Float = when (layout) {
        VerseLayout.TOP -> 0.3f
        VerseLayout.CENTER -> 0.5f
        VerseLayout.BOTTOM -> 0.68f
    }

    /** "Psalm 23:1 · KJV": the translation is always named, since entries may differ. */
    fun referenceLine(entry: GraceEntry): String = "${entry.reference} \u00B7 ${entry.translation}"

    fun quoted(verse: String): String = "“" + verse.trim() + "”"

    /**
     * Ranges (start, endExclusive) of the letters to set in small capitals: "LORD" in the KJV is
     * printed as a capital L followed by small-capital ORD.
     */
    fun smallCapRanges(text: String): List<IntRange> {
        val out = ArrayList<IntRange>()
        var i = text.indexOf("LORD")
        while (i >= 0) {
            val beforeOk = i == 0 || !text[i - 1].isLetter()
            val afterOk = i + 4 >= text.length || !text[i + 4].isLetter()
            if (beforeOk && afterOk) out += (i + 1) until (i + 4)
            i = text.indexOf("LORD", i + 4)
        }
        return out
    }

    const val SMALL_CAP_SCALE = 0.8f

    /**
     * How dark the scrim behind the verse should be, from the average luminance (0..1) of the
     * artwork under the text. Bright skies get a deeper scrim; dark night scenes need almost none.
     */
    fun scrimAlpha(luminance: Float): Float = (0.18f + (luminance - 0.22f) * 1.05f).coerceIn(0.14f, 0.62f)
}
