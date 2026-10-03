package com.dailygrace.app.ui.components

import android.content.Context
import android.graphics.BitmapFactory
import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.FilterQuality
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipRect
import androidx.compose.ui.graphics.drawscope.withTransform
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import kotlin.math.PI
import kotlin.math.max
import kotlin.math.sin

/**
 * A painted scene split into layers (assets/animated/<name>/manifest.json) so it can move
 * gently: clouds drift, sheep wander and graze, grass sways and a few birds cross the sky.
 * The static wallpaper is the same layers at rest, so nothing jumps when motion is off.
 */
class LayeredScene(
    val width: Int,
    val height: Int,
    val background: ImageBitmap,
    val clouds: ImageBitmap?,
    val cloudsY: Int,
    val cloudLoopSeconds: Float,
    val sprites: List<Sprite>,
    val grass: ImageBitmap?,
    val grassY: Int,
    val grassSway: Float,
    val vignette: ImageBitmap?,
    val birds: Boolean,
) {
    class Sprite(val image: ImageBitmap, val x: Int, val y: Int, val wander: Float, val period: Float, val phase: Float)

    companion object {
        fun load(context: Context, name: String): LayeredScene? = runCatching {
            val dir = "animated/$name"
            fun bmp(file: String?): ImageBitmap? = file?.takeIf { it.isNotEmpty() }?.let { f ->
                context.assets.open("$dir/$f").use { BitmapFactory.decodeStream(it) }?.asImageBitmap()
            }
            val m = JSONObject(context.assets.open("$dir/manifest.json").bufferedReader().use { it.readText() })
            val clouds = m.optJSONObject("clouds")
            val grass = m.optJSONObject("grass")
            val spritesJson = m.optJSONArray("sprites")
            val sprites = (0 until (spritesJson?.length() ?: 0)).mapNotNull { i ->
                val o = spritesJson!!.getJSONObject(i)
                bmp(o.getString("image"))?.let {
                    Sprite(
                        it, o.getInt("x"), o.getInt("y"), o.optDouble("wander", 12.0).toFloat(),
                        o.optDouble("period", 20.0).toFloat(), o.optDouble("phase", 0.0).toFloat(),
                    )
                }
            }
            LayeredScene(
                width = m.getInt("width"),
                height = m.getInt("height"),
                background = bmp(m.getString("background")) ?: return null,
                clouds = bmp(clouds?.optString("image")),
                cloudsY = clouds?.optInt("y") ?: 0,
                cloudLoopSeconds = (clouds?.optDouble("secondsPerLoop", 300.0) ?: 300.0).toFloat(),
                sprites = sprites,
                grass = bmp(grass?.optString("image")),
                grassY = grass?.optInt("y") ?: 0,
                grassSway = (grass?.optDouble("sway", 6.0) ?: 6.0).toFloat(),
                vignette = bmp(m.optString("vignette")),
                birds = m.optBoolean("birds", false),
            )
        }.getOrNull()
    }
}

/** Loads a layered scene off the main thread; null until ready or if it is missing. */
@Composable
fun rememberLayeredScene(name: String): LayeredScene? {
    val context = LocalContext.current.applicationContext
    val scene by produceState<LayeredScene?>(null, name) {
        value = withContext(Dispatchers.IO) { LayeredScene.load(context, name) }
    }
    return scene
}

/**
 * Draws [scene] cropped to fill the canvas exactly like ContentScale.Crop with a vertical
 * [biasY] (-1 top, 1 bottom), so it lines up with the static artwork underneath.
 */
@Composable
fun AnimatedLayeredScene(scene: LayeredScene, biasY: Float, modifier: Modifier = Modifier) {
    var seconds by remember { mutableFloatStateOf(0f) }
    LaunchedEffect(scene) {
        val start = withFrameNanos { it }
        while (true) {
            withFrameNanos { seconds = (it - start) / 1_000_000_000f }
        }
    }
    Canvas(modifier) {
        val scale = max(size.width / scene.width, size.height / scene.height)
        val ox = (size.width - scene.width * scale) / 2f
        val oy = (size.height - scene.height * scale) * (1f + biasY) / 2f
        withTransform({
            translate(ox, oy)
            scale(scale, scale, pivot = Offset.Zero)
        }) {
            drawScene(scene, seconds)
        }
    }
}

private fun DrawScope.image(img: ImageBitmap, x: Float, y: Float) {
    drawImage(
        img,
        dstOffset = IntOffset(x.toInt(), y.toInt()),
        dstSize = IntSize(img.width, img.height),
        filterQuality = FilterQuality.Medium,
    )
}

private fun DrawScope.drawScene(scene: LayeredScene, t: Float) {
    image(scene.background, 0f, 0f)

    // Clouds: a mirror-tiled strip twice the scene width, drifting left to right.
    scene.clouds?.let { c ->
        val period = c.width.toFloat()
        val shift = (t / scene.cloudLoopSeconds * period) % period
        clipRect(0f, 0f, scene.width.toFloat(), (scene.cloudsY + c.height).toFloat()) {
            drawImage(c, dstOffset = IntOffset((shift - period).toInt(), scene.cloudsY), dstSize = IntSize(c.width, c.height),
                filterQuality = FilterQuality.Medium)
            drawImage(c, dstOffset = IntOffset(shift.toInt(), scene.cloudsY), dstSize = IntSize(c.width, c.height),
                filterQuality = FilterQuality.Medium)
        }
    }

    if (scene.birds) drawBirds(scene, t)

    // Sheep amble a few steps back and forth, with a tiny grazing bob.
    for (s in scene.sprites) {
        val p = 2f * PI.toFloat() * (t / s.period + s.phase)
        val dx = s.wander * sin(p)
        val dy = 1.2f * max(0f, sin(p * 3f))
        image(s.image, s.x + dx, s.y + dy)
    }

    // Grass sways from its roots: the band is drawn in slices, each skewed a little out of phase.
    scene.grass?.let { g ->
        val slices = 8
        val sliceW = g.width / slices
        for (i in 0 until slices) {
            val x0 = i * sliceW
            val w = if (i == slices - 1) g.width - x0 else sliceW
            val sway = scene.grassSway * sin(t * 0.9f + i * 0.45f) + scene.grassSway * 0.4f * sin(t * 2.3f + i)
            val skew = -sway / g.height
            clipRect(x0.toFloat(), scene.grassY.toFloat() - 40f, (x0 + w).toFloat(), scene.height.toFloat()) {
                drawContext.canvas.save()
                drawContext.canvas.translate(0f, (scene.grassY + g.height).toFloat())
                drawContext.canvas.skew(skew, 0f)
                drawImage(g, dstOffset = IntOffset(0, -g.height), dstSize = IntSize(g.width, g.height), filterQuality = FilterQuality.Medium)
                drawContext.canvas.restore()
            }
        }
    }

    scene.vignette?.let { v ->
        drawImage(v, dstOffset = IntOffset.Zero, dstSize = IntSize(scene.width, scene.height), filterQuality = FilterQuality.Low)
    }
}

private val BirdColor = Color(0xFF3C4A55)

/** Three small birds glide across the upper sky every minute or so, wings beating slowly. */
private fun DrawScope.drawBirds(scene: LayeredScene, t: Float) {
    val loop = 64f
    val u = (t % loop) / loop
    val baseX = -200f + u * (scene.width + 400f)
    val baseY = scene.height * 0.17f - u * 60f
    val offsets = listOf(Triple(0f, 0f, 1f), Triple(-70f, 38f, 0.8f), Triple(-130f, -20f, 0.7f))
    for ((i, o) in offsets.withIndex()) {
        val (ox, oy, k) = o
        val flap = sin(t * 5.2f + i * 1.7f)
        val span = 26f * k
        val lift = 9f * k * flap
        val x = baseX + ox
        val y = baseY + oy + 4f * sin(t * 0.8f + i)
        val stroke = Stroke(width = 3.2f * k, cap = StrokeCap.Round)
        val path = androidx.compose.ui.graphics.Path().apply {
            moveTo(x - span, y - lift)
            quadraticTo(x - span * 0.45f, y - lift * 0.2f - 6f * k, x, y)
            quadraticTo(x + span * 0.45f, y - lift * 0.2f - 6f * k, x + span, y - lift)
        }
        drawPath(path, BirdColor.copy(alpha = 0.75f), style = stroke)
    }
}
