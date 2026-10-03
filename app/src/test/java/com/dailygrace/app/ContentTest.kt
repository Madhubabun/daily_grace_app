package com.dailygrace.app

import com.dailygrace.app.data.ContentParser
import com.dailygrace.app.data.VerseLayout
import com.dailygrace.app.image.VerseStyle
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class ContentTest {
    private fun asset(path: String): File {
        val candidates = listOf(File("src/main/assets/$path"), File("app/src/main/assets/$path"))
        return candidates.first { it.exists() }
    }

    @Test
    fun bundledContentLoadsAndEveryImageExists() {
        val images = asset("wallpapers").list()!!.toSet()
        val thumbs = asset("wallpapers/thumbs").list()!!.toSet()
        val content = ContentParser.parseContent(asset("content/verses.json").readText())
        assertEquals("KJV", content.translation.code)
        assertTrue(content.entries.size >= 20)
        for (e in content.entries) {
            assertTrue("${e.id} image", e.image in images)
            assertTrue("${e.id} thumb", e.image in thumbs)
            assertTrue("${e.id} categories", e.categories.all { it in content.categories })
            assertFalse("${e.id} verse has no stray spaces", e.verse.contains(" ,") || e.verse.contains(" .") || e.verse.contains("  "))
        }
        assertEquals(content.entries.size, content.entries.map { it.id }.toSet().size)
    }

    @Test
    fun psalm23IsExactKjv() {
        val content = ContentParser.parseContent(asset("content/verses.json").readText())
        val e = content.entries.first { it.reference == "Psalm 23:1" }
        assertEquals("The LORD is my shepherd; I shall not want.", e.verse)
    }

    @Test
    fun brokenEntriesAreSkippedNotFatal() {
        val json = """
            {"entries":[
              {"id":"a","verse":"","reference":"x"},
              {"id":"b","verse":"Jesus wept.","reference":"John 11:35","layout":"centre","categories":["Jesus"]},
              {"id":"b","verse":"dup","reference":"dup"},
              {"id":"c","verse":"Pray without ceasing.","reference":"1 Thessalonians 5:17","image":"missing.jpg"}
            ]}
        """.trimIndent()
        val content = ContentParser.parseContent(json) { it != "missing.jpg" }
        assertEquals(listOf("b"), content.entries.map { it.id })
        assertEquals(VerseLayout.CENTER, content.entries[0].layout)
        assertEquals(listOf("Jesus"), content.categories)
    }

    @Test
    fun prayersLoad() {
        val sections = ContentParser.parsePrayers(asset("content/prayers.json").readText())
        assertTrue(sections.any { it.id == "morning" })
        assertTrue(sections.flatMap { it.prayers }.any { it.title.contains("Lord") && it.scripture })
    }

    @Test
    fun lordIsSetInSmallCapsOnlyAsAWholeWord() {
        val text = "“The LORD is my shepherd; LORDS and LORD’s”"
        val ranges = VerseStyle.smallCapRanges(text)
        assertEquals(2, ranges.size)
        assertEquals("ORD", text.substring(ranges[0].first, ranges[0].last + 1))
    }
}
