package com.dailygrace.app.image

import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/** A crop rectangle in source-image pixels. */
data class CropRect(val left: Int, val top: Int, val right: Int, val bottom: Int) {
    val width: Int get() = right - left
    val height: Int get() = bottom - top
}

/**
 * Fits 20:9 master artwork to any phone without stretching.
 *
 * The crop is the largest rectangle of the screen's aspect ratio that fits in the image, so
 * zoom is the minimum possible. It is positioned around the artwork's focus and then nudged
 * so the critical safe zone (the central [SAFE_FRACTION] of the composition) stays inside
 * whenever the geometry allows.
 */
object WallpaperFit {
    /** Fraction of width and height that holds verse, faces, cross and other critical content. */
    const val SAFE_FRACTION = 0.72f

    fun crop(
        imageWidth: Int,
        imageHeight: Int,
        targetWidth: Int,
        targetHeight: Int,
        focusX: Float = 0.5f,
        focusY: Float = 0.5f,
    ): CropRect {
        require(imageWidth > 0 && imageHeight > 0 && targetWidth > 0 && targetHeight > 0)
        val targetAspect = targetWidth.toDouble() / targetHeight
        val imageAspect = imageWidth.toDouble() / imageHeight
        val cropW: Int
        val cropH: Int
        if (imageAspect > targetAspect) {
            cropH = imageHeight
            cropW = min(imageWidth, (imageHeight * targetAspect).roundToInt())
        } else {
            cropW = imageWidth
            cropH = min(imageHeight, (imageWidth / targetAspect).roundToInt())
        }
        val left = place(imageWidth, cropW, focusX)
        val top = place(imageHeight, cropH, focusY)
        return CropRect(left, top, left + cropW, top + cropH)
    }

    /** Centres the crop on the focus, keeps the safe band inside if it can, and stays in bounds. */
    private fun place(full: Int, crop: Int, focus: Float): Int {
        if (crop >= full) return 0
        val margin = (full * (1f - SAFE_FRACTION) / 2f)
        val safeStart = margin.roundToInt()
        val safeEnd = (full - margin).roundToInt()
        var start = (focus * full - crop / 2f).roundToInt()
        if (crop >= safeEnd - safeStart) {
            // The whole safe band fits: never cut into it.
            start = start.coerceIn(safeEnd - crop, safeStart)
        }
        return start.coerceIn(0, full - crop)
    }

    /** How much of the safe zone survives a crop (1.0 = all of it). Used by tests and the preview. */
    fun safeZoneCoverage(imageWidth: Int, imageHeight: Int, crop: CropRect): Float {
        val mx = imageWidth * (1f - SAFE_FRACTION) / 2f
        val my = imageHeight * (1f - SAFE_FRACTION) / 2f
        val sl = mx; val sr = imageWidth - mx; val st = my; val sb = imageHeight - my
        val w = max(0f, min(sr, crop.right.toFloat()) - max(sl, crop.left.toFloat()))
        val h = max(0f, min(sb, crop.bottom.toFloat()) - max(st, crop.top.toFloat()))
        return (w * h) / ((sr - sl) * (sb - st))
    }

    /** Scale from source pixels to screen pixels. 1.0 means the image is shown at native size. */
    fun scale(crop: CropRect, targetWidth: Int): Float = targetWidth.toFloat() / crop.width
}
