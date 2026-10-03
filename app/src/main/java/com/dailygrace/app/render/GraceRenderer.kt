package com.dailygrace.app.render

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.Shader
import android.graphics.Typeface
import android.text.Layout
import android.text.SpannableString
import android.text.Spanned
import android.text.StaticLayout
import android.text.TextPaint
import android.text.style.RelativeSizeSpan
import androidx.core.content.res.ResourcesCompat
import com.dailygrace.app.R
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.image.WallpaperFit
import com.dailygrace.app.image.VerseStyle
import kotlin.math.roundToInt

/** Where the composed image is going; decides text placement and branding. */
enum class RenderTarget { WALLPAPER, SHARE, PREVIEW }

/**
 * Draws artwork + verse + reference onto a bitmap of any size. The verse is real text set in
 * Cormorant Garamond, never baked into the artwork, so it is always crisp and correct.
 */
object GraceRenderer {

    fun render(
        context: Context,
        art: Bitmap,
        entry: GraceEntry,
        width: Int,
        height: Int,
        target: RenderTarget,
        includeVerse: Boolean = true,
    ): Bitmap {
        val out = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(out)

        val crop = WallpaperFit.crop(art.width, art.height, width, height, 0.5f, entry.focusY)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG or Paint.DITHER_FLAG)
        canvas.drawBitmap(art, Rect(crop.left, crop.top, crop.right, crop.bottom), Rect(0, 0, width, height), paint)

        if (includeVerse) {
            val center = when (target) {
                RenderTarget.SHARE -> VerseStyle.shareBandCenter(entry.layout)
                else -> VerseStyle.wallpaperBandCenter(entry.layout)
            }
            drawVerse(context, canvas, art, crop, entry, width, height, center)
        }
        if (target == RenderTarget.SHARE) drawBranding(context, canvas, width, height)
        return out
    }

    private fun drawVerse(
        context: Context,
        canvas: Canvas,
        art: Bitmap,
        crop: com.dailygrace.app.image.CropRect,
        entry: GraceEntry,
        width: Int,
        height: Int,
        bandCenter: Float,
    ) {
        val serif = ResourcesCompat.getFont(context, R.font.cormorant_garamond_500) ?: Typeface.SERIF
        val sans = ResourcesCompat.getFont(context, R.font.inter_500) ?: Typeface.SANS_SERIF

        val verseText = VerseStyle.quoted(entry.verse)
        val spannable = SpannableString(verseText)
        for (r in VerseStyle.smallCapRanges(verseText)) {
            spannable.setSpan(RelativeSizeSpan(VerseStyle.SMALL_CAP_SCALE), r.first, r.last + 1, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        }
        val versePaint = TextPaint(Paint.ANTI_ALIAS_FLAG or Paint.SUBPIXEL_TEXT_FLAG).apply {
            typeface = serif
            color = Color.WHITE
            textSize = width * VerseStyle.verseSizeFraction(entry.verse)
            setShadowLayer(width * 0.012f, 0f, width * 0.002f, Color.argb(110, 0, 0, 0))
        }
        val textWidth = (width * VerseStyle.TEXT_WIDTH_FRACTION).roundToInt()
        val verseLayout = StaticLayout.Builder.obtain(spannable, 0, spannable.length, versePaint, textWidth)
            .setAlignment(Layout.Alignment.ALIGN_CENTER)
            .setLineSpacing(0f, 1.08f)
            .setIncludePad(false)
            .setBreakStrategy(Layout.BREAK_STRATEGY_BALANCED)
            .build()

        val refPaint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            typeface = sans
            color = Color.rgb(241, 221, 180)
            textSize = width * VerseStyle.REFERENCE_SIZE_FRACTION
            letterSpacing = 0.14f
            textAlign = Paint.Align.CENTER
            setShadowLayer(width * 0.008f, 0f, 0f, Color.argb(120, 0, 0, 0))
        }
        val reference = VerseStyle.referenceLine(entry).uppercase()
        val gap = width * 0.05f
        val refHeight = refPaint.fontSpacing
        val blockHeight = verseLayout.height + gap + refHeight
        val top = (height * bandCenter - blockHeight / 2f).coerceIn(height * 0.08f, height * 0.92f - blockHeight)

        // Scrim: darkness depends on how bright the artwork actually is under the text.
        val lum = bandLuminance(art, crop, top / height, (top + blockHeight) / height)
        val alpha = (VerseStyle.scrimAlpha(lum) * 255).roundToInt()
        val pad = width * 0.22f
        val scrimTop = top - pad
        val scrimBottom = top + blockHeight + pad
        val scrim = Paint().apply {
            shader = LinearGradient(
                0f, scrimTop, 0f, scrimBottom,
                intArrayOf(Color.TRANSPARENT, Color.argb(alpha, 8, 10, 16), Color.argb(alpha, 8, 10, 16), Color.TRANSPARENT),
                floatArrayOf(0f, 0.32f, 0.68f, 1f),
                Shader.TileMode.CLAMP,
            )
        }
        canvas.drawRect(RectF(0f, scrimTop, width.toFloat(), scrimBottom), scrim)

        canvas.save()
        canvas.translate((width - textWidth) / 2f, top)
        verseLayout.draw(canvas)
        canvas.restore()

        val refBaseline = top + verseLayout.height + gap - refPaint.fontMetrics.ascent
        canvas.drawText(reference, width / 2f, refBaseline, refPaint)
    }

    private fun drawBranding(context: Context, canvas: Canvas, width: Int, height: Int) {
        val sans = ResourcesCompat.getFont(context, R.font.inter_500) ?: Typeface.SANS_SERIF
        val p = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            typeface = sans
            color = Color.argb(170, 255, 255, 255)
            textSize = width * 0.024f
            letterSpacing = 0.32f
            textAlign = Paint.Align.CENTER
            setShadowLayer(width * 0.006f, 0f, 0f, Color.argb(120, 0, 0, 0))
        }
        val shade = Paint().apply {
            shader = LinearGradient(0f, height * 0.88f, 0f, height.toFloat(), Color.TRANSPARENT, Color.argb(90, 0, 0, 0), Shader.TileMode.CLAMP)
        }
        canvas.drawRect(0f, height * 0.88f, width.toFloat(), height.toFloat(), shade)
        canvas.drawText("DAILY GRACE", width / 2f, height * 0.955f, p)
    }

    /** Mean luminance of the source pixels that end up under the verse (rows given as fractions of the output). */
    private fun bandLuminance(art: Bitmap, crop: com.dailygrace.app.image.CropRect, from: Float, to: Float): Float {
        val y0 = (crop.top + from.coerceIn(0f, 1f) * crop.height).toInt().coerceIn(0, art.height - 1)
        val y1 = (crop.top + to.coerceIn(0f, 1f) * crop.height).toInt().coerceIn(y0 + 1, art.height)
        val x0 = crop.left + crop.width / 10
        val x1 = crop.right - crop.width / 10
        val step = (art.width / 120).coerceAtLeast(1)
        var sum = 0.0
        var n = 0
        var y = y0
        while (y < y1) {
            var x = x0
            while (x < x1) {
                val c = art.getPixel(x, y)
                sum += 0.2126 * Color.red(c) / 255.0 + 0.7152 * Color.green(c) / 255.0 + 0.0722 * Color.blue(c) / 255.0
                n++
                x += step
            }
            y += step
        }
        return if (n == 0) 0.5f else (sum / n).toFloat()
    }
}
