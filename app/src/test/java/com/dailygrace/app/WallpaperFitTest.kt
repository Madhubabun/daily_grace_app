package com.dailygrace.app

import com.dailygrace.app.image.WallpaperFit
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * The master art is 1440 x 3200. These are the screens Daily Grace must fit without stretching
 * and without cutting into the central safe zone.
 */
class WallpaperFitTest {
    private val artW = 1440
    private val artH = 3200

    private val screens = mapOf(
        "Galaxy S22 Ultra WQHD+ (19.3:9)" to (1440 to 3088),
        "Galaxy S22 Ultra FHD+ (19.3:9)" to (1080 to 2316),
        "6.5in 20:9" to (1080 to 2400),
        "6.7in 19.5:9" to (1080 to 2340),
        "6.7in Pixel 20:9" to (1344 to 2992),
        "6.9in 19.5:9" to (1320 to 2868),
        "Older 18:9" to (1080 to 2160),
        "Older 16:9" to (1080 to 1920),
    )

    @Test
    fun cropMatchesScreenAspectWithoutStretching() {
        for ((name, size) in screens) {
            val (w, h) = size
            val crop = WallpaperFit.crop(artW, artH, w, h, 0.5f, 0.5f)
            val cropAspect = crop.width.toDouble() / crop.height
            val screenAspect = w.toDouble() / h
            assertEquals("$name aspect", screenAspect, cropAspect, 0.002)
            assertTrue("$name inside image", crop.left >= 0 && crop.top >= 0 && crop.right <= artW && crop.bottom <= artH)
        }
    }

    @Test
    fun modernPhonesUseFullWidthWithMinimalZoom() {
        for ((name, size) in screens) {
            val (w, h) = size
            val crop = WallpaperFit.crop(artW, artH, w, h)
            // The crop always spans the full width or the full height: the least zoom possible.
            assertTrue("$name minimal zoom", crop.width == artW || crop.height == artH)
            // And it never throws away more than 1% of the width on a 19.5:9-20:9 phone.
            if (h.toFloat() / w > 2.1f) assertTrue("$name width ${crop.width}", crop.width >= artW * 0.99f)
        }
    }

    @Test
    fun safeZoneSurvivesOnEverySupportedScreen() {
        for ((name, size) in screens) {
            val (w, h) = size
            for (focus in listOf(0.4f, 0.5f, 0.6f)) {
                val crop = WallpaperFit.crop(artW, artH, w, h, 0.5f, focus)
                val kept = WallpaperFit.safeZoneCoverage(artW, artH, crop)
                assertEquals("$name focus $focus", 1f, kept, 0.0001f)
            }
        }
    }

    @Test
    fun s22UltraLosesOnlyAFewPercentOfHeight() {
        val crop = WallpaperFit.crop(artW, artH, 1440, 3088)
        assertEquals(3088, crop.height)
        assertTrue(crop.top in 0..112)
        assertEquals(1f, WallpaperFit.scale(crop, 1440), 0.0001f)
    }

    @Test
    fun focusNeverPushesCropOutOfBounds() {
        val top = WallpaperFit.crop(artW, artH, 1080, 1920, 0.5f, 0f)
        val bottom = WallpaperFit.crop(artW, artH, 1080, 1920, 0.5f, 1f)
        assertTrue(top.top >= 0)
        assertTrue(bottom.bottom <= artH)
    }
}
