package com.dailygrace.app.actions

import android.content.ClipData
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import androidx.core.content.FileProvider
import com.dailygrace.app.DailyGraceApp
import com.dailygrace.app.data.GraceEntry
import com.dailygrace.app.render.GraceRenderer
import com.dailygrace.app.render.RenderTarget
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/** Builds a 1080x1920 image (artwork, verse, reference, small branding) and opens the share sheet. */
object Sharer {
    private const val SHARE_W = 1080
    private const val SHARE_H = 1920

    suspend fun share(context: Context, entry: GraceEntry, translationCode: String): Result<Unit> = runCatching {
        val file = withContext(Dispatchers.Default) {
            val app = context.applicationContext as DailyGraceApp
            val art = app.images.loadFull(entry.imagePath) ?: error("Artwork could not be loaded")
            val bitmap = GraceRenderer.render(context, art, entry, SHARE_W, SHARE_H, RenderTarget.SHARE, true)
            art.recycle()
            val dir = File(context.cacheDir, "shared").apply { mkdirs() }
            dir.listFiles()?.forEach { it.delete() }
            val f = File(dir, "daily-grace-${entry.id}.jpg")
            withContext(Dispatchers.IO) {
                f.outputStream().use { bitmap.compress(Bitmap.CompressFormat.JPEG, 92, it) }
            }
            bitmap.recycle()
            f
        }
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.shares", file)
        val caption = "“${entry.verse}”\n${entry.reference} ($translationCode)"
        val send = Intent(Intent.ACTION_SEND).apply {
            type = "image/jpeg"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_TEXT, caption)
            clipData = ClipData.newRawUri("Daily Grace", uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        val chooser = Intent.createChooser(send, "Share today’s grace").apply {
            if (context !is android.app.Activity) addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(chooser)
    }
}
