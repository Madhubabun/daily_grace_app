package com.dailygrace.app.data

import org.json.JSONArray
import org.json.JSONObject

/**
 * Parses the bundled content files. Kept free of Android types so it can be unit tested.
 * Invalid entries are skipped rather than crashing the app, so a typo in one new wallpaper
 * never takes the whole app down.
 */
object ContentParser {

    fun parseContent(json: String, imageExists: (String) -> Boolean = { true }): Content {
        val root = JSONObject(json)
        val t = root.optJSONObject("translation")
        val translation = Translation(
            code = t?.optString("code").orEmpty().ifBlank { "KJV" },
            name = t?.optString("name").orEmpty().ifBlank { "King James Version" },
            note = t?.optString("note").orEmpty(),
        )
        val entriesJson = root.optJSONArray("entries") ?: JSONArray()
        val seen = HashSet<String>()
        val entries = buildList {
            for (i in 0 until entriesJson.length()) {
                val o = entriesJson.optJSONObject(i) ?: continue
                val entry = parseEntry(o, i + 1) ?: continue
                if (!seen.add(entry.id)) continue
                if (!imageExists(entry.image)) continue
                add(entry)
            }
        }.sortedWith(compareBy({ it.dateIndex }, { it.id }))

        val declared = root.optJSONArray("categories").strings()
        // Categories used by entries but not declared still show up, so adding content never needs code changes.
        val used = entries.flatMap { it.categories }.distinct()
        val categories = declared + used.filter { it !in declared }
        return Content(translation, categories, entries)
    }

    private fun parseEntry(o: JSONObject, fallbackIndex: Int): GraceEntry? {
        val id = o.optString("id").trim()
        val verse = o.optString("verse").trim()
        val reference = o.optString("reference").trim()
        if (id.isEmpty() || verse.isEmpty() || reference.isEmpty()) return null
        val image = o.optString("image").trim().ifEmpty { "wallpaper_$id.jpg" }
        val categories = o.optJSONArray("categories").strings().ifEmpty {
            listOfNotNull(o.optString("theme").takeIf { it.isNotBlank() })
        }
        return GraceEntry(
            id = id,
            dateIndex = o.optInt("dateIndex", fallbackIndex),
            image = image,
            verse = verse,
            reference = reference,
            theme = o.optString("theme").trim(),
            categories = categories,
            reflection = o.optString("reflection").trim().takeIf { it.isNotEmpty() },
            prayer = o.optString("prayer").trim().takeIf { it.isNotEmpty() },
            layout = VerseLayout.parse(o.optString("layout")),
            focusY = o.optDouble("focusY", defaultFocus(VerseLayout.parse(o.optString("layout")))).toFloat().coerceIn(0f, 1f),
            excerpt = o.optBoolean("excerpt", false),
        )
    }

    /** With no explicit focus, the subject sits opposite the text. */
    private fun defaultFocus(layout: VerseLayout): Double = when (layout) {
        VerseLayout.TOP -> 0.6
        VerseLayout.CENTER -> 0.5
        VerseLayout.BOTTOM -> 0.4
    }

    fun parsePrayers(json: String): List<PrayerSection> {
        val root = JSONObject(json)
        val sections = root.optJSONArray("sections") ?: return emptyList()
        return buildList {
            for (i in 0 until sections.length()) {
                val s = sections.optJSONObject(i) ?: continue
                val list = s.optJSONArray("prayers") ?: JSONArray()
                val prayers = buildList {
                    for (j in 0 until list.length()) {
                        val p = list.optJSONObject(j) ?: continue
                        val text = p.optString("text").trim()
                        if (text.isEmpty()) continue
                        add(
                            Prayer(
                                id = p.optString("id").ifBlank { "${s.optString("id")}_$j" },
                                title = p.optString("title").trim(),
                                text = text,
                                reference = p.optString("reference").trim().takeIf { it.isNotEmpty() },
                                scripture = p.optBoolean("scripture", false),
                            )
                        )
                    }
                }
                if (prayers.isNotEmpty()) {
                    add(PrayerSection(s.optString("id"), s.optString("title"), s.optString("subtitle"), prayers))
                }
            }
        }
    }

    private fun JSONArray?.strings(): List<String> {
        if (this == null) return emptyList()
        return (0 until length()).mapNotNull { optString(it).trim().takeIf { s -> s.isNotEmpty() } }
    }
}
