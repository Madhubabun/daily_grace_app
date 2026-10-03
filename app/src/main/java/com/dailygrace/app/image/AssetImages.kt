package com.dailygrace.app.image

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.LruCache
import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import com.dailygrace.app.DailyGraceApp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Decodes bundled artwork at the size it is shown and keeps recent bitmaps in memory. */
class AssetImages(private val context: Context) {
    private val cache = object : LruCache<String, Bitmap>(cacheBytes()) {
        override fun sizeOf(key: String, value: Bitmap) = value.allocationByteCount
    }
    private val luminance = HashMap<String, Float>()

    fun cached(path: String, targetWidth: Int): Bitmap? = cache.get(key(path, sampleFor(path, targetWidth)))

    suspend fun load(path: String, targetWidth: Int): Bitmap? = withContext(Dispatchers.IO) {
        val sample = sampleFor(path, targetWidth)
        val key = key(path, sample)
        cache.get(key) ?: decode(path, sample)?.also { cache.put(key, it) }
    }

    /** Full-resolution decode for wallpaper and share rendering; not cached. */
    suspend fun loadFull(path: String): Bitmap? = withContext(Dispatchers.IO) { decode(path, 1) }

    /**
     * Average luminance of the band of the artwork where the verse sits, measured on the
     * thumbnail. Lets every wallpaper get just enough scrim without per-image tuning.
     */
    suspend fun bandLuminance(thumbPath: String, bandCenter: Float, bandHalfHeight: Float = 0.13f): Float =
        withContext(Dispatchers.IO) {
            val k = "$thumbPath@$bandCenter"
            synchronized(luminance) { luminance[k] }?.let { return@withContext it }
            val bmp = load(thumbPath, 216) ?: return@withContext 0.5f
            val y0 = ((bandCenter - bandHalfHeight) * bmp.height).toInt().coerceIn(0, bmp.height - 1)
            val y1 = ((bandCenter + bandHalfHeight) * bmp.height).toInt().coerceIn(y0 + 1, bmp.height)
            val x0 = (bmp.width * 0.1f).toInt()
            val x1 = (bmp.width * 0.9f).toInt()
            var sum = 0.0
            var n = 0
            var y = y0
            while (y < y1) {
                var x = x0
                while (x < x1) {
                    val c = bmp.getPixel(x, y)
                    val r = (c shr 16 and 0xff) / 255.0
                    val g = (c shr 8 and 0xff) / 255.0
                    val b = (c and 0xff) / 255.0
                    sum += 0.2126 * r + 0.7152 * g + 0.0722 * b
                    n++
                    x += 3
                }
                y += 3
            }
            val lum = if (n == 0) 0.5f else (sum / n).toFloat()
            synchronized(luminance) { luminance[k] = lum }
            lum
        }

    private fun sampleFor(path: String, targetWidth: Int): Int {
        if (targetWidth <= 0) return 1
        val isThumb = path.contains("/thumbs/")
        val sourceWidth = if (isThumb) 432 else 1440
        var sample = 1
        while (sourceWidth / (sample * 2) >= targetWidth) sample *= 2
        return sample
    }

    private fun key(path: String, sample: Int) = "$path#$sample"

    private fun decode(path: String, sample: Int): Bitmap? = try {
        context.assets.open(path).use { input ->
            BitmapFactory.decodeStream(input, null, BitmapFactory.Options().apply {
                inSampleSize = sample
                inPreferredConfig = Bitmap.Config.ARGB_8888
            })
        }
    } catch (e: Exception) {
        null
    }

    private companion object {
        fun cacheBytes(): Int = (Runtime.getRuntime().maxMemory() / 6).coerceAtMost(96L * 1024 * 1024).toInt()
    }
}

/** Loads an asset bitmap for display. Returns the cached image immediately when available. */
@Composable
fun rememberAssetImage(path: String, targetWidthPx: Int): State<ImageBitmap?> {
    val images = (LocalContext.current.applicationContext as DailyGraceApp).images
    val state = remember(path, targetWidthPx) { mutableStateOf(images.cached(path, targetWidthPx)?.asImageBitmap()) }
    LaunchedEffect(path, targetWidthPx) {
        if (state.value == null) state.value = images.load(path, targetWidthPx)?.asImageBitmap()
    }
    return state
}
