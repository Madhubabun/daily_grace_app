package com.dailygrace.app.ui.components

import android.provider.Settings
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.FilterQuality
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.BiasAlignment
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.image.rememberAssetImage
import com.dailygrace.app.ui.theme.Grace

/** True when the user turned animations off in Android's accessibility settings. */
@Composable
fun rememberReduceMotion(): Boolean {
    val context = LocalContext.current
    return remember {
        runCatching {
            Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
        }.getOrDefault(false)
    }
}

/**
 * Full-bleed artwork. Shows the small thumbnail instantly, then fades in the full-resolution
 * image. With [motion] on, the scene breathes very slowly: a gentle drift and a soft shift of
 * light, never fast enough to feel like a GIF.
 */
@Composable
fun ArtworkImage(
    entry: GraceEntry,
    modifier: Modifier = Modifier,
    motion: Boolean = false,
    parallaxPx: Float = 0f,
) {
    BoxWithConstraints(modifier.background(Grace.Night)) {
        val widthPx = with(LocalDensity.current) { maxWidth.roundToPx() }
        val alignment = remember(entry.focusY) { BiasAlignment(0f, (entry.focusY * 2f - 1f).coerceIn(-1f, 1f)) }
        val thumb by rememberAssetImage(entry.thumbPath, 216)
        val full by rememberAssetImage(entry.imagePath, widthPx)
        val fullAlpha by animateFloatAsState(if (full != null) 1f else 0f, tween(500), label = "fullAlpha")

        val reduce = rememberReduceMotion()
        val animate = motion && !reduce
        val drift: Float
        val light: Float
        if (animate) {
            val transition = rememberInfiniteTransition(label = "breathe")
            val d by transition.animateFloat(
                0f, 1f, infiniteRepeatable(tween(26_000, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "drift",
            )
            val l by transition.animateFloat(
                0f, 1f, infiniteRepeatable(tween(9_000, easing = LinearEasing), RepeatMode.Reverse), label = "light",
            )
            drift = d
            light = l
        } else {
            drift = 0.5f
            light = 0.5f
        }

        val layer = Modifier
            .fillMaxSize()
            .graphicsLayer {
                val s = if (animate) 1.045f + 0.03f * drift else 1f
                scaleX = s
                scaleY = s
                translationX = if (animate) (drift - 0.5f) * size.width * 0.018f else 0f
                translationY = parallaxPx * 0.35f
            }

        thumb?.let {
            Image(it, null, layer, alignment = alignment, contentScale = ContentScale.Crop, filterQuality = FilterQuality.Low)
        }
        full?.let {
            Image(it, null, layer.alpha(fullAlpha), alignment = alignment, contentScale = ContentScale.Crop, filterQuality = FilterQuality.High)
        }
        if (animate) {
            // A slow, barely visible bloom of morning light from above.
            Canvas(Modifier.fillMaxSize()) {
                val c = Offset(size.width * (0.35f + 0.3f * drift), size.height * 0.18f)
                drawRect(
                    Brush.radialGradient(
                        listOf(Color(0xFFFFF1D6).copy(alpha = 0.05f + 0.07f * light), Color.Transparent),
                        center = c,
                        radius = size.width * 1.1f,
                    )
                )
            }
        }
    }
}

/** Soft vertical shade so overlaid UI stays readable. */
@Composable
fun VerticalShade(modifier: Modifier, from: Color, to: Color) {
    Box(modifier.background(Brush.verticalGradient(listOf(from, to))))
}
