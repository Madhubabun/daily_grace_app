package com.dailygrace.app.data

/** Where the verse sits on the artwork. Chosen per wallpaper so text never covers the subject. */
enum class VerseLayout {
    TOP, CENTER, BOTTOM;

    companion object {
        fun parse(value: String?): VerseLayout = when (value?.trim()?.lowercase()) {
            "top", "upper" -> TOP
            "center", "centre", "middle" -> CENTER
            else -> BOTTOM
        }
    }
}

data class Translation(val code: String, val name: String, val note: String)

data class GraceEntry(
    val id: String,
    val dateIndex: Int,
    val image: String,
    val verse: String,
    val reference: String,
    val theme: String,
    val categories: List<String>,
    val reflection: String?,
    val prayer: String?,
    val layout: VerseLayout,
    /** Vertical centre of the important artwork, 0..1. Used to bias cropping. */
    val focusY: Float,
    val excerpt: Boolean,
) {
    val imagePath: String get() = "wallpapers/$image"
    val thumbPath: String get() = "wallpapers/thumbs/$image"
}

data class Content(
    val translation: Translation,
    val categories: List<String>,
    val entries: List<GraceEntry>,
) {
    private val byId = entries.associateBy { it.id }
    fun entry(id: String): GraceEntry? = byId[id]
    fun inCategory(category: String): List<GraceEntry> = entries.filter { category in it.categories }
}

data class Prayer(
    val id: String,
    val title: String,
    val text: String,
    val reference: String?,
    val scripture: Boolean,
)

data class PrayerSection(
    val id: String,
    val title: String,
    val subtitle: String,
    val prayers: List<Prayer>,
)
