package com.dailygrace.app.actions

import android.app.WallpaperManager
import android.content.Context
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.render.GraceRenderer
import com.dailygrace.app.render.RenderTarget
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

enum class WallpaperDestination { HOME, LOCK, BOTH }

/**
 * Applies a static, full-resolution wallpaper rendered at the phone's exact screen size, so the
 * system never has to zoom or re-crop it.
 */
object WallpaperApplier {

    suspend fun apply(
        context: Context,
        entry: GraceEntry,
        destination: WallpaperDestination,
        includeVerse: Boolean,
    ): Result<Unit> = withContext(Dispatchers.Default) {
        runCatching {
            val app = context.applicationContext as DailyGraceApp
            val art = app.images.loadFull(entry.imagePath) ?: error("Artwork could not be loaded")
            val (w, h) = physicalScreenSize(context)
            val bitmap = GraceRenderer.render(context, art, entry, w, h, RenderTarget.WALLPAPER, includeVerse)
            art.recycle()
            val wm = WallpaperManager.getInstance(context)
            if (!wm.isWallpaperSupported || !wm.isSetWallpaperAllowed) error("This phone does not allow changing the wallpaper")
            runCatching { wm.suggestDesiredDimensions(w, h) }
            val flags = when (destination) {
                WallpaperDestination.HOME -> WallpaperManager.FLAG_SYSTEM
                WallpaperDestination.LOCK -> WallpaperManager.FLAG_LOCK
                WallpaperDestination.BOTH -> WallpaperManager.FLAG_SYSTEM or WallpaperManager.FLAG_LOCK
            }
            withContext(Dispatchers.IO) { wm.setBitmap(bitmap, null, true, flags) }
            bitmap.recycle()
            Unit
        }
    }
}
