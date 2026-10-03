package com.dailygrace.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

/** Loads the bundled verses and prayers from assets/content once and keeps them in memory. */
class ContentRepository(private val context: Context) {
    private val mutex = Mutex()
    @Volatile private var content: Content? = null
    @Volatile private var prayers: List<PrayerSection>? = null

    suspend fun content(): Content = content ?: mutex.withLock {
        content ?: withContext(Dispatchers.IO) { loadContent() }.also { content = it }
    }

    suspend fun prayers(): List<PrayerSection> = prayers ?: withContext(Dispatchers.IO) {
        ContentParser.parsePrayers(readAsset("content/prayers.json"))
    }.also { prayers = it }

    /** For broadcast receivers, which run briefly off the UI. */
    fun contentBlocking(): Content = content ?: loadContent().also { content = it }

    private fun loadContent(): Content {
        val images = context.assets.list("wallpapers")?.toSet().orEmpty()
        val parsed = ContentParser.parseContent(readAsset("content/verses.json")) { it in images }
        check(parsed.entries.isNotEmpty()) { "No verses could be loaded" }
        return parsed
    }

    private fun readAsset(path: String): String =
        context.assets.open(path).bufferedReader(Charsets.UTF_8).use { it.readText() }
}
