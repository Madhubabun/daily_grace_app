package com.dailygrace.app.ui.components

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.PathBuilder
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

/** Thin line icons drawn for Daily Grace so the navigation stays quiet and consistent. */
object GraceIcons {

    private fun lineIcon(name: String, width: Float = 1.6f, block: PathBuilder.() -> Unit): ImageVector =
        ImageVector.Builder(name, 24.dp, 24.dp, 24f, 24f).apply {
            path(
                fill = null,
                stroke = SolidColor(Color.Black),
                strokeLineWidth = width,
                strokeLineCap = StrokeCap.Round,
                strokeLineJoin = StrokeJoin.Round,
                pathBuilder = block,
            )
        }.build()

    private fun PathBuilder.circle(cx: Float, cy: Float, r: Float) {
        moveTo(cx - r, cy)
        arcTo(r, r, 0f, true, true, cx + r, cy)
        arcTo(r, r, 0f, true, true, cx - r, cy)
        close()
    }

    private fun PathBuilder.roundRect(l: Float, t: Float, r: Float, b: Float, rad: Float) {
        moveTo(l + rad, t)
        lineTo(r - rad, t)
        arcTo(rad, rad, 0f, false, true, r, t + rad)
        lineTo(r, b - rad)
        arcTo(rad, rad, 0f, false, true, r - rad, b)
        lineTo(l + rad, b)
        arcTo(rad, rad, 0f, false, true, l, b - rad)
        lineTo(l, t + rad)
        arcTo(rad, rad, 0f, false, true, l + rad, t)
        close()
    }

    /** Sun rising over the horizon. */
    val Today: ImageVector by lazy {
        lineIcon("Today") {
            moveTo(3f, 18f); lineTo(21f, 18f)
            moveTo(7f, 18f); arcTo(5f, 5f, 0f, false, true, 17f, 18f)
            moveTo(12f, 6.5f); lineTo(12f, 9f)
            moveTo(5.2f, 10.2f); lineTo(6.9f, 11.9f)
            moveTo(18.8f, 10.2f); lineTo(17.1f, 11.9f)
            moveTo(6f, 21f); lineTo(18f, 21f)
        }
    }

    /** Picture with mountains. */
    val Wallpapers: ImageVector by lazy {
        lineIcon("Wallpapers") {
            roundRect(4f, 3f, 20f, 21f, 2.5f)
            moveTo(4.5f, 17.5f); lineTo(9f, 12.5f); lineTo(13f, 16.5f); lineTo(15f, 14.5f); lineTo(19.5f, 19f)
            circle(15f, 8f, 1.6f)
        }
    }

    /** Clock face. */
    val History: ImageVector by lazy {
        lineIcon("History") {
            circle(12f, 12f, 8.5f)
            moveTo(12f, 7.5f); lineTo(12f, 12f); lineTo(15f, 14f)
        }
    }

    /** Hands folded in prayer, drawn as a pointed arch. */
    val Prayer: ImageVector by lazy {
        lineIcon("Prayer") {
            moveTo(12f, 3f)
            curveTo(10f, 5.5f, 8.5f, 9f, 8.5f, 14f)
            lineTo(8.5f, 18f)
            lineTo(15.5f, 18f)
            lineTo(15.5f, 14f)
            curveTo(15.5f, 9f, 14f, 5.5f, 12f, 3f)
            close()
            moveTo(12f, 5f); lineTo(12f, 18f)
            moveTo(7f, 18f); lineTo(17f, 18f); lineTo(17f, 21f); lineTo(7f, 21f); close()
        }
    }

    /** Phone with artwork, for "Set Wallpaper". */
    val SetWallpaper: ImageVector by lazy {
        lineIcon("SetWallpaper") {
            roundRect(6.5f, 2.5f, 17.5f, 21.5f, 2.5f)
            moveTo(7f, 16f); lineTo(10f, 13f); lineTo(12.5f, 15.5f); lineTo(14f, 14f); lineTo(17f, 17f)
            moveTo(10.5f, 5.5f); lineTo(13.5f, 5.5f)
        }
    }

    /** Small cross, used as a quiet ornament. */
    val Cross: ImageVector by lazy {
        lineIcon("Cross", 1.4f) {
            moveTo(12f, 4f); lineTo(12f, 20f)
            moveTo(7.5f, 9f); lineTo(16.5f, 9f)
        }
    }

    val ChevronDown: ImageVector by lazy {
        lineIcon("ChevronDown") {
            moveTo(6f, 9.5f); lineTo(12f, 15f); lineTo(18f, 9.5f)
        }
    }
}
